import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).parent
adapter = str(ROOT / "kilo_seraphis_adapter.py")
reflected = ROOT / "artifacts" / "reflected_memory.json"

def run(*args):
    print("[RUN]", " ".join(args))
    res = subprocess.run([sys.executable, *args], cwd=str(ROOT))
    if res.returncode != 0:
        raise SystemExit(res.returncode)

def main():
    if not reflected.exists():
        print(f"No reflected file at {reflected}")
        return
    data = json.loads(reflected.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit("reflected_memory.json must be a list of items")

    for idx, item in enumerate(data, start=1):
        q = str(item.get("query", "")).strip()
        if not q:
            continue
        cat   = str(item.get("category", "reflected"))
        score = str(item.get("score", 7.0))
        chunk = str(item.get("chunk_id", idx))
        run(adapter, "learn", "--query", q, "--category", cat, "--score", score, "--chunk-id", chunk)

    print(f"Loaded {len(data)} reflected entries.")

if __name__ == "__main__":
    main()
