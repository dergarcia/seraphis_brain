import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Load the ranked memory file
with open("ranked_memory.json", "r", encoding="utf-8") as f:
    memory_chunks = json.load(f)

# Multi-step reflection prompt function
def reflection_prompt(content, step):
    if step == 1:
        return f"Summarize the following memory chunk in one sentence:\n\n{content}"
    elif step == 2:
        return f"Extract the key insight or lesson from this memory:\n\n{content}"
    elif step == 3:
        return f"Suggest how this knowledge could be applied in future reasoning:\n\n{content}"
    else:
        return f"Reflect on this memory chunk:\n\n{content}"

# Run reflection on each chunk
reflected_memory = []

for idx, item in enumerate(memory_chunks):
    content = item.get("content") or item.get("chunk")  # fallback support
    if not content:
        continue

    reflection = {"original": content}

    for step in range(1, 4):
        prompt = reflection_prompt(content, step)

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"[ERROR: {e}]"

        reflection[f"step_{step}"] = reply
        time.sleep(1.2)  # rate limit safety

    reflected_memory.append(reflection)

# Save the reflected results
with open("reflected_memory.json", "w", encoding="utf-8") as f:
    json.dump(reflected_memory, f, ensure_ascii=False, indent=2)

print("✅ Reflection complete. Results saved to reflected_memory.json")
