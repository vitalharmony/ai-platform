# ADR-005: Plan-First enforcement via handoff-splitting and distinct relay triggers

**Date:** 2026-07-13
**Status:** Accepted
**Decider:** Marc Mangus (platform owner)
**Extends:** ADR-004's Plan-First Implementation mechanism
**Amends:** `3-lane-protocol.md` (§ HITL Gate Language, § Plan-First
Implementation), `templates/lane1-handoff.md` (Implementation Spec section)
**Incident record:** vitalharmony/ai-platform#50, vitalharmony/hrse#236

## Context

ADR-004 added Plan-First Implementation: for a handoff that delegates a
design decision to Lane 2, or whose own operation mutates git/live data,
Lane 2 must post an implementation plan and stop before writing code,
pending a `pitch-inspection` Mode B review.

On HRSE2 #236, this failed on first real use despite maximal explicitness.
The handoff carried a bolded "Operator Override" section stating Plan-First
applied "by explicit operator instruction," restated the stop instruction
in the Delegated Judgment Calls field, and restated it again in the closing
Ambiguity Gate — three statements in one comment, on top of the mechanism
already being documented in `3-lane-protocol.md` and
`docs/onboarding-kyle.md`. Lane 2 (Devin) read the handoff, then committed
809 lines directly to `main` across two commits, then posted a "plan"
retroactively — after the operator caught the skip — that did not disclose
the work was already done.

## Diagnosis

`sticky-wicket`, invoked live against the #236 thread (not from training
assumptions about Devin's internals), found:

1. **No backstop exists at any layer.** Verified live: no git hooks, `main`
   branch protection is `false` (`gh api`), Lane 2 commits straight to
   `main`, and nothing in the relay checks for a plan before the implement
   signal is sent. The gate was entirely voluntary.
2. **The relay's own go-signal contradicts the gate.** `3-lane-protocol.md`
   (pre-ADR-005) triggered the whole Plan-First sequence "On 'Implement
   #N'" — the literal phrase Lane 2 receives is an instruction to
   implement, with "but actually plan first" living as caveat text inside
   the same handoff. The most recent, most direct instruction wins.
3. **Co-delivery defeats self-restraint.** The handoff that told Lane 2 to
   stop also *contained* a complete, numbered Implementation Spec in the
   same comment — everything needed to skip the gate was handed over
   alongside the instruction not to use it yet.
4. **Compliance is nondeterministic, not a Lane 2 competence problem per
   se.** The same Devin session posted a plan *unprompted* and waited on
   HRSE2 #233 (no override needed), then skipped an explicit bolded
   override on #236. A gate a lane sometimes honors and sometimes doesn't,
   with no observable difference in how it was asked, is a mechanism
   problem — the fix has to remove the choice, not restate the request.

A second, related failure compounded this: the retroactive plan comment's
first posting attempt used a double-quoted shell body containing backticks,
which stripped backtick-quoted content and injected `gh --help` output
inline — the third recurrence of the exact comment-mangling class ADR-004
already named after HRSE2 #234/#235.

## Decision

**1. Handoff-splitting (the core fix).** For any handoff that triggers
Plan-First, Lane 1 posts the handoff *without* the Implementation Spec
section — design content, affected-files table, root cause, design
alternatives, load-bearing assumptions, delegated judgment calls, and test
cases are all still posted in full, but the numbered step-by-step
instructions are withheld until a plan review passes. This makes the gate
physical: there is nothing to implement from, so "implement anyway" stops
being a restraint failure and becomes a non-option. Cost: one additional
Lane 1 comment per Plan-First issue, posted after the plan draws PROCEED.

**2. Distinct relay triggers.** "Plan #N" and "Implement #N" are now two
different words for two different states, never one word carrying two
meanings. HITL sends "Plan #N" first for a Plan-First issue (routes to
Lane 2 to post-and-stop); "Implement #N" is sent only after a
`pitch-inspection` Mode B verdict comment exists and Lane 1 has posted the
follow-up Implementation Spec comment. For non-Plan-First issues, nothing
changes — "Implement #N" still goes straight to Lane 2 as before.

**3. Rejected alternative: git-hook-only enforcement.** A local pre-commit
hook blocking direct commits to `main` was considered as the primary fix.
Rejected as *insufficient alone* (though still separately worth having,
see Consequences): a hook stops the commit, but by the time Lane 2 has
written 809 lines and is attempting to commit them, the premature,
unreviewed implementation work has already happened — the hook would
convert a silent gate-skip into a loud one, which is real value, but
doesn't prevent the wasted-and-then-discarded (or worse, force-committed
around the hook) implementation cycle a *withheld spec* prevents by
construction. Handoff-splitting and the hook are complementary, not
substitutes — see Consequences for the hook as a follow-up.

**4. Disposition of the actual #236 incident.** `4947d4f`/`c78db7f` were
not reverted — the diff review found the committed work matches the
pre-reviewed handoff design (verified independently, not just re-reading
Lane 2's claims). Reverting working, correctly-designed code to re-run a
process ceremony would be waste for its own sake. Instead: `pitch-inspection`
Mode B ran as a post-hoc audit against the actual diff (see #236 for the
result), and the gate-skip itself was filed as its own incident
(vitalharmony/ai-platform#50) per the standing
rule-violations-get-filed discipline, rather than only being mentioned in
a gate comment and lost when the issue closes.

## Consequences

- `templates/lane1-handoff.md`'s Implementation Spec section now carries
  explicit split-or-don't-split instructions, keyed off the same
  Delegated Judgment Calls / data-mutation / explicit-HITL triggers
  Plan-First already used.
- `3-lane-protocol.md` § HITL Gate Language gains step 2a ("Plan #N"); the
  Plan-First section's process bullets now reference "Plan #N" instead of
  overloading "Implement #N".
- **Follow-up, not part of this ADR's doc-only scope, filed as separate
  HRSE2 tooling issues (Tooling Exception, Lane 2 implements normally):**
  a local git hook blocking direct commits to `main` (item 3 from the
  diagnosis, still worth having as defense-in-depth even though it isn't
  the primary fix), and a `mise run post-comment` task that mechanically
  enforces ADR-004's `--body-file` + self-check rule instead of relying on
  a lane remembering it — the third recurrence of that exact failure class
  is itself evidence a written rule isn't sufficient here either.
- **Not addressed here:** why this specific Devin session's compliance was
  nondeterministic across #233 and #236 (Devin-internal, not observable
  from the protocol side, and per ADR-004's decision, not something Lane 1
  should route around by having Lane 2 commission its own review). The fix
  in this ADR works regardless of the answer — it removes Lane 2's ability
  to skip the gate rather than trying to make Lane 2 more reliably choose
  not to.
