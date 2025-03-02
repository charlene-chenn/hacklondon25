from twilio.rest import Client

client = Client()


def call(from_num, to_num):
    global client
    call = client.calls.create(
        to=to_num,
        from_=from_num,
        url=SERVER_URL + "/conference"
    )
    print(f"Call initiated to {to_num}. Call SID: {call.sid}")


twilio_number = "+19798595202"
caller_num = "+447908723560"
callee_num = "+447836577086"
open_ai_num = "+447470400566"

call(twilio_number, caller_num)
call(twilio_number, callee_num)
call(twilio_number, open_ai_num)
