# brain_cli.py
# Seraphis brain CLI:
#   Default: ask -> synthesize -> score -> reason
#   --learn:  run one auto-learn cycle via auto_write_loop.py

import argparse
import subprocess
import sys
import shlex
import os

# Paths (relative to this file). If you run from another dir, we stay safe.
HERE = "."
SYNTH = f"{HERE}/synthesize_memory_response.py"
SCORE = f"{HERE}/score_memory_entry.py"
REASON = f"{HERE}/reasoning_module.py"
AUTO   = f"{HERE}/auto_write_loop.py"

def run(cmd: str):
    """Run a command, stream output, and exit on non-zero."""
    print(f"\n[RUN] {cmd}")
    # Capture text but avoid emojis; our other scripts print ASCII only now.
    result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr)
        sys.exit(result.returncode)

def main():
    p = argparse.ArgumentParser(description="Seraphis brain: ask, store, reason (or auto-learn)")
    p.add_argument("--learn", action="store_true",
                   help="Run one auto-learn cycle (delegates to auto_write_loop.py)")
    p.add_argument("--query", required=True, help="Your question/prompt")
    p.add_argument("--category", default="system_self_knowledge",
                   help="Memory category for this entry")
    p.add_argument("--score", type=float, default=9.0,
                   help="Priority/importance score (0.0–10.0)")
    p.add_argument("--chunk-id", type=int, default=1,
                   help="Chunk id for this synthetic entry (logical slot)")
    args = p.parse_args()

    if args.learn:
        # Delegate to the orchestrator (auto_write_loop.py)
        if not os.path.exists(AUTO):
            print("auto_write_loop.py not found. Create it in the same folder as brain_cli.py.")
            sys.exit(2)
        cmd = (
            f'python {AUTO} '
            f'--query "{args.query}" '
            f'--category {args.category} '
            f'--score {args.score:.1f} '
            f'--chunk-id {args.chunk_id}'
        )
        run(cmd)
        print("\n[OK] Learn cycle finished.")
        return

    # Default path: 1) synthesize -> 2) score/store -> 3) reason
    run(f'python {SYNTH} --query "{args.query}"')
    run(
        f'python {SCORE} '
        f'--query "{args.query}" '
        f'--category {args.category} '
        f'--score {args.score:.1f} '
        f'--chunk-id {args.chunk_id}'
    )
    run(f"python {REASON}")
    print("\n[OK] Ask->Store->Reason cycle finished.")

if __name__ == "__main__":
    main()
