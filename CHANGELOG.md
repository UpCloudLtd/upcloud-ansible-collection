# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2025-06-24

### Changed

- **Breaking**: Rename collection to `upcloud.cloud` to enable releasing to Ansible Galaxy.
- **Breaking**: Rename inventory plugin to `servers`.

## [0.6.0] - 2023-09-25

### Added

- Inventory support for filtering with server labels and server groups

### Changed

- Servers that are not reachable with matching `connect_with` option are skipped, instead of returning an error.

## [0.5.1] - 2021-10-19

### Changed
- Fixed `Invalid value "community.upcloud.upcloud"` when simply trying to use the plugin

## [0.5.0] - 2021-05-19

First release for the new UpCloud Ansible Collection! :tada:

### Added

- Ansible inventory for UpCloud servers, allowing filtering with zones, tags, networks or server states.

[Unreleased]: https://github.com/UpCloudLtd/upcloud-ansible-collection/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/UpCloudLtd/upcloud-ansible-collection/releases/tag/v0.7.0
[0.6.0]: https://github.com/UpCloudLtd/upcloud-ansible-collection/releases/tag/v0.6.0
[0.5.1]: https://github.com/UpCloudLtd/upcloud-ansible-collection/releases/tag/v0.5.1
[0.5.0]: https://github.com/UpCloudLtd/upcloud-ansible-collection/releases/tag/v0.5.0
