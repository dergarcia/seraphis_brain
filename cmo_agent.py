import os
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run(user_question: str):
    # Define memory file path
    memory_file = r"C:\Users\degarcia\Seraphis\Tools\Memory\marketing_memory.md"
    os.makedirs(os.path.dirname(memory_file), exist_ok=True)

    # Define system prompt
    system_prompt = (
        "You are a CMO Agent with expertise in digital marketing, viral growth, and "
        "audience targeting. Give specific, high-ROI, low-budget strategies that scale fast. "
        "Prioritize content that attracts organic traffic and conversions."
    )

    # Call OpenAI
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question},
        ],
        temperature=0.7
    )

    # Extract the agent's message
    answer = response.choices[0].message.content

    # Save the response to memory
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"### Question ({timestamp}):\n{user_question}\n\n### CMO Response:\n{answer}\n\n"
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(entry)

    print("\n🧠 ✅ Decision saved to marketing memory.")
    return answer
