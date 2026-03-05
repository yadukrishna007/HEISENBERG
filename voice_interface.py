import whisper
import sounddevice as sd
import numpy as np
import pyttsx3
import queue

# ---------------- AUDIO SETTINGS ----------------
SAMPLE_RATE = 16000

# Adjust these if needed
SILENCE_THRESHOLD = 0.01     # mic sensitivity (increase if noise triggers)
SILENCE_DURATION = 1.2       # seconds of silence before stopping

# ------------------------------------------------

model = whisper.load_model("medium")   # base / small / medium
engine = pyttsx3.init()

audio_queue = queue.Queue()


# ---------------- TEXT TO SPEECH ----------------
def speak(text: str):
    engine.say(text)
    engine.runAndWait()


# ---------------- AUDIO CALLBACK ----------------
def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(indata.copy())


# ---------------- DYNAMIC LISTEN ----------------
def listen() -> str:
    print("Calibrating microphone... stay silent")

    # --- Measure background noise ---
    noise_sample = sd.rec(
        int(1 * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32"
    )
    sd.wait()

    noise_level = np.linalg.norm(noise_sample) / len(noise_sample)

    # Dynamic threshold
    silence_threshold = noise_level * 5

    print(f"Listening... (threshold={silence_threshold:.5f})")

    recording = []
    speaking_started = False
    silence_time = 0.0

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        callback=audio_callback
    ):

        while True:
            data = audio_queue.get()
            volume = np.linalg.norm(data) / len(data)

            # Speech detected
            if volume > silence_threshold:
                speaking_started = True
                silence_time = 0.0
                recording.append(data)

            # Silence AFTER speaking
            elif speaking_started:
                silence_time += len(data) / SAMPLE_RATE
                recording.append(data)

                if silence_time > SILENCE_DURATION:
                    break

    print("Processing speech...")

    if not recording:
        return ""

    audio = np.concatenate(recording, axis=0)
    audio = np.squeeze(audio)

    result = model.transcribe(
        audio,
        fp16=False,
        language="en",
        task="transcribe"
    )

    text = result["text"].strip().lower()
    print(f"Heard: {text}")

    return text
