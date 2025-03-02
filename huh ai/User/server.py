import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from twilio.twiml.voice_response import Connect, Dial, VoiceResponse

from env import *

app = FastAPI()


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


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
