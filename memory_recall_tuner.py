import json
import openai
from dotenv import load_dotenv
import os

# Load environment variables and API key
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load core memory
with open("core_memory.json", "r", encoding="utf-8") as f:
    memory_chunks = json.load(f)

# Function to score relevance of a chunk for a query
def score_relevance(query, chunk):
    prompt = f"""
You are Seraphis, a strategic intelligence system.

Evaluate how relevant the following memory chunk is to answering the user's query.

User Query: "{query}"

Memory Chunk:
\"\"\"
{chunk}
\"\"\"

Respond only with a number from 0 to 10, where:
- 0 = completely unrelated
- 10 = perfectly relevant
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    try:
        score = float(response.choices[0].message.content.strip())
    except:
        score = 0.0
    return score

# Main recall function
def recall_top_chunks(query, top_n=5):
    scored = []
    for chunk in memory_chunks:
        score = score_relevance(query, chunk)
        scored.append({"chunk": chunk, "score": score})
    
    ranked = sorted(scored, key=lambda x: x["score"], reverse=True)
    top_chunks = [entry["chunk"] for entry in ranked[:top_n]]

    with open("recalled_chunks.json", "w", encoding="utf-8") as f:
        json.dump(top_chunks, f, indent=2, ensure_ascii=False)

    print(f"Top {top_n} relevant chunks saved to recalled_chunks.json.")

# === RUN TEST ===
if __name__ == "__main__":
    user_query = input("Enter your query: ")
    recall_top_chunks(user_query)
