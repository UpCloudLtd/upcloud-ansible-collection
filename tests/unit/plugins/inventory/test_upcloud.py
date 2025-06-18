__metaclass__ = type

import pytest

from ansible.inventory.data import InventoryData
from .....plugins.inventory.servers import InventoryModule


class Server:
    """
    Simple class representation of UpCloud Server instance for testing purposes.
    """

    updateable_fields = [
        'boot_order',
        'core_number',
        'firewall',
        'hostname',
        'labels',
        'memory_amount',
        'nic_model',
        'plan',
        'simple_backup',
        'title',
        'timezone',
        'video_model',
        'vnc',
        'vnc_password',
    ]

    optional_fields = [
        'avoid_host',
        'boot_order',
        'core_number',
        'firewall',
        'labels',
        'login_user',
        'memory_amount',
        'networking',
        'nic_model',
        'password_delivery',
        'plan',
        'server_group',
        'simple_backup',
        'timezone',
        'metadata',
        'user_data',
        'video_model',
        'vnc_password',
    ]

    def __init__(self, **entries):
        self.__dict__.update(entries)


class Network:
    """
    Simple class representation of UpCloud Network instance for testing purposes.
    """

    ATTRIBUTES = {
        'name': None,
        'type': None,
        'uuid': None,
        'zone': None,
        'ip_networks': None,
        'servers': None,
    }

    def __init__(self, **entries):
        self.__dict__.update(entries)


@pytest.fixture()
def inventory():
    r = InventoryModule()
    r.inventory = InventoryData()
    return r


def test_verify_file_bad_config(inventory):
    assert inventory.verify_file('upcloud_notvalid.yml') is False


def get_servers():
    servers_response = [
        {
            'core_number': '2',
            'created': 1599136169,
            'hostname': 'server1',
            'labels': {
                'label': []
            },
            'license': 0,
            'memory_amount': '4096',
            'plan': '2xCPU-4GB',
            'plan_ipv4_bytes': '0',
            'plan_ipv6_bytes': '0',
            'simple_backup': 'no',
            'state': 'started',
            'title': 'Server #1',
            'uuid': '00229adf-0e46-49b5-a8f7-cbd638d11f6a',
            'zone': 'de-fra1',
            'tags': ['foo', 'bar']
        },
        {
            'core_number': '1',
            'created': 1598526425,
            'hostname': 'server2',
            'labels': {
                'label': [
                    {
                        'key': 'foo',
                        'value': 'bar'
                    }
                ]
            },
            'license': 0,
            'memory_amount': '2048',
            'plan': '1xCPU-2GB',
            'plan_ipv4_bytes': '0',
            'plan_ipv6_bytes': '0',
            'simple_backup': 'no',
            'state': 'stopped',
            'title': 'Server #2',
            'uuid': '004d5201-e2ff-4325-7ac6-a274f1c517b7',
            'zone': 'nl-ams1',
            'tags': []
        },
        {
            'core_number': '1',
            'created': 1598526319,
            'hostname': 'server3',
            'labels': {
                'label': [
                    {
                        'key': 'foo',
                        'value': 'bar'
                    },
                    {
                        'key': 'private',
                        'value': 'yes'
                    }
                ]
            },
            'license': 0,
            'memory_amount': '2048',
            'plan': '1xCPU-2GB',
            'plan_ipv4_bytes': '0',
            'plan_ipv6_bytes': '0',
            'simple_backup': 'no',
            'state': 'started',
            'title': 'Server #3',
            'uuid': '0003295f-343a-44a2-8080-fb8196a6802a',
            'zone': 'nl-ams1',
            'tags': []
        }
    ]

    server_list = list()
    for server in servers_response:
        server_list.append(Server(**server))

    return server_list


