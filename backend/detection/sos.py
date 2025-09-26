# detection/sos.py
import sys
import os
import sqlite3
from datetime import datetime

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

    # Log to SQLite if trigger_text is provided (for voice-triggered SOS)
    if trigger_text:
        try:
            conn = sqlite3.connect('sos_logs.db')
            cursor = conn.cursor()
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sos_triggers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    trigger_text TEXT NOT NULL
                )
            ''')
            # Insert log with formatted timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO sos_triggers (timestamp, trigger_text)
                VALUES (?, ?)
            ''', (timestamp, trigger_text))
            conn.commit()
            print("[✅] SOS log saved to database.")
        except Exception as e:
            print("[❌] Failed to log to database:", e)
        finally:
            conn.close()
