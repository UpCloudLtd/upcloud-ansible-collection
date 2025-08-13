__metaclass__ = type

DOCUMENTATION = r'''
    name: servers
    author:
      - Antti Myyrä (@ajmyyra)
      - UpCloud (@UpCloudLtd)
    short_description: Ansible dynamic inventory plugin for UpCloud servers.
    requirements:
        - python >= 3.7
        - upcloud-api >= 2.5.0
    description:
        - Reads inventories from UpCloud API.
        - Uses a YAML configuration file that ends with upcloud.(yml|yaml).
    extends_documentation_fragment:
        - constructed
    options:
        plugin:
            description: The name of the UpCloud Ansible inventory plugin
            required: true
            choices: ["upcloud.cloud.servers"]
        username:
            description: UpCloud API username.
            required: false
        username_env:
            description: Environment variable to load the UpCloud API username from.
            default: UPCLOUD_USERNAME
            type: str
            required: false
        password:
            description: UpCloud API password.
            required: false
        password_env:
            description: Environment variable to load the UpCloud API username from.
            default: UPCLOUD_PASSWORD
            type: str
            required: false
        token:
            description: UpCloud API token.
            required: false
        token_env:
            description: Environment variable to load the UpCloud API token from.
            default: UPCLOUD_TOKEN
            type: str
            required: false
        connect_with:
            description: Connect to the server with the specified choice. Server is skipped if chosen type is not available.
            default: public_ipv4
            type: str
            choices:
                - public_ipv4
                - public_ipv6
                - hostname
                - private_ipv4
                - utility_ipv4
        server_group:
            description: Populate inventory with instances in this server group (UUID or title)
            default: ""
            type: str
            required: false
        zones:
            description: Populate inventory with instances in these zones.
            default: []
            type: list
            elements: str
            required: false
        tags:
            description: Populate inventory with instances with these tags.
            default: []
            type: list
            elements: str
            required: false
        labels:
            description: Populate inventory with instances with any of these labels, either just key or value ("foo" or "bar") or as a whole tag ("foo=bar")
            default: []
            type: list
            elements: str
            required: false
        states:
            description: Populate inventory with instances with these states.
            default: []
            type: list
            elements: str
            required: false
        network:
            description: Populate inventory with instances which are attached to this network name or UUID.
            default: ""
            type: str
            required: false
'''

EXAMPLES = r"""
# Minimal example. `UPCLOUD_USERNAME` and `UPCLOUD_PASSWORD` are available as environment variables.
plugin: upcloud.cloud.servers

# Example with username and password
plugin: upcloud.cloud.servers
username: YOUR_USERNAME
password: YOUR_PASSWORD
zones:
  - nl-ams1
labels:
  - role=prod
  - foo

# Example with locations, labels and server_group
plugin: upcloud.cloud.servers
zones:
  - es-mad1
  - fi-hel2
labels:
  - role=prod
  - foo
server_group: group name or uuid

# Group by a zone with prefix e.g. "upcloud_zone_us-nyc1"
# and state with prefix e.g. "server_state_running"
plugin: upcloud.cloud.servers
keyed_groups:
  - key: zone
    prefix: upcloud_zone
  - key: state
    prefix: server_state
"""

import os
from typing import List
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable
from ansible.release import __version__
from ansible.utils.display import Display

display = Display()

try:
    import upcloud_api
    from upcloud_api.errors import UpCloudAPIError
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False


class NoAvailableAddressException(Exception):
    """Raised when requested address type is not available"""
    pass


