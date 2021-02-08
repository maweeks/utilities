.PHONY: help prepareDevelop increment release releaseMajor releaseMinor releasePatch allMajor allMinor allPatch

help:          ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

prepareDevelop: ## Merge latest master into latest deveop branch
	git checkout master
	git pull
	git checkout develop
	git pull
	git merge master

increment:       ## Increment the version number
	@./incrementVersion.sh

release:       ## Increment the version number
	@./releaseWithGit.sh

releaseMajor: ## Increment to a new major version
	@$(MAKE) increment VERSION=major
	@$(MAKE) release

releaseMinor: ## Increment to a new minor version
	@$(MAKE) increment VERSION=minor
	@$(MAKE) release

releasePatch:   ## Increment to a new patch version
	@$(MAKE) increment VERSION=patch
	@$(MAKE) release

allMajor:       ## Prepare and complete a major release
	@$(MAKE) prepareDevelop
	@$(MAKE) releaseMajor

allMinor:       ## Prepare and complete a minor release
	@$(MAKE) prepareDevelop
	@$(MAKE) releaseMinor

allPatch:       ## Prepare and complete a patch release
	@$(MAKE) prepareDevelop
	@$(MAKE) releasePatch
