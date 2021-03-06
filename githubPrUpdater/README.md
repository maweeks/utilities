# GitHub PR Updater

## Installation

- Install python 3
- Install `json, re, requests, sys` from pip if not already installed

## How to run

`python updatePR.py "test-repo" "1" "0.0.1" "Y" "Y" "Y" "Y" "N" "N" "GITHUB_PASS" "TICKET_PASS" "SLACK" "DIR"`

Command line variables:

1. `PR_REPOSITORY` - GitHub repository name
2. `PR_ISSUE_NUMBER` - GitHub repository PR number
3. `PR_RELEASE` - Git tag of the release
4. `DRY_RUN` - `Y` to print and not send the `POST` and `PATCH` requests
5. `INCLUDE_DATE_GENERATED` - `Y` to include date generated in release notes in the format `YYYY-MM-DD`
6. `CREATE_GITHUB_RELEASE` - `Y` to create a github release for the provided tag
7. `UPDATE_PR_TEXT` - `Y` to update the title and description of the PR
8. `EXPORT_RELEASE_NOTES` - `Y` to output the release notes to a file
9. `POST_TO_SLACK` - `Y` to output the release notes to slack
10. `GITHUB_PASSWORD` - GitHub password
11. `TICKET_PASSWORD` - Ticket password
12. `SLACK_TOKEN` - Slack bearer token
13. `EXPORT_DIR` - String of directory to output to

Also update lines: 9-17 in `updatePR.py` and modify `get_ticket_details` to use anything but JIRA.

## How to run the E2E tests

1. Clear your unstaged `git diff` (these tests verify changes using `git diff`)
2. `./autoTest.sh "GITHUB_PASS" "TICKET_PASS"`

Command line variables:

1. `GITHUB_PASSWORD` - GitHub password
2. `TICKET_PASSWORD` - Ticket password

### How it works-ish

#### updatePR.py

- Generate a Github release using the parameters provided
- Get all commit messages from the main release commit
- Check the contents of the first line of each commit
  - Is a pull request merge
    - Get commits from feature pull request
      - Get tickets by code from branch name
      - Get tickets by code from PR commits
      - If PR has tickets
        - Add ticket to release notes
      - Else
        - Add branch name to release notes
  - Is a TeamCity change
    - Include TeamCity change in release notes ONCE
  - Is a commit not from a pull request
    - Add commit message as item in release notes
- Get ticket details from ticket API
- Sort release notes by ticket types
- Update release PR with labels, title and generated release notes

#### E2E tests

`autoTest.sh "GITHUB_PASS" "TICKET_PASS"` can be used to test the python script still outputs as expected. This bash script runs `updatePr.py` multiple times and verifies the output is as expected in `testOutput` directory. Your git unstaged changes need to be clear to run the tests.