class InventoryModule(BaseInventoryPlugin, Constructable):
    name = 'upcloud'

    def _initialize_upcloud_client(self):
        self.username_env = self.get_option("username_env")
        self.username = self.templar.template(self.get_option("username"), fail_on_undefined=False) or os.getenv(
            self.username_env
        )
        self.password_env = self.get_option("password_env")
        self.password = self.templar.template(self.get_option("password"), fail_on_undefined=False) or os.getenv(
            self.password_env
        )
        self.token_env = self.get_option("token_env")
        self.token = self.templar.template(self.get_option("token"), fail_on_undefined=False) or os.getenv(
            self.token_env
        )

        # Token support was added in upcloud-api 2.8.0, older versions will raise TypeError if token is provided.
        # Ignore the error if token is not provided, in which case older version should work as well.
        try:
            self.client = upcloud_api.CloudManager(
                username=self.username,
                password=self.password,
                token=self.token,
            )
        except TypeError:
            if self.token:
                raise AnsibleError(
                    'The version of upcloud-api you are using does not support token authentication. '
                    'Update upcloud-api to version 2.8.0 or later.'
                ) from None
            self.client = upcloud_api.CloudManager(self.username, self.password)

        self.client.api.user_agent = f"upcloud-ansible-inventory/{__version__}"

        api_root_env = "UPCLOUD_API_ROOT"
        if os.getenv(api_root_env):
            self.client.api.api_root = os.getenv(api_root_env)

    def _test_upcloud_credentials(self):
        try:
            self.client.authenticate()
        except UpCloudAPIError:
            raise AnsibleError("Invalid UpCloud API credentials.")

    def _fetch_servers(self):
        return self.client.get_servers()

    def _fetch_server_details(self, uuid):
        return self.client.get_server(uuid)

    def _fetch_network_details(self, uuid):
        return self.client.get_network(uuid)

    def _fetch_server_groups(self):
        return self.client.api.get_request("/server-group/")

    def _get_servers(self):
        self.servers = self._fetch_servers()

    def _filter_servers(self):
        if self.get_option("zones"):
            display.vv("Choosing servers by zone")
            tmp = []
            for server in self.servers:
                if server.zone in self.get_option("zones"):
                    tmp.append(server)

            self.servers = tmp

        if self.get_option("states"):
            display.vv("Choosing servers by server state")
            tmp = []
            for server in self.servers:
                if server.state in self.get_option("states"):
                    tmp.append(server)

            self.servers = tmp

        if self.get_option("tags"):
            display.vv("Choosing servers by tags")
            tmp = []
            for server in self.servers:
                disqualified = False
                for tag in self.get_option("tags"):
                    if tag not in server.tags:
                        disqualified = True

                if not disqualified:
                    tmp.append(server)

            self.servers = tmp

        if self.get_option("labels"):
            display.vv("Choosing servers by labels")
            tmp = []
            for server in self.servers:
                for wanted_label in self.get_option("labels"):
                    server_labels = _parse_server_labels(server.labels['label'])
                    for server_label in server_labels:
                        display.vvvv(f"Comparing wanted label {wanted_label} against labels {server_label} of server {server.hostname}")
                        if wanted_label in server_label:
                            tmp.append(server)

            self.servers = tmp

        if self.get_option("network"):
            display.vv("Choosing servers by network")
            try:
                self.network = self._fetch_network_details(self.get_option("network"))
            except UpCloudAPIError as exp:
                raise AnsibleError(str(exp))

            tmp = []
            if getattr(self.network, "servers"):
                for server in self.servers:
                    for net_server in self.network.servers["server"]:
                        if server.uuid == net_server["uuid"]:
                            tmp.append(server)

            self.servers = tmp

        if self.get_option("server_group"):
            display.vv("Choosing servers by server group")
            wanted_group = self.get_option("server_group")

            try:
                raw_groups = self._fetch_server_groups()
                groups = raw_groups["server_groups"]["server_group"]
            except UpCloudAPIError as exp:
                raise AnsibleError(str(exp))

            tmp = []
            server_group = None
            for group in groups:
                if str(wanted_group).lower() in [group["uuid"].lower(), group["title"].lower()]:
                    server_group = group["uuid"]
                    break

            if not server_group:
                raise AnsibleError(f"Requested server group {wanted_group} does not exist")

            for server in self.servers:
                if server.server_group == server_group:
                    tmp.append(server)

            self.servers = tmp

    def _get_server_attributes(self, server):
        server_details = self._fetch_server_details(server.uuid)

        def _new_attribute(key, attribute):
            return {"key": key, "attribute": attribute}

        attributes = [
            _new_attribute("id", to_native(server.uuid)),
            _new_attribute("hostname", to_native(server.hostname)),
            _new_attribute("state", to_native(server.state)), _new_attribute("zone", to_native(server.zone)),
            _new_attribute("firewall", to_native(server_details.firewall)),
            _new_attribute("plan", to_native(server.plan)), _new_attribute("tags", list(server_details.tags)),
            _new_attribute("metadata", to_native(server_details.metadata)),
            _new_attribute("labels", list(_parse_server_labels(server.labels["label"]))),
            _new_attribute("server_group", to_native(server_details.server_group))
        ]

        ipv4_addrs = []
        ipv6_addrs = []
        publ_addrs = []
        util_addrs = []
        for iface in server_details.networking["interfaces"]["interface"]:
            for addr in iface["ip_addresses"]["ip_address"]:
                address = addr.get("address")

                if addr.get("family") == "IPv4":
                    ipv4_addrs.append(address)
                else:
                    ipv6_addrs.append(address)
                if iface.get("type") == "public":
                    publ_addrs.append(address)
                if iface.get("type") == "utility":
                    util_addrs.append(address)

        public_ipv4 = list(set(ipv4_addrs) & set(publ_addrs))
        public_ipv6 = list(set(ipv6_addrs) & set(publ_addrs))

        # We default to IPv4 when available
        if len(public_ipv4) > 0:
            attributes.append(_new_attribute("public_ip", to_native(public_ipv4[0])))
        elif len(public_ipv6) > 0:
            attributes.append(_new_attribute("public_ip", to_native(public_ipv4[0])))

        if len(util_addrs) > 0:
            attributes.append(_new_attribute("utility_ip", to_native(util_addrs[0])))

        connect_with = self.get_option("connect_with")
        if connect_with == "public_ipv4":
            if len(public_ipv4) == 0:
                raise NoAvailableAddressException(
                    f"No available public IPv4 addresses for server {server.uuid} ({server.hostname})")
            attributes.append(_new_attribute("ansible_host", to_native(public_ipv4[0])))

        elif connect_with == "public_ipv6":
            if len(public_ipv6) == 0:
                raise NoAvailableAddressException(
                    f"No available public IPv6 addresses for server {server.uuid} ({server.hostname})")
            attributes.append(_new_attribute("ansible_host", to_native(public_ipv6[0])))
        elif connect_with == "utility_ipv4":
            if len(util_addrs) == 0:
                raise NoAvailableAddressException(
                    f"No available utility addresses for server {server.uuid} ({server.hostname})")
            attributes.append(_new_attribute("ansible_host", to_native(util_addrs[0])))
        elif connect_with == "hostname":
            attributes.append(_new_attribute("ansible_host", to_native(server.hostname)))
        elif connect_with == "private_ipv4":
            if self.get_option("network"):
                for iface in server_details.networking["interfaces"]["interface"]:
                    if iface["network"] == self.network.uuid:
                        attributes.append(_new_attribute(
                            "ansible_host",
                            to_native(iface["ip_addresses"]["ip_address"][0].get("address")))
                        )
            else:
                raise AnsibleError("You can only connect with private IPv4 if you specify a network")

        return attributes

    def verify_file(self, path):
        """Return if a file can be used by this plugin"""
        return (
            super(InventoryModule, self).verify_file(path) and
            path.endswith(("upcloud.yaml", "upcloud.yml"))
        )

    def _populate(self):
        self._initialize_upcloud_client()
        self._test_upcloud_credentials()
        self._get_servers()
        self._filter_servers()

        # Add 'upcloud' as a top group
        self.inventory.add_group(group="upcloud")

        for server in self.servers:
            display.vv(f"Evaluating server {server.uuid} ({server.hostname})")

            try:
                attributes = self._get_server_attributes(server)
            except NoAvailableAddressException as e:
                display.vv(str(e))
                display.v(
                    f"Skipping server {server.hostname} as it doesn't have requested connection "
                    f"type ({self.get_option('connect_with')}) available"
                )
                continue

            self.inventory.add_host(server.hostname, group="upcloud")
            for attr in attributes:
                self.inventory.set_variable(server.hostname, attr["key"], attr["attribute"])

            strict = self.get_option('strict')

            # Composed variables
            self._set_composite_vars(self.get_option('compose'), self.inventory.get_host(server.hostname).get_vars(),
                                     server.hostname, strict=strict)

            # Complex groups based on jinja2 conditionals, hosts that meet the conditional are added to group
            self._add_host_to_composed_groups(self.get_option('groups'), {}, server.hostname, strict=strict)

            # Create groups based on variable values and add the corresponding hosts to it
            self._add_host_to_keyed_groups(self.get_option('keyed_groups'), {}, server.hostname, strict=strict)

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        if not UC_AVAILABLE:
            raise AnsibleError(
                "UpCloud dynamic inventory plugin requires upcloud-api Python module, "
                + "see https://pypi.org/project/upcloud-api/")

        self._read_config_data(path)

        self._populate()


def _parse_server_labels(labels: List):
    processed = []

    for label in labels:
        processed.append(f"{label['key']}={label['value']}")

    return processed
