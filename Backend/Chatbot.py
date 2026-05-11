from groq import Groq
from dotenv import dotenv_values
import datetime

# ================= CONFIG =================
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Nova")

if not GroqAPIKey:
    raise ValueError("Missing Groq API Key")

client = Groq(api_key=GroqAPIKey)

# ================= MEMORY =================
chat_history = []

MAX_HISTORY = 6  # limit memory

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = f"""
You are {Assistantname}, a smart and concise AI assistant.

Rules:
- Give short, clear answers
- Do NOT explain unnecessarily
- Always reply in English
- Be accurate and direct
"""

# ================= REALTIME INFO =================
def get_time_context():
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# ================= CLEAN OUTPUT =================
def clean_answer(ans: str):
    return "\n".join([line for line in ans.split("\n") if line.strip()])

# ================= MAIN CHATBOT =================
def ChatBot(query: str) -> str:
    if not query.strip():
        return "Please say something."

    try:
        # Add user input
        chat_history.append({"role": "user", "content": query})

        # Limit memory
        if len(chat_history) > MAX_HISTORY:
            chat_history.pop(0)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ UPDATED MODEL
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": get_time_context()},
                *chat_history
            ],
            temperature=0.5,
            max_tokens=300
        )

        answer = response.choices[0].message.content.strip()

        # Save response
        chat_history.append({"role": "assistant", "content": answer})

        return clean_answer(answer)

    except Exception as e:
        print("Chatbot Error:", e)
        return "Something went wrong."
        

# ================= TEST =================
if __name__ == "__main__":
    print("🤖 Chatbot Ready...\n")

    while True:
        q = input("You: ")
        print("AI:", ChatBot(q))
        if q=="exit":
            break