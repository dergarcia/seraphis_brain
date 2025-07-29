import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run(query):
    # Define memory file path
    memory_file = "C:/Users/degarcia/Seraphis/Tools/Memory/financial_memory.md"
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)

    # Define system prompt
    system_prompt = """
    You are a CFO Agent for Seraphis. Your expertise includes startup finance, pricing models,
    cost analysis, and long-term financial strategy. Respond with clear, tactical insights only
    within your domain.
    """

    # Call OpenAI ChatCompletion using new v1+ API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": query}
        ],
        temperature=0.5,
    )

    # Extract and save
    answer = response.choices[0].message.content.strip()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"## CFO Agent Decision ({timestamp}):\n**Query:** {query}\n\n**Response:**\n{answer}\n\n"

    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)

    print("\n📌 CFO Agent Response:\n")
    print(answer)
    print("\n✅ Decision saved to financial memory.")

    return answer
