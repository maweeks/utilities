from generateTicketStatusPage import *


def test_introContent():
    assert introContent()[:12] == "# Test title"


def test_getTicketData():
    expected = [{"title": "Extra tickets in epic", "tickets": []}]
    assert expected == getTicketData([])


def test_getTicketLink_without_ticket_code():
    assert "ABC-_____" == getTicketLink({})


def test_getTicketLink_with_ticket_code():
    assert "[ABC-123](https://testBase.atlassian.net/browse/ABC-123)" == getTicketLink(
        {"code": "ABC-123"})


def test_getTicketStatusIcons_with_status_not_blocked():
    assert "✅" == getTicketStatusIcons({"status": "done"})
    assert "🟣" == getTicketStatusIcons({"status": "test"})
    assert "🟡" == getTicketStatusIcons({"status": "ready"})
    assert "📝" == getTicketStatusIcons({"status": "design"})


def test_getTicketStatusIcons_with_status_blocked():
    assert "✅⛔" == getTicketStatusIcons({"status": "done", "blocked": True})
    assert "🟣⛔" == getTicketStatusIcons({"status": "test", "blocked": True})
    assert "🟡⛔" == getTicketStatusIcons({"status": "ready", "blocked": True})
    assert "📝⛔" == getTicketStatusIcons({"status": "design", "blocked": True})


def test_getTicketStatusIcons_without_status_not_blocked():
    assert "❔" == getTicketStatusIcons({})


def test_getTicketStatusIcons_without_status_blocked():
    assert "❔⛔" == getTicketStatusIcons({"blocked": True})
