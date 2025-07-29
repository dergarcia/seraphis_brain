import json

# Load reflected memory
with open("reflected_memory.json", "r", encoding="utf-8") as f:
    reflected_data = json.load(f)

core_memory = []

for entry in reflected_data:
    chunk = entry.get("original", "")
    summary = entry.get("step_1", "")
    insight = entry.get("step_2", "")
    application = entry.get("step_3", "")

    refined = {
        "chunk": chunk,
        "summary": summary,
        "insight": insight,
        "application": application
    }

    core_memory.append(refined)

# Save the final version
with open("core_memory.json", "w", encoding="utf-8") as f:
    json.dump(core_memory, f, ensure_ascii=False, indent=2)

print("🧠 Core memory finalized. Saved to core_memory.json")
---  
🧠 **New Query Recorded** – 2025-07-23 14:56:25  
**Query:** How does Seraphis finalize core memory?  
**Final Answer:** Seraphis finalizes core memory by first initializing an empty list for core memory. Then, refined data is appended to this list. Finally, the core memory is saved to a JSON file named 'core_memory.json'. A message is printed to indicate that the core memory has been finalized and saved.  
**Reasoning Summary:** These memory chunks were selected because they provide a step-by-step process of how Seraphis finalizes core memory. They show the initialization of the core memory, the addition of refined data, and the final saving of the core memory to a file.  

**Chunks Used:**  
[
  {
    "chunkId": 3,
    "chunk": "core_memory = []",
    "tags": [
      "core_memory",
      "empty_list"
    ],
    "category": "Data Structures",
    "priorityScore": 0.2
  },
  {
    "chunkId": 6,
    "chunk": "core_memory.append(refined)",
    "tags": [
      "coding",
      "data_storage"
    ],
    "category": "Programming",
    "priorityScore": 0.4
  },
  {
    "chunkId": 7,
    "chunk": "# Save the final version\nwith open(\"core_memory.json\", \"w\", encoding=\"utf-8\") as f:\n    json.dump(core_memory, f, ensure_ascii=False, indent=2)",
    "tags": [
      "json",
      "file-saving",
      "core_memory"
    ],
    "category": "Data Management",
    "priorityScore": 0.7
  },
  {
    "chunkId": 8,
    "chunk": "print(\"🧠 Core memory finalized. Saved to core_memory.json\")",
    "tags": [
      "core_memory",
      "json",
      "finalized"
    ],
    "category": "System Operations",
    "priorityScore": 0.5
  }
]  
---

---  
🧠 **New Query Recorded** – 2025-07-23 14:59:58  
**Query:** How does Seraphis finalize core memory?  
**Final Answer:** Seraphis finalizes core memory by first initializing an empty list for core memory. Then, refined data is appended to this list. Finally, the core memory is saved to a JSON file named 'core_memory.json'. A message is printed to indicate that the core memory has been finalized and saved.  
**Reasoning Summary:** These memory chunks were selected because they provide a step-by-step process of how Seraphis finalizes core memory. They show the initialization of the core memory, the addition of refined data, and the final saving of the core memory to a file.  

**Chunks Used:**  
[
  {
    "chunkId": 3,
    "chunk": "core_memory = []",
    "tags": [
      "core_memory",
      "empty_list"
    ],
    "category": "Data Structures",
    "priorityScore": 0.2
  },
  {
    "chunkId": 6,
    "chunk": "core_memory.append(refined)",
    "tags": [
      "coding",
      "data_storage"
    ],
    "category": "Programming",
    "priorityScore": 0.4
  },
  {
    "chunkId": 7,
    "chunk": "# Save the final version\nwith open(\"core_memory.json\", \"w\", encoding=\"utf-8\") as f:\n    json.dump(core_memory, f, ensure_ascii=False, indent=2)",
    "tags": [
      "json",
      "file-saving",
      "core_memory"
    ],
    "category": "Data Management",
    "priorityScore": 0.7
  },
  {
    "chunkId": 8,
    "chunk": "print(\"🧠 Core memory finalized. Saved to core_memory.json\")",
    "tags": [
      "core_memory",
      "json",
      "finalized"
    ],
    "category": "System Operations",
    "priorityScore": 0.5
  }
]  
---

