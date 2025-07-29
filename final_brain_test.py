import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load memory
with open("tagged_memory.json", "r", encoding="utf-8") as f:
    memory_data = json.load(f)

# Retrieve top 5 relevant chunks
def get_relevant_chunks(query, memory, top_n=5):
    scores = []
    for item in memory:
        score_prompt = f"Rate the relevance of this memory chunk to the query below on a scale from 1 to 10.\n\nQuery: {query}\n\nMemory Chunk: {item['chunk']}"
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": score_prompt}],
            temperature=0.3
        )
        score_text = response.choices[0].message.content.strip()
        try:
            score = int(score_text.split()[0])
        except:
            score = 0
        scores.append((item, score))

    sorted_chunks = sorted(scores, key=lambda x: x[1], reverse=True)
    top_chunks = [item for item, score in sorted_chunks[:top_n]]
    return top_chunks

# Generate final response
def generate_response(query, relevant_chunks):
    context = "\n".join([item["chunk"] for item in relevant_chunks])
    prompt = f"""
You are Seraphis, a strategic AI advisor. Use the memory context below to answer the user's question.

Context:
{context}

User Query:
{query}
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

# Main function
if __name__ == "__main__":
    user_query = input("🧠 Enter your test query for Seraphis: ")
    print("\n🔍 Recalling top 5 relevant memory chunks...\n")
    relevant_chunks = get_relevant_chunks(user_query, memory_data)

    print("⚙️ Generating initial response...\n")
    raw_response = generate_response(user_query, relevant_chunks)

    print("💡 Seraphis says:\n")
    print(raw_response)
