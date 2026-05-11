from groq import Groq
from dotenv import dotenv_values
from googlesearch import search
import datetime

# ================= CONFIG =================
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("Missing Groq API Key")

client = Groq(api_key=GroqAPIKey)

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are a real-time AI assistant.

Use provided search results to answer accurately.
Keep answers short, clear, and factual.
Do not hallucinate.
"""

# ================= GOOGLE SEARCH =================
def google_search(query: str, num_results=3):
    try:
        results = list(search(query, num_results=num_results))

        formatted = "\n".join([f"- {r}" for r in results])
        return formatted

    except Exception:
        return "No search results found."

# ================= TIME CONTEXT =================
def get_time_context():
    now = datetime.datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# ================= CLEAN OUTPUT =================
def clean_answer(ans: str):
    return "\n".join([line for line in ans.split("\n") if line.strip()])

# ================= MAIN FUNCTION =================
def RealtimeSearchEngine(query: str) -> str:
    if not query.strip():
        return "Please provide a query."

    try:
        search_data = google_search(query)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": f"Search Results:\n{search_data}"},
                {"role": "system", "content": get_time_context()},
                {"role": "user", "content": query}
            ],
            temperature=0.4,
            max_tokens=300
        )

        answer = response.choices[0].message.content.strip()

        return clean_answer(answer)

    except Exception as e:
        print("Realtime Error:", e)
        return "Sorry, I couldn't fetch real-time information."
        

# ================= TEST =================
if __name__ == "__main__":
    print("🌐 Realtime Engine Ready...\n")

    while True:
        q = input(">>> ")
        print(RealtimeSearchEngine(q))