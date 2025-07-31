import requests
import json

# Base URL for Seraphis local API
BASE_URL = "http://127.0.0.1:5057"

def learn(query, category="operations", score=7.5, chunk_id=1):
    payload = {
        "query": query,
        "category": category,
        "score": score,
        "chunk_id": chunk_id
    }
    r = requests.post(f"{BASE_URL}/learn", json=payload)
    return r.json()

def retrieve(query, top_k=5):
    params = {"query": query, "top_k": top_k}
    r = requests.get(f"{BASE_URL}/retrieve", params=params)
    return r.json()

def reason():
    r = requests.post(f"{BASE_URL}/reason")
    return r.json()

if __name__ == "__main__":
    print("--- Smoke Test: Learn ---")
    print(learn("Draft a weekly QA smoke checklist for Seraphis.", "operations", 7.7, 10))

    print("--- Smoke Test: Retrieve ---")
    print(retrieve("smoke checklist", 5))

    print("--- Smoke Test: Reason ---")
    print(reason())
