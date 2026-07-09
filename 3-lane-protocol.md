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
- **Posts the handoff as a comment on the GitHub issue itself** — not just
  in chat. The issue is the permanent record: root cause, prompt, and (once
  Lane 2/3 finish) the diff and Lane 3 gate result all live on the same
  issue. This is deliberate — it's the raw material for any future
  cross-issue pattern analysis (recurring bug classes, handoff-quality vs.
  first-pass-success correlation), not just a courtesy copy.
- Never guesses at an ambiguous spec — stops and asks the Tech Lead.
- Does not write production code directly (exception: explicit platform/
  tooling assignments — see `rules/universal-claude.md`).

## Lane 2 — Devin Local (Muscle)

- Given a short trigger (e.g. "implement #N") rather than pasted content,
  **fetches the issue and Lane 1's handoff comment from GitHub directly**
  (`gh issue view N --comments`) before doing anything else — same
  expectation already placed on Lane 3 for its own independent issue read.
  Do not wait for or require the handoff to be pasted in chat.
- Executes exactly what the handoff specifies — no scope creep.
- Stays within the file targets the handoff defines.
- **Never executes the write/apply path of a data-modifying script —
  categorically, no exception, regardless of what the handoff says.**
  Lane 2 may write a migration/fix script and verify it via dry-run or
  fixture-only testing, but the actual execution against real data is
  never Lane 2's action — see Lane 3's execution authority below. This
  rule has no "unless explicitly authorized" clause on purpose: an earlier
  version of this rule had one, and it likely contributed to two real,
  confirmed violations in a row (#154 — Lane 2 hardcoded and ran a
  data-correcting script for a specific bad edge that was only ever cited
  as motivating context, not asked for as work; #155 — Lane 2 ran a
  properly-scoped migration's `--apply` flag against full production
  during its own implementation, when only dry-run/fixture verification
  was authorized). Both times, Lane 2 could correctly quote the
  then-current rule verbatim when asked directly — confirming this is not
  a stale-rules problem, it's that a textual prohibition alone doesn't
  reliably hold against the pull of "let me verify this actually works."
  The fix is structural, not another sentence: Lane 2 is never granted
  this capability at all, so there's nothing to correctly or incorrectly
  apply in the moment.
- Reads the cited file(s) and quotes the root-cause line before editing.
- Obeys `rules/universal-agent.md` + language-specific rule files (300-line
  cap, no raw LLM/API calls outside the designated gateway, parameterized
  queries).
- Signals completion with a structured diff summary back to Lane 1.

## Lane 3 — Devin Autonomous Agent (Control Gate)

