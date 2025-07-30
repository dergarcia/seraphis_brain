# seraphis_api.py
# Lightweight API around the proven scripts so Kilo (or any app) can call Seraphis.
# Pure-ASCII printing; uses subprocess to reuse your validated scripts as-is.

import subprocess
import sys
import shlex
from pathlib import Path

HERE = Path(__file__).parent

SYNTH = str(HERE / "synthesize_memory_response.py")
SCORE = str(HERE / "score_memory_entry.py")
REASON = str(HERE / "reasoning_module.py")
RETRIEVE = str(HERE / "retrieve_relevant_memory.py")

def _run(cmd: str) -> int:
    print(f"[RUN] {cmd}")
    proc = subprocess.run(shlex.split(cmd), stdout=sys.stdout, stderr=sys.stderr)
    return proc.returncode

# ---------- Public API ----------

def learn(query: str,
          category: str = "system_planning",
          score: float = 8.5,
          chunk_id: int = 2) -> None:
    """Synthesize -> score/store -> sanity reason."""
    rc = _run(f'python "{SYNTH}" --query "{query}"')
    if rc != 0:
        raise RuntimeError("synthesize_memory_response failed")

    rc = _run(
        f'python "{SCORE}" '
        f'--query "{query}" --category {category} --score {score:.1f} --chunk-id {chunk_id}'
    )
    if rc != 0:
        raise RuntimeError("score_memory_entry failed")

    # Not fatal if fails, but print output for visibility
    _run(f'python "{REASON}"')
    print("[OK] learn() complete.")

def retrieve(query: str, top_k: int = 5) -> None:
    """Retrieve relevant memory for a query."""
    cmd = f'python "{RETRIEVE}" --query "{query}" --top-k {top_k}'
    rc = _run(cmd)
    if rc != 0:
        raise RuntimeError("retrieve_relevant_memory failed")

def reason() -> None:
    """Run the reasoner alone."""
    rc = _run(f'python "{REASON}"')
    if rc != 0:
        raise RuntimeError("reasoning_module failed")

# ---------- CLI ----------

def _cli():
    # Minimal arg parsing without extra deps
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print(
            "Usage:\n"
            "  python seraphis_api.py learn --query \"...\" [--category X] [--score 8.5] [--chunk-id 2]\n"
            "  python seraphis_api.py retrieve --query \"...\" [--top-k 5]\n"
            "  python seraphis_api.py reason\n"
        )
        sys.exit(0)

    mode = args[0]
    # defaults
    query = None
    category = "system_planning"
    score = 8.5
    chunk_id = 2
    top_k = 5

    i = 1
    while i < len(args):
        if args[i] == "--query" and i + 1 < len(args):
            query = args[i + 1]; i += 2
        elif args[i] == "--category" and i + 1 < len(args):
            category = args[i + 1]; i += 2
        elif args[i] == "--score" and i + 1 < len(args):
            score = float(args[i + 1]); i += 2
        elif args[i] == "--chunk-id" and i + 1 < len(args):
            chunk_id = int(args[i + 1]); i += 2
        elif args[i] == "--top-k" and i + 1 < len(args):
            top_k = int(args[i + 1]); i += 2
        else:
            i += 1

    if mode == "learn":
        if not query: raise SystemExit("--query required for learn")
        learn(query, category, score, chunk_id)
    elif mode == "retrieve":
        if not query: raise SystemExit("--query required for retrieve")
        retrieve(query, top_k)
    elif mode == "reason":
        reason()
    else:
        raise SystemExit(f"Unknown command: {mode}")

if __name__ == "__main__":
    _cli()
