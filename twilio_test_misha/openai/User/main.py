import os

from dotenv import load_dotenv
from twilio.rest import Client

from env import *

load_dotenv()

print("TWILIO_ACCOUNT_SID:", os.getenv("TWILIO_ACCOUNT_SID"))
print("TWILIO_AUTH_TOKEN:", os.getenv("TWILIO_AUTH_TOKEN"))
client = Client(os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN"))


def call(from_num, to_num):
    global client
    call = client.calls.create(
        to=to_num,
        from_=from_num,
        url=SERVER_URL + "/conference"
    )
    print(f"Call initiated to {to_num}. Call SID: {call.sid}")


twilio_number = "+18578568746"
open_ai_num = "+18577995553"
caller_num = "+447908723560"
callee_num = "+447470400566"

call(twilio_number, caller_num)
call(twilio_number, callee_num)
call(twilio_number, open_ai_num)