def get_server1_details():
    return Server(**{
        'boot_order': 'disk',
        'core_number': '2',
        'created': 1599136169,
        'firewall': 'on',
        'hostname': 'server1',
        'labels': {
            'label': []
        },
        'license': 0,
        'memory_amount': '4096',
        'metadata': 'no',
        'networking': {
            'interfaces': {
                'interface': [
                    {
                        'bootable': 'no',
                        'index': 1,
                        'ip_addresses': {
                            'ip_address': [
                                {
                                    'address': '1.1.1.10',
                                    'family': 'IPv4',
                                    'floating': 'no'
                                },
                                {
                                    'address': '1.1.1.11',
                                    'family': 'IPv4',
                                    'floating': 'yes'
                                }
                            ]
                        },
                        'mac': '3b:a6:ba:4a:13:01',
                        'network': '031437b4-0f8c-483c-96f2-eca5be02909c',
                        'source_ip_filtering': 'yes',
                        'type': 'public'
                    }
                ]
            }
        },
        'nic_model': 'virtio',
        'plan': '2xCPU-4GB',
        'plan_ipv4_bytes': '0',
        'plan_ipv6_bytes': '0',
        'remote_access_enabled': 'no',
        'remote_access_password': 'barFoo5',
        'remote_access_type': 'vnc',
        'simple_backup': 'no',
        'state': 'started',
        'timezone': 'UTC',
        'title': 'Server #1',
        'uuid': '00229adf-0e46-49b5-a8f7-cbd638d11f6a',
        'video_model': 'vga',
        'zone': 'de-fra1',
        'tags': ['foo', 'bar']
    })


def get_server2_details():
    return Server(**{
        'boot_order': 'disk',
        'core_number': '1',
        'created': 1598526425,
        'firewall': 'on',
        'hostname': 'server2',
        'labels': {
            'label': [
                {
                    'key': 'foo',
                    'value': 'bar'
                }
            ]
        },
        'license': 0,
        'memory_amount': '2048',
        'metadata': 'no',
        'networking': {
            'interfaces': {
                'interface': [
                    {
                        'bootable': 'no',
                        'index': 1,
                        'ip_addresses': {
                            'ip_address': [
                                {
                                    'address': '1.1.1.12',
                                    'family': 'IPv4',
                                    'floating': 'no'
                                }
                            ]
                        },
                        'mac': '3b:a6:ba:4a:2c:d6',
                        'network': '031437b4-0f8c-483c-96f2-eca5be02909c',
                        'source_ip_filtering': 'yes',
                        'type': 'public'
                    }
                ]
            }
        },
        'nic_model': 'virtio',
        'plan': '1xCPU-2GB',
        'plan_ipv4_bytes': '0',
        'plan_ipv6_bytes': '0',
        'remote_access_enabled': 'no',
        'remote_access_password': 'fooBar',
        'remote_access_type': 'vnc',
        'simple_backup': 'no',
        'state': 'stopped',
        'timezone': 'UTC',
        'title': 'Server #2',
        'uuid': '004d5201-e2ff-4325-7ac6-a274f1c517b7',
        'video_model': 'vga',
        'zone': 'nl-ams1',
        'tags': [],
    })


def get_server3_details():
    return Server(**{
        'boot_order': 'disk',
        'core_number': '1',
        'created': 1598526319,
        'firewall': 'on',
        'hostname': 'server3',
        'labels': {
            'label': [
                {
                    'key': 'foo',
                    'value': 'bar'
                },
                {
                    'key': 'private',
                    'value': 'yes'
                }
            ]
        },
        'license': 0,
        'memory_amount': '2048',
        'metadata': 'yes',
        'networking': {
            'interfaces': {
                'interface': [
                    {
                        'bootable': 'no',
                        'index': 1,
                        'ip_addresses': {
                            'ip_address': [
                                {
                                    'address': '172.16.0.3',
                                    'family': 'IPv4',
                                    'floating': 'no'
                                }
                            ]
                        },
                        'mac': '3b:a6:ba:4a:4b:10',
                        'network': '035146a5-7a85-408b-b1f8-21925164a7d3',
                        'source_ip_filtering': 'yes',
                        'type': 'private'
                    }
                ]
            }
        },
        'nic_model': 'virtio',
        'plan': '1xCPU-2GB',
        'plan_ipv4_bytes': '0',
        'plan_ipv6_bytes': '0',
        'remote_access_enabled': 'no',
        'remote_access_password': 'fooBar',
        'remote_access_type': 'vnc',
        'simple_backup': 'no',
        'state': 'started',
        'timezone': 'UTC',
        'title': 'Server #3',
        'uuid': '0003295f-343a-44a2-8080-fb8196a6802a',
        'video_model': 'vga',
        'zone': 'nl-ams1',
        'tags': [],
    })


