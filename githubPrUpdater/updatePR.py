from datetime import date
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
NOTES_SECTIONS = ["Features", "Fixes", "Tickets", "Other"]
LOG_RESPONSES = False
SLACK_CHANNEL = "#general"
OUTPUT_LINE_BREAK = "##################################################"

PR_REPOSITORY = str(sys.argv[1])
PR_ISSUE_NUMBER = str(sys.argv[2])
PR_RELEASE = str(sys.argv[3])
DRY_RUN = "Y" == str(sys.argv[4])
INCLUDE_DATE_GENERATED = "Y" == str(sys.argv[5])
CREATE_GITHUB_RELEASE = "Y" == str(sys.argv[6])
UPDATE_PR_TEXT = "Y" == str(sys.argv[7])
EXPORT_RELEASE_NOTES = "Y" == str(sys.argv[8])
POST_TO_SLACK = "Y" == str(sys.argv[9])
GITHUB_CREDENTIALS = "token {0}".format(str(sys.argv[10]))
TICKET_CREDENTIALS = (TICKET_USER, str(sys.argv[11]))
SLACK_TOKEN = str(sys.argv[12])
EXPORT_DIR = str(sys.argv[13])


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


def get_github_pr_url(pr_number):
    return "https://github.com/{0}/{1}/pull/{2}".format(
        DEFAULT_REPO_OWNER, PR_REPOSITORY, pr_number
    )


def get_release_markdown_link(release):
    return "release [{0}]({1})".format(
        release, get_github_pr_url(PR_ISSUE_NUMBER)
    )


def get_release_slack_link(release):
    return "release <{1}|{0}>".format(
        release, get_github_pr_url(PR_ISSUE_NUMBER)
    )


def get_slack_pr_link(pr):
    return '<{1}|{0}>'.format(pr, get_github_pr_url(pr.replace('#', '')))


def get_ticket_markdown_link(ticket):
    return "[{0}]({1}browse/{0}) ".format(ticket, TICKET_BASE_URL)


def get_ticket_slack_link(ticket):
    return "<{1}browse/{0}|{0}> ".format(ticket, TICKET_BASE_URL)


def get_notes_item_text(item, section):
    item_md = ""
    item_slack = ""
    if item[2] == section:
        if len(item[1]) > 0:
            item[1].sort()
            item_md = ["{0}".format(str(pr)) for pr in item[1]]
            item_md = str(item_md).replace("'", "") + " "
            item_slack = [
                "{0}".format(get_slack_pr_link(str(pr)))
                for pr in item[1]
            ]
            item_slack = str(item_slack).replace("'", "") + " "
        if len(item[0]) > 0:
            item_md = get_ticket_markdown_link(item[0]) + item_md
            item_slack = get_ticket_slack_link(item[0]) + item_slack
        if item_md != "":
            item_md = "- " + item_md
            item_slack = "- " + item_slack
        if item[3] != "":
            item_md += "- {0}".format(item[3])
            item_slack += "- {0}".format(item[3]
                                         .replace('&', '&amp;')
                                         .replace('<', '&lt;')
                                         .replace('>', '&gt;'))
        if len(item_md) > 0:
            item_md = item_md.strip() + "\n"
            item_slack = item_slack.strip() + "\n"
    return item_md, item_slack


def get_pr_commits(issue_number):
    try:
        return requests.get(
            "https://api.github.com/repos/{0}/{1}/pulls/{2}/commits?per_page=250".format(
                DEFAULT_REPO_OWNER, PR_REPOSITORY, issue_number
            ),
            headers={"Authorization": GITHUB_CREDENTIALS},
        ).json()
    except Exception:
        print("Failed to get main PR commits {0}".format(PR_ISSUE_NUMBER))
        raise SystemExit()


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
    return tickets


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


def get_prs_from_pr(existing_pr_commits):
    commits = []
    prs = []
    teamcity_change = False
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
    return commits, prs, teamcity_change


def get_tickets_from_pr(commits, include_pr, pr_commits, pr_tickets):
    for pr_commit in pr_commits:
        pr_commit_message = pr_commit["commit"]["message"].split("\n")[
            0]
        if include_pr:
            pr_tickets += get_tickets_from_string(
                pr_commit_message
            )
        if pr_commit_message in commits:
            commits.remove(pr_commit_message)
    return commits, pr_tickets


