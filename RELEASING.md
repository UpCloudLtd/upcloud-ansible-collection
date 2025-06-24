# Releasing the Terraform provider

1. Merge all your changes to the stable branch
1. Create a new release branch e.g. `release-v2.3.5`
1. Update [CHANGELOG.md](CHANGELOG.md)
    1. Add new heading with the correct version e.g. `## [2.3.5]`
    1. Update links at the bottom of the page
    1. Leave "Unreleased" section at the top empty
1. Update `galaxy.yml` with the new version
1. Update README.md's download link with the new version
1. Merge your release branch to the stable branch
1. Create and push a new tag e.g `v2.3.5`
1. GitHub actions will trigger on tag and do a build & release of the tagged version
1. Check [the release page](https://github.com/UpCloudLtd/upcloud-ansible-collection/releases) for the release
1. Add correct changelog to the release if it's missing and publish the release
1. Done!
