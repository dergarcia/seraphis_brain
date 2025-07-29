import os
import json
import openai
from dotenv import load_dotenv

# Load environment
load_dotenv()
client = openai.OpenAI()

# Load tagged memory
with open("tagged_memory.json", "r", encoding="utf-8") as f:
    memory = json.load(f)

# Get user query
query = input("Enter your query: ")

# Build GPT prompt
def build_prompt(query, memory_chunks):
    formatted = "\n".join([
        f"ID: {chunk['chunkId']}\nText: {chunk['chunk']}" for chunk in memory_chunks
    ])
    
    return f"""
Seraphis has received the following user query:
\"\"\"{query}\"\"\"

Here are memory chunks from his brain:
{formatted}

Your task:
- Return the 3–5 most relevant memory chunks that should be used to respond to this query.
- Match based on meaning, not just keywords.
- Respond ONLY in this JSON format:
{{ "relevant_ids": [1, 3, 7] }}
"""

# Send prompt to GPT-4 (correct method)
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": build_prompt(query, memory)}],
    temperature=0.3
)

# Parse output
relevant_ids = json.loads(response.choices[0].message.content)["relevant_ids"]

# Filter matching chunks
best_context = [chunk for chunk in memory if chunk["chunkId"] in relevant_ids]

# Save to file
with open("recalled_chunks.json", "w", encoding="utf-8") as out:
    json.dump(best_context, out, indent=2, ensure_ascii=False)

print("✅ Best context bundle written to recalled_chunks.json")
