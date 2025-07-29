# score_memory_entry.py (non-interactive + timezone-aware + silent chunk_id default)
# Usage:
#   python score_memory_entry.py --query "..." --category system_self_knowledge --score 9 --chunk-id 1
# If args are omitted, falls back to stdin/prompt for query/category/score.
# chunk_id defaults to 1 WITHOUT prompting.

import argparse
import json
import os
from datetime import datetime, timezone
from typing import Tuple

TAGGED = "tagged_memory.json"
SYNTH_MD = "synthesized_memory.md"

def get_inputs(args: argparse.Namespace) -> Tuple[str, str, float, int]:
    q = args.query or ""
    c = args.category or ""
    s = args.score
    # IMPORTANT: default chunk_id=1 silently (no prompt)
    cid = 1 if args.chunk_id is None else int(args.chunk_id)

    # stdin fallback for query
    if not q:
        try:
            import sys
            if not sys.stdin.isatty():
                data = sys.stdin.read().strip()
                if data:
                    q = data.splitlines()[0].strip()
        except Exception:
            pass

    if not q:
        q = input("Enter the original user query again: ").strip()

    if not c:
        c = input("Category for this memory (e.g. system_self_knowledge): ").strip() or "unknown"

    if s is None:
        try:
            s = float(input("Enter relevance score (0–10): ").strip())
        except Exception:
            s = 0.0

    return q, c, float(s), int(cid)

def load_entries() -> list:
    if not os.path.exists(TAGGED):
        return []
    with open(TAGGED, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["entries"] if isinstance(data, dict) and "entries" in data else data

def save_entries(entries: list):
    with open(TAGGED, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

def read_synth() -> str:
    if os.path.exists(SYNTH_MD):
        with open(SYNTH_MD, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query")
    ap.add_argument("--category")
    ap.add_argument("--score", type=float)
    ap.add_argument("--chunk-id", type=int, dest="chunk_id", help="Associate this memory with a chunk ID (default 1)")
    args = ap.parse_args()

    q, c, s, cid = get_inputs(args)

    entry = {
        "question": q,
        "answer": read_synth(),
        "category": c,
        "score": s,
        "chunk_id": cid if cid and cid > 0 else 1,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")
    }

    entries = load_entries()
    entries.append(entry)
    save_entries(entries)
    print("✓ Memory entry added and saved.")

if __name__ == "__main__":
    main()
