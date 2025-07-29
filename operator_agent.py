import os
import json
from datetime import datetime
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
N8N_WEBHOOK_URL = os.getenv("N8N_OPERATOR_HOOK")
MEMORY_FILE = "seraphis_strategy_memory.json"
LOG_FILE = "operator_log.json"

# Helper: Read memory
def load_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"error": f"Failed to load memory: {str(e)}"}

# Helper: Log execution
def log_action(entry):
    try:
        timestamp = datetime.now().isoformat()
        entry["timestamp"] = timestamp

        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump([entry], f, indent=2)
        else:
            with open(LOG_FILE, "r+", encoding="utf-8") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Failed to write log: {str(e)}")

# Helper: Send task to n8n
def send_to_n8n(payload):
    try:
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        return response.status_code, response.text
    except Exception as e:
        return 500, f"Failed to send to n8n: {str(e)}"

# Agent Core
def run_operator():
    memory = load_memory()
    if "error" in memory:
        print(f"[ERROR] {memory['error']}")
        return

    latest_task = memory.get("latest_task")
    if not latest_task:
        print("[INFO] No task found in memory.")
        return

    print(f"[TASK] Executing: {latest_task.get('summary', 'No summary')}")

    payload = {
        "task": latest_task,
        "origin": "operator_agent",
        "execution_time": datetime.now().isoformat()
    }

    status, response = send_to_n8n(payload)
    log_action({
        "task": latest_task,
        "status": status,
        "response": response
    })

    print(f"[n8n] Status: {status} | Response: {response}")


if __name__ == "__main__":
    run_operator()
