import os
import json
import re
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI

# === Load API Key ===
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# === File Paths ===
INPUT_FILE = "seraphis_final_core.md"
OUTPUT_FILE = "tagged_memory.json"

# Default model - can be overridden with TAG_MODEL environment variable
DEFAULT_MODEL = "gpt-4"

# ---------- Helpers ----------

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    brace_count = 0
    start_idx = -1
    for i, char in enumerate(text):
        if char == "{":
            if start_idx == -1:
                start_idx = i
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0 and start_idx != -1:
                json_str = text[start_idx : i + 1]
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    start_idx = -1
                    continue
    return None


def load_existing_memory() -> Dict[int, Dict[str, Any]]:
    memory_file = Path(OUTPUT_FILE)
    if not memory_file.exists():
        return {}
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return {item.get("chunkId", i + 1): item for i, item in enumerate(data)}
        elif isinstance(data, dict):
            return data
        else:
            return {}
    except (json.JSONDecodeError, IOError):
        return {}


def save_memory(memory_data: Dict[int, Dict[str, Any]]) -> None:
    memory_list = [memory_data[chunk_id] for chunk_id in sorted(memory_data.keys())]
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(memory_list, f, ensure_ascii=False, indent=2)


def split_by_size(text: str, approx_size: int = 1200) -> List[str]:
    """Greedy split by approx char size, respecting word boundaries."""
    text = text.strip()
    if not text:
        return []
    words = text.split()
    chunks: List[str] = []
    cur: List[str] = []
    cur_len = 0
    for w in words:
        wl = len(w) + 1
        if cur and cur_len + wl > approx_size:
            chunks.append(" ".join(cur).strip())
            cur = [w]
            cur_len = wl
        else:
            cur.append(w)
            cur_len += wl
    if cur:
        chunks.append(" ".join(cur).strip())
    return [c for c in chunks if c]


def split_by_headings_or_dividers(text: str) -> List[str]:
    """Try semantic splits first (headings, divider lines, blank‑line blocks)."""
    t = text.strip()
    if not t:
        return []

    # Headings like "### ..." (allow preceding blank lines)
    parts = re.split(r"\n{1,}(?=### )", t)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    # Divider lines (--- or *** on their own line)
    parts = re.split(r"\n\s*[-*]{3,}\s*\n", t)
    if len(parts) > 1:
        return [p.strip() for p in parts if p.strip()]

    # Paragraph blocks (double newline)
    parts = [p.strip() for p in t.split("\n\n") if p.strip()]
    return parts


def build_chunks(content: str, force_split: str = "auto", chunk_size: int = 1200, min_chunks_for_auto: int = 5) -> List[str]:
    """
    Unified chunk builder used for ALL paths (list, only, full).
    - force_split='heading' → semantic only
    - force_split='size'    → size-based only
    - force_split='auto'    → semantic; if too few chunks, fall back to size
    """
    content = content.strip()
    if not content:
        return []

    if force_split == "heading":
        return split_by_headings_or_dividers(content)

    if force_split == "size":
        return split_by_size(content, approx_size=chunk_size)

    # auto: try semantic first
    chunks = split_by_headings_or_dividers(content)
    if len(chunks) < min_chunks_for_auto:
        # fall back to size-based to ensure enough granularity
        chunks = split_by_size(content, approx_size=chunk_size)
    return chunks


def tag_chunk_with_ai(chunk_content: str, model: str, strict_mode: bool = False) -> Optional[Dict[str, Any]]:
    if strict_mode:
        system_message = (
            "Return **only** JSON, no preface or trailing text. "
            "The JSON must contain 'tags' (array), 'category' (string), and 'priorityScore' (float 0-1)."
        )
        temperature = 0.0
        max_tokens = 500
    else:
        system_message = (
            "Analyze the following text chunk and return a JSON object with "
            "'tags' (array of relevant keywords), 'category' (single category string), and "
            "'priorityScore' (float from 0 to 1 indicating importance)."
        )
        temperature = 0.3
        max_tokens = 1000

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Text chunk to analyze:\n\n{chunk_content}"},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        txt = resp.choices[0].message.content
        return extract_json_from_text(txt)
    except Exception as e:
        print(f"API call failed: {e}")
        return None


