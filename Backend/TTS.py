import asyncio
import edge_tts
import os
import uuid
import tempfile
import threading
import subprocess
from dotenv import dotenv_values

# ================= CONFIG =================
env_vars = dotenv_values(".env")
VOICE = env_vars.get("AssistantVoice", "en-US-JennyNeural")


# ================= GENERATE AUDIO =================
async def _generate_audio(text: str):
    mp3_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.mp3")
    wav_path = mp3_path.replace(".mp3", ".wav")

    try:
        tts = edge_tts.Communicate(
            text,
            VOICE,
            rate="+10%",
            pitch="+2Hz"
        )
        await tts.save(mp3_path)

        # Convert MP3 → WAV
        result = subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "quiet", "-i", mp3_path, wav_path]
        )

        if result.returncode != 0 or not os.path.exists(wav_path):
            print("❌ FFmpeg conversion failed")
            return None, None

        return mp3_path, wav_path

    except Exception as e:
        print("[TTS] Generation error:", e)
        return None, None


# ================= PLAY AUDIO =================
def _play_audio(path: str):
    try:
        subprocess.run(
            [
                "powershell",
                "-c",
                f'(New-Object Media.SoundPlayer "{path}").PlaySync();'
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print("[TTS] Playback error:", e)


# ================= MAIN FUNCTION =================
def TextToSpeech(text: str) -> bool:
    if not text or not text.strip():
        return False

    def worker():
        try:
            print("🧠 Generating audio...")

            # 🔥 dedicated loop (safe)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            mp3_path, wav_path = loop.run_until_complete(_generate_audio(text))
            loop.close()

            if not wav_path:
                print("⚠️ TTS failed")
                return

            print("🔊 Speaking:", text)

            _play_audio(wav_path)

            # Cleanup
            for f in [mp3_path, wav_path]:
                try:
                    if f and os.path.exists(f):
                        os.remove(f)
                except:
                    pass

        except Exception as e:
            print("[TTS] Error:", e)

    # 🔥 NON-daemon → safe execution
    threading.Thread(target=worker).start()

    return True


# ================= TEST =================
if __name__ == "__main__":
    TextToSpeech("Hello, now your TTS is fully optimized and stable.")

    # keep alive for test
    import time
    time.sleep(5)