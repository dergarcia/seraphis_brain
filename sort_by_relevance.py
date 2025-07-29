import json

# Load scored memory
with open("relevance_scored_memory.json", "r", encoding="utf-8") as f:
    memory = json.load(f)

# Sort by relevance (descending)
sorted_memory = sorted(memory, key=lambda x: x.get("relevance_score", 0), reverse=True)

# Optionally trim to top 100 if needed
top_chunks = sorted_memory[:100]  # you can adjust this number

# Save sorted memory
with open("ranked_memory.json", "w", encoding="utf-8") as f:
    json.dump(top_chunks, f, indent=2, ensure_ascii=False)

print(f"✅ Done. Top {len(top_chunks)} chunks saved to ranked_memory.json.")
