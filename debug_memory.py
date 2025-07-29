import json

with open("tagged_memory.json", "r", encoding="utf-8") as f:
    raw_memory = json.load(f)

invalid = [m for m in raw_memory if not isinstance(m, dict) or 'question' not in m or 'answer' not in m]

print(f"\nTotal entries: {len(raw_memory)}")
print(f"Invalid entries: {len(invalid)}\n")

for i, m in enumerate(invalid, 1):
    print(f"--- Invalid Entry #{i} ---")
    print(m)
    print()
