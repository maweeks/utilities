.PHONY: help install run test

help:          ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

install:       ## Install requirements to run and test this project
	pip3 install -r requirements.txt

run:           ## Run the script
	python3 generateTicketStatusPage.py

test:          ## Run the tests
	mv configSecret.py configSecret.temp.py
	cp configSecret.test.py configSecret.py
	python3 -m pytest || true
	mv configSecret.temp.py configSecret.py
