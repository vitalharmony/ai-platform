# Onboarding Addendum — Kyle (CymaGraph / HRSE2)

Read `../3-lane-protocol.md` and `../ai-platform.md` first. This file covers
only what's different for HRSE2 specifically, or still pending from your
earlier onboarding.

## Still Pending From Original Onboarding

Per prior notes: NDA/GitHub/email access is done. Still outstanding —
`.env` + Neo4j DB dump share, and Google Cloud setup. Ping Marc directly for
these; they're out-of-band (the DB dump is gitignored and shared separately
from the repo per `setup/first_time_setup.md`).

## HRSE2-Specific Overrides You Need to Know

These are real deviations from the generic platform description — don't be
surprised by them:

1. **Service lifecycle is `hrse_manager.py`, full stop.** Never run
   `uvicorn`, `npm run dev`, or `git commit`/`push` manually on this repo,
   even to save time. If the manager script itself is broken, the fix is to
   fix the manager, not route around it.
   ```bash
   python3 hrse_manager.py --restart --no-browser        # normal restart, bumps + commits
   python3 hrse_manager.py --restart --no-bump --no-git --no-browser   # tooling/test-only
   ```
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
