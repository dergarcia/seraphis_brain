import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load tagged memory
with open("tagged_memory.json", "r", encoding="utf-8") as f:
    memory = json.load(f)

# Ask for a question
query = input("Enter your question or situation: ").strip()

def generate_decision_options(query):
    # Safely extract chunks
    context = "\n\n".join([chunk.get("chunk", "") for chunk in memory])

    messages = [
        {
            "role": "system",
            "content": "You are Seraphis, a strategic decision-making AI designed to weigh trade-offs and recommend the best path forward."
        },
        {
            "role": "user",
            "content": f"""Context:\n{context}\n\nQuestion:\n{query}\n\nGenerate a list of well-structured, multi-step recommendations (numbered) that answer the question with strategy, foresight, and practical reasoning."""
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()

def save_to_log(query, decision, feedback):
    log_entry = {
        "query": query,
        "decision": decision,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }

    try:
        with open("decision_log.json", "r", encoding="utf-8") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    logs.append(log_entry)

    with open("decision_log.json", "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# Generate & print decision
print("\n📡 Generating decisions...\n")
decision_output = generate_decision_options(query)
print(decision_output)

# Collect feedback & log
feedback = input("\n🧠 Feedback? (yes / no / write a note): ").strip()
save_to_log(query, decision_output, feedback)
print("✅ Decision + feedback saved to decision_log.json")
