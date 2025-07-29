import openai
from dotenv import load_dotenv
import os
import json

# Load .env
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load recalled memory chunks
with open("recalled_chunks.json", "r", encoding="utf-8") as f:
    recalled_chunks = json.load(f)

# Extract actual chunk content
chunk_texts = [chunk["chunk"] for chunk in recalled_chunks if "chunk" in chunk]
context = "\n\n".join(chunk_texts)

# Ask user for the previous response
user_input = input("Paste Seraphis' original response you want to reflect on:\n")

# Compose reflection prompt
reflection_prompt = f"""
You are Seraphis, an evolving intelligence that improves after every conversation.

Your previous response was:
\"\"\"
{user_input}
\"\"\"

Based on your current knowledge:
\"\"\"
{context}
\"\"\"

What parts of your response could be improved, corrected, or clarified?
Reflect on your reasoning and suggest a better version if needed.
"""

# Get improved reflection from GPT
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": reflection_prompt}],
    temperature=0.3,
)

improved = response.choices[0].message.content.strip()
print("\n🔁 Self-Reflection Complete:\n")
print(improved)
