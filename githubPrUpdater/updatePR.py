import json
import re
import requests
import sys

DEFAULT_REPO_OWNER = "maweeks"
LABEL_TO_ADD = "release"

TICKET_BASE_URL = "https://bob.atlassian.net/"
CODE_PREFIXES = ["ASDF", "QWER", "ZXCV"]
CODE_REGEX = "|".join(code + "-[0-9]+" for code in CODE_PREFIXES)
README_SECTIONS = ["Features", "Fixes", "Tickets", "Other"]

LOG_REQUESTS = False

PR_REPOSITORY = str(sys.argv[1])
PR_ISSUE_NUMBER = str(sys.argv[2])
PR_RELEASE = str(sys.argv[3])
DRY_RUN = "Y" == str(sys.argv[4])
CREATE_GITHUB_RELEASE = "Y" == str(sys.argv[5])
UPDATE_PR_TEXT = "Y" == str(sys.argv[6])
GITHUB_CREDENTIALS = ("maweeks", str(sys.argv[7]))
TICKET_CREDENTIALS = ("matthew.weeks", str(sys.argv[8]))


################################################################################


def printParameters():
    print("Parameters:")
    print("PR_REPOSITORY:         {0}".format(PR_REPOSITORY))
    print("PR_ISSUE_NUMBER:       {0}".format(PR_ISSUE_NUMBER))
    print("PR_RELEASE:            {0}".format(PR_RELEASE))
    print("DRY_RUN:               {0}".format(DRY_RUN))
    print("CREATE_GITHUB_RELEASE: {0}".format(CREATE_GITHUB_RELEASE))
    print("UPDATE_PR_TEXT:        {0}".format(UPDATE_PR_TEXT))
    print("GITHUB_CREDENTIALS:    {0}".format(GITHUB_CREDENTIALS))
    print("TICKET_CREDENTIALS:    {0}".format(TICKET_CREDENTIALS))


def getTicketsFromString(string):
    return re.findall(CODE_REGEX, string)


def getTicketContentUrl(ticket):
    return "{1}rest/api/3/issue/{0}?fields=summary,issuetype".format(
        ticket, TICKET_BASE_URL
    )


def getReleaseMarkdownLink(release):
    return "release [{0}](https://github.com/{1}/{2}/pull/{3})".format(
        release, DEFAULT_REPO_OWNER, PR_REPOSITORY, PR_ISSUE_NUMBER
    )


def getTicketMarkdownLink(ticket):
    return "[{0}]({1}browse/{0}) ".format(ticket, TICKET_BASE_URL)


def getReadmeItemText(item, section):
    itemString = ""
    if item[2] == section:
        if len(item[1]) > 0:
            item[1].sort()
            item[1] = ["{0}".format(str(pr)) for pr in item[1]]
            itemString += str(item[1]).replace("'", "") + " "
        if len(item[0]) > 0:
            itemString = getTicketMarkdownLink(item[0]) + itemString
        if itemString != "":
            itemString = "- " + itemString
        if item[3] != "":
            itemString += "- {0}\n".format(item[3])
    return itemString


def getPrCommits(issueNumber):
    return requests.get(
        "https://api.github.com/repos/{0}/{1}/pulls/{2}/commits".format(
            DEFAULT_REPO_OWNER, PR_REPOSITORY, issueNumber
        ),
        auth=GITHUB_CREDENTIALS,
    ).json()


def addTicketsToTickets(newTickets):
    for newTicket in newTickets:
        if newTicket in tickets:
            if pr[0] not in tickets[newTicket]:
                tickets[newTicket].append(pr[0])
        else:
            tickets[newTicket] = [pr[0]]


def getTicketDetails(ticket):
    try:
        ticketDetails = requests.get(
            getTicketContentUrl(ticket), auth=TICKET_CREDENTIALS
        ).json()

        ticketType = "Features"
        if ticketDetails["fields"]["issuetype"] in ["Bug"]:
            ticketType = "Fixes"
        return [ticket, tickets[ticket], ticketType, ticketDetails["fields"]["summary"]]
    except:
        return [ticket, tickets[ticket], "Tickets", ""]


