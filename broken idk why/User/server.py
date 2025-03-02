import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from twilio.rest import Client
from twilio.twiml.voice_response import Dial, VoiceResponse

from env import *

TWILIO_ACCOUNT_SID = "XXX"
TWILIO_AUTH_TOKEN = "XXX"

twilio_number = "+18578568746"
open_ai_num = "+18577995553"
caller_num = "+447908723560"
callee_num = "+447836577086"

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI()


def call(from_num, to_num):
    """Make a call to to_num from from_num."""
    global client
    call = client.calls.create(
        to=to_num,
        from_=from_num,
        url=SERVER_URL + "/conference"
    )
    print(f"Call initiated to {to_num}. Call SID: {call.sid}")


# Call all the numbers involved
def start():
    call(twilio_number, caller_num)
    call(twilio_number, callee_num)
    call(twilio_number, open_ai_num)


@app.api_route("/conference", methods=["GET", "POST"])
async def handle_conference(request: Request):
    """Handle conference logic."""
    response = VoiceResponse()

    response.say("Hi! You are being connected to your AI translator.")

    # Call the callee number
    dial = Dial()
    dial.conference("TranslatorConference", end_conference_on_exit=True)
    response.append(dial)


@app.get("/start_application", response_class=JSONResponse)
async def start_application():
    """Send status and call all numbers involved. Needed to start application through web."""
    start()
    return {"status": "success"}


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
