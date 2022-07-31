import configSecret as cs
import generateTicketStatusPage as gtsp


def test_get_intro_content():
    assert gtsp.get_intro_content()[:12] == "# Test title"


def test_get_ticket_data():
    expected = [{"title": "Extra tickets in epic", "tickets": []}]
    assert expected == gtsp.get_ticket_data([])


def test_get_ticket_link_without_ticket_code():
    assert "ABC-_____" == gtsp.get_ticket_link({})


def test_get_ticket_link_with_ticket_code():
    assert "[ABC-123](https://testBase.atlassian.net/browse/ABC-123)" == gtsp.get_ticket_link(
        {"code": "ABC-123"})


def test_get_ticket_status_icons_with_status_not_blocked():
    assert "✅" == gtsp.get_ticket_status_icons({"status": "done"})
    assert "🟣" == gtsp.get_ticket_status_icons({"status": "test"})
    assert "🟡" == gtsp.get_ticket_status_icons({"status": "ready"})
    assert "📝" == gtsp.get_ticket_status_icons({"status": "design"})


def test_get_ticket_status_icons_with_status_blocked():
    assert "✅⛔" == gtsp.get_ticket_status_icons(
        {"status": "done", "blocked": True})
    assert "🟣⛔" == gtsp.get_ticket_status_icons(
        {"status": "test", "blocked": True})
    assert "🟡⛔" == gtsp.get_ticket_status_icons(
        {"status": "ready", "blocked": True})
    assert "📝⛔" == gtsp.get_ticket_status_icons(
        {"status": "design", "blocked": True})


def test_get_ticket_status_icons_without_status_not_blocked():
    assert "❔" == gtsp.get_ticket_status_icons({})


def test_get_ticket_status_icons_without_status_blocked():
    assert "❔⛔" == gtsp.get_ticket_status_icons({"blocked": True})


def test_get_tickets_content():
    expected = """## Tickets

### Critical path

❔ [ABC-123](https://testBase.atlassian.net/browse/ABC-123) - Ticket 1
❔ ABC-_____ - Ticket 2

### Non critical path

❔ ABC-_____ - Ticket 3

### To be sorted

None
"""
    assert expected == gtsp.get_tickets_content(cs.ticket_groupings)