- Runs locally. Reads the GitHub issue independently — **never reads Lane
  2's code before writing its test spec.** This now explicitly includes
  **Lane 2's own implementation-report comment on the issue thread** — Lane
  1's handoff and Lane 2's diff summary both post to the same issue (see
  Lane 1/Lane 2 sections above), so when deriving its test spec Lane 3
  reads only: the issue body, Lane 1's original handoff comment, and (if
  present) a second Lane 1 comment specifically addressed to Lane 3 —
  written after Lane 2 finishes, carrying any caveats the HITL gate turned
  up (e.g. "the named test-pair's data has since changed, construct a
  fixture instead" — a real example from #153). Lane 3 must not open or be
  influenced by any Lane 2 comment already on the thread until after its
  spec is written and approved. Co-locating every lane's output on one
  issue is a deliberate convenience (it's what lets Lane 1 review by
  reading the thread instead of relaying pasted text) — it must not become
  a backdoor that lets Lane 3 anchor on Lane 2's self-report.
- Writes a test spec from the issue's acceptance criteria.
- Submits the test spec for Tech Lead HITL approval
  (`templates/hitl-test-review.md`) before executing anything.
- After approval, executes tests against Lane 2's implementation. See
  `rules/testing-gate.md` (standard) or `rules/frontend-ui-golden-path.md`
  (UI-only variant) for thresholds.
- **Lane 3 is the only lane authorized to execute a data-modifying
  script's write/apply path.** When an issue's scope is itself a data
  migration or correction (not just testing already-written application
  code — e.g. #155's shape), the test spec submitted for HITL approval
  must explicitly say so: the plan includes actually running the
  migration for real, not just verifying it works against fixtures. HITL
  approval of that spec is the approval to execute it. This is a
  deliberate reuse of the pre-execution approval gate Lane 3 already has
  for every test spec — it's a more suited fit for this kind of
  goal-seeking, spec-then-execute action than Lane 2's mechanical
  implement-exactly-what's-specified role, and it closes the #154/#155
  gap structurally: nothing runs against real data without HITL having
  explicitly approved that specific action first.
- Blocked from committing until 100% of tests pass at the required coverage
  threshold.
- 3 auto-fix attempts max on a single root cause; 4th failure escalates to
  Tech Lead instead of retrying.
- After tests pass, performs a style/refactor pass per the project's
  `.windsurfrules`.
- Every pass/fail claim must be backed by live execution (request/response,
  log line, before/after count) — a source-code citation is not evidence.

## HITL Gate Language

Lane 1 (Claude Code) and Lane 3 (Devin AA) can both post directly to the
GitHub issue thread — confirmed working in practice. This lets the human
operator (HITL) drive the loop with short, canonical trigger phrases
instead of relaying pasted content between tools. Every trigger names the
issue explicitly (`#N`) — multiple issues can be in flight at once, and an
unnumbered trigger is ambiguous. Some triggers go to Lane 1; others go
directly to Lane 2 or Lane 3 in their own respective interfaces, and Lane 1
never sees them or acts on them.

1. **Lane 1** diagnoses and posts a handoff comment on issue #N (and
   displays it in chat). No trigger needed — this happens unprompted once
   diagnosis is done.
2. **HITL says "Implement #N"** (→ Lane 2). Lane 2 fetches the issue and
   Lane 1's handoff comment from GitHub itself and implements it, posting
   its own completion report as a comment on #N.
3. **HITL says "Lane 2 done for #N"** (→ Lane 1). Lane 1 checks the **full
   working-tree diff** (`git status` / `git diff` across the whole repo,
   not just the files the handoff predicted) against the handoff's
   affected-files list and acceptance criteria — flagging scope creep for
   *anything* touched outside what was specified, including new untracked
   files. Checking only the predicted files is confirmation bias, not
   review, and it has already let a real violation through once (#154 —
   Lane 2 created and ran an unauthorized data-modifying script that a
   predicted-files-only diff never surfaced). Lane 1 also independently
   spot-verifies at least one significant behavioral claim live — never
   just re-reads Lane 2's own description and calls it confirmed.
   - **If a problem is found:** Lane 1 posts a correction comment on #N
     specifying exactly what Lane 2 needs to fix, and reports this to HITL
     instead of proceeding. Once addressed, HITL re-triggers with
     **"Reimplement #N"** (distinct from the first-pass **"Implement #N"**
     — this word specifically signals a correction loop, not new work),
     looping back to step 2.
   - **If confirmed clean:** Lane 1 drafts a second comment addressed to
     Lane 3 (carrying any caveats the review turned up) and posts it to
     #N, then tells HITL it's ready.
4. **HITL says "Test #N"** (→ Lane 3). Lane 3 independently fetches the
   issue body, Lane 1's original handoff comment, and Lane 1's
   Lane-3-addressed comment from step 3 — never Lane 2's comment — derives
   a test spec, and submits it for HITL approval
   (`templates/hitl-test-review.md`) before executing anything. After
   approval, Lane 3 executes and posts its gate report as a comment on #N.
5. **HITL says "Lane 3 done for #N"** (→ Lane 1). Lane 1 reads #N's Lane 3
   gate comment, confirms every claim is backed by live execution (not
   source-code reasoning), checks for protocol adherence (Lane 3 avoided
   Lane 2's comment before writing its spec, and did not implement any fix
   itself during its style/refactor pass — see `rules/testing-gate.md`),
   and independently spot-verifies at least one claim live if anything is
   surprising, high-stakes, or contradicts prior known state.
   - **If a problem is found:** Lane 1 reports the specific issue to HITL
     with a recommendation on whether it routes back to Lane 2 (an
     implementation bug — HITL says **"Reimplement #N"**, loop to step 2)
     or requires Lane 3 to re-test (a gate/spec issue — HITL says
     **"Retest #N"**, distinct from the first-pass **"Test #N"**, loop to
     step 4). HITL decides which.
   - **If confirmed clean:** Lane 1 recommends closing — never a
     unilateral close.
6. **HITL says "Close #N"** (→ Lane 1). Lane 1 posts a closing summary
   comment (referencing the gate evidence) and closes the issue. This is
   the only trigger that results in a close, and it is never self-initiated
   by Lane 1 regardless of how clean a prior gate looked.

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
