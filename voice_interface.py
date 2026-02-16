import whisper
import sounddevice as sd
import numpy as np
import pyttsx3

SAMPLE_RATE = 16000
DURATION = 4  # seconds (you can tune this)

model = whisper.load_model("medium")  # small / base / medium
engine = pyttsx3.init()

def speak(text: str):
    engine.say(text)
    engine.runAndWait()
 
def listen() -> str:
    print("Listening...")
    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    audio = np.squeeze(audio)

    result = model.transcribe(
        audio,
        fp16=False,
        language="en",
        task="transcribe"
    )
    return result["text"].strip().lower()