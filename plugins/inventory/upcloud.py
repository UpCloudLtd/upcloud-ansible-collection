__metaclass__ = type

DOCUMENTATION = r'''
    name: upcloud
    author:
      - Antti Myyrä (@ajmyyra)
    short_description: Ansible dynamic inventory plugin for UpCloud.
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
            choices: ["community.upcloud.upcloud"]
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
        connect_with:
            description: Connect to the server with the specified choice.
            default: public_ipv4
            type: str
            choices:
                - public_ipv4
                - public_ipv6
                - hostname
                - private_ipv4
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
          description: Populate inventory with instances having these labels
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
plugin: community.upcloud.upcloud

# Example with locations, types, groups, username and password
plugin: community.upcloud.upcloud
username: YOUR_USERNAME
password: YOUR_PASSWORD
zones:
  - nl-ams1
labels:
  - role=prod
  - foo

# Group by a zone with prefix e.g. "upcloud_zone_us-nyc1"
# and state with prefix e.g. "server_state_running"
plugin: community.upcloud.upcloud
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

        self.client = upcloud_api.CloudManager(self.username, self.password)
        self.client.api.user_agent = "upcloud-ansible-inventory/{0}".format(__version__)

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
                disqualified = False
                for wanted_label in self.get_option("labels"):
                    server_labels = _parse_server_labels(server.labels['label'])
                    for server_label in server_labels:
                        display.vvvv(f"Comparing {wanted_label} against {server_label}")
                        if wanted_label not in server_label:
                            disqualified = True

                if not disqualified:
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
                        if server.uuid == net_server.uuid:
                            tmp.append(server)

            self.servers = tmp

    def _set_server_attributes(self, server):
        server_details = self._fetch_server_details(server.uuid)

        self.inventory.set_variable(server.hostname, "id", to_native(server.uuid))
        self.inventory.set_variable(server.hostname, "hostname", to_native(server.hostname))
        self.inventory.set_variable(server.hostname, "state", to_native(server.state))
        self.inventory.set_variable(server.hostname, "zone", to_native(server.zone))
        self.inventory.set_variable(server.hostname, "firewall", to_native(server_details.firewall))
        self.inventory.set_variable(server.hostname, "plan", to_native(server.plan))
        self.inventory.set_variable(server.hostname, "tags", list(server_details.tags))
        self.inventory.set_variable(server.hostname, "metadata", to_native(server_details.metadata))
        self.inventory.set_variable(server.hostname, "labels", list(_parse_server_labels(server.labels["label"])))

        ipv4_addrs = []
        ipv6_addrs = []
        publ_addrs = []
        priv_addrs = []
        for iface in server_details.networking["interfaces"]["interface"]:
            for addr in iface["ip_addresses"]["ip_address"]:
                address = addr.get("address")

                if addr.get("family") == "IPv4":
                    ipv4_addrs.append(address)
                else:
                    ipv6_addrs.append(address)

                if iface.get("type") == "public":
                    publ_addrs.append(address)
                else:
                    priv_addrs.append(address)

        connect_with = self.get_option("connect_with")
        if connect_with == "public_ipv4":
            possible_addresses = list(set(ipv4_addrs) & set(publ_addrs))
            if len(possible_addresses) == 0:
                raise AnsibleError(
                    "No available public IPv4 addresses for server {0} ({1})".format(server.uuid, server.hostname)
                )
            self.inventory.set_variable(server.hostname, "ansible_host", to_native(possible_addresses[0]))
        elif connect_with == "public_ipv6":
            possible_addresses = list(set(ipv6_addrs) & set(publ_addrs))
            if len(possible_addresses) == 0:
                raise AnsibleError(
                    "No available public IPv6 addresses for server {0} ({1})".format(server.uuid, server.hostname)
                )
            self.inventory.set_variable(server.hostname, "ansible_host", to_native(possible_addresses[0]))
        elif connect_with == "hostname":
            self.inventory.set_variable(server.hostname, "ansible_host", to_native(server.hostname))
        elif connect_with == "private_ipv4":
            if self.get_option("network"):
                for iface in server_details.networking["interfaces"]["interface"]:
                    if iface.network == self.network.uuid:
                        self.inventory.set_variable(
                            server.hostname,
                            "ansible_host",
                            to_native(iface["ip_addresses"]["ip_address"][0].get("address"))
                        )
            else:
                raise AnsibleError("You can only connect with private IPv4 if you specify a network")

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
            self.inventory.add_host(server.hostname, group="upcloud")
            self._set_server_attributes(server)

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
            raise AnsibleError("UpCloud dynamic inventory plugin requires upcloud-api Python module")

        self._read_config_data(path)

        self._populate()


def _parse_server_labels(labels: List):
    processed = []

    for label in labels:
        processed.append(f"{label['key']}={label['value']}")

    return processed