def get_data_from_prs(commits, prs):
    notes_data = []
    tickets = {}
    for pr in prs:
        pr_tickets = get_tickets_from_string(pr[1])
        include_pr = False
        try:
            pr_commits = get_pr_commits(pr[0].split("#")[1])
            include_pr = should_include_pr(pr[0].split("#")[1])
            commits, pr_tickets = get_tickets_from_pr(
                commits, include_pr, pr_commits, pr_tickets)
        except Exception:
            print("Failed to get feature PR commits {0}".format(
                PR_ISSUE_NUMBER))
            raise SystemExit()

        if include_pr:
            if len(pr_tickets) == 0:
                notes_data.append(
                    ["", [pr[0]], "Other", pr[1].split("/")[-1]])
            else:
                tickets = add_tickets_to_tickets(pr_tickets, tickets, pr)
    return commits, notes_data, tickets


def get_data_from_commits(commits, notes_data, tickets):
    for commit in commits:
        commit_tickets = get_tickets_from_string(commit)
        if len(commit_tickets) > 0:
            for new_ticket in commit_tickets:
                if new_ticket not in tickets:
                    tickets[new_ticket] = []
        else:
            notes_data.append(["", [], "Other", commit])
    return notes_data, tickets


def generate_notes_data():
    existing_pr_commits = get_pr_commits(PR_ISSUE_NUMBER)
    commits, prs, teamcity_change = get_prs_from_pr(existing_pr_commits)
    commits, notes_data, tickets = get_data_from_prs(commits, prs)
    notes_data, tickets = get_data_from_commits(
        commits, notes_data, tickets)

    for ticket in tickets:
        notes_data.append(get_ticket_details(ticket, tickets))

    if teamcity_change:
        notes_data.append(["", [], "Other", "Updated TeamCity build(s)."])

    notes_data.sort(key=lambda x: (x[0], x[3]))
    return notes_data


def get_notes_heading(link):
    return "{0} {1}:\n".format(PR_REPOSITORY.capitalize(), link)


def generate_notes_strings(notes_data):
    notes_md = get_notes_heading(get_release_markdown_link(PR_RELEASE))
    notes_slack = "<!here> " + \
        get_notes_heading(get_release_slack_link(PR_RELEASE))

    if INCLUDE_DATE_GENERATED:
        date_string = date.today().strftime("%Y-%m-%d")
        notes_md += "\nRelease generated: {0}\n".format(date_string)
        notes_slack += "\nRelease generated: {0}\n".format(date_string)

    for section in NOTES_SECTIONS:
        section_md = ""
        section_slack = ""
        for item in notes_data:
            item_md, item_slack = get_notes_item_text(item, section)
            section_md += item_md
            section_slack += item_slack
        if section_md != "":
            notes_md += "\n{0}:\n\n{1}".format(section, section_md)
            notes_slack += "\n{0}:\n\n{1}".format(section, section_slack)

    print(OUTPUT_LINE_BREAK)
    print(notes_md)
    print(OUTPUT_LINE_BREAK)
    print(notes_slack)
    print(OUTPUT_LINE_BREAK)

    return notes_md, notes_slack


def write_to_file(contents, file_extension):
    if EXPORT_RELEASE_NOTES:
        try:
            os.makedirs(EXPORT_DIR)
        except OSError:
            pass
        text_file = open("{0}/{1}-{2}.{3}".format(EXPORT_DIR,
                                                  PR_REPOSITORY,
                                                  PR_ISSUE_NUMBER,
                                                  file_extension
                                                  ), "w")
        text_file.write(contents)
        text_file.close()
    else:
        print("Skipping write to file.")


def update_pr(contents):
    existing_pr = ""
    try:
        existing_pr = requests.get(
            get_issue_url(),
            headers={"Authorization": GITHUB_CREDENTIALS},
        ).json()
    except Exception:
        print("Failed to get existing PR")
        raise SystemExit()

    pr_data = {}
    labels = get_pr_labels(existing_pr)

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
        if DRY_RUN:
            print("DRY RUN: Post slack message:")
            print("https://slack.com/api/chat.post_message")
            print(json.dumps(data))
        else:
            try:
                post_message = requests.post(
                    "https://slack.com/api/chat.postMessage",
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
    print('--------------------------------------------------')
    create_release()
    notes_data = generate_notes_data()
    notes_markdown_string, notes_slack_string = generate_notes_strings(
        notes_data)
    write_to_file(notes_markdown_string, 'md')
    write_to_file(notes_slack_string, 'txt')
    update_pr(notes_markdown_string)
    post_slack_message(generate_message_data(notes_slack_string))
    print("Script complete.")
    print('--------------------------------------------------')


######################################################################


if __name__ == '__main__':
    run_script()
