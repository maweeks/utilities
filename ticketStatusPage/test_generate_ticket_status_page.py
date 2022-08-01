import datetime

import config_secret_test as cs
import generate_ticket_status_page as gtsp


def test_get_epic_api_url(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'jira_base_url',
                        cs.jira_base_url)
    expected = "https://testBase.atlassian.net/rest/agile/latest/epic/EPC-13/issue?maxResults=200"
    assert expected == gtsp.get_epic_api_url(cs.epics[0])


def test_get_ticket_api_url(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'jira_base_url',
                        cs.jira_base_url)
    expected = "https://testBase.atlassian.net/rest/agile/latest/issue/ABC-313"
    assert expected == gtsp.get_ticket_api_url('ABC-313')


def test_call_get_epic_issues_fail(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'jira_base_url',
                        cs.jira_base_url)
    monkeypatch.setattr(gtsp, 'jira_auth', "")
    assert [] == gtsp.call_get_epic_issues(cs.epics)


def test_call_get_ticket_fail(monkeypatch):
    monkeypatch.setattr(gtsp.config, 'jira_base_url',
                        cs.jira_base_url)
    monkeypatch.setattr(gtsp, 'jira_auth', "")
    assert {} == gtsp.call_get_ticket('ABC-123')


def test_get_epic_issues_empty():
    assert [] == gtsp.get_epic_issues([])


def test_get_epic_issues_with_epic(monkeypatch):
    monkeypatch.setattr(gtsp, 'call_get_epic_issues',
                        lambda x: [{"key": "ABC-123", "fields": {"status": 'In Progress'}},
                                   {"key": "ABC-135", "fields": {"status": 'Testing'}}])
    assert [{"key": "ABC-123", "fields": {"status": 'In Progress'}},
            {"key": "ABC-135", "fields": {"status": 'Testing'}}] == gtsp.get_epic_issues(["EPC-1"])


def test_merge_ticket_details():
    assert {"title": "Test Summary 1", 'status': 'done'} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary 1", "status": {"name": "AWAITING RELEASE"}}})

    assert {"title": "Test Summary 2", 'status': 'test'} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary 2", "status": {"name": "Testing"}}})

    assert {"title": "Test Summary 3", 'status': 'ready'} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary 3", "status": {"name": "In Progress"}}})

    assert {"title": "Test Summary 4", 'status': 'ready'} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary 4", "status": {"name": "UpNext"}}})

    assert {"title": "Test Summary 5", 'status': 'ready'} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary 5", "status": {"name": "Up Next"}}})

    assert {"title": "Test Summary 6", 'status': 'design'} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary 6", "status": {"name": "Backlog"}}})

    assert {"title": "Test Summary Title Provided", 'status': 'ready'} == gtsp.merge_ticket_details(
        {"title": "Test Summary Title Provided"}, {"fields": {"summary": "Test Summary Jira Title", "status": {"name": "In Progress"}}})

    assert {"title": "Test Summary Blocked", 'status': 'ready', 'blocked': True} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary Blocked", "status": {"name": "In Progress"}, 'labels': ['Blocked']}})

    assert {"title": "Test Summary On hold", 'status': 'ready', 'blocked': True} == gtsp.merge_ticket_details(
        {}, {"fields": {"summary": "Test Summary On hold", "status": {"name": "In Progress"}, 'labels': ['OnHold']}})


def test_get_ticket_data_no_epics(monkeypatch):
    expected = [{
        "title": "Important path",
        "tickets": [
            {"code": "TST-123", "title": "Ticket 1"},
            {"code": "TST-314", "title": "Ticket 6"},
            {"title": "Ticket 2", "status": "design"}
        ]
    },
        {
        "title": "Other path",
        "tickets": [
            {"title": "Ticket 3", "status": "design"}
        ]
    },
        {
        "title": "To be sorted",
        "tickets": []
    }, {
        "title": "Extra tickets in epic",
        "tickets": []
    }]
    assert expected == gtsp.get_ticket_data(cs.ticket_groupings, [])


def test_get_ticket_data_with_epics(monkeypatch):
    tickets = [
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

    epic_tickets = [{"key": "TST-123", "fields": {"summary": "123", "status": {"name": 'In Progress'}}},
                    {"key": "TST-135", "fields": {"summary": "234", "status": {"name": 'Testing'}}}]
    monkeypatch.setattr(gtsp, 'call_get_epic_issues', lambda x: epic_tickets)

    expected = [
        {
            "title": "Important path",
            "tickets": [{'code': 'TST-123', 'title': 'Ticket 1', 'status': 'ready'},
                        {'code': 'TST-314', 'title': 'Ticket 6'},
                        {'title': 'Ticket 2', "status": "design"}]
        },
        {
            "title": "Other path",
            "tickets": [{'title': 'Ticket 3', "status": "design"}]
        },
        {
            "title": "To be sorted",
            "tickets": []
        },
        {
            "title": "Extra tickets in epic",
            "tickets": [{"code": "TST-135", "title": "234", 'status': 'test'}]
        }
    ]

    assert expected == gtsp.get_ticket_data(tickets, epic_tickets)


def test_get_intro_content_first_few_lines(monkeypatch):
    date_time = datetime.datetime

    class MyDatetime():
        @staticmethod
        def now():
            return date_time(2022, 7, 6, 5, 4, 3)

    monkeypatch.setattr(gtsp.config, 'document_link', cs.document_link)
    monkeypatch.setattr(gtsp.config, 'title', cs.title)
    monkeypatch.setattr(gtsp.datetime, 'datetime', MyDatetime)

    assert gtsp.get_intro_content()[:113] == """# Test Title

[Current page](https://testDoc.atlassian.net/wiki/spaces/testFile)

Updated at: 06/07/2022 05:04:03"""


def test_get_ticket_data_add_extra_tickets_section():
    expected = [{"title": "Extra tickets in epic", "tickets": []}]
    assert expected == gtsp.get_ticket_data([], [])


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
🟠 [TST-314](https://testBase.atlassian.net/browse/TST-314) - Ticket 6
🔵 TST-_____ - Ticket 2

### Other path

🔵 TST-_____ - Ticket 3

### To be sorted

None
"""
    assert expected == gtsp.get_tickets_content(cs.ticket_groupings)
