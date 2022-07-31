#!/usr/bin/env python3

from datetime import datetime
from authSecret import *
from configSecret import *


def introContent():
    return f"# {title}\n\n\
[Current page]({documentLink})\n\n\
Updated at: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n\
This is a general overview for what’s required for each stage - Jira is source of truth for individual ticket status. @Matt Weeks will update this page every so often.\n\n\
## Key\n\n\
{icons['done']} Done\n\
{icons['test']} In test\n\
{icons['ready']} Ready to pick up / in progress\n\
{icons['blocked']} Defined/started but blocked from progress\n\
{icons['design']} Not ready to pick up / not yet defined\n\
{icons['unknown']} Status unknown 😨\n\
{defaultTicketCode}-_____ - No ticket created yet\n\
\n\
**Example:**\n\
{icons['unknown']} [{defaultTicketCode}-]({jiraBaseUrl}browse/{defaultTicketCode}-) - Description\n\n"


def getTicketData(data):
    processedData = data
    processedData += [{"title": "Extra tickets in epic", "tickets": []}]
    return processedData


def getTicketLink(ticket):
    if 'code' in ticket:
        return f"[{ticket['code']}]({jiraBaseUrl}browse/{ticket['code']})"
    else:
        return f"{defaultTicketCode}-_____"


def getTicketStatusIcons(ticket):
    iconString = ""
    if ("status" in ticket) and (ticket['status'] in ['done', 'test', 'ready', 'design']):
        iconString += icons[ticket['status']]
    else:
        iconString += f"{icons['unknown']}"
    if "blocked" in ticket and ticket['blocked']:
        iconString += icons['blocked']
    return iconString


def ticketsContent(data):
    # output = "## Tickets\n"
    output = "**Tickets**"
    for group in data:
        # output += f"\n## {group['title']}\n\n"
        output += f"\n**{group['title']}:**\n"
        if len(group['tickets']) > 0:
            for ticket in group['tickets']:
                output += f"{getTicketStatusIcons(ticket)} {getTicketLink(ticket)} - {ticket['title']}\n"
        else:
            output += "None\n"
    return output


def generateOutput(data):
    return introContent() + ticketsContent(data)


def outputToFile(output):
    text_file = open(fileName, "w")
    text_file.write(output)
    text_file.close()


def main():
    print('Running generate ticket status:')
    print('Getting ticket statuses...')
    processedData = getTicketData(ticketGroupings)
    print('Generating ticket status output...')
    output = generateOutput(processedData)
    print('Saving ticket status output to file...')
    outputToFile(output)
    # print('Uploading ticket status to confluence...')?
    print('Generate ticket status complete!')


if __name__ == "__main__":
    main()
