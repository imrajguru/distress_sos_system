 # detection/sos.py
import sys
import os

from twilio.rest import Client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import TWILIO_SID, TWILIO_AUTH, TWILIO_PHONE, EMERGENCY_CONTACT

client = Client(TWILIO_SID, TWILIO_AUTH)

def send_sos(trigger_text=None):
    print("[🚨] Sending SOS alert via SMS and Call...")

    # SMS
    try:
        message = client.messages.create(
            body="🚨 Distress Detected! Please check on the user immediately.",
            from_=TWILIO_PHONE,
            to=EMERGENCY_CONTACT
        )
        print("[✅] SMS sent:", message.sid)
    except Exception as e:
        print("[❌] Failed to send SMS:", e)

    # Call
    try:
        call = client.calls.create(
            twiml='<Response><Say>This is an emergency alert. The user may be in danger.</Say></Response>',
            from_=TWILIO_PHONE,
            to=EMERGENCY_CONTACT
        )
        print("[✅] Call initiated:", call.sid)
    except Exception as e:
        print("[❌] Failed to make call:", e)

