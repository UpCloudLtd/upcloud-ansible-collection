# Ansible UpCloud Collection


[![Ansible sanity tests](https://github.com/UpCloudLtd/upcloud-ansible-collection/actions/workflows/sanity-test.yml/badge.svg)](https://github.com/UpCloudLtd/upcloud-ansible-collection/actions/workflows/sanity-test.yml)
[![unit tests](https://github.com/UpCloudLtd/upcloud-ansible-collection/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/UpCloudLtd/upcloud-ansible-collection/actions/workflows/unit-tests.yml)

This collection provides an inventory plugin for using your UpCloud servers in an Ansible inventory.

For managing your UpCloud infrastructure as code, we recommend OpenTofu or [Terraform](https://upcloud.com/docs/guides/get-started-terraform/).

## Getting Started

### Prerequisites

UpCloud Collection requires [UpCloud API's Python bindings](https://pypi.org/project/upcloud-api/) version 2.5.0 or newer in order to work. Use version 2.8.0 or later for API token and system keyring support. It can be installed from the Python Package Index with the `pip` tool:

```bash
pip3 install upcloud-api>=2.5.0
```

The collection itself can be installed with the `ansible-galaxy` command that comes with the Ansible package:

```bash
ansible-galaxy collection install upcloud.cloud
```

You can also install the collection from GitHub Releases by replacing the upcloud.cloud collection name with the release artifact download URL.

### Inventory usage

Inventory file must be named so that it ends either in `upcloud.yml` or `upcloud.yaml`. It is also possible to filter
servers based on their zone, tags, state, or the network they belong to.

#### Quick Start

Create an `upcloud.yml` file with these contents:

```yaml
plugin: upcloud.cloud.servers
```

Set environment variables for API authentication:

```bash
export UPCLOUD_USERNAME="upcloud-api-access-enabled-user"
export UPCLOUD_PASSWORD="verysecretpassword"
```

And show the Ansible inventory information as a graph:

```bash
ansible-inventory -i upcloud.yml --graph --vars
```

You should see a list of hosts and their host variables you can use in playbooks.

#### Further examples

You can filter based on multiple data points:

```yaml
plugin: upcloud.cloud.servers
zones:
  - fi-hel2
labels:
  - role=prod
  - foo
states:
  - started
connect_with: private_ipv4
network: 035a0a8a-7704-4da5-820d-129fc8232714
server_group: Group name or UUID
```

Servers can also be grouped by status, zone etc by specifying them as `keyed_groups`.

```yaml
plugin: upcloud.cloud.servers
keyed_groups:
  - key: zone
    prefix: upcloud_zone
  - key: state
    prefix: server_state
```

Examples here assume that API credentials are available as environment variables (`UPCLOUD_USERNAME` and `UPCLOUD_PASSWORD` or `UPCLOUD_TOKEN`) or in system keyring. Use `upctl account login` command to store the credentials in keyring.

## Troubleshooting

If you are having problems loading, finding or enabling the collection, you might need to create or modify your
existing `ansible.cfg`config. Adding the following settings should ensure that the collection can be found and is
enabled:

```
[default]
collections_paths = ~/.ansible/collections:/usr/share/ansible/collections

[inventory]
enable_plugins = upcloud.cloud.servers
```

Note that, if you are using any other plugins, those should be listed in `enable_plugins` as well.

## Changelog

Changelog is available [in its own file](CHANGELOG.md).

## Development

This collection follows [Ansible Developer Guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html), with
the exception that Python 2.7 is not supported as the support has been dropped from UpCloud's Python SDK.

All functionality should include [relevant tests](https://docs.ansible.com/ansible/latest/dev_guide/testing.html).

Tests can be run with `ansible-test` tool (comes with Ansible) in the collection folder (default:
~/.ansible/collections/ansible_collections/community/upcloud):

```bash
$ cd ~/.ansible/collections/ansible_collections/community/upcloud
$ ansible-test sanity --docker -v --color
...
$ ansible-test units -v --color --docker --coverage
...
```

### Building and installing a new version locally

A new version can be built and tested locally with the `ansible-galaxy` tool that is packaged with Ansible.

```bash
ansible-galaxy collection build
ansible-galaxy collection install community-upcloud-<VERSION>.tar.gz
```
