help:    ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

release:       ## Increment the version number
	./incrementVersion.sh

releaseMajor: ## Increment to a new major version
	$(MAKE) release VERSION=major

releaseMinor: ## Increment to a new minor version
	$(MAKE) release VERSION=minor

releasePatch: ## Increment to a new patch version
	$(MAKE) release VERSION=patch
