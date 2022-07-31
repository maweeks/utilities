.PHONY: help all install run test

help:              ## Show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

all:               ## Install, test and run
	@${MAKE} install
	@${MAKE} test
	@${MAKE} run

install:           ## Install requirements to run and test this project
	pip3 install -r requirements.txt

run:               ## Run the script
	python3 generate_ticket_status_page.py

test:              ## Run the tests
	python3 -m pytest
