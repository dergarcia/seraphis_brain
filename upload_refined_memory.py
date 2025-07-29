from client_utils import client
import os
import openai
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
# Load existing tagged memory
tagged_memory_path = "C:\\Users\\degarcia\\Seraphis\\Memory\\tagged_memory.json"
try:
    with open(tagged_memory_path, "r", encoding="utf-8") as f:
        tagged_memory = json.load(f)
except FileNotFoundError:
    tagged_memory = []

# Load decision log entries
with open("decision_log.json", "r", encoding="utf-8") as f:
    decisions = json.load(f)

# Extract previously uploaded content to avoid duplicates
existing_chunks = set(item["chunk"] for item in tagged_memory)

new_entries = []

for decision in decisions:
    content = f"""💡 Strategic Decision:\n{decision['decision']}\n\n🗣️ Original Prompt:\n{decision['query']}\n\n🧠 Feedback:\n{decision['feedback']}"""
    
    if content not in existing_chunks:
        entry = {
            "chunk": content,
            "tags": ["strategic_decision", "feedback_loop", "seraphis_brain"],
            "source": "auto_refined",
            "timestamp": decision.get("timestamp", datetime.now().isoformat())
        }
        tagged_memory.append(entry)
        new_entries.append(entry)

# Save updated memory
with open(tagged_memory_path, "w", encoding="utf-8") as f:
    json.dump(tagged_memory, f, indent=2, ensure_ascii=False)

print(f"✅ {len(new_entries)} new decision(s) added to Seraphis' long-term memory.")
