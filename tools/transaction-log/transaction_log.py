#!/usr/bin/env python3
"""transaction-log.md helpers — generic, project-agnostic (harmonic-forge#40).

Extracted from HRSE2's implementation (scripts/transaction_log.py,
scripts/git_commit.py) after it proved itself live across the hrse#224
cutover epic. Two differences from a bespoke per-project copy:
  - project root is a CLI flag / constructor argument, never hardcoded.
  - usable both as a library (import transaction_log) and as a CLI, so a
    project's own mise task can shell out to it directly.

See README.md in this directory for the pattern this implements and why.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

START_MARKER = "<!-- TRANSACTION_LOG_START -->"
END_MARKER = "<!-- TRANSACTION_LOG_END -->"

_FILLER_RE = re.compile(
    r"^[\s\-*]*("
    r"n/?a|none|no (other |additional |further )?(significant |notable )?changes( detected| made)?|"
    r"nothing else changed"
    r")[\s.():,]*("
    r"n/?a|no (other |additional |further )?(significant |notable )?changes( detected| made)?|"
    r"nothing else changed"
    r")?[\s.():,]*$",
    re.IGNORECASE,
)


def _strip_filler_bullets(summary: str) -> str:
    """Drop zero-information bullets (e.g. '- N/A (no other significant changes)')."""
    kept = [line for line in summary.splitlines() if not _FILLER_RE.match(line)]
    return "\n".join(kept).strip()


def newest_entry_header(log_path: Path) -> str | None:
    """Return the header line (e.g. '## msg') of the newest log entry, or
    None if the file/markers are missing or the log is empty. Never raises.

    Used to detect a duplicate append after a failed-commit retry: if a
    prior invocation appended an entry but the commit itself then failed
    (e.g. a hook rejection), a naive re-run would append a second,
    duplicate entry before the retried commit succeeds.
    """
    try:
        raw = log_path.read_text()
    except FileNotFoundError:
        return None
    if START_MARKER not in raw or END_MARKER not in raw:
        return None
    between = raw.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    for line in between.splitlines():
        if line.startswith("## "):
            return line
    return None


def append_log_entry(log_path: Path, commit_msg: str, summary: str) -> bool:
    """Insert a new entry immediately after START_MARKER (newest-first).

    The header is the commit message itself, not a commit hash — a hash
    can't be known before the commit exists, but the message can, which is
    what lets the entry be written and staged in the *same* commit as the
    change it describes (see README.md — this is the fix for the two-phase-
    commit bug the original hrse_manager.py had).

    Returns True on success; prints a warning and False if the file or
    markers are missing. Never raises.
    """
    try:
        raw = log_path.read_text()
    except FileNotFoundError:
        print(f"[WARN] {log_path} not found; skipping append", file=sys.stderr)
        return False

    if START_MARKER not in raw or END_MARKER not in raw:
        print(f"[WARN] {log_path} markers missing; skipping append", file=sys.stderr)
        return False

    summary = _strip_filler_bullets(summary) or "- No substantive changes in this commit"
    entry = f"\n## {commit_msg}\n{summary}\n"
    new_raw = raw.replace(START_MARKER, f"{START_MARKER}{entry}", 1)
    try:
        log_path.write_text(new_raw)
    except Exception as exc:
        print(f"[WARN] Could not write {log_path}: {exc}", file=sys.stderr)
        return False
    return True


def clear_log(log_path: Path) -> str:
    """Clear all entries between the markers (call on version bumps).

    Prior content needs no separate archive — the file is committed before
    each clear, so `git log -p <log_path>` replays all of it.

    Returns one of "cleared", "empty", or "failed". Never raises.
    """
    try:
        raw = log_path.read_text()
    except FileNotFoundError:
        print(f"[WARN] {log_path} not found; skipping clear", file=sys.stderr)
        return "failed"

    if START_MARKER not in raw or END_MARKER not in raw:
        print(f"[WARN] {log_path} markers missing; skipping clear", file=sys.stderr)
        return "failed"

    between = raw.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    if not between.strip():
        return "empty"

    pre = raw.split(START_MARKER, 1)[0]
    post = raw.split(END_MARKER, 1)[1]
    try:
        log_path.write_text(f"{pre}{START_MARKER}\n{END_MARKER}{post}")
    except Exception as exc:
        print(f"[WARN] Could not clear {log_path}: {exc}", file=sys.stderr)
        return "failed"
    return "cleared"


def _default_log_path(project_root: Path) -> Path:
    return project_root / "transaction-log.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="transaction-log.md helpers")
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Project root (default: cwd)")
    parser.add_argument("--log-path", type=Path, default=None, help="Override the log file path (default: <project-root>/transaction-log.md)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_append = sub.add_parser("append", help="Append a new entry")
    p_append.add_argument("--message", required=True, help="Entry header (typically the commit message)")
    p_append.add_argument("--summary", required=True, help="Entry body (typically a diffstat summary)")

    sub.add_parser("clear", help="Clear all entries (call on version bumps)")
    sub.add_parser("newest-header", help="Print the newest entry's header line, or nothing if empty/missing")

    args = parser.parse_args()
    log_path = args.log_path or _default_log_path(args.project_root)

    if args.command == "append":
        ok = append_log_entry(log_path, args.message, args.summary)
        return 0 if ok else 1
    if args.command == "clear":
        result = clear_log(log_path)
        print(result)
        return 0 if result != "failed" else 1
    if args.command == "newest-header":
        header = newest_entry_header(log_path)
        if header:
            print(header)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
