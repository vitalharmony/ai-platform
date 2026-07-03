#!/usr/bin/env python3
"""
ai-platform bootstrapper.

Wires a project's .claude/rules/ into this platform repo's universal rule
files via symlinks, so every project always reads the current platform
rules rather than a stale copy.

Usage:
    python3 ~/ai-platform/sync_rules.py --project /path/to/project
    python3 ~/ai-platform/sync_rules.py --pull
"""

import argparse
import subprocess
import sys
from pathlib import Path

PLATFORM_ROOT = Path(__file__).resolve().parent
RULES_DIR = PLATFORM_ROOT / "rules"

# Rule files that are universal across every project's stack.
UNIVERSAL_RULE_FILES = [
    "backend-python.md",
    "frontend-typescript.md",
]


def pull_platform() -> bool:
    """Pulls the latest ai-platform rules via git."""
    print(f"[SYNC] Pulling latest platform rules in {PLATFORM_ROOT}...")
    result = subprocess.run(
        ["git", "-C", str(PLATFORM_ROOT), "pull", "--ff-only"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[ERROR] git pull failed:\n{result.stderr}", file=sys.stderr)
        return False
    print(result.stdout.strip() or "[SYNC] Already up to date.")
    return True


def link_project(project_root: Path) -> bool:
    """Symlinks project .claude/rules/ entries to platform universal rules."""
    claude_rules_dir = project_root / ".claude" / "rules"
    claude_rules_dir.mkdir(parents=True, exist_ok=True)

    ok = True
    for rule_filename in UNIVERSAL_RULE_FILES:
        source = RULES_DIR / rule_filename
        target = claude_rules_dir / rule_filename

        if not source.exists():
            print(f"[ERROR] Platform rule file missing: {source}", file=sys.stderr)
            ok = False
            continue

        if target.is_symlink():
            if target.resolve() == source.resolve():
                print(f"[OK] {target} already linked correctly.")
                continue
            print(f"[FIX] {target} points elsewhere — relinking.")
            target.unlink()
        elif target.exists():
            print(
                f"[SKIP] {target} exists as a real file, not a symlink. "
                f"Remove or back it up manually, then re-run.",
                file=sys.stderr,
            )
            ok = False
            continue

        target.symlink_to(source)
        print(f"[LINK] {target} -> {source}")

    return ok


def verify_links(project_root: Path) -> bool:
    """Confirms every expected symlink resolves to the platform source."""
    claude_rules_dir = project_root / ".claude" / "rules"
    all_good = True
    for rule_filename in UNIVERSAL_RULE_FILES:
        target = claude_rules_dir / rule_filename
        if not target.is_symlink():
            print(f"[BROKEN] {target} is not a symlink.", file=sys.stderr)
            all_good = False
            continue
        if not target.resolve().exists():
            print(f"[BROKEN] {target} points to a missing file.", file=sys.stderr)
            all_good = False
    return all_good


def print_remaining_steps(project_root: Path) -> None:
    print("\n[REMAINING STEPS]")
    print(f"  1. Confirm {project_root}/CLAUDE.md points to ai-platform/3-lane-protocol.md")
    print(f"  2. Confirm {project_root}/.windsurfrules only carries project-specific overrides")
    print("  3. Read ai-platform/3-lane-protocol.md before pulling a first ticket")
    print("  4. Re-run with --pull whenever platform rules change")


def main() -> int:
    parser = argparse.ArgumentParser(description="ai-platform sync bootstrapper")
    parser.add_argument("--project", type=str, help="Path to the project root to link")
    parser.add_argument(
        "--pull", action="store_true", help="Pull latest platform rules via git"
    )
    args = parser.parse_args()

    if not args.project and not args.pull:
        parser.print_help()
        return 1

    if args.pull:
        if not pull_platform():
            return 1
        if not args.project:
            return 0

    if args.project:
        project_root = Path(args.project).resolve()
        if not project_root.is_dir():
            print(f"[ERROR] Not a directory: {project_root}", file=sys.stderr)
            return 1

        if not link_project(project_root):
            return 1

        if not verify_links(project_root):
            print("[ERROR] Symlink verification failed.", file=sys.stderr)
            return 1

        print(f"\n[OK] {project_root} is linked to ai-platform rules.")
        print_remaining_steps(project_root)

    return 0


if __name__ == "__main__":
    sys.exit(main())
