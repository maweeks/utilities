# Custom Post to Slack

## Installation

- Install python 3
- Install `json, requests, sys` from pip if not already installed

## How to run

`python postToSlack.py "token" "#general" "Hello world!"`

Command line variables:

1. `SLACK_TOKEN` - Bearer token for slack
2. `SLACK_CHANNEL` - Slack channel including `#`
3. `SLACK_MESSAGE` - Message in mrkdwn, see below

## Slack message

Slack doesn't use proper markdown, see more [here](https://api.slack.com/reference/surfaces/formatting)

Links:

```text
# Markdown
Release [2.0.6](https://github.com/maweeks/test-utilities/pull/2):\n\nOther:\n\n- 2.0.5\n

# Mrkdwn
Release <https://github.com/maweeks/test-utilities/pull/2|2.0.6>:\n\nOther:\n\n- 2.0.5\n
```
