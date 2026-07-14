# tools/gh/ — repo-agnostic GitHub issue/comment helpers

Two `gh`-CLI wrappers, extracted from HRSE2's originals (ai-platform#53)
after a hardcoded repo default caused a real mis-post: `mise run
post-comment` was run for an `ai-platform` issue out of HRSE2 habit, and —
because the script defaulted to `REPO = "vitalharmony/hrse"` — silently
posted the comment to an unrelated HRSE2 issue instead. Caught and fixed
immediately, but it's the same failure shape as ADR-004/005 already named
for a different mechanism: **make the compliant path the only easy one to
invoke.** A hardcoded default that can silently target the wrong repo is
the opposite of that — so both tools require `--repo` explicitly, with no
default, and print a banner naming the resolved target before acting.

## Files

- **`post_comment.py`** — post a GitHub issue comment via `--body-file`,
  then refetch and byte-diff it against the source (ADR-004/005's mandatory
  self-check). No project-specific state beyond the repo slug.
  ```bash
  python3 post_comment.py --repo vitalharmony/hrse --issue 251 --file /path/to/body.md
  ```
- **`gh_issue.py`** — `gh issue create`, then optionally `gh project
  item-add` + set `Status=Todo` if a project board is configured. Board
  owner/number come from `--project-owner`/`--project-number` or the
  `GH_PROJECT_OWNER`/`GH_PROJECT_NUMBER` env vars (a project's own
  `mise.toml` supplies these via `[env]`). **Board-add is skipped, not
  treated as an error, when neither is set** — not every project has a
  project board yet, and this tool shouldn't force one into existing.
  ```bash
  GH_PROJECT_OWNER=vitalharmony GH_PROJECT_NUMBER=3 \
    python3 gh_issue.py --repo vitalharmony/ai-platform --title "..." --labels "tech-debt"
  ```

Both are importable (`from post_comment import post_comment`, `from
gh_issue import create_issue, add_to_board`) as well as CLI-invocable, same
convention as `tools/transaction-log/`.

## Wiring into a project's `mise.toml`

Set the repo (and, if applicable, board) slug once in `[env]`, then have
your tasks call these with `$GH_REPO` etc. — the value lives in one visible
config line per project instead of being hand-copied into a script:

```toml
[env]
GH_REPO = "vitalharmony/hrse"
GH_PROJECT_OWNER = "vitalharmony"
GH_PROJECT_NUMBER = "1"

[tasks.gh-new-issue]
run = 'python3 ~/ai-platform/tools/gh/gh_issue.py --repo "$GH_REPO" --title "$usage_title" --body "$usage_body" --labels "$usage_labels"'

[tasks.post-comment]
run = 'python3 ~/ai-platform/tools/gh/post_comment.py --repo "$GH_REPO" --issue "$usage_issue" --file "$usage_file"'
```

A project without a board simply omits `GH_PROJECT_OWNER`/
`GH_PROJECT_NUMBER` — `gh_issue.py` prints a notice and skips that step
rather than failing.

## What this does not cover

- Which repo/board a project uses — that's the one thing every project
  supplies itself, by design (see the incident above for why it's not a
  default).
- Migrating a project already running its own local copy of these scripts
  (e.g. HRSE2's `scripts/post_comment.py`/`scripts/gh_issue.py`) — that's
  a separate, per-project follow-up issue, not part of this extraction.
