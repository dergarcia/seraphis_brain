import os
import openai
from dotenv import load_dotenv
import json

# Load environment and OpenAI client
load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load agents
from ceo_agent import run as ceo_run
from cmo_agent import run as cmo_run
from cfo_agent import run as cfo_run
from coo_agent import run as coo_run

# Load memory
def load_memory():
    memory_path = "business_memory.json"
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Check for relevant memory
def find_relevant_memory(question, memory):
    prompt = (
        f"Search this memory for anything useful to help answer:\n\n"
        f"Question: {question}\n\n"
        f"Memory:\n" + "\n".join([f"Q: {m['question']}\nA: {m['answer']}" for m in memory])
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You identify relevant prior answers from memory that can inform the current question."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# Synthesis logic
def synthesize_responses(agent_outputs, question, memory_context):
    prompt = (
        f"The following agents answered the business question:\n\n"
        f"Question: {question}\n\n"
        f"Relevant Memory:\n{memory_context}\n\n" +
        "\n\n".join([f"{agent}:\n{response}" for agent, response in agent_outputs.items()]) +
        "\n\nSynthesize all responses into a single, intelligent insight."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a strategic AI that combines expert agent input and memory to form the best possible business insight."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )
    return response.choices[0].message.content

# Save to memory
def save_to_memory(question, final_answer):
    memory_path = "business_memory.json"
    memory = load_memory()
    memory.append({"question": question, "answer": final_answer})
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)
    print(f"💾 Memory saved to: {os.path.abspath(memory_path)}")

# Main loop
def run_reasoning_loop():
    print("🧠 Seraphis Multi-Agent Reasoning Engine")
    question = input("🔍 Enter a business question:\n> ")
    memory = load_memory()
    memory_context = find_relevant_memory(question, memory)

    print("\n📣 Calling all agents...\n")
    agent_outputs = {
        "CEO": ceo_run(question),
        "CMO": cmo_run(question),
        "CFO": cfo_run(question),
        "COO": coo_run(question)
    }

    for agent, output in agent_outputs.items():
        print(f"\n🔹 {agent} Agent Response:\n{output}")

    final_answer = synthesize_responses(agent_outputs, question, memory_context)
    print("\n✅ Final Synthesized Answer:\n", final_answer)

    save_to_memory(question, final_answer)

if __name__ == "__main__":
    run_reasoning_loop()
