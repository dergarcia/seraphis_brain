from client_utils import client
import os
import openai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
# Define model
MODEL = "gpt-4-0613"

# Ask the user for a technical question
question = input("🤖 CTO Agent | What technical decision or infrastructure do you need help with?\n> ")

# Set system role prompt
system_prompt = (
    "You are the CTO Agent. Provide expert guidance on system architecture, infrastructure, cloud automation, "
    "API integrations, performance, and scalability. Your answers should be technically sound and designed for a lean AI business stack "
    "that includes GPT-4, Claude, and n8n."
)

# Use updated OpenAI API call
response = openai.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ],
    temperature=0.7
)

# Extract message
answer = response.choices[0].message.content.strip()

# Display response
print("\n💡 CTO Agent Response:\n")
print(answer)

# Save to markdown file
timestamp = datetime.now().isoformat()
memory_path = "C:\\Users\\degarcia\\Seraphis\\Memory\\cto_memory.md"

with open(memory_path, "a", encoding="utf-8") as f:
    f.write(f"\n### {timestamp}\n")
    f.write(f"**Question:** {question}\n")
    f.write(f"**Response:**\n{answer}\n")

print("\n✅ Decision saved to CTO memory.")
