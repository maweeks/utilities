help:          ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

major:          ## Prepare version and push a new major release
	@$(MAKE) prepareDevelop && \
	npm version major && \
	$(MAKE) pullRequest

minor:          ## Prepare version and push a new minor release
	@$(MAKE) prepareDevelop && \
	npm version minor && \
	$(MAKE) pullRequest

patch:          ## Prepare version and push a new patch release
	@$(MAKE) prepareDevelop && \
	npm version patch && \
	$(MAKE) pullRequest

prepareDevelop: ## Merge latest master into latest deveop branch
	@git checkout master && \
	git pull && \
	git checkout develop && \
	git pull && \
	git merge master

pullRequest:    ## Push release and open PR URL
	@git push && \
	git push --tags && \
	open https://github.com/maweeks/test-utilities/compare/master...develop
