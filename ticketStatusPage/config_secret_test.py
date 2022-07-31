#!/usr/bin/env python3

title = "Test Title"
file_name = "testStatusFile.md"
document_link = "https://testDoc.atlassian.net/wiki/spaces/testFile"
jira_base_url = "https://testBase.atlassian.net/"
author = "Matt Weeks"
icons = {
    "done": "🚀",
    "test": "⚙️",
    "ready": "🥳",
    "blocked": "🔴",
    "design": "🔵",
    "unknown": "🟠"
}
default_ticket_code = "TST"
epics = ['EPC-13']
ticket_groupings = [
    {
        "title": "Important path",
        "tickets": [
            {"code": "TST-123", "title": "Ticket 1"},
            {"code": "TST-314", "title": "Ticket 6"},
            {"title": "Ticket 2"}
        ]
    },
    {
        "title": "Other path",
        "tickets": [
            {"title": "Ticket 3"}
        ]
    },
    {
        "title": "To be sorted",
        "tickets": []
    }
]
