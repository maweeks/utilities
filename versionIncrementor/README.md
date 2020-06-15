# Version Incrementor

## Current scripts

- `checkVersionDeployed.sh` - keep checking that the expected version is deployed
- `incrementVersion.sh` - increment the version number in VERSION file
  - `incrementVersion.sh -M` - increment major value
  - `incrementVersion.sh -m` - increment minor value
  - `incrementVersion.sh -p` - increment patch value
- `releaseWithGit.sh` - commit, tag and push to git origin

  - `releaseWithGit.sh MESSAGE='Commit message'` - release with commit message

- `NpmRelease.mk` - `make major`, `make minor`, `make patch` for npm tagging
