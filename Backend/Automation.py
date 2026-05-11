from AppOpener import close, open as appopen
from pywhatkit import search as google_search, playonyt
from dotenv import dotenv_values
from groq import Groq
import webbrowser
import subprocess
import asyncio
import os
import sys
from typing import List, Optional

# ================= CONFIG =================
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey) if GroqAPIKey else None

# ================= LOGGER =================
def log(msg):
    print(f"[Automation] {msg}")

# ================= CORE FUNCTIONS =================

APP_PATHS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "spotify": r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
    "notepad": "notepad.exe",
    "cmd": "cmd.exe"
}

def OpenApp(app: str) -> bool:
    app = app.lower().strip()

    try:
        # ⚡ STEP 1: Direct launch (instant)
        if app in APP_PATHS:
            path = os.path.expandvars(APP_PATHS[app])
            subprocess.Popen(path)
            log(f"⚡ Fast launch: {app}")
            return True

        # ⚡ STEP 2: Try system command (fast)
        try:
            subprocess.Popen(app)
            log(f"⚡ System launch: {app}")
            return True
        except:
            pass

        # 🐢 STEP 3: Fallback (slow)
        appopen(app, match_closest=True, output=False)
        log(f"🐢 Fallback AppOpener: {app}")
        return True

    except Exception as e:
        log(f"❌ Failed to open {app}: {e}")
        webbrowser.open(f"https://www.google.com/search?q={app}")
        return False


def CloseApp(app: str) -> bool:
    try:
        close(app, match_closest=True, output=False)
        log(f"Closed app: {app}")
        return True
    except Exception as e:
        log(f"Failed to close {app}: {e}")
        return False


def PlayYoutube(query: str) -> bool:
    try:
        playonyt(query)
        log(f"Playing: {query}")
        return True
    except Exception as e:
        log(f"Play error: {e}")
        return False


def GoogleSearch(query: str) -> bool:
    try:
        google_search(query)
        log(f"Searching: {query}")
        return True
    except Exception as e:
        log(f"Search error: {e}")
        return False


def YoutubeSearch(query: str) -> bool:
    try:
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        log(f"YouTube search: {query}")
        return True
    except Exception as e:
        log(f"YouTube search error: {e}")
        return False


def System(command: str) -> bool:
    import keyboard
    cmd = command.lower()

    try:
        if "mute" in cmd:
            keyboard.press_and_release("volume mute")
        elif "volume up" in cmd:
            keyboard.press_and_release("volume up")
        elif "volume down" in cmd:
            keyboard.press_and_release("volume down")
        log(f"System command: {command}")
        return True
    except Exception as e:
        log(f"System error: {e}")
        return False


def GenerateContent(prompt: str) -> bool:
    if not client:
        log("Groq API missing")
        return False

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Write clean and structured content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.6
        )

        content = response.choices[0].message.content.strip()

        os.makedirs("Data", exist_ok=True)
        filename = "".join(c for c in prompt if c.isalnum())[:20]
        path = os.path.join("Data", f"{filename}.txt")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        # Cross-platform open
        if sys.platform == "win32":
            subprocess.Popen(["notepad.exe", path])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

        log(f"Content generated: {path}")
        return True

    except Exception as e:
        log(f"Content error: {e}")
        return False


# ================= EXECUTOR =================

async def execute_command(command: str):
    cmd = command.lower().strip()

    if cmd.startswith("open "):
        return await asyncio.to_thread(OpenApp, cmd[5:])

    elif cmd.startswith("close "):
        return await asyncio.to_thread(CloseApp, cmd[6:])

    elif cmd.startswith("play "):
        return await asyncio.to_thread(PlayYoutube, cmd[5:])

    elif cmd.startswith("content "):
        return await asyncio.to_thread(GenerateContent, cmd[8:])

    elif cmd.startswith("google search "):
        return await asyncio.to_thread(GoogleSearch, cmd[14:])

    elif cmd.startswith("youtube search "):
        return await asyncio.to_thread(YoutubeSearch, cmd[15:])

    elif cmd.startswith("system "):
        return await asyncio.to_thread(System, cmd[7:])

    else:
        log(f"Unknown command: {command}")
        return False


# ================= MAIN =================

async def Automation(commands: List[str]) -> List[bool]:
    if not commands:
        return []

    tasks = [execute_command(cmd) for cmd in commands]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return results


# ================= TEST =================
if __name__ == "__main__":
    cmds = [
    
    "open camera","open spotify", "play never gonna give you up", "google search python programming", "youtube search cute cats", "system volume up", "content write a poem about the ocean", "close spotify"
]
    results = asyncio.run(Automation(cmds))
    print("Results:", results)