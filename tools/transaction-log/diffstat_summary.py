#!/usr/bin/env python3
"""Deterministic, LLM-free delta summary from a git diffstat (ai-platform#40).

git diff --stat is the only summarization path — no LLM call, no provider
abstraction. Evidence for dropping the LLM path entirely (not just making
it optional): HRSE2's real transaction-log.md history showed a ~25% hard
failure rate on a local 2B model, each failure silently falling back to
this exact diffstat path anyway. See ai-platform ADR (referenced in this
tool's own issue) for the full decision record.

Guards preserved from the original hrse_manager.py implementation:
  - empty diff -> a single explanatory bullet, never a blank summary.
  - markdown-only diff -> a distinct "[docs]" bullet, since a doc-only
    commit is worth flagging as such at a glance in the log.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _git(project_root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=str(project_root)
    ).stdout


def diffstat_summary(project_root: Path, cached: bool = True, max_lines: int = 4) -> str:
    """Return a markdown bullet-list summary of the current diff.

    `cached=True` (default) summarizes the staged diff (`git diff --cached`)
    — the right choice when called *before* a commit, so the summary can be
    computed and appended to the log in the same commit as the change it
    describes. `cached=False` summarizes the working-tree diff instead.
    """
    diff_flag = ["--cached"] if cached else []

    changed_files = [
        f for f in _git(project_root, "diff", *diff_flag, "--name-only").strip().splitlines() if f.strip()
    ]
    if not changed_files:
        return "- No changes detected"

    if all(f.endswith(".md") for f in changed_files):
        return "- [docs] Markdown-only commit — no code changes. Files: " + ", ".join(changed_files)

    stat_output = _git(project_root, "diff", *diff_flag, "--stat").strip()
    lines = [f"- {line.strip()}" for line in stat_output.splitlines()[-max_lines:] if line.strip()]
    return "\n".join(lines) if lines else "- (no diffstat available)"


def main() -> int:
    parser = argparse.ArgumentParser(description="Print a deterministic diffstat-based delta summary")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--unstaged", action="store_true", help="Summarize the working-tree diff instead of the staged diff")
    parser.add_argument("--max-lines", type=int, default=4, help="Max diffstat lines to include (default: 4)")
    args = parser.parse_args()

    print(diffstat_summary(args.project_root, cached=not args.unstaged, max_lines=args.max_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
