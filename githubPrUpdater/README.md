# GitHub PR Updater

## Installation

- Install python 3
- Install `json, re, requests, sys` from pip if not already installed

## How to run

`python updatePR.py "test-repo" "1" "0.0.1" "Y" "Y" "Y" "GITHUB_PASS" "TICKET_PASS"`

Command line variables:

1. `PR_REPOSITORY` - GitHub repository name
2. `PR_ISSUE_NUMBER` - GitHub repository PR number
3. `PR_RELEASE` - Git tag of the release
4. `DRY_RUN` - `Y` to print and not send the `POST` and `PATCH` requests
5. `CREATE_GITHUB_RELEASE` - `Y` to create a github release for the provided tag
6. `UPDATE_PR_TEXT` - `Y` to update the title and description of the PR
7. `GITHUB_PASSWORD` - GitHub password
8. `TICKET_PASSWORD` - Ticket password

Also update lines: 6, 7, 9, 10, 11, 22, 23 in `updatePR.py`
