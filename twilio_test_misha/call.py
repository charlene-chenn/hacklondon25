from twilio.rest import Client

client = Client()
call = client.calls.create(
    from_="+19798595202",
    to="+447908723560",
    url="https://handler.twilio.com/twiml/EH8626511b84d8a6b96122fb745bf771c0"
)
