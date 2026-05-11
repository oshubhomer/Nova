from groq import Groq
from dotenv import dotenv_values
import re
import json

# ================= CONFIG =================
env = dotenv_values(".env")
GroqAPIKey = env.get("GroqAPIKey")

if not GroqAPIKey:
    raise ValueError("Missing Groq API Key")

client = Groq(api_key=GroqAPIKey)

# ================= MEMORY =================
CONTEXT_HISTORY = []
CACHE = {}

def update_context(prompt):
    CONTEXT_HISTORY.append(prompt)
    if len(CONTEXT_HISTORY) > 5:
        CONTEXT_HISTORY.pop(0)

def get_context():
    return " ".join(CONTEXT_HISTORY[-3:])

# ================= CLEAN =================
def clean_text(text):
    text = text.lower()
    text = re.sub(r"(hello)+", "hello", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ================= SELF CORRECT =================
COMMON_FIXES = {
    "spoitfy": "spotify",
    "youtbe": "youtube",
    "pla": "play",
    "musc": "music"
}

def self_correct(text):
    return " ".join([COMMON_FIXES.get(w, w) for w in text.split()])

# ================= RULE ENGINE =================
def quick_rules(p):

    # GREETING
    if p in ["hi", "hello", "hey"]:
        return [{"command": "general", "input": p, "confidence": 0.9}]

    # EXIT
    if any(x in p for x in ["exit", "bye", "goodbye"]):
        return [{"command": "exit", "input": "", "confidence": 1.0}]

    # AUTOMATION
    if p.startswith("open "):
        return [{"command": "open", "input": p.replace("open", "").strip(), "confidence": 0.95}]

    if p.startswith("play "):
        return [{"command": "play", "input": p.replace("play", "").strip(), "confidence": 0.95}]

    # IMAGE
    if any(x in p for x in ["image", "picture", "photo", "art"]) and any(x in p for x in ["create", "generate", "make"]):
        cleaned = re.sub(r"(create|generate|make|image|picture|photo|art|of)", "", p)
        return [{"command": "generate image", "input": cleaned.strip(), "confidence": 0.9}]

    # CONTENT
    if any(x in p for x in ["write", "blog", "post", "caption", "essay"]):
        return [{"command": "create content", "input": p, "confidence": 0.8}]

    # TIME / DATE
    if any(x in p for x in ["time", "day", "date"]):
        return [{"command": "realtime", "input": p, "confidence": 0.9}]

    return None

# ================= AI REASONING =================
def ai_reason(prompt):

    if prompt in CACHE:
        return CACHE[prompt]

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": """
You are Nova AI Brain.

ONLY use these commands:
exit, general, realtime, open, close, play, generate image, create content

STRICT RULES:
- NEVER invent commands
- NEVER use words like get, search, fetch
- If unsure → use "general"
- Split multiple intents if present

Return ONLY JSON list.

Example:
[
 {"command": "open", "input": "spotify"},
 {"command": "play", "input": "music"}
]
"""
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        text = response.choices[0].message.content.strip()
        CACHE[prompt] = text
        return text

    except Exception as e:
        print("AI Error:", e)
        return None

# ================= MAIN =================
def FirstLayerDMM(prompt):

    if not prompt or not prompt.strip():
        return [{"command": "general", "input": "", "confidence": 0.6}]

    prompt = clean_text(prompt)
    prompt = self_correct(prompt)

    # ⚡ RULE FIRST
    rule = quick_rules(prompt)
    if rule:
        update_context(prompt)
        return rule

    # 🧠 CONTEXT (SAFE)
    context = get_context()

    if len(prompt.split()) < 3:
        enriched_prompt = (context + " " + prompt).strip()
    else:
        enriched_prompt = prompt

    # 🧠 AI CALL (ONCE)
    ai = ai_reason(enriched_prompt)

    if ai:
        try:
            commands = json.loads(ai)

            # ✅ VALIDATION (CRITICAL FIX)
            valid_commands = []
            allowed = ["exit", "general", "realtime", "open", "close", "play", "generate image", "create content"]

            for c in commands:
                if c.get("command") in allowed:
                    valid_commands.append(c)

            if valid_commands:
                update_context(prompt)
                return valid_commands

        except Exception as e:
            print("Parse Error:", e)

    # 🔒 SAFE FALLBACK
    update_context(prompt)
    return [{"command": "general", "input": prompt, "confidence": 0.6}]


# ================= TEST =================
if __name__ == "__main__":
    print("🧠 Nova Model (Fixed) Ready\n")

    while True:
        q = input(">>> ")

        if q.lower() in ["exit", "bye"]:
            break

        print("Decision:", FirstLayerDMM(q))
        print("-" * 50)