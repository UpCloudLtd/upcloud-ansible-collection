import os

try:
    import upcloud_api
    from upcloud_api.errors import UpCloudAPIError
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False


# This value will be replaced in build-and-release workflow
VERSION = "dev"


def initialize_upcloud_client(username=None, password=None, token=None):
    if not UC_AVAILABLE:
        raise RuntimeError(
            "UpCloud Ansible collection requires upcloud-api Python module, "
            + "see https://pypi.org/project/upcloud-api/")

    # Token support was added in upcloud-api 2.8.0, older versions will raise TypeError if token is provided.
    # Ignore the error if token is not provided, in which case older version should work as well.
    try:
        credentials = upcloud_api.Credentials.parse(
            username=username,
            password=password,
            token=token,
        )
        client = upcloud_api.CloudManager(**credentials.dict)
    except (AttributeError, TypeError):
        try:
            client = upcloud_api.CloudManager(username, password)
        except Exception:
            raise RuntimeError(
                'Invalid or missing UpCloud API credentials. '
                'The version of upcloud-api you are using does not support token authentication or parsing credentials from the environment. '
                'Update upcloud-api to version 2.8.0 or later.'
            ) from None

    version = VERSION
    client.api.user_agent = f"upcloud-ansible-collection/{version}"

    api_root_env = "UPCLOUD_API_ROOT"
    if os.getenv(api_root_env):
        client.api.api_root = os.getenv(api_root_env)

    try:
        client.authenticate()
    except UpCloudAPIError:
        raise RuntimeError("Invalid UpCloud API credentials.")

    return client
