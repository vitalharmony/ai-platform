# Operator Diffs — Where HRSE2 Practice Deviates From `ai-platform.md`

Written for Marc, not for Kyle/Greg. These are gaps between the aspirational
platform spec and what's actually true on HRSE2 today. Some need a decision;
some are just things worth knowing before you assume the platform doc is
already reality.

## 1. RESOLVED — Verification gate coverage gap (Option C chosen)

`rules/testing-gate.md` (platform-universal) requires **≥80% line coverage**
as a hard block on commit. Checked before deciding: HRSE2 has **no test
suite at all** — no pytest, no vitest, no `.test.ts`/`.spec.ts` files
anywhere; `backend/scripts/test_*.py` are one-off manual connection checks,
not an automated suite. So this was never "wire up a coverage tool" — it was
"write tests from zero, then gate on them."

Three options were considered: (A) build to the full 80%-coverage spec now
(weeks of work, competes with feature work), (B) explicitly override the
threshold in HRSE2's `.windsurfrules` and park test-suite-building
indefinitely, (C) same override as B, plus a scoped pilot issue to start
concretely rather than leave it fully unowned.

**Decision: Option C.** `.windsurfrules` §VERIFICATION GATE now carries an
explicit "Coverage gate — HRSE2-specific override" note stating the 80%
threshold is not enforced and verification is lint+build+mypy+live-check
only. A scoped pilot ticket — vitalharmony/hrse#135 — targets
`app/services/relationship_health.py` specifically (documented as a pure
decay engine with no I/O, the cleanest first unit-test target). Explicitly
out of scope for #135: full repo-wide coverage, any frontend test tooling.

## 2. `.claude/rules/cypher.md` is intentionally NOT part of the platform sync

This was a deliberate design choice while drafting the universal rule files,
not an oversight: Neo4j/Cypher-specific guidance can't be "universal" since
Ke'nekted/LeasePAL/OWE likely don't use Neo4j. It stays as an HRSE2-local
file. If another project later adopts Neo4j, this file becomes a candidate
for its own project-local copy — not a platform file — unless multiple
projects converge on the same graph DB, at which point promoting it to
`rules/` would make sense.

## 3. RESOLVED — HRSE2's `.claude/rules/` is now symlinked (issue #6 landed)

`sync_rules.py` was tested live against HRSE2 and correctly refused to
overwrite the real files (by design — it won't clobber silently). The two
HRSE2-specific items that would've been lost by a straight symlink swap
(the exact `app/database.py`/`llm_gateway.py` file pointers, and the "no
React Router" rule) were preserved in two new local-only files:
`.claude/rules/backend-hrse2.md` and `.claude/rules/frontend-hrse2.md`.
`.windsurfrules` and `CLAUDE.md` were also trimmed of now-duplicated generic
content, verified via full diff against the originals before editing, and
confirmed via a live restart (lint/build/mypy gate + `db_connected: true`).

**Known portability quirk, by design, not a bug:** the committed symlinks
carry the absolute path from whichever machine created them (mine —
`/home/mmangus/ai-platform/...`). Every other developer must run
`sync_rules.py --project .` right after cloning/pulling to relink them to
their own machine's `~/ai-platform` checkout — the script already detects
and fixes a mismatched target automatically. This is called out explicitly
in `docs/onboarding-kyle.md` and should be repeated in Greg's doc once it's
made concrete.

## 4. Lane 3 is local — no cloud dispatch

Earlier in troubleshooting this session, Claude Code incorrectly floated a
"Devin Cloud vs. Devin Local" distinction for Lane 3, reasoning that an
isolated remote VM would lack `.env`/`GH_PAT` access. You corrected this:
Devin AA was always intended to be local, and local `gh` CLI access already
works. The platform doc (`ai-platform.md` §2) states this explicitly now so
it doesn't get re-litigated. No action needed — just don't let a future
session reintroduce the cloud framing.

## 5. A project's service-lifecycle tool is HRSE2-only, not a platform primitive

The platform's `universal-agent.md` deliberately doesn't hardcode any one
tool — it says "every project designates exactly one service-lifecycle
path" and defers the actual mechanism to the project's own `.windsurfrules`.
HRSE2's is `mise run restart`/`check`/`bump`/`commit` (mise + process-compose,
adopted 2026-07-13 per ADR-001, replacing the retired custom
`hrse_manager.py` script). This means Ke'nekted will need its own equivalent
(or an explicit decision that it doesn't need one) — that's an open item in
`docs/onboarding-greg.md`, not something this platform repo can supply for
you. ADR-001 is worth reading as precedent either way: "adopt mature OSS
over building custom" is likely Marc's default answer for Ke'nekted's
equivalent gap too.

## 6. What actually still needs your decision

- Approve or amend the coverage-gate gap (#1) before treating
  `rules/testing-gate.md` as binding on HRSE2.
- Confirm whether Ke'nekted/LeasePAL/OWE Studio repos exist yet and where —
  the project registry in `ai-platform.md` §7 is `TBD` for all three, which
  blocks writing anything concrete for Greg beyond the placeholder doc.
