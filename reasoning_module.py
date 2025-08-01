# reasoning_module.py
# Usage:
#   python reasoning_module.py               # show top 3 priorities
#   python reasoning_module.py --top-k 5     # show top 5

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# --- Lock working directory to repo root (prevents System32 path issues) ---
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)

TAGGED = ROOT / "tagged_memory.json"


def _load_tagged() -> List[Dict[str, Any]]:
    """Load entries from tagged_memory.json (handles list or {'entries': [...]})."""
    if not TAGGED.exists():
        return []
    try:
        data = json.loads(TAGGED.read_text(encoding="utf-8"))
    except Exception:
        return []
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return data["entries"]
    return data if isinstance(data, list) else []


def _coerce_score(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        return float("-inf")  # send bad scores to the bottom


def load_and_process_memory(top_k: int = 3) -> int:
    """
    Load memory entries from tagged_memory.json, normalize fields, sort by score,
    and display top-k.
    """
    entries = _load_tagged()
    if not entries:
        print("No entries found in tagged_memory.json")
        return 0

    # Normalize: accept either 'question' or 'query'
    required_fields = ("score", "category", "answer")
    normalized: List[Dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        q = (e.get("query") or e.get("question") or "").strip()
        cat = (e.get("category") or "").strip()
        ans = (e.get("answer") or "").strip()
        if not q or not cat or not ans:
            continue
        sc = _coerce_score(e.get("score", 0))
        normalized.append({"score": sc, "category": cat, "query": q, "answer": ans})

    if not normalized:
        print("No valid entries found in tagged_memory.json")
        return 0

    # Sort by score desc and take top_k
    normalized.sort(key=lambda x: x["score"], reverse=True)
    top = normalized[: max(1, top_k)]

    # Print in the expected format
    for i, entry in enumerate(top, 1):
        print(f"--- Priority #{i} ---")
        # print score with one decimal if it looks like an int-ish float
        score = entry["score"]
        score_str = f"{score:.1f}" if isinstance(score, (int, float)) else str(score)
        print(f"Score: {score_str}")
        print(f"Category: {entry['category']}")
        print(f"Question: {entry['query']}")
        print(f"Answer: {entry['answer']}")
        if i < len(top):
            print()

    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Render prioritized insights from tagged memory.")
    ap.add_argument("--top-k", type=int, default=3, help="How many priorities to display (default 3)")
    args = ap.parse_args()
    return load_and_process_memory(top_k=args.top_k)


if __name__ == "__main__":
    sys.exit(main())
