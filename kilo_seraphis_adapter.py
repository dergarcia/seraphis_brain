import os
import sys
import json
import argparse
import requests
from pathlib import Path

# --- Force working directory to repo root (prevents System32 path issues) ---
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)

# Base URL for Seraphis local API
BASE_URL = "http://127.0.0.1:5057"
# Increase timeouts so long operations (learn, retrieve, reason) don't bomb at 20s
TIMEOUT = 60

def learn(query, category="operations", score=7.5, chunk_id=1):
    payload = {
        "query": query,
        "category": category,
        "score": score,
        "chunk_id": chunk_id
    }
    r = requests.post(f"{BASE_URL}/learn", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def retrieve(query, top_k=5):
    params = {"query": query, "top_k": top_k}
    r = requests.get(f"{BASE_URL}/retrieve", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def reason():
    r = requests.post(f"{BASE_URL}/reason", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def _print(obj):
    if isinstance(obj, (dict, list)):
        print(json.dumps(obj, indent=2))
    else:
        print(obj)

def main():
    parser = argparse.ArgumentParser(prog="kilo_seraphis_adapter")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_learn = sub.add_parser("learn")
    p_learn.add_argument("--query", required=True)
    p_learn.add_argument("--category", default="operations")
    p_learn.add_argument("--score", type=float, default=7.5)
    p_learn.add_argument("--chunk-id", type=int, default=1)

    p_retr = sub.add_parser("retrieve")
    p_retr.add_argument("--query", required=True)
    p_retr.add_argument("--top-k", type=int, default=5)

    sub.add_parser("reason")

    args = parser.parse_args()

    if args.cmd == "learn":
        _print(learn(args.query, args.category, args.score, args.chunk_id))
    elif args.cmd == "retrieve":
        _print(retrieve(args.query, args.top_k))
    elif args.cmd == "reason":
        _print(reason())

if __name__ == "__main__":
    main()
