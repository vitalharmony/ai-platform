# 3-Lane Protocol (Agent-Readable)

Condensed operational directives. For philosophy/rationale, see
`ai-platform.md`. This file is what agents load — no narrative prose.

```
[GitHub Issue] → Dev pulls ticket → [Local 3-Lane Loop] → GitHub PR
                                       │
                                 Lane 1: Claude Code (Blueprint)
                                 Lane 2: Devin Local (Muscle)
                                 Lane 3: Devin AA (Control Gate) — local
```

## Lane 1 — Claude Code (Blueprint)

- Reads the GitHub issue (spec, acceptance criteria, labels).
- Maps required changes against the project's `CLAUDE.md`/`.windsurfrules`.
- Cites exact file(s) and line range(s) affected before writing the handoff.
- Produces a Lane 1 Handoff Artifact (`templates/lane1-handoff.md`).
- Includes one concrete test case per requirement in the handoff.
- Never guesses at an ambiguous spec — stops and asks the Tech Lead.
- Does not write production code directly (exception: explicit platform/
  tooling assignments — see `rules/universal-claude.md`).

## Lane 2 — Devin Local (Muscle)

- Executes exactly what the handoff specifies — no scope creep.
- Stays within the file targets the handoff defines.
- Reads the cited file(s) and quotes the root-cause line before editing.
- Obeys `rules/universal-agent.md` + language-specific rule files (300-line
  cap, no raw LLM/API calls outside the designated gateway, parameterized
  queries).
- Signals completion with a structured diff summary back to Lane 1.

## Lane 3 — Devin Autonomous Agent (Control Gate)

- Runs locally. Reads the GitHub issue independently — **never reads Lane
  2's code before writing its test spec.**
- Writes a test spec from the issue's acceptance criteria.
- Submits the test spec for Tech Lead HITL approval
  (`templates/hitl-test-review.md`) before executing anything.
- After approval, executes tests against Lane 2's implementation. See
  `rules/testing-gate.md` (standard) or `rules/frontend-ui-golden-path.md`
  (UI-only variant) for thresholds.
- Blocked from committing until 100% of tests pass at the required coverage
  threshold.
- 3 auto-fix attempts max on a single root cause; 4th failure escalates to
  Tech Lead instead of retrying.
- After tests pass, performs a style/refactor pass per the project's
  `.windsurfrules`.
- Every pass/fail claim must be backed by live execution (request/response,
  log line, before/after count) — a source-code citation is not evidence.

## Escalation

Any lane escalates to the Tech Lead (human) rather than guessing, looping, or
silently narrowing scope, when:
- The issue spec is ambiguous (Lane 1).
- The handoff itself is unclear or contradicts `.windsurfrules` (Lane 2).
- The same root cause survives 3 fix attempts (Lane 3), or a check cannot be
  live-verified in the current environment (Lane 3 — report the gap, don't
  fake the check).

## Team Topology

| Role | Person | Responsibility |
|---|---|---|
| Platform owner | Marc | Owns `ai-platform`; sets golden paths; merges platform PRs |
| Feature delivery | Kyle (CymaGraph/HRSE2), Greg (Ke'nekted) | Consume golden paths; run the 3-lane loop locally; never edit platform rules directly |
| Product demand | Shawn | Defines acceptance criteria on issues; approves shipped features |
