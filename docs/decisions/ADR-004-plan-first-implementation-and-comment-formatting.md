# ADR-004: Plan-First Implementation (Lane 2 plan review) + GitHub comment formatting

**Date:** 2026-07-13
**Status:** Accepted
**Decider:** Marc Mangus (platform owner)
**Extends:** ADR-003's mechanism (`pitch-inspection`) to a second invocation point
**Amends:** `3-lane-protocol.md` (two new sections), `templates/lane1-handoff.md`
(new field), `agents/pitch-inspection.md` (Mode B)
**Extended by:** ADR-005 (enforcement — handoff-splitting + distinct relay
triggers, after this mechanism's Plan-First gate was skipped on its first
real use despite explicit written instructions, HRSE2 #236)

## Context

Marc, footing the Devin credit bill directly, observed that each "big"
issue in the #224 epic (hrse_manager.py → mise/process-compose cutover)
consumes roughly 25% of his daily Devin token budget, and asked whether
Fable subagents could be used earlier in the loop — specifically when
Lane 2 (Devin) forms its own implementation plan — to catch problems
before Devin spends real credits, rather than only via Lane 1's
`pitch-inspection` review of Lane 1's *own* handoff (which happens before
Lane 2 starts) or via `sticky-wicket` after Lane 2 has already burned
rounds thrashing.

Separately, in the same session: Lane 2's completion comments on both
HRSE2 #234 and #235 arrived with swallowed/mangled code blocks — content
posted via an inline `gh issue comment --body "$(cat <<'EOF' ... EOF)"`
heredoc containing nested triple-backtick fences collided with GitHub's
markdown parser, dropping content silently.

## Decision 1: Plan-First Implementation

Evaluated via `product-strategy` (Fable), 2026-07-13. The evaluation is
worth recording in full because it corrects an assumption Marc's own
framing raised and rejects the naive version of the mechanism.

**Marc's framing asked whether Devin itself could invoke a Fable subagent
directly** (Devin uses Adaptive model routing and can call different
models). Live research confirmed Devin genuinely has subagents, playbooks,
and multi-model routing — richer capabilities than assumed — and one
secondary source suggests a possible Devin-Desktop-to-Claude-agent bridge
via ACP. **Decision: route through Lane 1 regardless, by design, not just
technical necessity.** Even if a bridge exists, Lane 2 commissioning its
own review is the maker-grades-own-work failure relocated one layer down,
it would cross vendor/credential boundaries between lanes (a standing
violation — a lane never borrows another lane's tool/credentials), and it
would bypass the fresh-context guarantee that makes the review meaningful
(Lane 2 configuring its own reviewer is not independent review).

**Should this be required, and when?** Yes, but narrowly — keyed on
self-declared *delegation*, not issue size or epic membership (both
considered and rejected as unverifiable heuristics, the same category
ADR-003 already rejected once for `pitch-inspection`'s own trigger). The
decisive evidence: `templates/lane1-handoff.md` already demands "explicit
step-by-step instruction — no ambiguity." When Lane 1 actually delivers
that, Lane 2's plan is a restatement and reviewing it is pure overhead.
Lane 2's plan only carries genuinely new, unreviewed design content when
the handoff *deliberately delegates* a decision — which is precisely what
happened on HRSE2 #233 (Lane 1's own handoff explicitly flagged "the
disposable-resource design" as "the judgment call," left for Lane 2 to
resolve).

**What review the plan gets:** `pitch-inspection`, reused with a new
invocation mode (Mode B), not a second agent to build and maintain. Its
existing four-check structure (verify assertions live, red-team the
design and its failure paths, check standing constraints, name the
failure class) applies unchanged to a plan — what differs is scope: Mode B
reviews only the delta Lane 2 introduced against an already-reviewed
handoff, not a full re-review.

**Why not a Lane 1 solo read instead** (the informal precedent that
already happened once, on HRSE2 #233)? The #233 thread is the decisive
evidence against it: Lane 1 posted a solo review of Lane 2's implementation
plan on 2026-07-12, caught two real gaps, and explicitly *approved* the
disposable-branch design — the exact structural flaw that went on to
generate the issue's recurring bug class across roughly ten rounds. A
Lane 1 solo read is better than nothing but has already been observed,
directly, to miss the failure class that matters most. The mechanism that
actually caught the analogous flaw later that same night was a
fresh-context `sticky-wicket` run, which falsified a worktree design
Lane 1's own self-assessment had endorsed. Fresh context is not a nicety
here — it is the specific thing that worked when a solo read didn't.

**Honest cost/benefit, not just justification:** the benefit is real but
partial, the same "half the incident" shape ADR-003 already gave the
design-time mechanism. Applied retroactively to #233: the disposable-
branch design flaw and the interactive-sudo gap are in scope (plausibly
caught). The false-completion-report rounds, the stash/branch confusion,
and the wrong "passes twice consecutively" acceptance contract are **not**
— those are verification-honesty and spec-contract failures no plan
review touches. The strongest case against the mechanism: now that
`pitch-inspection` reviews handoffs at all (it didn't exist when #233's
handoff was written), a fully-specified handoff often leaves Lane 2
nothing design-shaped to get wrong, making this redundant *in the common
case* — which is exactly why the trigger is delegation-keyed, not
universal. Where a handoff delegates nothing and mutates nothing, this
adds zero steps, by construction.

**Single most likely failure mode of the mechanism itself:** Lane 1
writing "none" in Delegated Judgment Calls while the spec actually leaves
ambiguity. Mitigation already exists in the protocol: Lane 2's standing
Ambiguity Gate ("if any instruction is unclear, stop and escalate") is the
backstop that surfaces an undeclared delegation.

## Decision 2: GitHub comment formatting

Mechanical, not a judgment call — no subagent involved. Standing rule
added: any lane posting a comment containing a code block writes it to a
file first and posts via `--body-file`, then fetches the comment back to
confirm it rendered legibly before considering the post done. Same
verify-live-not-source discipline, applied to a lane's own GitHub output
rather than to code behavior.

## Consequences

- `templates/lane1-handoff.md` gains a third mandatory field (after
  Design Alternatives Considered and Load-Bearing Assumptions from
  ADR-003): Delegated Judgment Calls. Three fields now cost nothing to
  fill in as "none"/"none"/"none" for the common, undelegated,
  fully-verified handoff.
- `agents/pitch-inspection.md` gains Mode B; same agent, same model, same
  never-mutate constraint, same one-pass rule.
- Every future Lane 2 GitHub comment with a code block should use
  `--body-file` and self-check rendering — a real behavior change for
  Lane 2's own posting habits, not just Lane 1's.
- Not addressed here, explicitly out of scope: verification-honesty
  failures (false completion claims) and issue-level acceptance-criteria
  defects. Both remain governed by existing mechanisms
  (verify-live-not-source, Lane 1's full-diff review). If either recurs as
  its own pattern, that is a future ADR, not a retrofit onto this one.
