#!/usr/bin/env python3

title = "Test title"
file_name = "testStatusFile.md"
document_link = "https://testDoc.atlassian.net/wiki/spaces/testFile"
jira_base_url = "https://testBase.atlassian.net/"
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