def getUpdatedPrLabels(existingPrJson):
    labels = []
    if LOG_REQUESTS:
        print("Old PR response:")
        print(existingPrJson)

    for label in existingPrJson["labels"]:
        labels.append(label["name"])

    if LABEL_TO_ADD not in labels:
        labels.append(LABEL_TO_ADD)
        updateLabels = True

    return labels


################################################################################
# Create release

if CREATE_GITHUB_RELEASE:
    data = {
        "tag_name": PR_RELEASE,
        "name": PR_RELEASE,
        "body": getReleaseMarkdownLink(PR_RELEASE).capitalize(),
        "draft": False,
        "prerelease": False,
    }

    try:
        if DRY_RUN:
            print("DRY RUN: Create release request:")
            print(
                "https://api.github.com/repos/maweeks/{0}/releases".format(
                    PR_REPOSITORY
                )
            )
            print(json.dumps(data))
        else:
            createRelease = requests.post(
                "https://api.github.com/repos/maweeks/{0}/releases".format(
                    PR_REPOSITORY
                ),
                auth=GITHUB_CREDENTIALS,
                data=json.dumps(data),
            )
            if LOG_REQUESTS:
                print("Create release response:")
                print(createRelease.text)
    except:
        print("fail")
        raise SystemExit(e)
else:
    print("Skipping create release.")


################################################################################
# Generate release notes

existingPrCommits = getPrCommits(PR_ISSUE_NUMBER)

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
            branch = commit[len(prNumber) + 24 :]
            prs.append([prNumber, branch])
        else:
            commits.append(commit)

for pr in prs:
    prTickets = getTicketsFromString(pr[1])

    prCommits = getPrCommits(pr[0].split("#")[1])
    for prCommit in prCommits:
        prTickets += getTicketsFromString(prCommit["commit"]["message"].split("\n")[0])
        commits.remove(prCommit["commit"]["message"])

    if len(prTickets) == 0:
        readmeData.append(["", [], "Other", pr[1].split("/")[-1]])
    else:
        addTicketsToTickets(prTickets)

for commit in commits:
    commitTickets = getTicketsFromString(commit)
    if len(commitTickets) > 0:
        addTicketsToTickets(commitTickets)
    else:
        readmeData.append(["", [], "Other", commit])

for ticket in tickets:
    readmeData.append(getTicketDetails(ticket))

# [ticket,    prs,     type,   message]
# ["OXA-123", [13, 2], "Bugs", "Message"]
if teamcityChange:
    readmeData.append(["", [], "Other", "Updated TeamCity build(s)."])

readmeData.sort(key=lambda x: (x[0], x[3]))

readmeString = "{0} {1}:".format(
    PR_REPOSITORY.capitalize(), getReleaseMarkdownLink(PR_RELEASE)
)

for section in README_SECTIONS:
    sectionString = ""
    for item in readmeData:
        sectionString += getReadmeItemText(item, section)
    if sectionString != "":
        readmeString += "\n\n{0}:\n\n{1}".format(section, sectionString)

print("##################################################")
print(readmeString)
print("##################################################")


################################################################################
# Update PR

updateLabels = False
labels = []

existingPr = requests.get(
    "https://api.github.com/repos/maweeks/{0}/issues/{1}".format(
        PR_REPOSITORY, PR_ISSUE_NUMBER
    ),
    auth=GITHUB_CREDENTIALS,
).json()

prData = {"labels": getUpdatedPrLabels(existingPr)}

if UPDATE_PR_TEXT:
    prData["title"] = "Release {0}".format(PR_RELEASE)
    prData["body"] = readmeString

if DRY_RUN:
    print("DRY RUN: Create release request:")
    print(
        "https://api.github.com/repos/maweeks/{0}/issues/{1}".format(
            PR_REPOSITORY, PR_ISSUE_NUMBER
        )
    )
    print(json.dumps(prData))
else:
    updatePR = requests.patch(
        "https://api.github.com/repos/maweeks/{0}/issues/{1}".format(
            PR_REPOSITORY, PR_ISSUE_NUMBER
        ),
        auth=GITHUB_CREDENTIALS,
        data=json.dumps(prData),
    )

    if LOG_REQUESTS:
        print("Update PR response:")
        print(updatePR.text)

print("Script complete.")
