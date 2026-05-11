import os
import requests
from typing import List

# ================= CONFIG =================
SAVE_DIR = "Data"
os.makedirs(SAVE_DIR, exist_ok=True)

# ================= MAIN FUNCTION =================

def GenerateImages(prompt: str, count: int = 2) -> List[str]:
    if not prompt.strip():
        return []

    saved_paths = []

    try:
        for i in range(count):
            url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ', '%20')}"

            response = requests.get(url, timeout=60)

            if response.status_code == 200:
                filename = f"{prompt.replace(' ', '_')}_{i}.jpg"
                path = os.path.join(SAVE_DIR, filename)

                with open(path, "wb") as f:
                    f.write(response.content)

                saved_paths.append(path)
            else:
                print(f"[Image] Error: {response.status_code}")

    except Exception as e:
        print(f"[Image] Error: {e}")

    return saved_paths


# ================= TEST =================
if __name__ == "__main__":
    imgs = GenerateImages("a serene landscape with mountains and a river", count=3)

    print("\nGenerated Images:")
    for i in imgs:
        print(i)