import asyncio
import edge_tts
import os

async def speak(text):
    file = "tts.mp3"
    tts = edge_tts.Communicate(text, "en-US-JennyNeural")
    await tts.save(file)

    print("Playing...")
    os.startfile(file)   # 🔥 guaranteed to play

def TextToSpeech(text):
    asyncio.run(speak(text))

