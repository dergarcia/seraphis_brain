# audit_sdk_calls.py — stable version (no lookbehinds)
import argparse, json, re
from pathlib import Path

# Detect a real assignment to openai.api_key at line level (ignore comment lines)
ASSIGN_API_KEY = re.compile(r"^[ \t]*(?!#)openai\s*\.\s*api_key\s*=", re.ASCII)

# Simple patterns (no lookbehind). We'll filter out quoted occurrences manually.
OTHER_PATTERNS = {
    "ChatCompletion.create": re.compile(r"\bopenai\.ChatCompletion\.create\(", re.ASCII),
    "Completion.create": re.compile(r"\bopenai\.Completion\.create\(", re.ASCII),
    "Embedding.create": re.compile(r"\bopenai\.Embedding\.create\(", re.ASCII),
    "Image.create": re.compile(r"\bopenai\.Image\.create\(", re.ASCII),
    "Image.create_edit": re.compile(r"\bopenai\.Image\.create_edit\(", re.ASCII),
    "Audio.transcriptions.create (old)": re.compile(r"\bopenai\.Audio\.transcriptions\.create\(", re.ASCII),
    "responses.beta": re.compile(r"\bclient\.responses\.beta\.", re.ASCII),
    "deprecated_chat_model_param": re.compile(r"model\s*=\s*['\"]gpt-3\.5[^'\"]*['\"]", re.ASCII),
}

RECOMMENDATION = {
    "ChatCompletion.create": "Use: from openai import OpenAI; client = OpenAI(); client.chat.completions.create(model='gpt-4o-mini', messages=[...])",
    "Completion.create": "Use chat.completions or responses API instead.",
    "Embedding.create": "Use: client.embeddings.create(model='text-embedding-3-large', input=...)",
    "Image.create": "Use: client.images.generate(model='gpt-image-1', prompt=...)",
    "Image.create_edit": "Use: client.images.edits(...) or images.generate with image[] params.",
    "Audio.transcriptions.create (old)": "Use: client.audio.transcriptions.create(model='whisper-1', file=...)",
    "clientless openai.api_key": "Use: client = OpenAI() with OPENAI_API_KEY in .env (no global openai.api_key=).",
    "responses_beta": "Prefer stable endpoints (chat.completions, or responses if GA).",
    "deprecated_chat_model_param": "Upgrade to current models (e.g., gpt-4o-mini).",
}

def line_is_in_string_context(line: str, idx: int) -> bool:
    """Crude check: odd count of quotes before index => inside quotes."""
    prefix = line[:idx]
    return (prefix.count("'") % 2 == 1) or (prefix.count('"') % 2 == 1)

def scan_file(path: Path):
    # Skip this file
    if path.name == Path(__file__).name:
        return []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    findings = []
    for i, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue

        # api_key assignment
        m = ASSIGN_API_KEY.search(line)
        if m and not line_is_in_string_context(line, m.start()):
            findings.append({"pattern":"clientless openai.api_key","line":i,"excerpt":line.strip()})

        # other patterns
        for name, rx in OTHER_PATTERNS.items():
            m2 = rx.search(line)
            if not m2:
                continue
            if line_is_in_string_context(line, m2.start()):
                continue
            if line.lstrip().startswith("#"):
                continue
            findings.append({"pattern":name,"line":i,"excerpt":line.strip()})
    return findings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Root directory to scan")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    results = []
    for p in root.rglob("*.py"):
        if any(seg in {".venv","venv","__pycache__"} for seg in p.parts):
            continue
        f = scan_file(p)
        if f:
            results.append({"file": str(p), "findings": f})

    print(json.dumps({"summary":{"files_with_findings":len(results)},
                      "results":results,
                      "recommendations":RECOMMENDATION}, indent=2))

if __name__ == "__main__":
    main()
