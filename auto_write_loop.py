# auto_write_loop.py
# Orchestrates a single "learn" cycle using existing scripts.
# ASCII-only output to avoid Windows cp1252 encoding issues.

import subprocess
import sys
import shlex

def run(cmd: str) -> int:
    print(f"[RUN] {cmd}")
    # Use shell=False with shlex.split for safety, capture output to pass through
    proc = subprocess.run(shlex.split(cmd), stdout=sys.stdout, stderr=sys.stderr)
    return proc.returncode

def learn_once(query: str, category: str = "system_planning", score: float = 8.5, chunk_id: int = 2) -> int:
    # 1) Synthesize a candidate memory entry from the query
    rc = run(f'python synthesize_memory_response.py --query "{query}"')
    if rc != 0:
        print("[ERR] synthesize_memory_response failed")
        return rc

    # 2) Score and save that entry to memory
    rc = run(
        f'python score_memory_entry.py --query "{query}" --category {category} --score {score} --chunk-id {chunk_id}'
    )
    if rc != 0:
        print("[ERR] score_memory_entry failed")
        return rc

    # 3) Optional: quick sanity check that reasoning still runs (no guard repair here)
    rc = run("python reasoning_module.py")
    if rc != 0:
        print("[WARN] reasoning_module returned non-zero; learning still may have saved.")
        # Not fatal

    print("[OK] Learn cycle complete.")
    return 0

def main():
    # Simple CLI: python auto_write_loop.py --query "your question" [--category X] [--score 8.5] [--chunk-id 2]
    # Keep parsing minimal to avoid external deps
    args = sys.argv[1:]
    if not args or "--query" not in args:
        print('Usage: python auto_write_loop.py --query "What should I ship next?" [--category system_planning] [--score 8.5] [--chunk-id 2]')
        sys.exit(2)

    # Defaults
    query = None
    category = "system_planning"
    score = "8.5"
    chunk_id = "2"

    i = 0
    while i < len(args):
        if args[i] == "--query" and i + 1 < len(args):
            query = args[i + 1]
            i += 2
        elif args[i] == "--category" and i + 1 < len(args):
            category = args[i + 1]
            i += 2
        elif args[i] == "--score" and i + 1 < len(args):
            score = args[i + 1]
            i += 2
        elif args[i] == "--chunk-id" and i + 1 < len(args):
            chunk_id = args[i + 1]
            i += 2
        else:
            i += 1

    if not query:
        print("[ERR] --query is required")
        sys.exit(2)

    # Convert types where needed
    try:
        score_f = float(score)
        chunk_i = int(chunk_id)
    except Exception:
        print("[ERR] --score must be float and --chunk-id must be int")
        sys.exit(2)

    sys.exit(learn_once(query, category, score_f, chunk_i))

if __name__ == "__main__":
    main()
