# store_memory_entry.py
# Usage examples:
#   python store_memory_entry.py --query "Draft a weekly QA smoke checklist for Seraphis." --category operations --score 7.7 --chunk-id 10 --answer "..."
#   python synthesize_memory_response.py --query "..." | python store_memory_entry.py --query "..." --category ops --score 7.0 --chunk-id 1
# If --answer is omitted, the script will try to read from STDIN; if still empty, it will try Memory/synthesized_memory.md (last synthesis).

from __future__ import annotations
import argparse, os, sys, json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

# --- Lock working directory to repo root (prevents System32 issues) ---
ROOT = Path(__file__).parent.resolve()
os.chdir(ROOT)

MEM_DIR = ROOT / "Memory"
MD_PATH = MEM_DIR / "synthesized_memory.md"
TAGGED_JSON = ROOT / "tagged_memory.json"


def read_answer_from_stdin() -> str | None:
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read().strip()
            return data if data else None
    except Exception:
        pass
    return None


def read_answer_fallback() -> str | None:
    # Last synthesis often stored here; if present, read it all.
    try:
        if MD_PATH.exists():
            return MD_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    # Legacy location (if any)
    legacy = ROOT / "synthesized_memory.md"
    try:
        if legacy.exists():
            return legacy.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return None


def append_markdown(query: str, answer: str) -> None:
    MEM_DIR.mkdir(parents=True, exist_ok=True)
    with MD_PATH.open("a", encoding="utf-8") as f:
        f.write(
            f"\n\n**User Query:** {query}\n\n"
            f"**Answer:** {answer}\n\n"
            f"---"
        )


def load_tagged_list() -> List[Dict[str, Any]]:
    if not TAGGED_JSON.exists():
        return []
    try:
        data = json.loads(TAGGED_JSON.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("entries"), list):
            return data["entries"]
        if isinstance(data, list):
            return data
    except Exception:
        pass
    return []


def save_tagged_list(entries: List[Dict[str, Any]]) -> None:
    # Write as a simple list for robustness (reader handles both list/dict).
    tmp = TAGGED_JSON.with_suffix(".tmp.json")
    tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(TAGGED_JSON)


def update_tagged(query: str, answer: str, category: str, score: float, chunk_id: int) -> None:
    entries = load_tagged_list()
    entries.append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "query": query,
        "answer": answer,
        "category": category,
        "score": float(score),
        "chunk_id": int(chunk_id)
    })
    save_tagged_list(entries)


def main() -> int:
    ap = argparse.ArgumentParser(description="Store a memory entry (markdown + tagged JSON).")
    ap.add_argument("--query", required=True, help="Original user query")
    ap.add_argument("--answer", help="Answer text; if omitted, read from stdin or fallback")
    ap.add_argument("--category", default="operations")
    ap.add_argument("--score", type=float, default=7.5)
    ap.add_argument("--chunk-id", type=int, default=1)
    args = ap.parse_args()

    answer = (args.answer or read_answer_from_stdin() or read_answer_fallback())
    if not answer:
        print("ERROR: No answer provided (pass --answer, pipe via stdin, or ensure Memory/synthesized_memory.md exists).", file=sys.stderr)
        return 2

    append_markdown(args.query, answer)
    update_tagged(args.query, answer, args.category, args.score, args.chunk_id)

    print(json.dumps({
        "ok": True,
        "saved_markdown": str(MD_PATH),
        "updated_json": str(TAGGED_JSON),
        "category": args.category,
        "score": args.score,
        "chunk_id": args.chunk_id
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
