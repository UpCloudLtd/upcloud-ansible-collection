# Ansible UpCloud Collection

UpCloud inventory as a modernized Ansible collection. Current scope only covers UpCloud's servers offering,
but depending on the demand we might include our other services (networks, (object) storages, routers, databases etc)
in it as well. Same goes for plugins for other API actions. We recommend using
[Terraform](https://upcloud.com/community/tutorials/get-started-terraform/) for automated management of your UpCloud
infrastructure, but we might implement some server control plugins for Ansible in the future if the demand is there.

If you find yourself needing a specific service as an inventory, please open an
[issue](https://github.com/UpCloudLtd/upcloud-ansible-collection/issues). Please see the development & contribution
sections below for development quickstart if you're interested in adding new features or making fixes.

## Requirements

UpCloud Collection requires [UpCloud API's Python bindings](https://pypi.org/project/upcloud-api/) to be installed
in order to work. It can be installed from the Python Package Index with the `pip` tool. The collection
itself can be installed with the `ansible-galaxy` command that comes in the Ansible package.

```bash
pip3 install upcloud-api
ansible-galaxy collection install https://github.com/path/to/release.tar.gz
```

## Inventory usage

As UpCloud Collection is not part of the official Ansible release and Ansible itself still has some figuring out
to do with collections, a few extra files are needed for your playbook to function. Following configuration
options should be either in your existing config, or if you're using defaults, just have these in `ansible.cfg`
in your playbook's root folder.

```
[default]
collections_paths = ~/.ansible/collections:/usr/share/ansible/collections

[inventory]
enable_plugins = community.upcloud.upcloud
```

Inventory file must be named so that it ends either in `upcloud.yml` or `upcloud.yaml`. If you want to include
all your servers in the inventory, inventory file can just have `plugin: community.upcloud.upcloud` as its content.
It is also possible to filter servers based on their zone, tags, state, or the network they belong to:

```
plugin: community.upcloud.upcloud
zones:
  - fi-hel2
tags:
  - app
  - db
states:
  - started
network: 035a0a8a-7704-4da5-820d-129fc8232714
```

Servers can also be grouped by status, zone etc by specifying them as `keyed_groups`.

```
plugin: community.upcloud.upcloud
keyed_groups:
  - key: zone
    prefix: upcloud_zone
  - key: state
    prefix: server_state
```

Examples here assume that API credentials are available as environment variables
(`UPCLOUD_USERNAME` & `UPCLOUD_PASSWORD`). They can also be defined in inventory file:

```
plugin: community.upcloud.upcloud
username: YOUR_USERNAME
password: YOUR_PASSWORD
```

## Development

This collection follows [Ansible Developer Guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html), with
the exception that Python 2.7 is not supported as the support has been dropped from UpCloud's Python SDK.

All functionality should include [relevant tests](https://docs.ansible.com/ansible/latest/dev_guide/testing.html).

Tests can be run with `ansible-test` tool (comes with Ansible) in the collection folder (default:
~/.ansible/collections/ansible_collections/community/upcloud):

```bash
$ cd ~/.ansible/collections/ansible_collections/community/upcloud
$ pip install --user -r requirements-dev.txt
$ ansible-test sanity
...
$ ansible-test units -v --color --coverage
...
```

### Building and installing a new version locally

A new version can be built and tested locally with the `ansible-galaxy` tool that is packaged with Ansible.

```bash
ansible-galaxy collection build
ansible-galaxy collection install community-upcloud-<VERSION>.tar.gz
```
