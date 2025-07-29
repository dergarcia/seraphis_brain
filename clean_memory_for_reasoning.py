import json

# Load tagged memory
with open("tagged_memory.json", "r", encoding="utf-8") as f:
    raw_entries = json.load(f)

# Valid structure fields
valid_fields = {"question", "answer", "tags", "category", "priorityScore"}
cleaned_entries = []

# Attempt to clean and extract valid entries
for i, entry in enumerate(raw_entries):
    if all(k in entry for k in ("question", "answer")):
        cleaned_entry = {k: entry[k] for k in valid_fields if k in entry}
        cleaned_entries.append(cleaned_entry)
    else:
        print(f"Skipping entry #{i} – missing question or answer")

# Save to validated file
with open("validated_memory.json", "w", encoding="utf-8") as f:
    json.dump(cleaned_entries, f, ensure_ascii=False, indent=2)

print(f"\n✅ Cleaned {len(cleaned_entries)} valid memory entries.")
print("Saved to validated_memory.json")
