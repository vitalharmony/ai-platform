<!-- Lane 1 → Lane 2 handoff artifact. Copy this structure for every handoff. -->

## Handoff: [Issue #N — Short Title]

### Issue
- GitHub: {url}
- Labels: {labels}
- Acceptance criteria: reference the issue body by default — Lane 2 fetches
  it directly (`gh issue view`). Quote a specific line verbatim only when
  this handoff's spec depends on exact wording (e.g. disambiguating a
  criterion that reads differently than Lane 1's diagnosis) — otherwise a
  copy silently drifts if the issue is edited after handoff.

### Lane 3 Gate Variant
{standard (`rules/testing-gate.md`) | UI golden path
(`rules/frontend-ui-golden-path.md`) | project-specific skill, e.g. HRSE2's
`.devin/skills/lane3-gate/SKILL.md`} — name it explicitly so Lane 3 doesn't
have to infer which gate applies.

### Affected Files
| File | Lines | Change type |
|---|---|---|
| path/to/file.py | 45–78 | Modify — replace X with Y |
| path/to/other.py | new | Create — new service module |

### Root Cause / Entry Point
> "{quoted line or condition that is the root cause}"

### Implementation Spec
{explicit step-by-step instruction for Lane 2 — no ambiguity}

**No secrets in this handoff.** Name the env var a step depends on, never
its value — this handoff is posted as a permanent comment on the GitHub
issue, a wider audience than a local file.

### Test Cases (for Lane 3)
1. After fixing, [action] must produce [Y] and must NOT produce [Z].
2. ...

### Read-Before-Edit Instruction
Read the cited lines and quote the root-cause line or condition before
making any change.

### Ambiguity Gate
If any instruction above is unclear, Lane 2 must stop and escalate to the
Tech Lead before making any change.
