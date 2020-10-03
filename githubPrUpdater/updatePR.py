import json
import os
import re
import requests
import sys


DEFAULT_REPO_OWNER = "maweeks"
LABEL_TO_ADD = ":rocket: release :rocket:"
TICKET_BASE_URL = "https://bob.atlassian.net/"
TICKET_USER = "matthew.weeks"
CODE_PREFIXES = ["ASDF", "QWER", "ZXCV"]
CODE_REGEX = "|".join(code + "-[0-9]+" for code in CODE_PREFIXES)
README_SECTIONS = ["Features", "Fixes", "Tickets", "Other"]
LOG_RESPONSES = False
SLACK_CHANNEL = "#general"

PR_REPOSITORY = str(sys.argv[1])
PR_ISSUE_NUMBER = str(sys.argv[2])
PR_RELEASE = str(sys.argv[3])
DRY_RUN = "Y" == str(sys.argv[4])
CREATE_GITHUB_RELEASE = "Y" == str(sys.argv[5])
UPDATE_PR_TEXT = "Y" == str(sys.argv[6])
GITHUB_CREDENTIALS = "token {0}".format(str(sys.argv[7]))
TICKET_CREDENTIALS = (TICKET_USER, str(sys.argv[8]))
EXPORT_RELEASE_NOTES = "Y" == str(sys.argv[9])
EXPORT_DIR = str(sys.argv[10])
SLACK_TOKEN = str(sys.argv[11])
POST_TO_SLACK = "Y" == str(sys.argv[12])


######################################################################


def print_parameters():
    print("Parameters:")
    print("PR_REPOSITORY:         {0}".format(PR_REPOSITORY))
    print("PR_ISSUE_NUMBER:       {0}".format(PR_ISSUE_NUMBER))
    print("PR_RELEASE:            {0}".format(PR_RELEASE))
    print("DRY_RUN:               {0}".format(DRY_RUN))
    print("CREATE_GITHUB_RELEASE: {0}".format(CREATE_GITHUB_RELEASE))
    print("UPDATE_PR_TEXT:        {0}".format(UPDATE_PR_TEXT))
    print("GITHUB_CREDENTIALS:    {0}".format(GITHUB_CREDENTIALS))
    print("TICKET_CREDENTIALS:    {0}".format(TICKET_CREDENTIALS))
    print("EXPORT_RELEASE_NOTES:  {0}".format(EXPORT_RELEASE_NOTES))
    print("EXPORT_DIR:            {0}".format(EXPORT_DIR))
    print("SLACK_TOKEN:           {0}".format(SLACK_TOKEN))
    print("POST_TO_SLACK:         {0}".format(POST_TO_SLACK))


def create_release():
    if CREATE_GITHUB_RELEASE:
        data = {
            "tag_name": PR_RELEASE,
            "name": PR_RELEASE,
            "body": get_release_markdown_link(PR_RELEASE).capitalize(),
            "draft": False,
            "prerelease": False,
        }

        if DRY_RUN:
            print("DRY RUN: Create release request:")
            print(get_create_release_url())
            print(json.dumps(data))
        else:
            try:
                create_release = requests.post(
                    get_create_release_url(),
                    headers={"Authorization": GITHUB_CREDENTIALS},
                    data=json.dumps(data),
                )
                if LOG_RESPONSES:
                    print("Create release response:")
                    print(create_release.text)
            except Exception:
                print("Failed to create release")
                raise SystemExit()
    else:
        print("Skipping create release.")


def get_tickets_from_string(string):
    return re.findall(CODE_REGEX, string)


def get_ticket_content_url(ticket):
    return "{1}rest/api/3/issue/{0}?fields=summary,issuetype".format(
        ticket, TICKET_BASE_URL
    )


def get_release_markdown_link(release):
    return "release [{0}](https://github.com/{1}/{2}/pull/{3})".format(
        release, DEFAULT_REPO_OWNER, PR_REPOSITORY, PR_ISSUE_NUMBER
    )


def get_ticket_markdown_link(ticket):
    return "[{0}]({1}browse/{0}) ".format(ticket, TICKET_BASE_URL)


