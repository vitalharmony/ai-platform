# transaction-log pattern

A per-commit, in-flight context primer for agents — not a permanent
changelog, not a replacement for `git log`. Extracted from HRSE2's
implementation (ai-platform#40) after the pattern proved itself live across
the hrse#224 cutover epic (~50+ real commits).

## Why this exists

A session-bound agent (Claude Code, Devin, etc.) starting fresh has no
memory of what happened in the last few commits unless it re-derives it
from `git log`, which is slow and easy to skip. `transaction-log.md` is a
small, always-current file an agent reads once at session start (per
`CLAUDE.md`'s "Session start: recent context" convention) to get a fast,
structured summary of what changed recently — without re-deriving it.

## The pattern

1. A markdown file (`transaction-log.md` by convention) with two HTML
   comment markers, `<!-- TRANSACTION_LOG_START -->` and
   `<!-- TRANSACTION_LOG_END -->`, wrapping the entry list.
2. Every commit that changes tracked files appends one entry between the
   markers: a `## <commit message>` header, followed by a short bullet-list
   summary of the diff (see `diffstat_summary.py`).
3. The entry is computed from the **staged** diff and appended **before**
   the commit, then committed in the *same* commit as the change it
   describes — never as a separate follow-up write. This is load-bearing,
   not a style choice: HRSE2's original implementation computed the
   summary and wrote the log entry *after* committing, as a second,
   unstaged file write — which meant the working tree was always left
   dirty by exactly one pending entry, and could never converge to clean
   through the tool's own normal operation (see hrse#242). Compute-before-
   commit, single-commit-total is the fix, not an optimization.
4. On a version bump (whatever "version bump" means for the project — a
   `package.json` version, a git tag, etc.), the log is **cleared**, not
   archived separately — prior content is fully preserved because it was
   already committed before the clear, so `git log -p transaction-log.md`
   replays the entire history. No parallel archive file, no Neo4j/DB
   write, nothing to keep in sync.
5. The summary itself is **`git diff --stat`-based, deterministic, no
   LLM call.** This was evaluated and explicitly rejected, not just left
   out for simplicity: HRSE2's real history showed a ~25% hard-failure
   rate on a local 2B model, every failure silently falling back to this
   exact diffstat path anyway. A 2B model's prose summary is a marginal
   upgrade over the diffstat + the already-hand-written commit message —
   not worth the reliability cost or the local-LLM RAM footprint for this
   specific feature. (Local LLM use elsewhere in a project — sentiment
   scoring, embeddings, etc. — is unaffected; this is scoped to
   transaction-log summarization only.)

## Files

- **`transaction_log.py`** — `append_log_entry`/`clear_log`/
  `newest_entry_header`, both importable and CLI-invocable
  (`python3 transaction_log.py --project-root <path> append --message ... --summary ...`).
  `newest_entry_header` exists to detect a duplicate append after a failed
  commit retry (append succeeds, the commit itself then fails — e.g. a
  hook rejection — and a naive re-run would double the entry before the
  retried commit lands).
- **`diffstat_summary.py`** — the deterministic summary generator. Two
  guards preserved from the original: an empty diff produces a single
  explanatory bullet (never a blank summary), and a markdown-only diff
  produces a distinct `[docs]` bullet rather than a generic diffstat —
  worth flagging as such at a glance in the log.

## Wiring it into a project

Neither file assumes a specific task runner — a project's own `mise.toml`
(or equivalent) task should call them in this order, before the commit:

```
1. git add .
2. summary = diffstat_summary.py --project-root <root>   # from the now-staged diff
3. transaction_log.py --project-root <root> append --message "<commit msg>" --summary "$summary"
4. git add transaction-log.md   # stage the log's own edit alongside everything else
5. git commit -m "<commit msg>"
```

See HRSE2's `scripts/git_commit.py` and `scripts/transaction_log.py` for a
concrete, live-verified reference implementation of this wiring (that
project's version predates this generic extraction and is tightly coupled
to its own repo layout — treat it as a worked example, not something to
symlink).

## What this does not cover

- Choosing *when* to bump a version, or what a "version bump" means for a
  given project — that's project-specific.
- Push behavior — this pattern only touches local commits; whether/when to
  push is a separate policy.