def get_network_details(uuid):
    return Network(**{
        "name": "Test private net",
        "type": "private",
        "uuid": uuid,
        "zone": "nl-ams1",
        "ip_networks": {
            "ip_network": [
                {
                    "address": "172.16.0.0/24",
                    "dhcp": "yes",
                    "dhcp_default_route": "no",
                    "dhcp_dns": [
                        "172.16.0.10",
                        "172.16.1.10"
                    ],
                    "family": "IPv4",
                    "gateway": "172.16.0.1"
                }
            ]
        },
        "labels": [],
        "servers": {
            "server": [
                {"uuid": "0003295f-343a-44a2-8080-fb8196a6802a", "title": "Server #2"}
            ]
        }
    })


def _mock_initialize_client():
    return


def _mock_test_credentials():
    return


def get_option(option):
    options = {
        'plugin': 'upcloud.cloud.servers',
        'strict': False,
    }
    return options.get(option)


def test_populate_hostvars(inventory, mocker):
    inventory._fetch_servers = mocker.MagicMock(side_effect=get_servers)
    inventory._fetch_server_details = mocker.MagicMock(
        side_effects=[get_server1_details, get_server2_details, get_server3_details]
    )
    inventory.get_option = mocker.MagicMock(side_effect=get_option)

    inventory._initialize_upcloud_client = _mock_initialize_client
    inventory._test_upcloud_credentials = _mock_test_credentials

    inventory._populate()

    host1 = inventory.inventory.get_host('server1')
    host2 = inventory.inventory.get_host('server2')
    host3 = inventory.inventory.get_host('server3')

    assert host1.vars['id'] == "00229adf-0e46-49b5-a8f7-cbd638d11f6a"
    assert host1.vars['state'] == "started"
    assert len(host1.vars['labels']) == 0
    assert host2.vars['plan'] == "1xCPU-2GB"
    assert len(host2.vars['labels']) == 1
    assert host2.vars['labels'][0] == "foo=bar"
    assert host3.vars['id'] == "0003295f-343a-44a2-8080-fb8196a6802a"
    assert len(host3.vars['labels']) == 2


def get_filtered_labeled_option(option):
    options = {
        'plugin': 'upcloud.cloud.servers',
        'labels': ['foo=bar'],
    }
    return options.get(option)


def test_filtering_with_labels(inventory, mocker):
    inventory._fetch_servers = mocker.MagicMock(side_effect=get_servers)
    inventory._fetch_server_details = mocker.MagicMock(
        side_effects=[get_server1_details, get_server2_details, get_server3_details]
    )
    inventory.get_option = mocker.MagicMock(side_effect=get_filtered_labeled_option)

    inventory._initialize_upcloud_client = _mock_initialize_client
    inventory._test_upcloud_credentials = _mock_test_credentials

    inventory._populate()

    assert len(inventory.inventory.hosts) == 2
    host2 = inventory.inventory.get_host('server2')
    host3 = inventory.inventory.get_host('server3')

    assert host2.vars['id'] == "004d5201-e2ff-4325-7ac6-a274f1c517b7"
    assert host2.vars['labels'][0] == "foo=bar"
    assert host3.vars['id'] == "0003295f-343a-44a2-8080-fb8196a6802a"
    assert len(host3.vars['labels']) == 2
    assert host3.vars['labels'][1] == "private=yes"


def get_filtered_connect_with_option(option):
    options = {
        'plugin': 'upcloud.cloud.servers',
        'connect_with': 'private_ipv4',
        'network': '035146a5-7a85-408b-b1f8-21925164a7d3'
    }
    return options.get(option)


def test_filtering_with_connect_with(inventory, mocker):
    inventory._fetch_servers = mocker.MagicMock(side_effect=get_servers)
    inventory._fetch_server_details = mocker.MagicMock(
        side_effects=[get_server1_details, get_server2_details, get_server3_details]
    )
    inventory.get_option = mocker.MagicMock(side_effect=get_filtered_connect_with_option)

    inventory._initialize_upcloud_client = _mock_initialize_client
    inventory._test_upcloud_credentials = _mock_test_credentials

    inventory._fetch_network_details = get_network_details

    inventory._populate()

    assert len(inventory.inventory.hosts) == 1
    host3 = inventory.inventory.get_host('server3')

    assert host3.vars['id'] == "0003295f-343a-44a2-8080-fb8196a6802a"
