import asyncio
import base64
import json
import os

import websockets
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.twiml.voice_response import Connect, VoiceResponse

from env import *


app = FastAPI()


@app.route("/openai-call", methods=["GET", "POST"])
async def handle_openai_call(request: Request):
    """Handle incoming Twilio calls and connect to OpenAI Realtime API."""
    response = VoiceResponse()

    # Add OpenAI translator to the call
    host = request.url.hostname
    connect = Connect()
    connect.stream(url=f"wss://{host}/media-stream")
    response.append(connect)

    return HTMLResponse(content=str(response), media_type="application/xml")


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""

    print("Client connected")

    # Accept incoming WebSocket connection from Twilio
    await websocket.accept()

    # Connect to OpenAI Realtime API
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

                    # If we start speaking stop the AI translator's response
                    if response["type"] == "input_audio_buffer.speech_started":
                        print("Speech Start:", response["type"])
                        # Clear Twilio buffer
                        clear_twilio = {
                            "streamSid": stream_sid,
                            "event": "clear"
                        }
                        await websocket.send_json(clear_twilio)
                        print("Cleared Twilio buffer.")

                        # Send interrupt message to OpenAI
                        interrupt_message = {
                            "type": "response.cancel"
                        }
                        await openai_ws.send(json.dumps(interrupt_message))
                        print("Cancelling AI speech from the server.")

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
            "temperature": MODEL_TEMPERATURE,
        }
    }

    print("Sending session update:",
          json.dumps(session_update))
    await openai_ws.send(json.dumps(session_update))

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 8080))

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
