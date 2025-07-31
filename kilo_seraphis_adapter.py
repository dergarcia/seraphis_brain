# kilo_seraphis_adapter.py
"""
Thin adapter that calls the Seraphis Brain CLI (seraphis_api.py) in the brain repo.
This avoids Python import path headaches between the two folders and is very portable.

Usage (from Seraphis/Tools folder):
  python kilo_seraphis_adapter.py learn --query "..." [--category X] [--score 8.5] [--chunk-id 2]
  python kilo_seraphis_adapter.py retrieve --query "..." [--top-k 5]
  python kilo_seraphis_adapter.py reason
"""

import argparse
import subprocess
import sys
import shlex
from pathlib import Path

# >>> EDIT THIS if your brain path changes <<<
BRAIN_DIR = Path(r"C:\Users\degarcia\Kilo\tools\seraphis_brain")
API = BRAIN_DIR / "seraphis_api.py"

def run(cmd: str):
    """Run a command with cwd=brain folder; stream output live."""
    print(f"[RUN] {cmd}")
    proc = subprocess.run(
        shlex.split(cmd),
        cwd=str(BRAIN_DIR),
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=False,
    )
    return proc.returncode

def learn(query: str, category: str = "system_planning", score: float = 8.5, chunk_id: int = 2) -> int:
    cmd = f'python "{API}" learn --query "{query}" --category {category} --score {score:.1f} --chunk-id {chunk_id}'
    return run(cmd)

def retrieve(query: str, top_k: int = 5) -> int:
    cmd = f'python "{API}" retrieve --query "{query}" --top-k {top_k}'
    return run(cmd)

def reason() -> int:
    cmd = f'python "{API}" reason'
    return run(cmd)

def main():
    p = argparse.ArgumentParser(description="Kilo adapter → Seraphis Brain")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_learn = sub.add_parser("learn")
    p_learn.add_argument("--query", required=True)
    p_learn.add_argument("--category", default="system_planning")
    p_learn.add_argument("--score", type=float, default=8.5)
    p_learn.add_argument("--chunk-id", type=int, default=2)

    p_retrieve = sub.add_parser("retrieve")
    p_retrieve.add_argument("--query", required=True)
    p_retrieve.add_argument("--top-k", type=int, default=5)

    sub.add_parser("reason")

    args = p.parse_args()
    if args.cmd == "learn":
        sys.exit(learn(args.query, args.category, args.score, args.chunk_id))
    if args.cmd == "retrieve":
        sys.exit(retrieve(args.query, args.top_k))
    if args.cmd == "reason":
        sys.exit(reason())

if __name__ == "__main__":
    main()
