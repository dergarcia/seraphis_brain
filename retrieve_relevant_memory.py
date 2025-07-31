import os
import re
import sys
import json
import argparse
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

# ---------- Setup ----------
load_dotenv()
client = OpenAI()

MEMORY_FOLDER = "Memory"
MEMORY_FILES = [
    "synthesized_memory.md",
    "seraphis_memory.md",
    "seraphis_knowledge.md",
    "normalized_inputs.md",
    "compressed_memory.md",
]
MEMORY_PATHS = [os.path.join(MEMORY_FOLDER, f) for f in MEMORY_FILES]


# ---------- Helpers ----------
def load_chunks_from_md(filepath: str) -> List[Dict[str, str]]:
    """Extract (Query, Answer) chunks from a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Matches **User Query:** or **Q:** followed by **Answer:** or **A:**
    pattern = r"\*\*(?:User Query|Q):\*\*(.*?)\n.*?\*\*(?:Answer|A):\*\*(.*?)(?=\n\*\*|$)"
    chunks = re.findall(pattern, content, re.DOTALL)
    return [
        {"file": os.path.basename(filepath), "query": q.strip(), "answer": a.strip()}
        for q, a in chunks
        if q.strip() and a.strip()
    ]


def gather_memory() -> List[Dict[str, str]]:
    """Load all available memory chunks from the configured files."""
    all_chunks: List[Dict[str, str]] = []
    for path in MEMORY_PATHS:
        if os.path.exists(path):
            try:
                all_chunks.extend(load_chunks_from_md(path))
            except Exception:
                # Skip unreadable files; continue with what we have
                pass
    return all_chunks


def synthesize_answer(query: str, chunks: List[Dict[str, str]]) -> str:
    """Ask OpenAI to synthesize an answer from memory chunks."""
    if not chunks:
        context = "(no memory entries found)"
    else:
        context = "\n\n".join(
            f"Query: {c['query']}\nAnswer: {c['answer']}" for c in chunks
        )

    prompt = (
        "You are Seraphis. Based on the following memory entries, synthesize a concise, "
        "accurate response to the user query.\n\n"
        f"Memory Entries:\n{context}\n\n"
        f"User Query: {query}\n\n"
        "Respond with the most accurate and insightful answer using the memory above."
    )

    # Keep current API style for compatibility
    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return resp.choices[0].message.content.strip()


def save_to_synthesized(query: str, answer: str) -> None:
    os.makedirs(MEMORY_FOLDER, exist_ok=True)
    filepath = os.path.join(MEMORY_FOLDER, "synthesized_memory.md")
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n\n**User Query:** {query}\n\n**Answer:** {answer}\n\n---")


def safe_print(label: str, text: str) -> None:
    """Print text without breaking on cp1252 consoles (ASCII label, UTF‑8 body)."""
    try:
        print(label + text)
    except UnicodeEncodeError:
        # Fallback: write UTF-8 bytes directly
        sys.stdout.buffer.write((label + text).encode("utf-8", errors="replace"))
        sys.stdout.buffer.write(b"\n")


# ---------- CLI ----------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Retrieve/synthesize an answer from Seraphis memory."
    )
    p.add_argument("--query", help="The question to answer")
    p.add_argument("--top-k", type=int, default=5, help="Max memory entries to use")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    # Decide how to get the query:
    # - If provided on CLI, use it.
    # - If interactive TTY, prompt.
    # - Otherwise, fail fast (non-interactive run expects --query).
    query = args.query
    if not query:
        if sys.stdin.isatty():
            query = input("Enter your query: ")
        else:
            print("ERROR: --query is required for non-interactive use.", file=sys.stderr)
            return 2

    chunks = gather_memory()
    if args.top_k > 0 and len(chunks) > args.top_k:
        chunks = chunks[: args.top_k]

    answer = synthesize_answer(query, chunks)

    # ASCII-only labels, UTF-8 safe content
    safe_print("\nSynthesized Answer:\n", answer)

    save_to_synthesized(query, answer)
    print("\nOK: Entry saved to Memory/synthesized_memory.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
