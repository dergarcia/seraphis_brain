import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

memory_folder = "Input_Documents/memory_chunks"

def load_chunks_from_folder(folder_path):
    chunks = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                chunk_data = json.load(f)
                chunks.append(chunk_data)
    return chunks

def get_relevant_chunks(query, chunks):
    relevant_chunks = []
    for chunk in chunks:
        text = chunk.get("text") or chunk.get("answer") or ""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Determine if this chunk is relevant to the query."},
                {"role": "user", "content": f"Query: {query}\n\nChunk:\n{text}\n\nIs this relevant? Reply 'Yes' or 'No'."}
            ]
        )
        is_relevant = "yes" in response.choices[0].message.content.lower()
        if is_relevant:
            relevant_chunks.append(chunk)
    return relevant_chunks

if __name__ == "__main__":
    query = input("💬 What would you like to ask Seraphis' memory loop?\n> ")

    chunks = load_chunks_from_folder(memory_folder)
    relevant = get_relevant_chunks(query, chunks)

    if relevant:
        print("\n🧠 Relevant Chunks Found:\n")
        for chunk in relevant:
            print(json.dumps(chunk, indent=2))
    else:
        print("\n⚠️ No relevant chunks found.")
