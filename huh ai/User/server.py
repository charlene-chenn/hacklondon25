import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, Dial, VoiceResponse

from env import *

app = FastAPI()

client = Client("xxx",
                "xxx")


def call(from_num, to_num):
    global client
    call = client.calls.create(
        to=to_num,
        from_=from_num,
        url=SERVER_URL + "/conference"
    )
    print(f"Call initiated to {to_num}. Call SID: {call.sid}")


def call_all():
    twilio_number = "+18578568746"
    open_ai_num = "+18577995553"
    caller_num = "+447908723560"
    callee_num = "+447470400566"

    call(twilio_number, caller_num)
    call(twilio_number, callee_num)
    call(twilio_number, open_ai_num)


@app.api_route("/conference", methods=["GET", "POST"])
async def handle_conference(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()

    response.say("Hi! You are being connected to your AI translator.")

    # Call the callee number
    dial = Dial()
    dial.conference("TranslatorConference", end_conference_on_exit=True)
    response.append(dial)

    # Add OpenAI translator to the call
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)

    return HTMLResponse(content=str(response), media_type="application/xml")


@app.get("/start", response_class=JSONResponse)
async def start():
    """Start the OpenAI translator."""
    call_all()
    return {"message": "Translator started."}


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
