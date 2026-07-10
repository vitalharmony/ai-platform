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
- **For test cases requiring interactive UI verification, front-loads
  concrete selectors/interaction paths already known from reading the
  code** (exact button labels, roles, click sequences) rather than telling
  Lane 3 to "verify X live" with no starting point. Real cost of not doing
  this: a handoff that just said "use Playwright for real verification"
  left Lane 3 to blind-guess selectors through repeated trial and error,
  costing significant time and command failures on #152 — compare to a
  handoff that already named exact button text, which went smoothly on
  #159. This doesn't replace Lane 3's own exploration where genuinely
  needed, it just removes the exploration Lane 1 could have shortcut by
  already having read the component.
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
- **3 fix attempts max on a single root cause; 4th failure stops and
  reports back instead of continuing to iterate.** This cap already
  existed for Lane 3 (see Escalation, below) but was never written for
  Lane 2 — a real gap: Lane 2 is the lane that does most of the iterative
  "try something, test it, try again" work on a genuinely hard bug, and
  had no explicit trigger to stop and ask for help instead of continuing
  to churn. Real incident: #152's focus-trap fix (a live-DOM behavioral
  bug, hard to iterate on blind without a visual feedback loop) took
  substantially more churn than it should have before Lane 2 landed a
  working fix. It got there, but an adversarial check-in after a few
  failed attempts — comparing notes with Lane 1 or escalating to the Tech
  Lead — would likely have converged faster than continuing to iterate
  solo. When reporting completion after multiple attempts, **include what
  was tried and ruled out**, not just the final working diff — that
  history is exactly what Lane 1's review should look at when deciding if
  the fix is sound or got there by luck.
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

- **Own directives file: `~/.config/devin/AGENTS.md`** (local, machine-specific
  — not part of this repo, not synced by `sync_rules.py`). This is where
  direct, durable corrections to Lane 3's own behavior go, separate from the
  shared protocol/rule files above that steer all three lanes. Devin AA also
  writes to this file itself (not purely human-maintained) — check it, don't
  assume the `ai-platform` rules are the only lever when Lane 3's behavior
  needs adjusting.
- **Own skill file, per-project: `{project}/.devin/skills/lane3-gate/SKILL.md`**
  (repo-local, not `~/.config` like `AGENTS.md` above, and — as of 2026-07-10
  — not yet synced across projects by `sync_rules.py`; currently HRSE2-only).
  This is a hard-wired enforcement mechanism for the never-fixes-anything
  constraint two sections below, drafted by Devin AA itself after diagnosing
  that prose rules alone weren't preventing it from rationalizing past them
  ("I found the fix and it was easy" / "the fix is obviously correct"). The
  skill explicitly names `ai-platform/3-lane-protocol.md` and
  `rules/testing-gate.md` as authoritative — it is the enforcement layer, not
  a second source of truth, and should be updated to match if the two ever
  drift. Cites the real incidents (`#176`, `#52`) that produced it. If this
  pattern proves out, worth revisiting whether it should be added to
  `sync_rules.py`'s distribution so other projects get the same hard-wired
  protection, not just prose.
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
- **Interactive tool modes are never used for automated execution.** Any
  browser-automation invocation (Playwright, etc.) runs headless with a
  non-interactive reporter (e.g. `--reporter=line`) — never `--debug`,
  `--ui`, `codegen`, or any other mode that opens an inspector/GUI and
  blocks waiting for human interaction. A collapsed or non-interactive
  terminal has no way to surface that prompt, so the command just hangs
  until a human notices and manually cancels it — the same failure shape
  as the `sudo`/`npx install` hangs already seen this session, just in a
  different tool. If a command needs interactive confirmation, that's a
  signal to stop and ask, not to keep invoking variants of the same
  command hoping one works headlessly.
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
- **Lane 3 never fixes application code, ever, under any circumstance —
  full stop.** This applies regardless of whether the bug is self-introduced,
  pre-existing, trivial, or blocking test execution entirely. Lane 3's only
  permitted write actions are: writing/refactoring its own test specs and
  test scripts, and executing an already-HITL-approved data-migration
  script's write/apply path (the one explicit exception above — a
  pre-approved action, not an in-the-moment fix). Every other case: stop
  and report back to Lane 1, or ask the human operator directly for
  authorization to proceed (as HITL did live during #176's port-conflict
  fix — that's the correct pattern: human directs it live, not Lane 3
  deciding on its own). "3 auto-fix attempts max" below refers strictly to
  retrying/adjusting Lane 3's own test spec against a genuine test-authoring
  problem (a bad fixture, a wrong assertion) — never to modifying the code
  under test. Real incident: on HRSE2 #176, Lane 3 self-fixed three things
  during one gate run — one was live-authorized by the human operator (fine),
  two were not (a real pre-existing bug fixed inline instead of reported,
  and a hardcoded plaintext credential written into a compose file to work
  around a variable-interpolation problem instead of fixing the invocation
  or reporting it). Marc: "L3 is falling into 'git 'er done' bias mode more
  than L1 or L2 and it shouldn't be fixing ANYTHING EVER, only running
  tests, scripts, or refactoring." **Why this matters structurally, not just
  as a boundary rule**: Marc: "we WANT the tests to fail if L1/L2 built
  something wrong, we don't want it intervening and fixing it, defeats the
  purpose of the protocol." Lane 3's entire value is as an *independent*
  check — a test that gets silently patched by the tester the moment it
  fails can never fail meaningfully again, which makes the whole gate
  structure pointless. A failing test is the protocol working correctly,
  not a problem for Lane 3 to make go away.
