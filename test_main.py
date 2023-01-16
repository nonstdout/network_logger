from email_poller import parse_email, ParsedEmail
from main import app, UnparsedEmail
from fastapi.testclient import TestClient
import mock

client = TestClient(app)

#todo add mocks for emails
def test_get_emails():
    response = client.get("/helpdesk/get-email/")
    assert response.status_code == 200
    assert response.json()['message'] == "email read"
    isinstance(response.json()['detail'], UnparsedEmail)

#todo add mocks for emails
def test_get_emails_all_read():
    response = client.get("/helpdesk/get-email/")
    assert response.status_code == 200
    assert response.json()['message'] == "no unread emails"
    isinstance(response.json()['detail'], UnparsedEmail)
    
def test_parse_email():
    filename = "tests/test_email.txt"
    with open(filename, "r") as f:
        email = f.read()
    assert parse_email(email) == {
        "provider": "Fiber Provider",
        "customer": "AwesomeCorp",
        "ref": "PWIC12345",
        "start": "2019-Apr-09 06:00",
        "end": "2019-Apr-09 10:00",
        "timezone": "UTC",
        "city": "Santa Clara",
        "state": "CA",
        "country": "US",
        "service_id": "IC-99999",
        "impact": 10800,
        "contact_email":"noc@fiberprovider.com",
        "contact_phone":"8675309",
        "prev_cancelled": "PWIC45678",
        "action": "Fault repair work",
        "reason": "Card replacement due to malfunction transmission system card"
    }
    isinstance(parse_email(email), ParsedEmail)

def test_get_parsed_emails():
    find = mock.Mock(return_value=[])
    database = {}
    database['emails'] = mock.Mock()
    database['emails'].attach_mock(find,'find')
    with mock.patch("main.database", database):
        response=client.get("/database/get-emails/", params={"limit":2})
        database['emails'].find.assert_called_with(limit=2)
        assert response.status_code == 200

def test_insert_email():
    email = {
        "provider": "Fiber Provider",
        "customer": "AwesomeCorp",
        "ref": "PWIC12345",
        "start": "2019-Apr-09 06:00",
        "end": "2019-Apr-09 10:00",
        "timezone": "UTC",
        "city": "Santa Clara",
        "state": "CA",
        "country": "US",
        "service_id": "IC-99999",
        "impact": 10800,
        "contact_email":"noc@fiberprovider.com",
        "contact_phone":"8675309",
        "prev_cancelled": "PWIC45678",
        "action": "Fault repair work",
        "reason": "Card replacement due to malfunction transmission system card"
    }
    find_one = mock.Mock(return_value={})
    insert_one = mock.Mock(return_value=mock.Mock(spec=['inserted_id',"1234"]))
    database = {}
    database['emails'] = mock.Mock()
    database['emails'].attach_mock(find_one,'find_one')
    database['emails'].attach_mock(insert_one,'insert_one')
    with mock.patch("main.database", database):
        response = client.post("/database/insert-email/",json=email)
        database['emails'].insert_one.assert_called()
        database['emails'].find_one.assert_called()
        assert response.status_code == 201


from calculate_downtime import check_outage_planned
def test_check_outage_planned():
    work = {
        "planned_work": ["2019-Apr-09 07:28", "2019-Apr-09 07:30"],
        "outage": ["2019-Apr-09 07:28", "2019-Apr-09 07:30"]
        }

    assert check_outage_planned(work['planned_work'], work['outage']) == True

    work = {
        "planned_work": ["2019-Apr-09 07:28", "2019-Apr-09 07:30"],
        "outage": ["2019-Apr-09 07:29", "2019-Apr-09 07:30"]
        }

    assert check_outage_planned(work['planned_work'], work['outage']) == True

    work = {
        "planned_work": ["2019-Apr-09 07:28", "2019-Apr-09 07:30"],
        "outage": ["2019-Apr-09 07:21", "2019-Apr-09 07:30"]
        }

    assert check_outage_planned(work['planned_work'], work['outage']) == False

    work = {
        "planned_work": ["2019-Apr-09 07:28", "2019-Apr-09 07:30"],
        "outage": ["2019-Apr-09 07:29", "2019-Apr-09 07:33"]
        }

    assert check_outage_planned(work['planned_work'], work['outage']) == False

    work = {
        "planned_work": ["2019-Apr-09 07:28", "2019-Apr-09 07:30"],
        "outage": ["2022-Apr-09 07:28", "2019-Apr-09 07:29"]
        }

    assert check_outage_planned(work['planned_work'], work['outage']) == False
