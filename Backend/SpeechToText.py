import os
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"  # remove HF warning

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from scipy.io.wavfile import write
import tempfile
from dotenv import dotenv_values

# ================= CONFIG =================
env = dotenv_values(".env")

INPUT_LANGUAGE = env.get("InputLanguage", "en-US").split("-")[0]

SAMPLE_RATE = 16000
SILENCE_THRESHOLD = 250
MAX_RECORD_SECONDS = 8
MAX_SILENCE_AFTER_SPEECH = 25

# ================= MIC DETECTION =================
def get_working_mic():
    devices = sd.query_devices()

    for i, d in enumerate(devices):
        if d['max_input_channels'] > 0:
            print(f"🎤 Using Mic: {d['name']} (ID: {i})")
            return i

    print("❌ No microphone found!")
    return None


DEVICE_ID = get_working_mic()

# ================= MODEL =================
print("🧠 Loading Whisper model...")

model = WhisperModel(
    "base",          # 🔥 best balance (use "small" if GPU)
    compute_type="int8"
)

print("✅ Whisper Ready")

# ================= RECORD AUDIO =================
def record_audio():
    if DEVICE_ID is None:
        print("❌ No mic available")
        return None

    print("🎤 Listening... (start speaking)")

    recording = []
    silence_count = 0
    speech_started = False

    def callback(indata, frames, time, status):
        nonlocal silence_count, speech_started

        volume = np.linalg.norm(indata) * 10

        if volume > SILENCE_THRESHOLD:
            speech_started = True

        if speech_started:
            recording.append(indata.copy())

            if volume < SILENCE_THRESHOLD:
                silence_count += 1
            else:
                silence_count = 0

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='int16',
            device=DEVICE_ID,
            callback=callback
        ):
            for _ in range(int(SAMPLE_RATE / 1024 * MAX_RECORD_SECONDS)):
                sd.sleep(50)

                if speech_started and silence_count > MAX_SILENCE_AFTER_SPEECH:
                    break

    except Exception as e:
        print("❌ Mic Error:", e)
        return None

    if not speech_started or not recording:
        return None

    audio = np.concatenate(recording, axis=0)

    if len(audio) < SAMPLE_RATE * 0.7:
        return None

    temp_path = os.path.join(tempfile.gettempdir(), "nova_input.wav")
    write(temp_path, SAMPLE_RATE, audio)

    return temp_path


# ================= TEXT CLEAN =================
def clean_repetition(text):
    words = text.split()
    filtered = []

    for w in words:
        if not filtered or w != filtered[-1]:
            filtered.append(w)

    return " ".join(filtered)


def process_text(text):
    text = text.strip().lower()

    if not text:
        return None

    text = clean_repetition(text)

    if text[-1] not in ".?!":
        if text.startswith(("how", "what", "who", "where", "when", "why")):
            text += "?"
        else:
            text += "."

    return text.capitalize()


# ================= MAIN FUNCTION =================
def SpeechRecognition():
    try:
        audio_path = record_audio()

        if not audio_path:
            print("⚠️ No audio captured")
            return None

        segments, _ = model.transcribe(
            audio_path,
            language=INPUT_LANGUAGE if INPUT_LANGUAGE else None,
            beam_size=5,
            vad_filter=True,
            temperature=0.0
        )

        raw_text = " ".join([seg.text.strip() for seg in segments])

        if not raw_text:
            return None

        text = process_text(raw_text)

        print("🗣 You said:", text)

        return text

    except Exception as e:
        print("[STT ERROR]", e)
        return None


# ================= TEST =================
def test_speech_module():
    print("\n🧪 Testing Speech Recognition Module...\n")

    success = 0
    attempts = 3

    for i in range(attempts):
        print(f"\n🎯 Test {i+1}/{attempts}")

        text = SpeechRecognition()

        if text:
            print("✅ SUCCESS:", text)
            success += 1
        else:
            print("❌ FAILED: No input detected")

    print("\n==============================")
    print(f"RESULT: {success}/{attempts} successful")
    print("==============================\n")

    if success == 0:
        print("⚠️ Mic issue — check device or permissions")
    elif success < attempts:
        print("⚠️ Partial success → speak clearly")
    else:
        print("🎉 STT working perfectly!")


# ================= RUN =================
if __name__ == "__main__":
    test_speech_module()