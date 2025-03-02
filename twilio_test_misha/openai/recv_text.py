from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=["GET", "POST"])
def sms_reply():
    # Get the message the user sent
    message_body = request.form.get('Body')
    from_number = request.form.get('From')

    print(f"Received SMS from {from_number}: {message_body}")

    # Optional: Reply to the SMS
    resp = MessagingResponse()
    resp.message("Thanks! I got your message.")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, port=8081)
