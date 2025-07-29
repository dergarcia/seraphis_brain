# repair_tagged_memory.py
# Repairs tagged_memory.json by:
# - dropping truly empty entries (no meaningful text)
# - fixing non‑numeric scores -> 0.0
# - clamping out‑of‑range or missing chunk_id into valid range 1..N
# - normalizing schema (list of dicts). Writes a repaired file + summary.
# Python 3.11+

import argparse, json, os, copy
from datetime import datetime
from typing import Any, Dict, List

DEF_INPUT_MD = "seraphis_final_core.md"
DEF_TAGGED = "tagged_memory.json"
DEF_OUT = "repaired_tagged_memory.json"
DEF_CHUNK_SIZE = 350
ARTIFACTS_DIR = "artifacts"

def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def size_split(text: str, chunk_size: int) -> List[str]:
    t = text.replace("\r\n", "\n")
    return [t[i:i+chunk_size] for i in range(0, len(t), chunk_size)] or [""]

def load_tagged(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict) and "entries" in data:
        return data["entries"]
    if isinstance(data, list):
        return data
    return [data]

def is_meaningful_text(e: Dict[str, Any]) -> bool:
    for k in ("answer","summary","chunk_text","content","text"):
        v = e.get(k)
        if isinstance(v, str) and v.strip():
            return True
    return False

def coerce_score(v: Any) -> float:
    try:
        return float(v)
    except Exception:
        # try alternates
        for k in ("relevance","priority"):
            try:
                return float(v.get(k))  # type: ignore
            except Exception:
                continue
        return 0.0

def clamp_chunk_id(e: Dict[str, Any], total_chunks: int) -> int:
    cid = e.get("chunk_id")
    try:
        n = int(cid)
    except Exception:
        n = 1
    if n < 1: n = 1
    if n > total_chunks: n = total_chunks
    return n

def main():
    p = argparse.ArgumentParser(description="Repair tagged_memory.json for coherence.")
    p.add_argument("--input", default=DEF_INPUT_MD)
    p.add_argument("--tagged", default=DEF_TAGGED)
    p.add_argument("--out", default=DEF_OUT)
    p.add_argument("--chunk-size", type=int, default=DEF_CHUNK_SIZE)
    p.add_argument("--drop-empty", action="store_true",
                   help="Drop entries with no meaningful text. Otherwise they are kept with score=0 and category='empty'.")
    args = p.parse_args()

    os.makedirs(ARTIFACTS_DIR, exist_ok=True)

    # Compute expected chunk range using our standardized splitter
    src = load_text(args.input)
    total_chunks = len(size_split(src, args.chunk_size))

    entries = load_tagged(args.tagged)
    orig_count = len(entries)

    repaired: List[Dict[str, Any]] = []
    stats = {"dropped_empty":0, "fixed_score":0, "fixed_chunk":0, "kept":0}

    for e in entries:
        e2 = copy.deepcopy(e)

        # Empty handling
        if not is_meaningful_text(e2):
            if args.drop_empty:
                stats["dropped_empty"] += 1
                continue
            else:
                e2.setdefault("category","empty")
                e2["score"] = 0.0

        # Score
        before_score = e2.get("score")
        s = coerce_score(before_score if before_score is not None else e2)
        if before_score != s:
            stats["fixed_score"] += 1
        e2["score"] = s

        # Chunk ID
        before_chunk = e2.get("chunk_id")
        c = clamp_chunk_id(e2, total_chunks)
        if before_chunk != c:
            stats["fixed_chunk"] += 1
        e2["chunk_id"] = c

        # Minimal schema hygiene
        if "category" not in e2 or (isinstance(e2["category"], str) and not e2["category"].strip()):
            e2["category"] = "unknown"

        repaired.append(e2)
        stats["kept"] += 1

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(repaired, f, ensure_ascii=False, indent=2)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = os.path.join(ARTIFACTS_DIR, f"repair_summary_{ts}.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "input_md": args.input,
                "tagged_file": args.tagged,
                "out_file": args.out,
                "chunk_size": args.chunk_size,
                "total_chunks_expected": total_chunks,
                "original_entries": orig_count,
                "repaired_entries": len(repaired)
            },
            "stats": stats
        }, f, indent=2)

    print(f"[Repair] Original entries: {orig_count} -> Repaired: {len(repaired)} "
          f"(dropped_empty={stats['dropped_empty']}, fixed_score={stats['fixed_score']}, fixed_chunk={stats['fixed_chunk']}).")
    print(f"[Repair] Summary: {summary_path}")
    print(f"[Repair] Repaired file written: {args.out}")

if __name__ == "__main__":
    main()
