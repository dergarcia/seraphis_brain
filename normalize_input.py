import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI()  # Pulls API key from your .env file

def normalize_input(user_input):
    prompt = f"""You are Seraphis, a wise AI. Normalize the user's messy question into a clean, structured prompt suitable for memory search and reasoning.
    
    Original question: {user_input}
    
    Normalized prompt:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You convert questions into clean, structured formats."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()


def save_to_log(user_input, normalized):
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    entry = f"""
## Normalization Entry [{timestamp}]

**Original Input**: {user_input}

**Normalized**: {normalized}

---
"""
    os.makedirs("./Memory", exist_ok=True)
    with open("./Memory/normalized_inputs.md", "a", encoding="utf-8") as f:
        f.write(entry)
    print("✅ Normalized input saved to './Memory/normalized_inputs.md'")


def main():
    user_input = input("What would you like to ask Seraphis? ")
    normalized = normalize_input(user_input)
    print(f"\n🧠 Normalized Prompt:\n{normalized}")
    save_to_log(user_input, normalized)


if __name__ == "__main__":
    main()
