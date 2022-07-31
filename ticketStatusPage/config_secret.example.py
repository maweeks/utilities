#!/usr/bin/env python3

title = "Random tickets"
file_name = "ticketStatusOutput.md"
document_link = "https://abc.atlassian.net/wiki/spaces/"
jira_base_url = "https://abc.atlassian.net/"
author = "Matt Weeks"
icons = {
    "done": "✅",
    "test": "🟣",
    "ready": "🟡",
    "blocked": "⛔",
    "design": "📝",
    "unknown": "❔"
}
default_ticket_code = "ABC"
epics = []
ticket_groupings = [
    {
        "title": "Critical path",
        "tickets": [
            {"code": "ABC-123", "title": "Ticket 1"},
            {"title": "Ticket 2"}
        ]
    },
    {
        "title": "Non critical path",
        "tickets": [
            {"title": "Ticket 3"}
        ]
    },
    {
        "title": "To be sorted",
        "tickets": []
    }
]
