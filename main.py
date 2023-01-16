from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List
import os, shutil, pymongo,uuid


class UnparsedEmail(BaseModel):
    name: str
    body: str

class ParsedEmail(BaseModel):
    id: str = Field(default_factory=uuid.uuid4, alias="_id")
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
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "_id": "066de609-b04a-4b30-b46c-32537c7f1f6e",
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

app = FastAPI()


conn_str = f"mongodb+srv://{os.getenv('USERNAME')}:{os.getenv('PASSWORD')}@cluster0.yybae.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(conn_str, serverSelectionTimeoutMS=5000)
database = client["packetfabric"]
try:
    print("Connecting to database../")
    print(client.server_info())
except Exception:
    print("Unable to connect to the server.")


@app.get("/helpdesk/get-email/")
async def get_email_from_helpdesk():
    """Simulate helpdesk api for email retreival. Get email and move to read."""
    email_obj :UnparsedEmail = {}
    try:
        email = os.listdir("unread_emails").pop()
        with open(f"unread_emails/{email}") as f:
            email_body = f.read()
            email_obj['name'] = email
            email_obj['body'] = email_body

            shutil.move(f"unread_emails/{email}", f"read_emails/{email}")
            return { "message": "email read",
                    "detail": email_obj }
    except IndexError as e:
        return { "message": "no unread emails",
                    "detail": email_obj }

@app.get("/database/get-emails/",response_model=List[ParsedEmail])
async def get_parsed_emails(limit: int = 100):
    """Get parsed emails from database."""
    return list(database['emails'].find(limit=limit))

@app.post("/database/insert-email/",status_code=201)
async def insert_email(email:ParsedEmail):
    """Get parsed emails from database."""
    email = jsonable_encoder(email)
    new_email = database['emails'].insert_one(email)
    created_email = database['emails'].find_one(
        {"_id": new_email.inserted_id}
    )
    return { "message": "added email to database",
                    "detail": created_email }
