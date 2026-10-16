import os
from twilio.rest import Client


def send_sms(to_number: str, body: str):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth = os.getenv("TWILIO_AUTH_TOKEN")
    sender = os.getenv("TWILIO_FROM")
    if not (sid and auth and sender):
        print(f"[sms] {to_number}: {body}")
        return True
    try:
        client = Client(sid, auth)
        client.messages.create(body=body, from_=sender, to=to_number)
        return True
    except Exception:
        return False
