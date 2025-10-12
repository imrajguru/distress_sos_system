# detection/listener.py

import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
from detection.emotion import analyze_emotion
from detection.sos import send_sos

# Load Vosk model
model = Model("model/vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

# Audio queue
q = queue.Queue()

# Flag to control start/stop
listening = False

def callback(indata, frames, time, status):
    if status:
        print("[!] Audio Status:", status)
    q.put(bytes(indata))

def capture_emotion():
    print("[*] Listening for emotional context after wake word...")
    collected = []

    for _ in range(10):  # ~10 audio chunks
        try:
            data = q.get(timeout=1)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                text = result.get("text", "")
                if text:
                    print(f"[Captured Emotion Speech] {text}")
                    collected.append(text)
        except queue.Empty:
            print("[!] No audio chunk received.")
            break

    full_text = " ".join(collected)
    print("[Collected Text for Emotion Analysis]:", full_text)
    return full_text

def audio_stream():
    global listening
    print("🎙️ Voice detection started. Say 'help me' to trigger SOS.")
    
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        while listening:
            try:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    print(f"[Voice Input]: {text}")

                    if "help me" in text.lower():
                        print("🚨 Wake word detected!")
                        emotion_text = capture_emotion()

                        if emotion_text.strip() == "":
                            print("[❌] No text captured for emotion analysis.")
                        else:
                            emotion = analyze_emotion(emotion_text)
                            print(f"[Detected Emotion]: {emotion}")

                            if emotion in ["fear"]:
                                send_sos(trigger_text=emotion_text)  # Pass the text that triggered SOS
                                print("[🚨] SOS Triggered.")
                                break  # Stop listening after SOS
                            else:
                                print("[ℹ️] Emotion not considered distress. Listening continues.")

            except Exception as e:
                print("[💥] Error in stream:", e)
                break

def start_listening():
    global listening
    listening = True
    audio_stream()

def stop_listening():
    global listening
    listening = False
    print("🛑 Voice detection stopped.")
