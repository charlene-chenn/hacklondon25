import asyncio
import base64
import json
import os

import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, Say, Stream, VoiceResponse

load_dotenv()

# Configuration
# requires OpenAI Realtime API Access
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8080))

SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about "
    "anything the user is interested in and is prepared to offer them facts. "
    "You have a penchant for dad jokes, owl jokes, and rickrolling – subtly. "
    "Always stay positive, but work in a joke when appropriate."
)
VOICE = "alloy"  # "alloy" or "jenny"
# https://platform.openai.com/docs/guides/realtime/
LOG_EVENT_TYPES = [
    "response.content.done", "rate_limits.updated", "response.done",
    "input_audio_buffer.committed", "input_audio_buffer.speech_stopped",
    "input_audio_buffer.speech_started", "session.created"
]
app = FastAPI()
if not OPENAI_API_KEY:
    raise ValueError(
        "Missing the OpenAI API key. Please set it in the .env file.")


def initiate_call(server_url, to_num, from_num="+19798595202"):
    """
    Make a call using Twilio API.
    Parameters:
        server_url: str
            The URL of the server controlling the call.
        to_num:     str
            Phone number to call.
        from_num:   str (default="+19798595202")
            Phone number to call from.
    """
    if server_url:
        client = Client()
        call = client.calls.create(
            from_=from_num,
            to=to_num,
            url=server_url+"/incoming-call"
        )
    else:
        raise ValueError("URL is required to make a call.")


@app.api_route("/incoming-call", methods=["GET", "POST"])
async def handle_incoming_call(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""
    response = VoiceResponse()

    # TODO consider playing an MP3 file here using the same voice as OpenAI translator
    response.say(
        "Please wait while we connect your call to the A. I. voice assistant, powered by Twilio and the Open-A.I. Realtime API")
    response.pause(length=1)
    response.say("O.K. you can start talking!")

    # Add OpenAI translator to the call
    # TODO instruct GPT to explain that they will call bossman and that you should wait
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""

    print("Client connected")

    await websocket.accept()

    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17",
        additional_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:

        await send_session_update(openai_ws)
        stream_sid = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid
            try:
                async for message in websocket.iter_text():
                    data = json.loads(message)

                    # If audio data received on Twilio websocket, forward to OpenAI websocket
                    if data["event"] == "media":
                        audio_append = {
                            "type": "input_audio_buffer.append",
                            "audio": data["media"]["payload"]
                        }
                        await openai_ws.send(json.dumps(audio_append))

                    # If Twilio sends a start event, store the stream SID
                    elif data["event"] == "start":
                        stream_sid = data["start"]["streamSid"]
                        print(f"Incoming stream has started {stream_sid}")

            # If Twilio websocket disconnects (i.e. call probably over), close OpenAI websocket
            except WebSocketDisconnect:
                print("Client disconnected.")
                await openai_ws.close()

        async def send_to_twilio():
            """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
            nonlocal stream_sid

            try:
                async for openai_message in openai_ws:
                    response = json.loads(openai_message)

                    # Log events
                    if response["type"] in LOG_EVENT_TYPES:
                        print(f"Received event: {response["type"]}", response)
                        print("")

                    if response["type"] == "session.updated":
                        print("Session updated successfully:", response)
                        print("")

                    # If OpenAI sends audio data, forward to Twilio websocket
                    if response["type"] == "response.audio.delta" and response.get("delta"):
                        try:
                            audio_payload = base64.b64encode(
                                base64.b64decode(response["delta"])).decode("utf-8")
                            audio_delta = {
                                "event": "media",
                                "streamSid": stream_sid,
                                "media": {
                                    "payload": audio_payload
                                }
                            }
                            await websocket.send_json(audio_delta)
                        # If problem with audio data, log it
                        except Exception as e:
                            print(f"Error processing audio data: {e}")
            except Exception as e:
                print(f"Error in send_to_twilio: {e}")

        # Start receiving and sending data concurrently
        await asyncio.gather(receive_from_twilio(), send_to_twilio())


async def send_session_update(openai_ws):
    """Send session update to OpenAI WebSocket."""
    session_update = {
        "type": "session.update",
        "session": {
            "turn_detection": {"type": "server_vad"},
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,
        }
    }
    print("Sending session update:",
          json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

if __name__ == "__main__":
    initiate_call("https://d538-144-82-8-234.ngrok-free.app", "+447908723560")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
