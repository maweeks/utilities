#!/usr/bin/env python3

from datetime import datetime
import authSecret as auth
import configSecret as config


def get_intro_content():
    return f"# {config.title}\n\n\
[Current page]({config.document_link})\n\n\
Updated at: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n\
This is a general overview for what’s required for each stage - Jira is source of truth for individual ticket status. @Matt Weeks will update this page every so often.\n\n\
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


def get_ticket_data(data):
    processed_data = data
    processed_data += [{"title": "Extra tickets in epic", "tickets": []}]
    return processed_data


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
    processed_data = get_ticket_data(config.ticket_groupings)
    print('Generating ticket status output...')
    output = generate_output(processed_data)
    print('Saving ticket status output to file...')
    output_to_file(output)
    print('Generate ticket status complete!')


if __name__ == "__main__":
    main()
