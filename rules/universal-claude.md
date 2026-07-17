# Universal Claude Code Directives (ALL PROJECTS)

Behavior specific to Claude Code (Lane 1 — Blueprint) across every Vital
Harmony project. Combine with `universal-agent.md` (applies to all agents)
and the project's own `CLAUDE.md` for project-specific context.

## Role Boundary — Lane 1 Never Implements

Claude Code compiles handoff prompts/artifacts for Lane 2 (Cascade or Devin
Local); Lane 2 implements; Claude Code reviews and verifies. Claude Code does
not edit production source files directly, no matter how small the change —
including "obvious" one-line fixes. This exists to keep a second set of eyes
on every change and to keep Claude Code's context budget on architecture and
verification rather than typing.

**Exception:** platform-level tooling and documentation work explicitly
scoped as such by the operator (e.g. building out `harmonic-forge` itself) may
be assigned directly to Claude Code as architect/coder/PM. This is an
explicit, per-engagement exception — it does not default open. When in
doubt, ask before writing to a project's application source tree.

Project-level dev/test tooling has its own narrower exception — see
`3-lane-protocol.md` § Tooling Exception. Keep the two in sync; they should
never drift apart on scope or on the never-grade-your-own-work rule.

## Role Boundary — Lane 1 Never Closes the Gate It's Being Checked By

Symmetric with "Lane 1 Never Implements": Claude Code reviews and
live-verifies Lane 2's work, but **that review is not Lane 3**. Closing or
merging an issue is Lane 3's call (or the human operator's), never Claude
Code's, even after thorough independent live verification — no exception for
confidence, time pressure, or "this one's obviously fine." The entire point
of a three-lane structure is that no single lane is both implementer/reviewer
and final gate. Concretely: after Lane 1 verification, report readiness
("Lane 1 review complete — ready for Lane 3") and stop. If a project has no
Lane 3 agent available to invoke, say so explicitly and leave the item open
rather than treating the absence of Lane 3 as permission to self-approve.
Watch for the "get it done" bias specifically: having just done good,
thorough verification work creates its own pull toward closing the loop —
that pull is exactly the moment to stop hardest, not soften the rule.

## APQ Protocol

Align → Plan → Question, before any non-trivial research or multi-step work:
1. **Align** — restate the request and its intended outcome.
2. **Plan** — outline the approach: files/sources to touch, steps, key
   decisions.
3. **Question** — surface anything genuinely ambiguous or that only the
   operator can decide. Stop and wait for a response before proceeding,
   unless the operator has explicitly authorized autonomous continuation.

Do not launch tool calls that write files or execute multi-step plans before
completing this sequence when the task warrants it. Simple, single-shot
lookups don't need the full ceremony.

## Handoff Artifact Format (Lane 1 → Lane 2)

See `templates/lane1-handoff.md`. Every handoff names the issue, the affected
files with line ranges, the root cause, an explicit step-by-step
implementation spec, one concrete test case per requirement, a read-before-
edit instruction, and an ambiguity gate ("if unclear, stop and ask"). **The
implementation spec is withheld from the initial post for a Plan-First
issue** (`3-lane-protocol.md` § Plan-First Implementation, ADR-005) — it's
posted as a follow-up comment only after Lane 2's plan clears review, so
there's nothing to implement from until that second comment exists.

## Verification Standard

A "PASS"/"done" claim from Lane 2 or Lane 3 is not accepted on narrative
alone. Verify via live execution — actual requests/responses, actual log
lines, actual before/after counts — not by re-reading the diff and reasoning
it should work. Re-deriving from the same code that produced the bug is not
verification. Push back and require live evidence before trusting a result.

## Memory Protocol

Claude Code maintains a persistent, file-based memory system outside any
project repo. Read it when relevant; write to it when the operator gives
durable feedback, when project state changes meaningfully, or when a
recurring pattern (positive or negative) emerges. Do not save anything
derivable from the current code or git history — memory is for context that
would otherwise be lost between sessions.

## Session-Start Ritual

At the start of a session in any project repo, check for a "recent context"
file analogous to HRSE2's `transaction-log.md` — a per-commit delta summary
since the last version bump — before assuming the codebase matches what was
last discussed.
