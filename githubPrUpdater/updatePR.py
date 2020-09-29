import json
import os
import re
import requests
import sys

DEFAULT_REPO_OWNER = "maweeks"
LABEL_TO_ADD = ":rocket: release :rocket:"

TICKET_BASE_URL = "https://bob.atlassian.net/"
CODE_PREFIXES = ["ASDF", "QWER", "ZXCV"]
CODE_REGEX = "|".join(code + "-[0-9]+" for code in CODE_PREFIXES)
README_SECTIONS = ["Features", "Fixes", "Tickets", "Other"]

LOG_RESPONSES = False

PR_REPOSITORY = str(sys.argv[1])
PR_ISSUE_NUMBER = str(sys.argv[2])
PR_RELEASE = str(sys.argv[3])
DRY_RUN = "Y" == str(sys.argv[4])
CREATE_GITHUB_RELEASE = "Y" == str(sys.argv[5])
UPDATE_PR_TEXT = "Y" == str(sys.argv[6])
GITHUB_CREDENTIALS = "token {0}".format(str(sys.argv[7]))
TICKET_CREDENTIALS = ("matthew.weeks", str(sys.argv[8]))
EXPORT_RELEASE_NOTES = "Y" == str(sys.argv[9])
EXPORT_DIR = str(sys.argv[10])


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
        "https://api.github.com/repos/{0}/{1}/pulls/{2}/commits".format(
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


def add_tickets_to_tickets(new_tickets):
    for new_ticket in new_tickets:
        if new_ticket in tickets:
            if pr[0] not in tickets[new_ticket]:
                tickets[new_ticket].append(pr[0])
        else:
            tickets[new_ticket] = [pr[0]]


def get_ticket_details(ticket):
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


######################################################################
# Create release

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
            createRelease = requests.post(
                get_create_release_url(),
                headers={"Authorization": GITHUB_CREDENTIALS},
                data=json.dumps(data),
            )
            if LOG_RESPONSES:
                print("Create release response:")
                print(createRelease.text)
        except Exception:
            print("Failed to create release")
            raise SystemExit()
else:
    print("Skipping create release.")


######################################################################
# Generate release notes

existingPrCommits = []
try:
    existingPrCommits = get_pr_commits(PR_ISSUE_NUMBER)
except Exception:
    print("Failed to get main PR commits {0}".format(PR_ISSUE_NUMBER))
    raise SystemExit()

teamcityChange = False
commits = []
prs = []
tickets = {}
readmeData = []

for commitJSON in existingPrCommits:
    commit = commitJSON["commit"]["message"].split("\n")[0]
    if commit.startswith("TeamCity change in"):
        teamcityChange = True
    else:
        if commit.startswith("Merge pull request #"):
            prNumber = re.search("#[0-9]+", commit).group()
            branch = commit[len(prNumber) + 24:]
            prs.append([prNumber, branch])
        elif ((not commit.startswith("Merge remote-tracking branch"))
              and (not commit.startswith("Merge branch 'develop' into"))
              and (not commit.startswith("Merge branch 'master' into"))):
            commits.append(commit)

for pr in prs:
    prTickets = get_tickets_from_string(pr[1])
    includePr = False
    try:
        prCommits = get_pr_commits(pr[0].split("#")[1])
        includePr = should_include_pr(pr[0].split("#")[1])
        for prCommit in prCommits:
            prCommitMessage = prCommit["commit"]["message"].split("\n")[0]
            if includePr:
                prTickets += get_tickets_from_string(
                    prCommitMessage
                )
            if prCommitMessage in commits:
                commits.remove(prCommitMessage)
    except Exception:
        print("Failed to get feature PR commits {0}".format(PR_ISSUE_NUMBER))
        raise SystemExit()

    if includePr:
        if len(prTickets) == 0:
            readmeData.append(["", [], "Other", pr[1].split("/")[-1]])
        else:
            add_tickets_to_tickets(prTickets)

for commit in commits:
    commitTickets = get_tickets_from_string(commit)
    if len(commitTickets) > 0:
        for new_ticket in commitTickets:
            if new_ticket not in tickets:
                tickets[new_ticket] = []
    else:
        readmeData.append(["", [], "Other", commit])

for ticket in tickets:
    readmeData.append(get_ticket_details(ticket))

#  ticket,    prs,     type,   message
# ["OXA-123", [13, 2], "Bugs", "Message"]
if teamcityChange:
    readmeData.append(["", [], "Other", "Updated TeamCity build(s)."])

readmeData.sort(key=lambda x: (x[0], x[3]))

readmeString = "{0} {1}:\n".format(
    PR_REPOSITORY.capitalize(), get_release_markdown_link(PR_RELEASE)
)

for section in README_SECTIONS:
    sectionString = ""
    for item in readmeData:
        sectionString += get_readme_item_text(item, section)
    if sectionString != "":
        readmeString += "\n{0}:\n\n{1}".format(section, sectionString)

print("##################################################")
print(readmeString)
print("##################################################")

if EXPORT_RELEASE_NOTES:
    try:
        os.makedirs(EXPORT_DIR)
    except OSError:
        pass
    text_file = open("{0}/{1}-{2}.md".format(EXPORT_DIR,
                                             PR_REPOSITORY,
                                             PR_ISSUE_NUMBER
                                             ), "w")
    text_file.write(readmeString)
    text_file.close()

######################################################################
# Update PR

existingPr = ""
try:
    existingPr = requests.get(
        get_issue_url(),
        headers={"Authorization": GITHUB_CREDENTIALS},
    ).json()
except Exception:
    print("Failed to get existing PR")
    raise SystemExit()

prData = {}
labels = get_pr_labels(existingPr)

if LABEL_TO_ADD not in labels:
    labels.append(LABEL_TO_ADD)
    prData["labels"] = labels


if UPDATE_PR_TEXT:
    prData["title"] = "Release {0}".format(PR_RELEASE)
    prData["body"] = readmeString

if prData != {}:
    if DRY_RUN:
        print("DRY RUN: Create release request:")
        print(get_issue_url())
        print(json.dumps(prData))
    else:
        try:
            updatePR = requests.patch(
                get_issue_url(),
                headers={"Authorization": GITHUB_CREDENTIALS},
                data=json.dumps(prData),
            )

            if LOG_RESPONSES:
                print("Update PR response:")
                print(updatePR.text)

        except Exception:
            print("Failed to update PR")
            raise SystemExit()
else:
    print("No PR changes to be made.")

print("Script complete.")