def process_chunk(chunk_id: int, chunk_content: str, model: str) -> Optional[Dict[str, Any]]:
    result = tag_chunk_with_ai(chunk_content, model, strict_mode=False)
    if result is None:
        result = tag_chunk_with_ai(chunk_content, model, strict_mode=True)
    if result is None:
        return None

    required = ["tags", "category", "priorityScore"]
    if not all(k in result for k in required):
        return None
    if not isinstance(result["tags"], list):
        return None
    if not isinstance(result["category"], str):
        return None
    if not isinstance(result["priorityScore"], (int, float)):
        return None

    return {
        "chunkId": chunk_id,
        "chunk": chunk_content,
        "tags": result["tags"],
        "category": result["category"],
        "priorityScore": float(result["priorityScore"]),
    }


def find_memory_file() -> Optional[Path]:
    cur = Path(".")
    default_file = cur / INPUT_FILE
    if default_file.exists():
        return default_file
    patterns = ["memory.txt", "source.txt", "*.md", "*.txt"]
    for pattern in patterns:
        if pattern.startswith("*"):
            files = list(cur.glob(pattern))
            if files:
                return files[0]
        else:
            p = cur / pattern
            if p.exists():
                return p
    return None

# ---------- Main ----------

def main():
    parser = argparse.ArgumentParser(description="Tag memory chunks for Seraphis AI")
    parser.add_argument("--only", nargs="+", type=int, metavar="CHUNK_ID",
                        help="Only process specified chunk IDs (1-based)")
    parser.add_argument("--input", type=str, help=f"Input memory file (default: {INPUT_FILE} or auto-detected)")
    parser.add_argument("--list", action="store_true", help="List total chunks and valid IDs, then exit")
    parser.add_argument("--force-split", choices=["auto", "heading", "size"], default="auto",
                        help="Chunking method: auto (default), heading (semantic only), size (fixed-size only)")
    parser.add_argument("--chunk-size", type=int, default=1200,
                        help="Approx chars per chunk when using size-based splitting (default 1200)")
    args = parser.parse_args()

    model = os.getenv("TAG_MODEL", DEFAULT_MODEL)

    # Resolve input file
    input_path = Path(args.input) if args.input else find_memory_file()
    if not input_path or not input_path.exists():
        print(f"✖ No memory input file found (looking for {INPUT_FILE} or similar)")
        return 1

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()
    except IOError as e:
        print(f"✖ Failed to read {input_path}: {e}")
        return 1

    # Build chunks ONCE for all paths
    all_chunks = build_chunks(
        content,
        force_split=args.force_split,
        chunk_size=args.chunk_size,
        min_chunks_for_auto=5,
    )
    total_chunks = len(all_chunks)
    if total_chunks == 0:
        print("✖ No chunks found in input file")
        return 1

    if args.list:
        print(f"Total chunks detected: {total_chunks}")
        print(f"Valid chunk IDs: 1-{total_chunks}")
        return 0

    print(f"Total chunks detected: {total_chunks}")

    existing = load_existing_memory()

    # Determine which to process
    if args.only:
        bad = [cid for cid in args.only if cid < 1 or cid > total_chunks]
        if bad:
            print(f"✖ Chunk ID(s) {bad} out of range 1-{total_chunks}")
            return 1
        indices = [cid - 1 for cid in args.only]
        process_list = [(i, all_chunks[i], i + 1) for i in indices]
    else:
        process_list = [(i, all_chunks[i], i + 1) for i in range(total_chunks)]

    print(f"Processing {len(process_list)} chunk(s) with model {model}")

    succeeded = 0
    failed = 0
    for idx, chunk_content, original_chunk_id in process_list:
        result = process_chunk(original_chunk_id, chunk_content, model)
        if result:
            existing[original_chunk_id] = result
            print(f"✔ Chunk {original_chunk_id}: tagged successfully")
            succeeded += 1
        else:
            print(f"✖ Chunk {original_chunk_id}: failed to tag")
            failed += 1

    try:
        save_memory(existing)
        print(f"\nSummary: Processed {len(process_list)}, Succeeded {succeeded}, Failed {failed}")
    except IOError as e:
        print(f"✖ Failed to save {OUTPUT_FILE}: {e}")
        return 1

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
