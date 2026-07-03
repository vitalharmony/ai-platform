# Lane 3 Test Gate — Frontend UI Golden Path (Greg's variant)

For UI-only tickets where the change is presentational/interaction and does
not touch business logic, data contracts, or backend behavior.

| Metric | Threshold | Enforced by |
|---|---|---|
| Visual regression | 0 unreviewed diffs | Playwright screenshot comparison |
| Component smoke tests | 100% pass | Render + key interaction per component |
| Unit test requirement | Not required for pure UI | Waived for UI-only tickets |
| Test spec approval | HITL (Tech Lead) | Required before test execution begins |

## Rules

1. This path applies only when the ticket is genuinely UI-only. If the
   change touches a data contract, a service, or business logic alongside
   the UI, use the standard `testing-gate.md` path instead — don't waive
   coverage on a ticket that isn't actually UI-only.
2. Visual regression comparison runs via Playwright screenshot diffing.
   A diff that hasn't been explicitly reviewed and accepted blocks the gate
   — it does not auto-pass on "looks fine."
3. Smoke tests must actually render the component and exercise its key
   interaction (click, input, toggle) — a test that only imports the module
   without rendering it does not count.
4. Same HITL and live-verification standard as the standard path: no
   "Evidence type: Source" pass claims.

**Open item:** the visual-regression tooling itself (Playwright config,
baseline screenshots) is not yet set up on every project using this variant
— confirm it exists on a given project before relying on this gate for that
project's tickets.
