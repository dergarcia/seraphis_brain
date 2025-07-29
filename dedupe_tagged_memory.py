# dedupe_tagged_memory.py
# Remove duplicate memory entries from tagged_memory.json by semantic keys.
# Keeps the entry with the highest score; ties -> newest timestamp.
# Python 3.11+

import argparse, json, hashlib, os
from datetime import datetime
from typing import Dict, Any, List, Tuple

def norm(s: str) -> str:
    return " ".join((s or "").strip().lower().split())

def key_for(entry: Dict[str, Any]) -> str:
    q = norm(str(entry.get("question", "")))
    a = norm(str(entry.get("answer", entry.get("summary", entry.get("content", entry.get("text", ""))))))
    cat = norm(str(entry.get("category", "")))
    # If both q and a are empty, hash the chunk_id to avoid collapsing unrelated blanks
    if not q and not a:
        return f"empty:{entry.get('chunk_id')}"
    h = hashlib.sha1((q + "||" + a + "||" + cat).encode("utf-8")).hexdigest()
    return h

def parse_ts(s: Any) -> float:
    # Accept ISO-ish strings or epoch; fallback to 0
    if isinstance(s, (int, float)): return float(s)
    if isinstance(s, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                return datetime.strptime(s.replace("Z",""), fmt).timestamp()
            except Exception:
                pass
    return 0.0

def better(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    # Prefer higher score; tie-break by newer timestamp
    sa = float(a.get("score", a.get("relevance", a.get("priority", 0))) or 0)
    sb = float(b.get("score", b.get("relevance", b.get("priority", 0))) or 0)
    if sa > sb: return a
    if sb > sa: return b
    if parse_ts(a.get("timestamp")) >= parse_ts(b.get("timestamp")): return a
    return b

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="tagged_memory.json")
    ap.add_argument("--out", default="tagged_memory.json")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"[dedupe] Input not found: {args.input}")
        return

    data = json.load(open(args.input, "r", encoding="utf-8"))
    if isinstance(data, dict) and "entries" in data:
        entries = data["entries"]
        wrap = True
    elif isinstance(data, list):
        entries = data
        wrap = False
    else:
        print("[dedupe] Unsupported format.")
        return

    before = len(entries)
    buckets: Dict[str, Dict[str, Any]] = {}
    for e in entries:
        k = key_for(e)
        if k not in buckets:
            buckets[k] = e
        else:
            buckets[k] = better(buckets[k], e)

    deduped = list(buckets.values())
    after = len(deduped)
    removed = before - after

    # Write back in same format
    out_obj = {"entries": deduped} if wrap else deduped
    json.dump(out_obj, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[dedupe] Original: {before} -> Deduped: {after} (removed {removed}). Wrote: {args.out}")

if __name__ == "__main__":
    main()
