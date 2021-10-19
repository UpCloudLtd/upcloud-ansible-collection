# Releasing the Terraform provider

1. Merge all your changes to the stable branch
1. Create a new release branch e.g. `release-v2.3.5`
1. Update [CHANGELOG.md](CHANGELOG.md)
    1. Add new heading with the correct version e.g. `## [2.3.5]`
    1. Update links at the bottom of the page
    1. Leave "Unreleased" section at the top empty
1. Update `galaxy.yml` with the new version
1. Update README.md's download link with the new version
1. [Create a draft release in GitHub](https://github.com/UpCloudLtd/upcloud-ansible-collection/releases) with the new version
as the tag like `v2.3.5`
1. Build the collection .tar.gz using `ansible-galaxy collection build`
1. Attach the built .tar.gz into the release
1. Merge your release branch to the stable branch
1. Publish the release
