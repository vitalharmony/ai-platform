# Onboarding Addendum — Greg (Ke'nekted)

Read `../3-lane-protocol.md` and `../ai-platform.md` first. Repo:
https://github.com/harmonicarchitect/kenekted-platform (private, owned under
`marc@kenekted.ai` — see the security model below before assuming anything
about cross-repo access). Beyond the repo location, its stack and existing
tooling are still unconfirmed — treat the setup steps below as a starting
point, not verified fact.

## Security Model — Read This First

Ke'nekted and HRSE2/`vitalharmony` are **fully separate credential
universes**. This is intentional, not an oversight:

- `kenekted-platform` is private, under `marc@kenekted.ai`. The
  `vitalharmony` GitHub identity is **never** a collaborator on it, and never
  will be.
- Greg's GitHub access to `kenekted-platform` comes from Ke'nekted's own
  invite — nothing to do with `vitalharmony`.
- The only repo every project shares is `ai-platform`, and it's **public** —
  no invite, no credential, no cross-account grant needed to clone or pull
  it. That's the one deliberate exception; everything else stays isolated.
- Any tooling (Lane 2/3 agents, `gh` CLI, a service-lifecycle script) running
  inside `kenekted-platform` should resolve its GitHub token from a
  Ke'nekted-scoped credential — a fine-grained PAT under `marc@kenekted.ai`
  or Greg's own account, stored in `kenekted-platform`'s own gitignored env
  file — never from HRSE2's `.env` or a machine-global `gh auth login`
  session that happens to be logged in as `vitalharmony`.

## What's Confirmed

- Greg owns the **Frontend UI Golden Path** variant of the Lane 3 gate
  (`../rules/frontend-ui-golden-path.md`): visual regression via Playwright
  screenshot comparison, 100% component smoke-test pass, no unit-test
  requirement for tickets that are genuinely UI-only.
- The universal rules (`../rules/universal-agent.md`,
  `../rules/universal-claude.md`, `../rules/frontend-typescript.md`) apply
  the same way they do on HRSE2 — same 300-line cap, same "no raw fetch(),
  one designated HTTP client module" rule, same "no `any`" rule.

## What's Still Unknown — Fill In Before This Doc Is Complete

- [ ] Primary stack (frontend framework, backend framework/language, DB)
- [ ] Does the repo already have a `.windsurfrules`/`CLAUDE.md`-equivalent?
      If yes, this migration mirrors HRSE2's issue #6. If no, this is a
      greenfield setup instead of a migration.
- [ ] Is Playwright (or an equivalent visual-regression tool) already wired
      up? The golden-path gate assumes baseline screenshots exist — if not,
      that setup is a prerequisite, not an assumption.
- [ ] Does Ke'nekted have its own service-lifecycle script (like
      `hrse_manager.py`), or does it need one written as part of onboarding?
- [ ] Greg's OS — `sync_rules.py` symlinks work natively on macOS/Linux;
      Windows needs WSL. Confirm before assuming the setup steps below work
      as-is.

## New Since Roughly 2026-07-09 — Applies to Every Project, Not Just HRSE2

Landed the night of 2026-07-12/13, driven by a real incident on HRSE2 (#233
burned ~10 review rounds and a full day's Devin credit budget before the
pattern was caught). These are `ai-platform`-wide changes, so they apply to
Ke'nekted the moment you're on the platform, even though the incident that
produced them happened on a different project. Full records:
`docs/decisions/ADR-002` through `ADR-004` in this repo.

1. **Two new universal Fable subagents**, invoked by Lane 1 (not you):
   `agents/sticky-wicket.md` (reactive circuit breaker — fires after 2
   consecutive FAIL/declined-completion rounds on the same issue, reads
   the thread fresh, asks whether the *approach* is structurally wrong)
   and `agents/pitch-inspection.md` (proactive — reviews a Lane 1 handoff
   before it's posted to you, and reviews *your* implementation plan when
   Plan-First triggers, see below). You'll see their verdicts as issue
   comments.
2. **`templates/lane1-handoff.md` now has three mandatory fields** on
   every handoff: *Design Alternatives Considered*, *Load-Bearing
   Assumptions*, *Delegated Judgment Calls*.
3. **Plan-First Implementation:** when a handoff delegates a real design
   decision to you (non-"none" in that field) or your work mutates git/
   live data, post your implementation plan and stop before writing code —
   wait for a reviewed verdict comment first. This is specifically to
   catch a bad design before credits get spent building it.
4. **Tooling Exception:** dev/test tooling (never application code, never
   shipped) can skip the full 3-lane loop when explicitly scoped that way
   — single implementer, one human-reviewed pass.
5. **GitHub comment formatting:** any comment with a code block goes to a
   file first, posted via `gh issue comment --body-file <path>`, then
   fetched back to confirm it rendered correctly — a heredoc-with-nested-
   backticks pattern was silently mangling completion reports.
6. HRSE2 is also mid-migration off its custom `hrse_manager.py` service-
   lifecycle script onto **mise + process-compose**
   (`docs/decisions/ADR-001-adopt-mise-process-compose-over-custom-manager.md`)
   — not directly relevant to Ke'nekted's own (still-TBD) tooling, but
   worth reading as precedent if Ke'nekted ever needs a lifecycle script:
   the decision was "adopt mature OSS over building custom," which will
   likely be Marc's default answer for Ke'nekted's equivalent gap too.

## Setup Steps (Adjust Once the Above Is Known)

1. `git clone https://github.com/vitalharmony/ai-platform.git ~/ai-platform/`
   — public, no invite needed.
2. Clone `kenekted-platform` using Ke'nekted's own credentials (not
   `vitalharmony`'s).
3. From the Ke'nekted repo root: `python3 ~/ai-platform/sync_rules.py --project .`
4. Follow the Ke'nekted repo's own first-time-setup doc, if one exists —
   if not, that's a gap worth raising, not silently working around.
