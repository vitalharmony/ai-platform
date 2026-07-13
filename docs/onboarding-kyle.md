# Onboarding Addendum — Kyle (CymaGraph / HRSE2)

Read `../3-lane-protocol.md` and `../ai-platform.md` first. This file covers
only what's different for HRSE2 specifically, or still pending from your
earlier onboarding.

## Still Pending From Original Onboarding

Per prior notes: NDA/GitHub/email access is done. Still outstanding —
`.env` + Neo4j DB dump share, and Google Cloud setup. Ping Marc directly for
these; they're out-of-band (the DB dump is gitignored and shared separately
from the repo per `setup/first_time_setup.md`).

**When you do the `.env` setup (Section 4a of `first_time_setup.md`): as of
#175, `SESSION_SECRET_KEY` has no insecure fallback anymore — the backend
won't boot without it, and it's per-machine (generate your own, don't copy
Marc's). The exact command is in that section.**

## HRSE2-Specific Overrides You Need to Know

These are real deviations from the generic platform description — don't be
surprised by them:

1. **Service lifecycle is `hrse_manager.py`, full stop — until epic #224's
   cutover lands.** Never run `uvicorn`, `npm run dev`, or `git commit`/
   `push` manually on this repo, even to save time. If the manager script
   itself is broken, the fix is to fix the manager, not route around it.
   ```bash
   python3 hrse_manager.py --restart --no-browser        # normal restart, bumps + commits
   python3 hrse_manager.py --restart --no-bump --no-git --no-browser   # tooling/test-only
   ```
   **In progress (2026-07-13): `hrse_manager.py` is being replaced by
   mise + process-compose** (`ADR-001-adopt-mise-process-compose-over-custom-manager.md`
   in this repo). `mise.toml` + `process-compose.yaml` already exist at
   HRSE2's repo root as a working **alternative** — `mise run pc-up` /
   `pc-down` / `check` / `bump` / `commit` / `restart` — but **never run it
   concurrently with `hrse_manager.py`**; both default to the same ports
   (8002/5173) by design, and `hrse_manager.py`'s `pkill` on restart will
   kill the other tool's process out from under it. Bring one down before
   starting the other. `hrse_manager.py` stays the sanctioned tool for
   normal work until #237 (the final cutover) closes — don't switch your
   own daily habit yet, just don't be surprised the files exist.
2. **Neo4j/Cypher rules are HRSE2-local, not platform-universal.**
   `.claude/rules/cypher.md` stays as an HRSE2-specific file — it is not
   symlinked from `ai-platform` because most other Vital Harmony projects
   don't use Neo4j. Parameterized-Cypher discipline still applies, it's just
   documented locally instead of centrally.
3. **The 300-line cap and LLM-gateway pattern are real and enforced** —
   `app/services/llm_gateway.py` is the only place that talks to the model
   provider; `src/api/client.ts` (`apiClient`) is the only place the
   frontend talks to the backend. These match the platform's universal
   rules exactly, so nothing extra to learn there.
4. **Bug fixes/features go through the 3-lane loop as normal** — you are
   Lane 2 (Devin Local/Muscle) taking Lane 1 (Claude Code) handoffs, gated
   by Lane 3 before merge. First ticket: pull a `tech-debt`-labeled issue
   from https://github.com/vitalharmony/hrse/issues.

## Setup Steps

1. `git clone https://github.com/vitalharmony/ai-platform.git ~/ai-platform/`
2. Clone/pull the HRSE2 repo. `.claude/rules/backend-python.md` and
   `frontend-typescript.md` are now symlinks (issue #6 migration landed) —
   **but right after your clone, they'll point at Marc's machine**
   (`/home/mmangus/ai-platform/...`), because that's the absolute path baked
   into the symlink when it was committed. This is expected, not broken.
3. Immediately run, from the HRSE2 repo root:
   `python3 ~/ai-platform/sync_rules.py --project .`
   This detects the symlinks point somewhere other than your own
   `~/ai-platform` checkout and relinks them to your machine. Confirm with:
   `readlink .claude/rules/backend-python.md` — it should print a path under
   *your* home directory, not `/home/mmangus/...`.
4. Follow `setup/first_time_setup.md` in the HRSE2 repo for environment
   setup (backend `.venv`, frontend `npm install`, `.env`).
5. Read `README.md` and `hrse.md` in the HRSE2 repo for the domain/graph
   ontology before touching any ingestion or graph code.

## If You Ever See `.claude/rules/backend-hrse2.md` / `frontend-hrse2.md`

These are real files, not symlinks — they hold HRSE2-only additions layered
on top of the platform's universal rules. Don't delete or symlink these;
they're intentionally local-only and not part of the platform sync.

`frontend-hrse2.md` currently holds three real, enforced rules — not just
the "no React Router" one:

1. **No React Router** — `App.tsx` owns a single `activeTab` state.
2. **Data fetching — migrate opportunistically.** TanStack Query is the
   adopted caching/refetch layer (see `ADR-012-TanStack-Query-Data-Fetching.md`
   in the HRSE2 repo's `docs/architecture/decisions/`). If you're editing a
   component for any reason and it has a hand-rolled `useEffect` +
   `useState(loading)` fetch, convert it to `useQuery`/`useMutation` as part
   of that same change — don't leave it, and don't go looking for other
   components to convert either. Same "fix it when you're already there"
   discipline as the 300-line cap.
3. **Component layer — shadcn/ui, same policy.** See
   `ADR-013-shadcn-ui-Component-Layer.md`. If you touch a component with a
   hand-rolled modal, native `<select>`, dropdown, or toast, convert it to
   the matching shadcn/ui primitive in the same change. Same opportunistic
   rule as #2 — no dedicated sweep.

**Read `docs/architecture/decisions/` in the HRSE2 repo before assuming a
rule you don't understand is arbitrary** — every ADR there explains the
reasoning (what was measured, what alternatives were rejected, and why) for
exactly this kind of "convert when touched" rule. If a rule in
`frontend-hrse2.md` or `backend-hrse2.md` references an ADR by name, read
that ADR before pushing back on the rule or asking Marc about it.

## New Since 2026-07-09 — Protocol Mechanisms You'll See on Real Issues

Landed the night of 2026-07-12/13, driven directly by a real incident
(HRSE2 #233 burned ~10 review rounds and a full day's Devin credit budget
before the pattern was named). Read `docs/decisions/ADR-002` through
`ADR-004` in this repo for the full incident records — summary of what
changes your day-to-day work as Lane 2:

1. **Three new Fable subagents exist, invoked by Lane 1, not by you** —
   `agents/product-strategy.md` (HRSE2-local, architecture/strategy
   judgment calls), `agents/sticky-wicket.md` (reactive: fires after **2**
   consecutive FAIL/declined-completion rounds on the same issue — lowered
   from an original 3 — reads the whole thread fresh and asks whether the
   *approach* is wrong, not just the latest bug), `agents/pitch-inspection.md`
   (proactive: reviews Lane 1's handoff *before* it's posted to you, and —
   new as of ADR-004 — reviews *your* implementation plan too, see below).
   You'll see their verdicts show up as comments on issues; nothing for
   you to invoke yourself.
2. **`templates/lane1-handoff.md` now has three mandatory fields** you'll
   see on every handoff: *Design Alternatives Considered*, *Load-Bearing
   Assumptions*, *Delegated Judgment Calls*. Read all three before
   implementing — "Delegated Judgment Calls" specifically means Lane 1 is
   deliberately leaving a design decision to you.
3. **Plan-First Implementation (ADR-004):** if a handoff's Delegated
   Judgment Calls field is non-"none," or your implementation itself
   mutates git state or live data, **post your implementation plan as a
   comment and stop before writing any code.** This isn't extra
   bureaucracy for its own sake — it's specifically to catch a bad design
   before Devin credits get spent implementing it. Wait for a Lane 1 (via
   `pitch-inspection`) verdict comment before proceeding. Real incident
   this comes from: on #233, you posted a plan, got a solo Lane 1 read
   that approved a design which then generated ~10 rounds of recurring
   bugs — this mechanism exists so the review that plan gets is a fresh,
   independent one, not a repeat of the same mistake.
4. **Tooling Exception:** dev/test tooling issues (never application code,
   never shipped, labeled `infrastructure`/`tech-debt`) can skip the full
   3-lane loop — single implementer, one human-reviewed pass, no per-round
   Lane 3 gate. Only applies when the issue is explicitly scoped that way;
   don't assume it for anything touching application source.
5. **GitHub comment formatting — this one's about you directly.** Your
   completion comments on #234 and #235 both arrived with mangled/swallowed
   code blocks (a heredoc + nested-backtick escaping collision), costing
   real review time re-deriving what you'd actually verified. Going
   forward: write any comment containing a code block to a file first,
   post via `gh issue comment --body-file <path>`, then fetch it back
   (`gh issue view N --json comments`) and confirm it rendered legibly
   before considering the report done.
