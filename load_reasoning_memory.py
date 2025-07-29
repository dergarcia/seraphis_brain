import json

# Load validated memory
with open("validated_memory.json", "r", encoding="utf-8") as f:
    validated_memory = json.load(f)

print(f"✅ Loaded {len(validated_memory)} validated memory entries.\n")

# Display each entry for verification
for i, entry in enumerate(validated_memory):
    print(f"--- Memory #{i + 1} ---")
    print(f"Question: {entry.get('question')}")
    print(f"Answer: {entry.get('answer')}")
    print(f"Tags: {entry.get('tags')}")
    print(f"Category: {entry.get('category')}")
    print(f"Priority Score: {entry.get('priorityScore')}")
    print("\n")
