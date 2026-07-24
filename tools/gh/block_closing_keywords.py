#!/usr/bin/env python3
"""PreToolUse hook: block GitHub closing keywords in PR bodies/comments.

Extends harmonic-forge#85's gh-issue-close permission block to the
closing *intent*, not just that one command surface. #85 blocks
`gh issue close`/`gh issue reopen` directly; it does not and cannot
catch a `Closes #N`-style keyword written into a PR body or comment,
which delegates the same closing action to GitHub's own merge-triggered
automation. See harmonic-forge#93 for the incident record (6th instance
of the closed-without-authorization pattern, this one via a new
mechanism).

Only fires on `gh pr create`, `gh pr edit`, `gh issue comment`,
`gh issue edit`, and `gh api ... -X PATCH .../comments/...` — the
Bash commands whose string arguments can carry a closing keyword.
Non-closing references (Implements/Part of/Refs #N) are unaffected.
"""
import json
import re
import sys

CLOSING_KEYWORD = re.compile(
    r"(?i)\b(close|closes|closed|fix|fixes|fixed|resolve|resolves|resolved)"
    r"\s+(?:[\w.-]+(?:/[\w.-]+)?)?#\d+"
)

RELEVANT_COMMAND = re.compile(
    r"(?i)\bgh\s+(pr\s+(create|edit)|issue\s+(comment|edit)|api\b.*-X\s*PATCH)"
)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({}))
        return

    if data.get("tool_name") != "Bash":
        print(json.dumps({}))
        return

    command = (data.get("tool_input") or {}).get("command", "")
    if not RELEVANT_COMMAND.search(command):
        print(json.dumps({}))
        return

    match = CLOSING_KEYWORD.search(command)
    if not match:
        print(json.dumps({}))
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
        },
        "systemMessage": (
            f"Blocked: this command's body contains a GitHub closing "
            f"keyword ({match.group(0)!r}), which would auto-close the "
            f"referenced issue on merge without explicit human "
            f"authorization (harmonic-forge#84/#93). Use a non-closing "
            f"reference instead — \"Implements #N\" or \"Part of #N\" — "
            f"and close the issue explicitly, separately, only when told to."
        ),
    }))


if __name__ == "__main__":
    main()