def get_readme_item_text(item, section):
    item_string = ""
    if item[2] == section:
        if len(item[1]) > 0:
            item[1].sort()
            item[1] = ["{0}".format(str(pr)) for pr in item[1]]
            item_string += str(item[1]).replace("'", "") + " "
        if len(item[0]) > 0:
            item_string = get_ticket_markdown_link(item[0]) + item_string
        if item_string != "":
            item_string = "- " + item_string
        if item[3] != "":
            item_string += "- {0}".format(item[3])
        if len(item_string) > 0:
            item_string = item_string.strip() + "\n"
    return item_string


def get_pr_commits(issue_number):
    return requests.get(
        "https://api.github.com/repos/{0}/{1}/pulls/{2}/commits?per_page=250".format(
            DEFAULT_REPO_OWNER, PR_REPOSITORY, issue_number
        ),
        headers={"Authorization": GITHUB_CREDENTIALS},
    ).json()


def get_create_release_url():
    return "https://api.github.com/repos/{0}/{1}/releases".format(
        DEFAULT_REPO_OWNER, PR_REPOSITORY
    )


def get_issue_url():
    return "https://api.github.com/repos/{0}/{1}/issues/{2}".format(
        DEFAULT_REPO_OWNER, PR_REPOSITORY, PR_ISSUE_NUMBER
    )


def get_pr_url(pr_number):
    return "https://api.github.com/repos/{0}/{1}/pulls/{2}".format(
        DEFAULT_REPO_OWNER, PR_REPOSITORY, pr_number
    )


def add_tickets_to_tickets(new_tickets, tickets, pr):
    for new_ticket in new_tickets:
        if new_ticket in tickets:
            if pr[0] not in tickets[new_ticket]:
                tickets[new_ticket].append(pr[0])
        else:
            tickets[new_ticket] = [pr[0]]


def get_ticket_details(ticket, tickets):
    try:
        ticket_details = requests.get(
            get_ticket_content_url(ticket), auth=TICKET_CREDENTIALS
        ).json()

        ticket_type = "Features"
        if ticket_details["fields"]["issuetype"]["name"] in ["Bug"]:
            ticket_type = "Fixes"
        return [
            ticket,
            tickets[ticket],
            ticket_type,
            ticket_details["fields"]["summary"]
        ]
    except Exception:
        return [ticket, tickets[ticket], "Tickets", ""]


def get_pr_labels(existing_pr_json):
    labels = []
    if LOG_RESPONSES:
        print("Old PR response:")
        print(existing_pr_json)

    for label in existing_pr_json["labels"]:
        labels.append(label["name"])

    return labels


def should_include_pr(pr):
    pr_details = requests.get(
        get_pr_url(pr),
        headers={"Authorization": GITHUB_CREDENTIALS},
    ).json()
    return (pr_details["head"]["ref"] != "develop") or (
        pr_details["base"]["ref"] == "master"
    )


def generate_readme_data():
    existing_pr_commits = []
    try:
        existing_pr_commits = get_pr_commits(PR_ISSUE_NUMBER)
    except Exception:
        print("Failed to get main PR commits {0}".format(PR_ISSUE_NUMBER))
        raise SystemExit()

    teamcity_change = False
    commits = []
    prs = []
    tickets = {}
    readme_data = []

    for commit_json in existing_pr_commits:
        commit = commit_json["commit"]["message"].split("\n")[0]
        if commit.startswith("TeamCity change in"):
            teamcity_change = True
        else:
            if commit.startswith("Merge pull request #"):
                pr_number = re.search("#[0-9]+", commit).group()
                branch = commit[len(pr_number) + 24:]
                prs.append([pr_number, branch])
            elif ((not commit.startswith("Merge remote-tracking branch"))
                  and (not commit.startswith("Merge branch "))):
                commits.append(commit)

    for pr in prs:
        pr_tickets = get_tickets_from_string(pr[1])
        include_pr = False
        try:
            prCommits = get_pr_commits(pr[0].split("#")[1])
            include_pr = should_include_pr(pr[0].split("#")[1])
            for prCommit in prCommits:
                prCommitMessage = prCommit["commit"]["message"].split("\n")[0]
                if include_pr:
                    pr_tickets += get_tickets_from_string(
                        prCommitMessage
                    )
                if prCommitMessage in commits:
                    commits.remove(prCommitMessage)
        except Exception:
            print("Failed to get feature PR commits {0}".format(
                PR_ISSUE_NUMBER))
            raise SystemExit()

        if include_pr:
            if len(pr_tickets) == 0:
                readme_data.append(
                    ["", [pr[0]], "Other", pr[1].split("/")[-1]])
            else:
                add_tickets_to_tickets(pr_tickets, tickets, pr)

    for commit in commits:
        commit_tickets = get_tickets_from_string(commit)
        if len(commit_tickets) > 0:
            for new_ticket in commit_tickets:
                if new_ticket not in tickets:
                    tickets[new_ticket] = []
        else:
            readme_data.append(["", [], "Other", commit])

    for ticket in tickets:
        readme_data.append(get_ticket_details(ticket, tickets))

    #  ticket,    prs,     type,   message
    # ["OXA-123", [13, 2], "Bugs", "Message"]
    if teamcity_change:
        readme_data.append(["", [], "Other", "Updated TeamCity build(s)."])

    readme_data.sort(key=lambda x: (x[0], x[3]))
    return readme_data


