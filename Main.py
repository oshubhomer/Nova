import threading
import asyncio
import os
from time import sleep
from dotenv import dotenv_values

from Backend.Model import FirstLayerDMM
from Backend.Chatbot import ChatBot
from Backend.Realtime import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.Image_Generation import GenerateImages
from Backend.SpeechToText import SpeechRecognition
from Backend.TTS import TextToSpeech
from Backend import state

from Frontend.GUI import GraphicalUserInterface

# ================= CONFIG =================
env = dotenv_values(".env")
USERNAME = env.get("Username", "User")
ASSISTANT = env.get("Assistantname", "Nova")

last_query = ""

# ================= SAFE SPEAK =================
def speak(text):
    try:
        TextToSpeech(text)  # already threaded
    except Exception as e:
        print("[TTS ERROR]", e)


# ================= COMMAND HANDLER =================
async def handle_commands(commands, query):
    try:
        executed = False

        for cmd in commands:

            action = cmd.get("command")
            data = cmd.get("input", "")

            # ================= EXIT =================
            if action == "exit":
                state.mic_status = False
                speak("Goodbye!")
                os._exit(0)

            # ================= IMAGE =================
            elif action == "generate image":
                state.assistant_status = "Generating Image..."
                state.latest_response = f"{ASSISTANT}: Generating image..."

                state.mic_status = False
                GenerateImages(data)

                speak("Image generated")
                executed = True

            # ================= AUTOMATION =================
            elif action in ["open", "close", "play"]:
                state.assistant_status = "Executing..."
                state.mic_status = False

                await Automation([f"{action} {data}".strip()])
                executed = True

            # ================= REALTIME =================
            elif action == "realtime":
                state.assistant_status = "Searching..."
                state.mic_status = False

                answer = RealtimeSearchEngine(data)

                if not answer or not isinstance(answer, str):
                    answer = "I couldn't fetch that right now."

                state.latest_response = f"{ASSISTANT}: {answer}"
                speak(answer)
                executed = True

            # ================= CONTENT =================
            elif action == "create content":
                state.assistant_status = "Creating..."
                state.mic_status = False

                answer = ChatBot(data)

                if not answer or not isinstance(answer, str):
                    answer = "I couldn't create content right now."

                state.latest_response = f"{ASSISTANT}: {answer}"
                speak(answer)
                executed = True

            # ================= GENERAL =================
            elif action == "general":
                state.assistant_status = "Thinking..."
                state.mic_status = False

                answer = ChatBot(data if data else query)

                if not answer or not isinstance(answer, str):
                    answer = "I couldn't process that."

                state.latest_response = f"{ASSISTANT}: {answer}"
                speak(answer)
                executed = True

        # ================= FALLBACK =================
        if not executed:
            state.assistant_status = "Thinking..."
            state.mic_status = False

            answer = ChatBot(query)

            if not answer or not isinstance(answer, str):
                answer = "I couldn't process that."

            state.latest_response = f"{ASSISTANT}: {answer}"
            speak(answer)

    except Exception as e:
        print("[HANDLE ERROR]", e)
        state.latest_response = f"{ASSISTANT}: Error occurred"
        state.mic_status = False
        speak("Something went wrong")


# ================= MAIN LOOP =================
def main_loop():
    global last_query

    while True:
        try:
            if state.mic_status:

                # 🔒 lock mic immediately
                state.mic_status = False
                state.assistant_status = "Listening..."

                query = SpeechRecognition()
                print("DEBUG:", query)

                # ❌ empty input
                if not query or not query.strip():
                    state.assistant_status = "No input"
                    continue

                clean_query = query.lower().strip()

                # ❌ duplicate prevention
                if clean_query == last_query:
                    print("⚠️ Duplicate ignored")
                    continue

                last_query = clean_query

                # UI update
                state.latest_response = f"{USERNAME}: {query}"
                state.assistant_status = "Processing..."

                # 🧠 DECISION
                commands = FirstLayerDMM(query)

                # ⚡ SAFE ASYNC EXECUTION
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(handle_commands(commands, query))
                loop.close()

                # 🔁 small delay prevents mic retrigger
                sleep(0.2)

            else:
                sleep(0.1)

        except Exception as e:
            print("[MAIN LOOP ERROR]", e)
            sleep(0.5)


# ================= START =================
def start():
    threading.Thread(target=main_loop, daemon=True).start()
    GraphicalUserInterface()


# ================= ENTRY =================
if __name__ == "__main__":
    start()