- 3 auto-fix attempts max on a single root cause (test-spec issues only, per
  above); 4th failure escalates to Tech Lead instead of retrying.
- After tests pass, performs a style/refactor pass per the project's
  `.windsurfrules` — **report-only, same absolute rule as above**: identifies
  violations, never fixes them itself, even trivial ones.
- Every pass/fail claim must be backed by live execution (request/response,
  log line, before/after count) — a source-code citation is not evidence.
- **Fast-fail on external blockers.** If a live check is blocked by a
  genuine external dependency — a bug in another open issue this ticket's
  verification requires, a missing precondition, an environment gap that
  isn't this ticket's to fix — Lane 3 confirms the blocker is real with the
  minimum evidence needed (one clean repro, not exploratory workarounds),
  then stops and reports it as a gate finding **immediately**. It does not
  attempt workarounds, mocks, or alternate verification paths to route
  around it first. Real incident: on HRSE2 #204, Lane 3's live delete-flow
  test depended on a mutation endpoint broken by a concurrent bug in #187;
  rather than reporting this immediately, Lane 3 tried several workarounds
  (including a mocked-browser test) before finally surfacing the blocker —
  burning real cost chasing a blocker that had *already been fixed* by the
  time the report was filed. Marc: "L3 burned 3% of my credits trying all
  kinds of crazy work-arounds instead of admitting it was blocked. This is
  not acceptable. It needs to follow the fast-fail principle which is
  doctrine in software development." This is distinct from the auto-fix
  rule above (which governs Lane 3's own test-spec issues, not external
  blockers) — an external blocker in another lane's work is never something
  to route around, mock past, or retry; it is always an immediate
  stop-and-report.

## HITL Gate Language

Lane 1 (Claude Code) and Lane 3 (Devin AA) can both post directly to the
GitHub issue thread — confirmed working in practice. This lets the human
operator (HITL) drive the loop with short, canonical trigger phrases
instead of relaying pasted content between tools. Every trigger names the
issue explicitly (`#N`) — multiple issues can be in flight at once, and an
unnumbered trigger is ambiguous. Some triggers go to Lane 1; others go
directly to Lane 2 or Lane 3 in their own respective interfaces, and Lane 1
never sees them or acts on them.

**Before acting on any trigger, the receiving lane checks the issue's
state.** If `#N` is already closed, stop and ask HITL to confirm the
number before doing anything — don't proceed on the assumption a closed
issue was meant. A typo'd issue number (fat-fingering a digit, or naming
one that was just closed a few messages ago) is an easy, low-cost mistake
to make in a fast-moving session with many issues open at once, and
proceeding against the wrong issue wastes a full lane cycle and produces
a confusing record on the wrong thread. This applies to whichever lane
receives the trigger — Lane 1, Lane 2, or Lane 3 alike.

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
   just re-reads Lane 2's own description and calls it confirmed. **This
   spot-check stays to fast, deterministic, read-only tools (a curl call,
   a direct DB query, lint/build/mypy, a log grep) — it never runs a
   formal, interactive test suite that was built for Lane 3's own gated
   execution** (e.g. a Playwright suite once one exists). The moment a
   piece of tooling is built as *a lane's designated execution
   capability*, running it from another lane — even just to "spot-check" —
   does that lane's actual job instead of a lightweight check on it. This
   happened for real: Lane 1 ran the full Playwright suite #159 had just
   built (which exists specifically to give Lane 3 real interactive
   verification) as part of a routine "Lane 2 done" review, diluting the
   reason Lane 3's independent, HITL-gated execution exists. Same family
   as the Lane 2/Lane 3 data-execution-authority split above — once a
   capability is designated to one lane, another lane doesn't borrow it
   for convenience, no matter how tempting it is when the tooling is new.
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
   — **by any lane**, not just Lane 1, regardless of how clean a prior gate
   or implementation looked. This was originally written naming only Lane 1
   (after HRSE2's `#149` incident); that narrower wording let a real Lane 2
   violation slip through on HRSE2 `#186` — Lane 2 implemented a fix and
   closed the issue itself, with no Lane 3 gate having run at all. The rule
   is: closing requires the human operator's explicit "Close #N," every
   time, from every lane, with no exception for confidence or a clean local
   test pass.

## Escalation

Any lane escalates to the Tech Lead (human) rather than guessing, looping, or
silently narrowing scope, when:
- The issue spec is ambiguous (Lane 1).
- The handoff itself is unclear or contradicts `.windsurfrules` (Lane 2).
- The same root cause survives 3 fix attempts (Lane 3), or a check cannot be
  live-verified in the current environment (Lane 3 — report the gap, don't
  fake the check). **This covers repeated tool/command failures during test
  authoring, not just failed fix-attempts on a specific assertion** — if a
  command fails, hangs, or requires manual intervention 3 times in a row for
  the same underlying reason, that's the same signal as 3 failed fix
  attempts and escalates the same way. Real incident: Lane 3 hit repeated
  bad Playwright command failures while exploring how to interact with the
  app for #152, requiring Marc to manually cancel the terminal multiple
  times, well past the point escalation should have fired.

## Team Topology

| Role | Person | Responsibility |
|---|---|---|
| Platform owner | Marc | Owns `ai-platform`; sets golden paths; merges platform PRs |
| Feature delivery | Kyle (CymaGraph/HRSE2), Greg (Ke'nekted) | Consume golden paths; run the 3-lane loop locally; never edit platform rules directly |
| Product demand | Shawn | Defines acceptance criteria on issues; approves shipped features |
