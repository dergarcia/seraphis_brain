from client_utils import client
import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
# Load past decisions
with open("decision_log.json", "r", encoding="utf-8") as f:
    logs = json.load(f)

# Filter only decisions with bad or mixed feedback
candidates = [entry for entry in logs if entry["feedback"].lower() in ["no", "neutral"] or "improve" in entry["feedback"].lower()]

if not candidates:
    print("✅ No decisions need refinement. Seraphis is on point.")
    exit()

def generate_refinements(decisions):
    decision_texts = []
    for idx, entry in enumerate(decisions):
        decision_texts.append(f"{idx+1}. Query: {entry['query']}\nDecision: {entry['decision']}\nFeedback: {entry['feedback']}")
    
    messages = [
        {
            "role": "system",
            "content": "You are Seraphis, a strategic AI who reflects on past decisions and proposes improvements to your reasoning algorithms and logic flow."
        },
        {
            "role": "user",
            "content": f"""Here are past decisions and feedback:\n\n{chr(10).join(decision_texts)}\n\nFor each, generate a numbered list of refinements Seraphis should apply to improve future decision-making."""
        }
    ]

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5
    )

    return response.choices[0].message.content.strip()

print("\n🧠 Running Auto-Refinement...\n")
refinements = generate_refinements(candidates)
print(refinements)

# Optional: Save to file
with open("auto_refinements.txt", "w", encoding="utf-8") as f:
    f.write(refinements)

print("\n✅ Refinements saved to auto_refinements.txt")
