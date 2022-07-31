.PHONY: help install run test

help:          ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:       ## Install requirements to run and test this project
	pip3 install -r requirements.txt

run:           ## Run the script
	python3 generate_ticket_status_page.py

test:          ## Run the tests
	touch config_secret.py
	mv config_secret.py config_secret.temp.py
	cp config_secret.test.py config_secret.py
	python3 -m pytest || true
	mv config_secret.temp.py config_secret.py
