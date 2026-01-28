#!/usr/bin/env python3

import argparse
from pathlib import Path

from claude_backend import ClaudeBackend


SYSTEM_PROMPT = """You are Clawdbot — an elite software co-engineer.

Rules:
- Be precise and technical.
- If modifying files: output FULL replacement files.
- Prefix each file with: RM <filename>
- Never output partial diffs.
- Never add commentary outside RM blocks unless explicitly asked.
"""


def collect_repo_context(root: Path, max_files: int = 25) -> str:
    files = []
    for path in root.rglob("*.py"):
        if "__pycache__" in str(path) or ".venv" in str(path):
            continue
        files.append(path)
        if len(files) >= max_files:
            break

    context = []
    for path in files:
        try:
            code = path.read_text()
            context.append(f"\n# FILE: {path}\n{code}\n")
        except Exception:
            pass

    return "\n".join(context)


def main():
    parser = argparse.ArgumentParser(description="Clawdbot — terminal AI co-engineer")
    parser.add_argument("prompt", help="Instruction for Clawdbot")
    parser.add_argument("--repo", default=".", help="Repo root for context")
    parser.add_argument("--model", default="claude-sonnet-4-20250514", help="Claude model")

    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    context = collect_repo_context(repo_root)

    user_prompt = f"""
INSTRUCTION:
{args.prompt}

REPO CONTEXT:
{context}
"""

    backend = ClaudeBackend(model=args.model, max_tokens=2500)
    response = backend.judge(SYSTEM_PROMPT, user_prompt)

    print("\n=== CLAWDBOT RESPONSE ===\n")
    print(response.strip())
    print("\n=== END ===\n")


if __name__ == "__main__":
    main()
