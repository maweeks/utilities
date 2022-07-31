#!/usr/bin/env python3

from datetime import datetime
import authSecret as auth
import configSecret as config


def intro_content():
    return f"# {config.title}\n\n\
[Current page]({config.documentLink})\n\n\
Updated at: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n\
This is a general overview for what’s required for each stage - Jira is source of truth for individual ticket status. @Matt Weeks will update this page every so often.\n\n\
## Key\n\n\
{config.icons['done']} Done\n\
{config.icons['test']} In test\n\
{config.icons['ready']} Ready to pick up / in progress\n\
{config.icons['blocked']} Defined/started but blocked from progress\n\
{config.icons['design']} Not ready to pick up / not yet defined\n\
{config.icons['unknown']} Status unknown 😨\n\
{config.defaultTicketCode}-_____ - No ticket created yet\n\
\n\
**Example:**\n\
{config.icons['unknown']} [{config.defaultTicketCode}-]({config.jiraBaseUrl}browse/{config.defaultTicketCode}-) - Description\n\n"


def get_ticket_data(data):
    processedData = data
    processedData += [{"title": "Extra tickets in epic", "tickets": []}]
    return processedData


def getTicketLink(ticket):
    if 'code' in ticket:
        return f"[{ticket['code']}]({config.jiraBaseUrl}browse/{ticket['code']})"
    else:
        return f"{config.defaultTicketCode}-_____"


def getTicketStatusIcons(ticket):
    iconString = ""
    if ("status" in ticket) and (ticket['status'] in ['done', 'test', 'ready', 'design']):
        iconString += config.icons[ticket['status']]
    else:
        iconString += f"{config.icons['unknown']}"
    if "blocked" in ticket and ticket['blocked']:
        iconString += config.icons['blocked']
    return iconString


def ticketsContent(data):
    # output = "## Tickets\n"
    output = "**Tickets**"
    for group in data:
        # output += f"\n## {group['title']}\n\n"
        output += f"\n**{group['title']}:**\n"
        if len(group['tickets']) > 0:
            for ticket in group['tickets']:
                output += f"{config.getTicketStatusconfig.icons(ticket)} {getTicketLink(ticket)} - {ticket['title']}\n"
        else:
            output += "None\n"
    return output


def generateOutput(data):
    return intro_content() + ticketsContent(data)


def outputToFile(output):
    text_file = open(config.fileName, "w")
    text_file.write(output)
    text_file.close()


def main():
    print('Running generate ticket status:')
    print('Getting ticket statuses...')
    processedData = get_ticket_data(config.ticketGroupings)
    print('Generating ticket status output...')
    output = generateOutput(processedData)
    print('Saving ticket status output to file...')
    outputToFile(output)
    # print('Uploading ticket status to confluence...')?
    print('Generate ticket status complete!')


if __name__ == "__main__":
    main()
