from client_utils import client
import os
import openai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()
def filter_relevant_chunks(query, memory_chunks):
    """
    Filters memory chunks using tag and category relevance to the query.
    Falls back to full set if no matches found.
    """
    filtered_chunks = []
    query_lower = query.lower()

    for chunk in memory_chunks:
        category = chunk.get("category", "").lower()
        tags = [tag.lower() for tag in chunk.get("tags", [])]

        if category in query_lower or any(tag in query_lower for tag in tags):
            filtered_chunks.append(chunk)

    return filtered_chunks if filtered_chunks else memory_chunks

def synthesize_reasoning(query, context_chunks):
    """
    Sends the filtered memory context and query to GPT for reasoning.
    """
    context = "\n\n".join(chunk["content"] for chunk in context_chunks)

    messages = [
        {"role": "system", "content": "You are Seraphis, a powerful reasoning engine. Use the context below to answer the user query with logic, clarity, and precision."},
        {"role": "user", "content": f"Context:\n{context}\n\nQuery:\n{query}\n\nAnswer clearly and intelligently."}
    ]

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    return response.choices[0].message.content.strip()

def reason_through_query(query):
    """
    Loads memory, filters chunks by tag/category, and synthesizes an intelligent answer.
    """
    print("🧠 Loading tagged memory...")
    with open("tagged_memory.json", "r", encoding="utf-8") as f:
        memory_chunks = json.load(f)

    print("🔎 Filtering relevant memory...")
    relevant_chunks = filter_relevant_chunks(query, memory_chunks)

    print(f"🧪 Synthesizing reasoning with {len(relevant_chunks)} relevant chunks...")
    answer = synthesize_reasoning(query, relevant_chunks)

    print("\n💡 Answer:\n")
    print(answer)

if __name__ == "__main__":
    user_query = input("🗣️  Ask Seraphis a question:\n> ")
    reason_through_query(user_query)
