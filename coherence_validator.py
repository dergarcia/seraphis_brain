# coherence_validator.py
# Validates tagged_memory.json for empty/malformed entries and bad chunk references.
# No API calls. Python 3.11+.

import argparse
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

DEF_INPUT_MD = "seraphis_final_core.md"
DEF_TAGGED = "tagged_memory.json"
DEF_CHUNK_SIZE = 350
ARTIFACTS_DIR = "artifacts"

def load_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def naive_size_split(text: str, chunk_size: int) -> List[str]:
    """
    Deterministic size-based splitter to mirror --force-split size --chunk-size N.
    We keep it simple: collapse Windows newlines, then slice every N chars.
    """
    norm = text.replace("\r\n", "\n")
    return [norm[i:i+chunk_size] for i in range(0, len(norm), chunk_size)] or [""]

def load_tagged(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, dict) and "entries" in data:
                return data["entries"]
            if isinstance(data, list):
                return data
            # Fallback: wrap single dict
            return [data]
        except json.JSONDecodeError:
            return []

def is_empty_string(v: Any) -> bool:
    return isinstance(v, str) and len(v.strip()) == 0

def field(v: Dict[str, Any], candidates: List[str]) -> Tuple[str, Any]:
    for k in candidates:
        if k in v:
            return k, v[k]
    return "", None

def classify_entry(e: Dict[str, Any], total_chunks: int) -> List[str]:
    """
    Returns list of issue codes for this entry.
    Codes:
      - empty: no meaningful text fields
      - nocontent: text fields exist but are empty/whitespace
      - nocategory: missing or blank category
      - badscore: score missing or not a number
      - badchunk: chunk_id missing or out of range
    """
    issues = []

    # Content presence
    text_keys = ["answer", "summary", "chunk_text", "content", "text"]
    k, v = field(e, text_keys)
    if k == "":
        issues.append("empty")
    else:
        if v is None or (isinstance(v, str) and is_empty_string(v)):
            issues.append("nocontent")

    # Category
    cat = e.get("category")
    if cat is None or (isinstance(cat, str) and is_empty_string(cat)):
        issues.append("nocategory")

    # Score
    score = e.get("score")
    try:
        # some schemas use "relevance" or "priority"; accept numeric strings
        if score is None:
            # try alternates
            score = e.get("relevance") or e.get("priority")
        float(score)  # will raise if not numeric
    except Exception:
        issues.append("badscore")

    # Chunk ID
    cid = e.get("chunk_id")
    try:
        cid_int = int(cid)
        if not (1 <= cid_int <= max(1, total_chunks)):
            issues.append("badchunk")
    except Exception:
        issues.append("badchunk")

    return issues

def main():
    parser = argparse.ArgumentParser(description="Validate tagged_memory.json coherence.")
    parser.add_argument("--input", default=DEF_INPUT_MD, help="Path to source markdown used for chunking.")
    parser.add_argument("--tagged", default=DEF_TAGGED, help="Path to tagged_memory.json.")
    parser.add_argument("--chunk-size", type=int, default=DEF_CHUNK_SIZE, help="Chunk size to mirror.")
    args = parser.parse_args()

    # Prepare artifacts dir
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # Derive total chunks based on the standardized profile
    try:
        src = load_file(args.input)
    except FileNotFoundError:
        print(f"[ERROR] Input markdown not found: {args.input}")
        return

    chunks = naive_size_split(src, args.chunk_size)
    total_chunks = len(chunks)

    entries = load_tagged(args.tagged)
    if not entries:
        print(f"[WARN] No entries found in {args.tagged}. Nothing to validate.")
        return

    report = []
    counts = {"ok": 0, "empty": 0, "nocontent": 0, "nocategory": 0, "badscore": 0, "badchunk": 0}

    for idx, e in enumerate(entries):
        issues = classify_entry(e, total_chunks)
        if not issues:
            counts["ok"] += 1
        else:
            for code in issues:
                counts[code] += 1
        report.append({
            "index": idx,
            "chunk_id": e.get("chunk_id"),
            "category": e.get("category"),
            "score": e.get("score", e.get("relevance", e.get("priority"))),
            "question": e.get("question"),
            "summary_or_answer_present": any(k in e for k in ["answer","summary","chunk_text","content","text"]),
            "issues": issues
        })

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = os.path.join(ARTIFACTS_DIR, f"coherence_report_{ts}.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "input_md": args.input,
                "tagged_file": args.tagged,
                "chunk_size": args.chunk_size,
                "total_chunks_expected": total_chunks
            },
            "summary": counts,
            "report": report
        }, f, ensure_ascii=False, indent=2)

    # Compact console summary
    total = sum(v for k, v in counts.items())
    print(f"[Coherence Validator] Entries: {total} | OK: {counts['ok']} | "
          f"empty: {counts['empty']} | nocontent: {counts['nocontent']} | "
          f"nocategory: {counts['nocategory']} | badscore: {counts['badscore']} | "
          f"badchunk: {counts['badchunk']}")
    print(f"[Coherence Validator] Expected chunk IDs range: 1..{total_chunks} (size={args.chunk_size})")
    print(f"[Coherence Validator] Detailed report: {out_json}")

if __name__ == "__main__":
    main()
