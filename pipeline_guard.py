# pipeline_guard.py
# One-button run: validate -> (auto-repair if needed) -> synthesize -> score -> reason.
# Standardizes on size-based chunking with chunk_size=350.

import argparse, json, os, subprocess, sys
from datetime import datetime

DEF_INPUT = "seraphis_final_core.md"
DEF_TAGGED = "tagged_memory.json"
DEF_CHUNK_SIZE = 350

def run(cmd: str):
    print(f"\n[RUN] {cmd}")
    p = subprocess.run(cmd, shell=True)
    if p.returncode != 0:
        sys.exit(p.returncode)

def run_capture(cmd: str) -> str:
    print(f"\n[RUN] {cmd}")
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.stdout:
        print(p.stdout)
    if p.returncode != 0:
        if p.stderr:
            print(p.stderr)
        sys.exit(p.returncode)
    return p.stdout or ""

def parse_validator_summary(console_text: str) -> dict:
    report_path = None
    for line in console_text.splitlines():
        if "Detailed report:" in line:
            report_path = line.split("Detailed report:", 1)[1].strip()
            break
    if not report_path or not os.path.exists(report_path):
        return {}
    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("summary", {})

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=DEF_INPUT)
    ap.add_argument("--tagged", default=DEF_TAGGED)
    ap.add_argument("--chunk-size", type=int, default=DEF_CHUNK_SIZE)
    ap.add_argument("--query", default="What are the top priorities in Seraphis' current build?")
    ap.add_argument("--category", default="system_self_knowledge")
    ap.add_argument("--score", type=float, default=9.0)
    ap.add_argument("--chunk-id", type=int, default=1)
    args = ap.parse_args()

    # 0) Validate
    out = run_capture(
        f'python coherence_validator.py --input "{args.input}" --tagged "{args.tagged}" --chunk-size {args.chunk_size}'
    )
    summary = parse_validator_summary(out)
    issues = sum(summary.get(k, 0) for k in ("empty","nocontent","nocategory","badscore","badchunk"))
    if issues > 0:
        print(f"[GUARD] Found {issues} issues -> auto-repairing…")
        repaired = "repaired_tagged_memory.json"
        run(
            f'python repair_tagged_memory.py --input "{args.input}" --tagged "{args.tagged}" --out "{repaired}" --chunk-size {args.chunk_size} --drop-empty'
        )
        if os.path.exists(repaired):
            os.replace(repaired, args.tagged)
        out2 = run_capture(
            f'python coherence_validator.py --input "{args.input}" --tagged "{args.tagged}" --chunk-size {args.chunk_size}'
        )
        summary2 = parse_validator_summary(out2)
        issues2 = sum(summary2.get(k, 0) for k in ("empty","nocontent","nocategory","badscore","badchunk"))
        if issues2 > 0:
            print("[GUARD] Repair did not clear all issues.")
            sys.exit(2)
        print("[GUARD] Memory is coherent after repair.")

    # 1) Synthesize (non-interactive)
    run(f'python synthesize_memory_response.py --query "{args.query}"')

    # 2) Score (non-interactive; chunk-id explicitly passed)
    run(f'python score_memory_entry.py --query "{args.query}" --category {args.category} --score {args.score} --chunk-id {args.chunk_id}')

    # 3) Reason
    run("python reasoning_module.py")

    print("\n[GUARD] Pipeline completed successfully with standardized chunking and coherence checks.")

if __name__ == "__main__":
    main()
