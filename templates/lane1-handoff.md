<!-- Lane 1 → Lane 2 handoff artifact. Copy this structure for every handoff. -->

## Handoff: [Issue #N — Short Title]

### Issue
- GitHub: {url}
- Labels: {labels}
- Acceptance criteria: {copied verbatim from issue}

### Affected Files
| File | Lines | Change type |
|---|---|---|
| path/to/file.py | 45–78 | Modify — replace X with Y |
| path/to/other.py | new | Create — new service module |

### Root Cause / Entry Point
> "{quoted line or condition that is the root cause}"

### Implementation Spec
{explicit step-by-step instruction for Lane 2 — no ambiguity}

### Test Cases (for Lane 3)
1. After fixing, [action] must produce [Y] and must NOT produce [Z].
2. ...

### Read-Before-Edit Instruction
Read the cited lines and quote the root-cause line or condition before
making any change.

### Ambiguity Gate
If any instruction above is unclear, Lane 2 must stop and escalate to the
Tech Lead before making any change.
