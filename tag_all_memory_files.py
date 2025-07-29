import os
import json
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_DIR = "C:/Users/degarcia/Seraphis/Memory"
OUTPUT_FILE = "tagged_memory.json"

def categorize_and_tag(entry):
    messages = [
        {"role": "system", "content": "You are an expert data classifier. Categorize and tag this memory entry for AI recall."},
        {"role": "user", "content": f"Entry:\n{entry}\n\nReturn JSON with 'category', 'tags' (list), and 'summary' (1 sentence)."}
    ]
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    reply = response.choices[0].message.content.strip()

    # Try parsing the reply and make sure it's a dict
    try:
        parsed = json.loads(reply)
        if isinstance(parsed, list):
            parsed = parsed[0]  # Take first item if it’s a list
        if not isinstance(parsed, dict):
            raise ValueError("Parsed response is not a dictionary")
        return parsed
    except Exception as e:
        print(f"⚠️ Failed to parse reply:\n{reply}\nError: {e}")
        return {
            "category": "Uncategorized",
            "tags": [],
            "summary": "Failed to parse tags",
        }

def process_memory_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        entry = f.read()
    result = categorize_and_tag(entry)
    return {
        "file": os.path.basename(file_path),
        "category": result.get("category", ""),
        "tags": result.get("tags", []),
        "summary": result.get("summary", ""),
        "content": entry
    }

def run_all_tagging():
    print("🔄 Starting batch tagging...\n")
    tagged_entries = []
    for filename in os.listdir(MEMORY_DIR):
        if filename.endswith(".md") or filename.endswith(".txt"):
            file_path = os.path.join(MEMORY_DIR, filename)
            try:
                tagged_entry = process_memory_file(file_path)
                tagged_entries.append(tagged_entry)
                print(f"✅ Tagged: {filename}")
            except Exception as e:
                print(f"❌ Error processing {filename}: {e}")

    with open(os.path.join("C:/Users/degarcia/Seraphis/Tools", OUTPUT_FILE), "w", encoding="utf-8") as f:
        json.dump(tagged_entries, f, indent=2, ensure_ascii=False)
    print("\n🎉 Tagging complete. Results saved to tagged_memory.json")

if __name__ == "__main__":
    run_all_tagging()
