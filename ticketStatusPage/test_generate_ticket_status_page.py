import datetime

import config_secret_test as cs
import generate_ticket_status_page as gtsp


def test_get_intro_content_first_few_lines(monkeypatch):
    date_time = datetime.datetime

    class MyDatetime():
        def now():
            return date_time(2022, 7, 6, 5, 4, 3)

    monkeypatch.setattr(gtsp.config, 'document_link', cs.document_link)
    monkeypatch.setattr(gtsp.config, 'title', cs.title)
    monkeypatch.setattr(gtsp.datetime, 'datetime', MyDatetime)

    assert gtsp.get_intro_content()[:113] == """# Test Title

[Current page](https://testDoc.atlassian.net/wiki/spaces/testFile)

Updated at: 06/07/2022 05:04:03"""


def test_get_ticket_data():
    expected = [{"title": "Extra tickets in epic", "tickets": []}]
    assert expected == gtsp.get_ticket_data([])


def test_get_ticket_link_without_ticket_code(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'default_ticket_code',
                        cs.default_ticket_code)
    assert "TST-_____" == gtsp.get_ticket_link({})


def test_get_ticket_link_with_ticket_code(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'jira_base_url',
                        cs.jira_base_url)
    assert "[TST-123](https://testBase.atlassian.net/browse/TST-123)" == gtsp.get_ticket_link(
        {"code": "TST-123"})


def test_get_ticket_status_icons_with_status_not_blocked(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'icons',
                        cs.icons)
    assert "🚀" == gtsp.get_ticket_status_icons({"status": "done"})
    assert "⚙️" == gtsp.get_ticket_status_icons({"status": "test"})
    assert "🥳" == gtsp.get_ticket_status_icons({"status": "ready"})
    assert "🔵" == gtsp.get_ticket_status_icons({"status": "design"})


def test_get_ticket_status_icons_with_status_blocked(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'icons',
                        cs.icons)
    assert "🚀🔴" == gtsp.get_ticket_status_icons(
        {"status": "done", "blocked": True})
    assert "⚙️🔴" == gtsp.get_ticket_status_icons(
        {"status": "test", "blocked": True})
    assert "🥳🔴" == gtsp.get_ticket_status_icons(
        {"status": "ready", "blocked": True})
    assert "🔵🔴" == gtsp.get_ticket_status_icons(
        {"status": "design", "blocked": True})


def test_get_ticket_status_icons_without_status_not_blocked(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'icons',
                        cs.icons)
    assert "🟠" == gtsp.get_ticket_status_icons({})


def test_get_ticket_status_icons_without_status_blocked(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'icons',
                        cs.icons)
    assert "🟠🔴" == gtsp.get_ticket_status_icons({"blocked": True})


def test_get_tickets_content(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'default_ticket_code',
                        cs.default_ticket_code)
    monkeypatch.setattr(gtsp.config, 'icons',
                        cs.icons)
    monkeypatch.setattr(gtsp.config, 'jira_base_url',
                        cs.jira_base_url)
    expected = """## Tickets

### Important path

🟠 [TST-123](https://testBase.atlassian.net/browse/TST-123) - Ticket 1
🟠 TST-_____ - Ticket 2

### Other path

🟠 TST-_____ - Ticket 3

### To be sorted

None
"""
    assert expected == gtsp.get_tickets_content(cs.ticket_groupings)
