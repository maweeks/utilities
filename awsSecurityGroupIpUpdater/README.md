# AWS Security Group IP Updater

## Installation

- Install AWS CLI version 2 from [here](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html)
  - **If required** generate new credentials in AWS IAM
  - Configure aws command line using `aws configure`
    - Provide your AWS Access Key ID, AWS Secret Access Key and Default region name when asked
- Install `jq`
  `brew install jq`
- Update the variables in `variables.mk`
  - You should only need to update the `DESCRIPTION` variable
- Run `make updateIp`, which will:
  - Delete any ingress rules with the same description as provided
  - Add a new ingress rule with the provided IP address

## Available make targets

- `help` - Show this help.
- `listAllExistingRules` - Get all the existing ingress rules
- `listExistingRules` - Get the existing ingress rules with the specified description
- `addRuleToSecurityGroup` - Get current IP and add it to security group
- `deleteExistingRules` - Remove ingress rule with current description if exists
- `showIP`- Get your current IP from AWS and print it
- `updateIp`- Delete Security group rule and add current IP
