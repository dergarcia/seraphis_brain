# synthesize_memory_response.py (non-interactive ready)
# Usage:
#   python synthesize_memory_response.py --query "What are the top priorities in Seraphis' current build?"
# Falls back to stdin if --query omitted; if still missing, will prompt.

import argparse, os, json
from datetime import datetime
from client_utils import client  # shared OpenAI client

TAGGED = "tagged_memory.json"
OUT_MD = "synthesized_memory.md"

def get_user_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query.strip()
    try:
        import sys
        if not sys.stdin.isatty():
            s = sys.stdin.read().strip()
            if s:
                return s
    except Exception:
        pass
    # final fallback: prompt
    return input("Enter the original user query: ").strip()

def load_tagged() -> list:
    if not os.path.exists(TAGGED):
        return []
    with open(TAGGED, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["entries"] if isinstance(data, dict) and "entries" in data else data

def filter_relevant_chunks(query: str, entries: list) -> list:
    # Simple heuristic relevance using the model for reranking-lite (fast + robust)
    # If you have an embeddings index, swap this with cosine similarity.
    prompt = (
        "You will receive a user query and a list of memory entries.\n"
        "Return ONLY the top 5 entries most relevant to answering the query as a JSON array of indices.\n"
        "Be strict and prefer recency if scores tie.\n"
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps({"query": query, "entries": entries[:50]})}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0
    )
    text = resp.choices[0].message.content or "[]"
    try:
        idxs = json.loads(text)
        if isinstance(idxs, list):
            keep = [entries[i] for i in idxs if isinstance(i, int) and 0 <= i < len(entries)]
            return keep
    except Exception:
        pass
    # Fallback: take top 5 by existing score if present
    sorted_entries = sorted(entries, key=lambda e: float(e.get("score", 0)), reverse=True)
    return sorted_entries[:5]

def synthesize_answer(query: str, context_entries: list) -> str:
    context = json.dumps(context_entries, ensure_ascii=False)
    messages = [
        {"role": "system", "content": "You are Seraphis' memory synthesizer. Answer concisely using provided memory only."},
        {"role": "user", "content": f"Query: {query}\nMemory: {context}\nCompose the best answer."}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2
    )
    return resp.choices[0].message.content.strip()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="Original user query (non-interactive mode)")
    args = ap.parse_args()

    query = get_user_query(args)
    entries = load_tagged()
    relevant = filter_relevant_chunks(query, entries)
    answer = synthesize_answer(query, relevant)

    # Persist a simple artifact used by downstream scripts
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(answer + "\n")

    print(f"✓ Synthesized memory saved to {OUT_MD}")

if __name__ == "__main__":
    main()