def generate_readme_string(readme_data):
    readmeString = "{0} {1}:\n".format(
        PR_REPOSITORY.capitalize(), get_release_markdown_link(PR_RELEASE)
    )

    for section in README_SECTIONS:
        sectionString = ""
        for item in readme_data:
            sectionString += get_readme_item_text(item, section)
        if sectionString != "":
            readmeString += "\n{0}:\n\n{1}".format(section, sectionString)

    print("##################################################")
    print(readmeString)
    print("##################################################")

    return readmeString


def write_to_file(contents):
    if EXPORT_RELEASE_NOTES:
        try:
            os.makedirs(EXPORT_DIR)
        except OSError:
            pass
        text_file = open("{0}/{1}-{2}.md".format(EXPORT_DIR,
                                                 PR_REPOSITORY,
                                                 PR_ISSUE_NUMBER
                                                 ), "w")
        text_file.write(contents)
        text_file.close()
    else:
        print("Skipping write to file.")


def update_pr(contents):
    existingPr = ""
    try:
        existingPr = requests.get(
            get_issue_url(),
            headers={"Authorization": GITHUB_CREDENTIALS},
        ).json()
    except Exception:
        print("Failed to get existing PR")
        raise SystemExit()

    pr_data = {}
    labels = get_pr_labels(existingPr)

    if LABEL_TO_ADD not in labels:
        labels.append(LABEL_TO_ADD)
        pr_data["labels"] = labels

    if UPDATE_PR_TEXT:
        pr_data["title"] = "Release {0}".format(PR_RELEASE)
        pr_data["body"] = contents

    if pr_data != {}:
        if DRY_RUN:
            print("DRY RUN: Create release request:")
            print(get_issue_url())
            print(json.dumps(pr_data))
        else:
            try:
                update_pr = requests.patch(
                    get_issue_url(),
                    headers={"Authorization": GITHUB_CREDENTIALS},
                    data=json.dumps(pr_data),
                )

                if LOG_RESPONSES:
                    print("Update PR response:")
                    print(update_pr.text)

            except Exception:
                print("Failed to update PR")
                raise SystemExit()
    else:
        print("No PR changes to be made.")


def generate_message_data(message):
    return {
        "channel": SLACK_CHANNEL,
        "text": message
    }


def post_slack_message(data):
    if POST_TO_SLACK:
        try:
            post_message = requests.post(
                "https://slack.com/api/chat.post_message",
                headers={
                    "Authorization": 'Bearer {0}'.format(SLACK_TOKEN),
                    "Content-Type": "application/json"
                },
                data=json.dumps(data),
            )
            print(post_message.json())
        except Exception:
            print("Failed to send slack message")
            raise SystemExit()
    else:
        print("Skipping post to slack.")


def run_script():
    create_release()
    readme_data = generate_readme_data()
    readmeString = generate_readme_string(readme_data)
    write_to_file(readmeString)
    update_pr(readmeString)
    post_slack_message(generate_message_data(''))
    print("Script complete.")


# ######################################################################


if __name__ == '__main__':
    run_script()
