import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# ✅ Load environment and OpenAI key
load_dotenv()
client = OpenAI()

# Define the memory files to search
memory_folder = "Memory"
memory_files = [
    "synthesized_memory.md",
    "seraphis_memory.md",
    "seraphis_knowledge.md",
    "normalized_inputs.md",
    "compressed_memory.md"
]
memory_paths = [os.path.join(memory_folder, f) for f in memory_files]

def load_chunks_from_md(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    chunks = re.findall(r"\*\*(?:User Query|Q):\*\*(.*?)\n.*?\*\*(?:Answer|A):\*\*(.*?)(?=\n\*\*|$)", content, re.DOTALL)
    return [{"file": os.path.basename(filepath), "query": q.strip(), "answer": a.strip()} for q, a in chunks]

def retrieve_relevant_chunks(query):
    all_chunks = []
    for path in memory_paths:
        if os.path.exists(path):
            all_chunks.extend(load_chunks_from_md(path))

    context = "\n\n".join([f"Query: {c['query']}\nAnswer: {c['answer']}" for c in all_chunks])
    prompt = f"""You are Seraphis. Based on the following memory entries, synthesize a response to the query below:

Memory Entries:
{context}

User Query: {query}

Respond with the most accurate and insightful answer using the memory above.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content

def save_to_synthesized(query, answer):
    filepath = os.path.join("Memory", "synthesized_memory.md")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n\n**User Query:** {query}\n\n**Answer:** {answer}\n\n---")

if __name__ == "__main__":
    user_query = input("Enter your query: ")
    final_answer = retrieve_relevant_chunks(user_query)
    print("\n💡 Synthesized Answer:\n", final_answer)
    save_to_synthesized(user_query, final_answer)
    print("\n✅ Entry saved to synthesized_memory.md.")
