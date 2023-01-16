#!/usr/bin/env python3
from ttp import ttp
import json, requests
from main import UnparsedEmail
from pydantic import BaseModel
from time import sleep


class ParsedEmail(BaseModel):
    provider: str
    customer: str
    ref: str
    start: str
    end: str
    timezone: str
    city: str
    state: str
    country: str
    service_id: str
    impact: int
    contact_email:str
    contact_phone:str
    prev_cancelled: str
    action: str
    reason: str

    class Config:
        schema_extra = {
            "example": {
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
        }

def impact_in_seconds(result):
    impact = result.get("impact").split()
    multiple = int(impact[0])
    duration = int(impact[2])
    unit = impact[3]
    if unit == 'hours':
        result['impact'] = multiple * duration * 60 * 60


def parse_email(email:UnparsedEmail) -> ParsedEmail:
    parser = ttp(data=email, template="email_template.ttp", log_level='CRITICAL')
    parser.parse()
    result = parser.result(format="json")
    result = json.loads(result[0])[0]
    impact_in_seconds(result)

    return result


if __name__ == "__main__":
    base_url = "http://localhost:8000"
    while True:   
        print("polling for new emails...")
        response = requests.get(f"{base_url}/helpdesk/get-email/")
        message = response.json().get("message")
        email = response.json().get("detail").get("body")
        if message == "email read":
            print(message)
            parsed_email = parse_email(email)
            response = requests.post(f"{base_url}/database/insert-email/", json=parsed_email)
            print(response.json())
        else:
            print(message)
            sleep(30)