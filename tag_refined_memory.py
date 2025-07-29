import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load memory
with open("refined_memory.json", "r", encoding="utf-8") as f:
    memory_entries = json.load(f)

# Loop and tag each entry
for entry in memory_entries:
    if "tags" in entry:
        continue  # Skip if already tagged

    content = f"""You are an AI assistant. Given the following memory entry, extract 3–5 high-level tags that describe its core topics. Return them as a Python list.

Memory:
Query: {entry['query']}
Decision: {entry['decision']}
Feedback: {entry['feedback']}

Only return a Python list of tags. Example: ["AI Evolution", "Strategy", "Self-Awareness"]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a semantic tagger and topic classifier."},
            {"role": "user", "content": content}
        ],
        temperature=0.4
    )

    try:
        tags = eval(response.choices[0].message.content.strip())
        if isinstance(tags, list):
            entry["tags"] = tags
        else:
            entry["tags"] = ["Uncategorized"]
    except Exception:
        entry["tags"] = ["Uncategorized"]

# Save updated memory
with open("refined_memory.json", "w", encoding="utf-8") as f:
    json.dump(memory_entries, f, indent=2, ensure_ascii=False)

print("✅ All entries tagged and saved.")
