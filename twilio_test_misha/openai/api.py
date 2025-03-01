import asyncio
import base64
import json

import websockets
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, Say, Stream, VoiceResponse

from env import (LOG_EVENT_TYPES, MODEL_TEMPERATURE, OPENAI_API_KEY,
                 SYSTEM_MESSAGE, VOICE)

# FastAPI app configuration
app = FastAPI()


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
            url=server_url+"/call-entry-point"
        )
    else:
        raise ValueError("URL is required to make a call.")


@app.api_route("/add-number-to-call", methods=["GET", "POST"])
async def handle_add_number_to_call(request: Request):
    """
    Add a number to an ongoing call using Twilio API.
    Parameters:
        to_num: str
            Phone number to add to the call.
    """
    response = VoiceResponse()
    response.say("Adding another number to the call")
    response.dial("+447470400566")
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.get("/status", response_class=JSONResponse)
async def index_page():
    """Return the status of the Twilio Media Stream Server."""
    return {"message": "Twilio Media Stream Server is running!"}


@app.api_route("/call-entry-point", methods=["GET", "POST"])
async def call_entry_point(request: Request):
    """Handle incoming call and return TwiML response to connect to Media Stream."""

    response = VoiceResponse()

    # TODO consider playing an MP3 file here using the same voice as OpenAI translator
    response.say("Hi! You are being connected to your AI translator.")
    response.pause(length=1)

    # Add OpenAI translator to the call
    # TODO instruct GPT to explain that they will call bossman and that you should wait
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)
    dial =

    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def handle_media_stream(twilio_ws: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""

    print("Client connected")

    # Accept incoming WebSocket connection from Twilio
    await twilio_ws.accept()

    # Connect to OpenAI Realtime API
    async with websockets.connect(
        "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01",
        extra_headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "OpenAI-Beta": "realtime=v1"
        }
    ) as openai_ws:

        # Send session configuration to OpenAI through websocket
        await send_session_update(openai_ws)
        stream_sid = None

        async def receive_from_twilio():
            """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
            nonlocal stream_sid
            try:
                async for message in twilio_ws.iter_text():
                    data = json.loads(message)

                    # If audio data received on Twilio websocket, forward to OpenAI websocket
                    if data["event"] == "media" and openai_ws.open:
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
                if openai_ws.open:
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

                    if response["type"] == "session.updated":
                        print("Session updated successfully:", response)

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
                            await twilio_ws.send_json(audio_delta)
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
            "temperature": MODEL_TEMPERATURE,
        }
    }
    print("Sending session update to OpenAI WebSocket:", json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

