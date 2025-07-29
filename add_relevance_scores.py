import json
import os
import openai
from time import sleep
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Explicitly pass the API key to the client
client = openai.OpenAI(api_key=api_key)

def score_relevance(entry):
    try:
        chunk = entry["content"]
        query = "Rate how relevant this memory is to answering user queries on a scale from 0 to 100."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a relevance scoring engine."},
                {"role": "user", "content": f"{query}\n\nMemory:\n{chunk}"},
            ]
        )

        score_text = response.choices[0].message.content.strip()
        score = int(''.join(filter(str.isdigit, score_text)))  # Extract numeric score

        print(f"Scoring relevance: {score}%")
        return score

    except Exception as e:
        print("Error scoring chunk:", e)
        return 0

def add_scores_to_memory(input_file="tagged_memory.json", output_file="relevance_scored_memory.json"):
    with open(input_file, "r", encoding="utf-8") as f:
        memory_chunks = json.load(f)

    for entry in memory_chunks:
        entry["relevance_score"] = score_relevance(entry)
        sleep(1)  # Avoid rate limit

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(memory_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Relevance scores added and saved to {output_file}")

if __name__ == "__main__":
    add_scores_to_memory()
