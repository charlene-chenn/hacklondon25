import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.websockets import WebSocketDisconnect
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, Say, Stream, VoiceResponse

client = Client()
call = client.calls.create(
    from_="+19798595202",
    to="+447908723560",
    url="https://d538-144-82-8-234.ngrok-free.app/"
)

app = FastAPI()


@app.api_route("/", methods=["GET", "POST"])
async def default(request: Request):
    response = VoiceResponse()
    response.say("Adding another number to the call")
    response.dial("+447470400566")
    return HTMLResponse(content=str(response), media_type="application/xml")

uvicorn.run(app, host="0.0.0.0", port=8080)
