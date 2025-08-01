# synthesize_memory_response.py (non-interactive ready)
# Usage:
#   python synthesize_memory_response.py --query "What are the top priorities in Seraphis' current build?"
# Falls back to stdin if --query omitted; if still missing, will prompt.

import argparse
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# --- Lock working directory to the repo (prevents System32 path bugs) ---
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from client_utils import client  # shared OpenAI client

TAGGED = ROOT / "tagged_memory.json"
OUT_DIR = ROOT / "Memory"
OUT_MD = OUT_DIR / "synthesized_memory.md"


def get_user_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query.strip()
    try:
        if not sys.stdin.isatty():
            s = sys.stdin.read().strip()
            if s:
                return s
    except Exception:
        pass
    # final fallback: prompt
    return input("Enter the original user query: ").strip()


def load_tagged() -> List[Dict[str, Any]]:
    if not TAGGED.exists():
        return []
    try:
        with TAGGED.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return []
    if isinstance(data, dict) and "entries" in data and isinstance(data["entries"], list):
        return data["entries"]
    return data if isinstance(data, list) else []


def _json_from_model(text: str):
    """Best-effort to parse JSON even if wrapped in code fences."""
    t = text.strip()
    if t.startswith("```"):
        # strip ```...``` (optionally with 'json' fence)
        t = t.strip("`")
        t = t.replace("json\n", "").replace("json\r\n", "")
    try:
        return json.loads(t)
    except Exception:
        return None


def filter_relevant_chunks(query: str, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Lightweight reranking using the model; falls back to score-based sort."""
    prompt = (
        "You will receive a user query and a list of memory entries.\n"
        "Return ONLY the top 5 entries most relevant to answering the query as a JSON array of indices.\n"
        "Be strict and prefer recency if scores tie."
    )
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps({"query": query, "entries": entries[:50]}, ensure_ascii=False)},
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0,
    )
    text = (resp.choices[0].message.content or "[]").strip()
    idxs = _json_from_model(text)
    if isinstance(idxs, list):
        keep = [entries[i] for i in idxs if isinstance(i, int) and 0 <= i < len(entries)]
        if keep:
            return keep

    # Fallback: top 5 by numeric score
    def _score(e: Dict[str, Any]) -> float:
        try:
            return float(e.get("score", 0) or 0)
        except Exception:
            return 0.0

    return sorted(entries, key=_score, reverse=True)[:5]


def synthesize_answer(query: str, context_entries: List[Dict[str, Any]]) -> str:
    context = json.dumps(context_entries, ensure_ascii=False)
    messages = [
        {"role": "system", "content": "You are Seraphis' memory synthesizer. Answer concisely using provided memory only."},
        {"role": "user", "content": f"Query: {query}\nMemory: {context}\nCompose the best answer."},
    ]
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="Original user query (non-interactive mode)")
    args = ap.parse_args()

    query = get_user_query(args)
    entries = load_tagged()
    relevant = filter_relevant_chunks(query, entries)
    answer = synthesize_answer(query, relevant)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(answer + "\n", encoding="utf-8")
    print(f"Synthesized memory saved to {OUT_MD}")


if __name__ == "__main__":
    main()
