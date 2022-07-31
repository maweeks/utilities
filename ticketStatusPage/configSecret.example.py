#!/usr/bin/env python3

title = "Random tickets"
fileName = "ticketStatusOutput.md"
documentLink = "https://abc.atlassian.net/wiki/spaces/"
jiraBaseUrl = "https://abc.atlassian.net/"
author = "Matt Weeks"
icons = {
    "done": "✅",
    "test": "🟣",
    "ready": "🟡",
    "blocked": "⛔",
    "design": "📝",
    "unknown": "❔"
}
defaultTicketCode = "ABC"
ticketGroupings = [
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
