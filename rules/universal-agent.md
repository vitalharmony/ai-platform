# Universal Agent Directives (ALL PROJECTS)

Canonical process rules for every AI agent (Claude Code, Cascade, Devin Local,
Devin Autonomous Agent) on every Vital Harmony project. Project-level
`.windsurfrules` may add constraints but may not weaken these. Precedence:

```
ai-platform/rules/universal-*.md
  → ai-platform/rules/{language}.md
    → {project}/.windsurfrules  (project overrides)
      → {project}/CLAUDE.md     (session-specific context)
```

## SERVICE LIFECYCLE & GIT (NON-NEGOTIABLE)

- Every project designates exactly one service-lifecycle script (its project
  `.windsurfrules` names it — e.g. HRSE2's `hrse_manager.py`). All restarts,
  commits, version bumps, and pushes route through it. No agent manually runs
  `git add`/`commit`/`push`, or manually starts/stops dev servers, as a
  substitute.
- If the lifecycle script fails, diagnose and fix the script — do not bypass
  it with manual commands.
- Push to the remote only when the human operator explicitly asks.

## VERIFICATION GATE (HARD REQUIREMENT)

Before any commit-producing restart, the project's full verification gate
(lint + typecheck/build + backend type-check, at minimum) must pass. Fix
failures first — never commit broken code to satisfy a deadline.

Run gate commands one at a time, as separate tool calls, with absolute paths.
Never chain with `&&`/`||`/`;`/pipes. Wait for each result before proceeding.

## MODULARITY (SUB-300 LINES)

If an edit would push any source file over 300 lines, halt and decompose into
smaller modules before proceeding. Composition over monoliths. One-off/
migration scripts in a project's designated scripts directory are exempt.

## SECURITY

- Secrets never appear in code, logs, prompts, or commit messages.
- Any query language with injection risk (SQL, Cypher, etc.) must be
  parameterized — never build queries via string interpolation/concatenation.
- Any single-instance resource (DB driver, connection pool) is a module-level
  singleton owned by one file — no agent instantiates a second one elsewhere.

## CLOUD-NATIVE & 12-FACTOR READINESS

Target: every project survives a clean forklift to its cloud target.

- **Config:** zero hardcoded IPs, ports, URIs, keys, or model IDs — read from
  environment variables only. No `localhost` defaults baked into production
  paths.
- **Statelessness:** don't write user uploads to local disk if the project is
  meant to run in a stateless/containerized environment — design for
  object storage instead.
- **Observability:** no raw `print()`/`console.log()` debugging left in
  production paths — use the project's structured logger.
- **Multi-tenancy:** never hardcode a user/tenant identifier; context flows
  from the authenticated session.

## AI ABSTRACTION (LLM GATEWAY)

If a project makes LLM calls, all of them route through one designated
gateway module. No other module constructs a provider client directly or
hardcodes a model ID. Model/tier selection is env-first. LLM output is
untrusted input — parse and validate it, never `eval` it or raw-string-match
it for control flow.

## API ABSTRACTION (FRONTEND)

If a project has a frontend that calls its own backend, all such calls route
through one designated HTTP client module. No raw `fetch()`/axios calls
scattered elsewhere. Components degrade gracefully (mock data / empty states)
when the backend is offline rather than crashing.

## UTILITY / MIGRATION SCRIPTS

Check the project's designated scripts directory before writing a new
one-off. Never place single-use scripts inside the application source tree
(backend or frontend). Prefix single-use scripts so they sort together and
read as disposable (e.g. `1-fix_nodes.py`).

## BUG-FIX PROTOCOL (ALL AGENTS)

Every bug fix — implementing or reviewing — follows read-propose-execute.
Skipping a step is a protocol violation.

1. **Read before touching.** Locate and read the exact file sections involved
   before opening an editor.
2. **Propose before executing.** State in plain text: the root cause (not
   just the symptom), the exact change (which lines, what replaces what), and
   the expected outcome (what log line / API response / state confirms it
   worked).
3. **Execute, then verify against a stated test case.** Every bug-fix must
   include: "After fixing, [action] should produce [Y] and should NOT produce
   [Z]." Run that exact test against the live service — not just a re-read of
   the diff. See `rules/testing-gate.md` for what counts as live verification.

If fixing multiple bugs, address each as a numbered item. Do not infer or
invent a bug that was not explicitly described.

## SURGICAL CHANGES (KARPATHY PRINCIPLE)

Make the minimum change that accomplishes the stated task. Do not refactor,
rename, reorganize, or clean up adjacent code as part of a bug fix or small
feature — that is a separate task and a separate commit.

- A bug fix touches only the lines needed to fix the root cause.
- A small feature adds only what was asked for — no "while I'm here" cleanup.
- Pre-existing style issues, unused imports, or long lines you didn't
  introduce: leave them, unless the task is explicitly "clean up X."
- If decomposition is genuinely required to touch a file safely (it already
  exceeds the 300-line cap), say so explicitly before doing it, then do only
  that, then make the targeted change.

## ISSUE TRACKING

New bugs and features are tracked as GitHub Issues on the project's repo, not
appended to a local backlog file. Close issues directly on GitHub when work
completes and is verified.
