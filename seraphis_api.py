# seraphis_api.py
# Thin CLI that forwards to the underlying scripts with proper args.
import argparse
import os
import sys
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))

def runpy(script, args):
    return subprocess.run([sys.executable, os.path.join(HERE, script)] + args)

def do_learn(query, category, score, chunk_id):
    # Reuse your one-shot learn loop so all guards stay the same
    return runpy("auto_write_loop.py", [
        "--query", query,
        "--category", category,
        "--score", f"{score}",
        "--chunk-id", f"{chunk_id}",
    ])

def do_retrieve(query, top_k):
    # IMPORTANT: pass --query and --top-k through to the retriever
    return runpy("retrieve_relevant_memory.py", [
        "--query", query,
        "--top-k", f"{top_k}",
    ])

def do_reason():
    return runpy("reasoning_module.py", [])

def main():
    p = argparse.ArgumentParser(description="Seraphis API shim")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_learn = sub.add_parser("learn")
    p_learn.add_argument("--query", required=True)
    p_learn.add_argument("--category", default="system_planning")
    p_learn.add_argument("--score", type=float, default=8.5)
    p_learn.add_argument("--chunk-id", type=int, default=2)

    p_ret = sub.add_parser("retrieve")
    p_ret.add_argument("--query", required=True)
    p_ret.add_argument("--top-k", type=int, default=5)

    sub.add_parser("reason")

    args = p.parse_args()
    if args.cmd == "learn":
        r = do_learn(args.query, args.category, args.score, args.chunk_id)
    elif args.cmd == "retrieve":
        r = do_retrieve(args.query, args["top_k"] if isinstance(args, dict) else args.top_k)
    else:
        r = do_reason()

    sys.exit(r.returncode)

if __name__ == "__main__":
    main()
