import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with key from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Path to your relevant memory chunks
RELEVANT_CHUNKS_PATH = "Input_Documents/memory_chunks/chunk_2.json"  # Adjust if needed

def synthesize_memory(chunks):
    prompt = (
        "You are Seraphis' memory synthesizer.\n"
        "Your job is to merge the following memory chunks into one clear, human-friendly response.\n"
        "Do NOT repeat redundant information. Maintain the core ideas.\n\n"
        f"Memory Chunks:\n\n{chunks}\n\n"
        "Final Answer:"
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


def load_chunks():
    with open(RELEVANT_CHUNKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return json.dumps(data, indent=2)

if __name__ == "__main__":
    chunks_json = load_chunks()
    final_response = synthesize_memory(chunks_json)
    print("\n🧠 Synthesized Memory Response:\n")
    print(final_response)
