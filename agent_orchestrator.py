import os
import importlib.util
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === Memory Config ===
memory_file = r"C:\Users\degarcia\Seraphis\Tools\Memory\marketing_memory.md"
os.makedirs(os.path.dirname(memory_file), exist_ok=True)

# === Agent Paths ===
AGENT_MAP = {
    "marketing": "cmo_agent.py",
    "sales": "cmo_agent.py",
    "tiktok": "cmo_agent.py",
    "instagram": "cmo_agent.py",
    "social media": "cmo_agent.py",
    "finance": "cfo_agent.py",
    "financials": "cfo_agent.py",
    "budget": "cfo_agent.py",
    "operations": "coo_agent.py",
    "logistics": "coo_agent.py",
    "business strategy": "ceo_agent.py",
    "leadership": "ceo_agent.py",
    "vision": "ceo_agent.py",
}

DEFAULT_AGENT = "ceo_agent.py"
TOOLS_PATH = r"C:\Users\degarcia\Seraphis\Tools"

# === Function: GPT selects best agent ===
def get_best_agent(query):
    prompt = f"""
You are a router AI. Your job is to decide which type of agent should handle the user's request.

Known agents and their domains:
- CMO Agent → marketing, social media, TikTok, Instagram, content
- CFO Agent → finance, budgeting, profitability
- COO Agent → operations, logistics, delivery, systems
- CEO Agent → business strategy, leadership, vision

Query: "{query}"

Which agent is the best fit? Reply with only one word: CMO, CFO, COO, or CEO.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}],
    )
    answer = response.choices[0].message.content.strip().lower()

    if "cmo" in answer:
        return "cmo_agent.py"
    elif "cfo" in answer:
        return "cfo_agent.py"
    elif "coo" in answer:
        return "coo_agent.py"
    elif "ceo" in answer:
        return "ceo_agent.py"
    else:
        return DEFAULT_AGENT

# === Function: Run selected agent ===
def run_agent(agent_path, query):
    try:
        full_path = os.path.join(TOOLS_PATH, agent_path)
        spec = importlib.util.spec_from_file_location("agent_module", full_path)
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)

        if hasattr(agent_module, "run"):
            return agent_module.run(query)
        else:
            return f"Agent loaded, but no 'run' method found in {agent_path}."
    except Exception as e:
        return f"Error running agent {agent_path}: {e}"

# === Function: Save to memory ===
def save_to_memory(question, answer):
    try:
        with open(memory_file, "a", encoding="utf-8") as f:
            f.write(f"\n### Q: {question}\nA: {answer}\n---\n")
        print("✅ Memory saved.")
    except Exception as e:
        print(f"❌ Failed to save memory: {e}")

# === Start Orchestration ===
if __name__ == "__main__":
    print("Welcome to Seraphis Orchestrator")
    query = input("🧠 What do you need help with? ").strip()

    selected_agent = get_best_agent(query)
    print(f"📡 Routing to: {selected_agent.replace('_agent.py', '').upper()} Agent")

    response = run_agent(selected_agent, query)
    print(f"\n🗣️ Agent Response:\n{response}")

    save_to_memory(query, response)


