from flask import Flask, request
from twilio.twiml.voice_response import Conference, Dial, VoiceResponse

from env import *

app = Flask(__name__)


@app.route("/conference-twiml", methods=['POST'])
def conference_twiml():
    """
    This endpoint returns TwiML to place any incoming call into 'MyThreeWayConference'.
    """
    response = VoiceResponse()
    dial = Dial()
    # Put the caller into the named conference
    dial.conference("MyThreeWayConference")
    response.append(dial)

    return str(response)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
