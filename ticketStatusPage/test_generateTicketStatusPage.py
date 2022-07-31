import generateTicketStatusPage as gtsp


def test_intro_content():
    assert gtsp.intro_content()[:12] == "# Test title"


def test_get_ticket_data():
    expected = [{"title": "Extra tickets in epic", "tickets": []}]
    assert expected == gtsp.get_ticket_data([])


def test_getTicketLink_without_ticket_code():
    assert "ABC-_____" == gtsp.getTicketLink({})


def test_getTicketLink_with_ticket_code():
    assert "[ABC-123](https://testBase.atlassian.net/browse/ABC-123)" == gtsp.getTicketLink(
        {"code": "ABC-123"})


def test_getTicketStatusIcons_with_status_not_blocked():
    assert "✅" == gtsp.getTicketStatusIcons({"status": "done"})
    assert "🟣" == gtsp.getTicketStatusIcons({"status": "test"})
    assert "🟡" == gtsp.getTicketStatusIcons({"status": "ready"})
    assert "📝" == gtsp.getTicketStatusIcons({"status": "design"})


def test_getTicketStatusIcons_with_status_blocked():
    assert "✅⛔" == gtsp.getTicketStatusIcons(
        {"status": "done", "blocked": True})
    assert "🟣⛔" == gtsp.getTicketStatusIcons(
        {"status": "test", "blocked": True})
    assert "🟡⛔" == gtsp.getTicketStatusIcons(
        {"status": "ready", "blocked": True})
    assert "📝⛔" == gtsp.getTicketStatusIcons(
        {"status": "design", "blocked": True})


def test_getTicketStatusIcons_without_status_not_blocked():
    assert "❔" == gtsp.getTicketStatusIcons({})


def test_getTicketStatusIcons_without_status_blocked():
    assert "❔⛔" == gtsp.getTicketStatusIcons({"blocked": True})
