import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_FILE = "synthesized_memory.md"

def load_memory_chunks():
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        content = f.read()
        chunks = content.split("###")
        return [chunk.strip() for chunk in chunks if chunk.strip()]

def is_relevant(chunk, query):
    system = "You are an intelligent filter. Return only 'yes' or 'no'."
    user = f"Does this memory chunk help answer the query?\n\nQuery: {query}\n\nMemory:\n{chunk}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0
    )
    answer = response.choices[0].message.content.strip().lower()
    return "yes" in answer

def summarize_relevant_chunks(relevant_chunks, query):
    system = "You are Seraphis. Respond with a clear, concise, and intelligent answer based on the provided memory chunks."
    user = f"Use these memory chunks to answer the query intelligently.\n\nQuery: {query}\n\nMemory:\n{relevant_chunks}"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def main():
    query = input("Enter query: ").strip()
    chunks = load_memory_chunks()
    relevant = [chunk for chunk in chunks if is_relevant(chunk, query)]

    if not relevant:
        print("⚠️ No relevant memory found.")
        return

    combined = "\n\n###\n\n".join(relevant)
    answer = summarize_relevant_chunks(combined, query)
    print("\n🧠 Seraphis' Answer:\n" + answer)

if __name__ == "__main__":
    main()
