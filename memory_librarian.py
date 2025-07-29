import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load memory
with open("refined_memory.json", "r", encoding="utf-8") as f:
    memory_entries = json.load(f)

print(f"📚 Reviewing {len(memory_entries)} memory entries...")

for entry in memory_entries:
    if "summary" in entry:
        continue  # Already processed

    content = f"""You are a memory librarian AI. Summarize the core insight of this memory entry in 1–2 sentences and return 3 high-level tags.

Query: {entry['query']}
Decision: {entry['decision']}
Feedback: {entry['feedback']}

Return:
Summary: ...
Tags: ["...", "...", "..."]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You summarize and organize memory entries."},
            {"role": "user", "content": content}
        ]
    )

    try:
        result = response.choices[0].message.content.strip().split("Tags:")
        summary = result[0].replace("Summary:", "").strip()
        tags = eval(result[1].strip())

        entry["summary"] = summary
        entry["tags"] = tags
    except Exception:
        entry["summary"] = "Summary failed."
        entry["tags"] = ["Uncategorized"]

# Save enriched memory
with open("refined_memory.json", "w", encoding="utf-8") as f:
    json.dump(memory_entries, f, indent=2, ensure_ascii=False)

print("✅ Memory entries updated with summaries and tags.")
