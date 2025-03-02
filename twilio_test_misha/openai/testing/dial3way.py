import os

from twilio.rest import Client

from env import *

client = Client()

# The publicly-accessible URL for /conference-twiml (e.g. if using ngrok, something like "https://abc123.ngrok.io/conference-twiml")
conference_twiml_url = "https://d538-144-82-8-234.ngrok-free.app/conference-twiml"

# Your Twilio phone number to appear as the caller ID
twilio_number = "+19798595202"

# The three phone numbers you want to call
phone_numbers = [
    "+447836577086",
    "+447908723560",
    "+447470400566"
]

for number in phone_numbers:
    call = client.calls.create(
        to=number,
        from_=twilio_number,
        url=conference_twiml_url
    )
    print(f"Call initiated to {number}. Call SID: {call.sid}")
