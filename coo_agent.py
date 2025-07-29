import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run(query):
    memory_file = "C:/Users/degarcia/Seraphis/Tools/Memory/operations_memory.md"
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)

    system_prompt = """
    You are a COO Agent for Seraphis. Your expertise includes streamlining business operations, optimizing workflows,
    allocating resources efficiently, and scaling digital product systems. Respond with actionable, real-world strategies
    that prioritize speed, efficiency, and growth without compromising quality.
    """

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": query}
        ],
        temperature=0.5,
    )

    answer = response.choices[0].message.content.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"## COO Agent Decision ({timestamp}):\n**Query:** {query}\n\n**Response:**\n{answer}\n\n"

    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)

    print("\n📌 COO Agent Response:\n")
    print(answer)
    print("\n✅ Decision saved to operations memory.")

    return answer
