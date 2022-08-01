#!/usr/bin/env python3

import datetime
import requests


from auth_secret import jira_auth
import config_secret as config


def get_epic_api_url(epic_code):
    return f"{config.jira_base_url}rest/agile/latest/epic/{epic_code}/issue?maxResults=200"


def get_ticket_api_url(ticket_code):
    return f"{config.jira_base_url}rest/agile/latest/issue/{ticket_code}"


def call_get_epic_issues(epic_code):
    try:
        response = requests.get(
            get_epic_api_url(epic_code), auth=jira_auth
        ).json()
        return response['issues']
    except Exception:
        print(f'Failed to get epic: {epic_code}')
        return []


def call_get_ticket(ticket_code):
    try:
        response = requests.get(get_ticket_api_url(
            ticket_code), auth=jira_auth).json()
        return response
    except Exception:
        print(f'Failed to get ticket: {ticket_code}')
        return {}


def get_epic_issues(epics):
    epic_issues = []
    for epic in epics:
        epic_issues += call_get_epic_issues(epic)
    return epic_issues


def merge_ticket_details(ticket, jira_ticket):
    if ('labels' in jira_ticket['fields'] and (
        'Blocked' in jira_ticket['fields']['labels'] or
        'OnHold' in jira_ticket['fields']['labels']
    )):
        ticket['blocked'] = True

    jira_status = jira_ticket['fields']['status']['name']
    if jira_status in ['AWAITING RELEASE']:
        ticket['status'] = 'done'
    elif jira_status in ['Testing']:
        ticket['status'] = 'test'
    elif jira_status in ['UpNext', 'In Progress']:
        ticket['status'] = 'ready'
    elif jira_status in ['Backlog']:
        ticket['status'] = 'design'
    elif 'Up Next':
        if ('labels' in jira_ticket['fields'] and ('OnHold' in jira_ticket['fields']['labels'])):
            ticket['status'] = 'design'
        else:
            ticket['status'] = 'ready'

    if 'title' not in ticket:
        ticket['title'] = jira_ticket['fields']['summary']
    return ticket


def get_ticket_data(data, epic_issues):
    processed_data = []
    listed_epic_issues = []
    extra_epic_issues = []
    for group in data:
        group_data = {"title": group['title'], "tickets": []}
        for ticket in group['tickets']:
            if 'code' in ticket:
                jira_ticket_details = [
                    p for p in epic_issues if p['key'] == ticket['code']]
                if len(jira_ticket_details) > 0:
                    listed_epic_issues += [ticket['code']]

                    group_data['tickets'] += [
                        merge_ticket_details(ticket, jira_ticket_details[0])]
                else:
                    jira_ticket_details = call_get_ticket(ticket['code'])
                    if 'key' in jira_ticket_details:
                        ticket = merge_ticket_details(ticket, jira_ticket_details)
                    group_data['tickets'] += [ticket]
            else:
                ticket['status'] = 'design'
                group_data['tickets'] += [ticket]
        processed_data += [group_data]

    for issue in epic_issues:
        if issue['key'] not in listed_epic_issues:
            listed_epic_issues += [issue['key']]
            extra_epic_issues += [merge_ticket_details(
                {"code": issue['key']}, issue)]

    processed_data += [{"title": "Extra tickets in epic",
                        "tickets": extra_epic_issues}]
    return processed_data


def get_intro_content():
    now = datetime.datetime.now()
    return f"# {config.title}\n\n\
[Current page]({config.document_link})\n\n\
Updated at: {now.strftime('%d/%m/%Y %H:%M:%S')}\n\n\
This is a general overview for what’s required for each stage - Jira is source of truth for individual ticket status. @{config.author} will update this page every so often.\n\n\
## Key\n\n\
{config.icons['done']} Done\n\
{config.icons['test']} In test\n\
{config.icons['ready']} Ready to pick up / in progress\n\
{config.icons['blocked']} Defined/started but blocked from progress\n\
{config.icons['design']} Not ready to pick up / not yet defined\n\
{config.icons['unknown']} Status unknown 😨\n\
{config.default_ticket_code}-_____ - No ticket created yet\n\
\n\
**Example:**\n\
{config.icons['unknown']} [{config.default_ticket_code}-]({config.jira_base_url}browse/{config.default_ticket_code}-) - Description\n\n"


def get_ticket_link(ticket):
    if 'code' in ticket:
        return f"[{ticket['code']}]({config.jira_base_url}browse/{ticket['code']})"
    else:
        return f"{config.default_ticket_code}-_____"


def get_ticket_status_icons(ticket):
    icon_string = ""
    if ("status" in ticket) and (ticket['status'] in ['done', 'test', 'ready', 'design']):
        icon_string += config.icons[ticket['status']]
    else:
        icon_string += f"{config.icons['unknown']}"
    if "blocked" in ticket and ticket['blocked']:
        icon_string += config.icons['blocked']
    return icon_string


def get_tickets_content(data):
    output = "## Tickets\n"
    for group in data:
        output += f"\n### {group['title']}\n\n"
        if len(group['tickets']) > 0:
            for ticket in group['tickets']:
                output += f"{get_ticket_status_icons(ticket)} {get_ticket_link(ticket)} - {ticket['title']}\n"
        else:
            output += "None\n"
    return output


def generate_output(data):
    return get_intro_content() + get_tickets_content(data)


def output_to_file(output):
    text_file = open(config.file_name, "w")
    text_file.write(output)
    text_file.close()


def main():
    print('Running generate ticket status:')
    print('Getting ticket statuses...')
    processed_data = get_ticket_data(
        config.ticket_groupings, get_epic_issues(config.epics))
    print('Generating ticket status output...')
    output = generate_output(processed_data)
    print('Saving ticket status output to file...')
    output_to_file(output)
    print('Generate ticket status complete!')


if __name__ == "__main__":
    main()
