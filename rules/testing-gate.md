# Lane 3 Test Gate — Standard Path

Applies to backend and full-stack tickets. See `frontend-ui-golden-path.md`
for the UI-only variant.

| Metric | Threshold | Enforced by |
|---|---|---|
| Test pass rate | 100% | Devin AA — hard block on commit |
| Line coverage | ≥ 80% | Devin AA — hard block on commit |
| Test spec approval | HITL (Tech Lead) | Required before test execution begins |
| Max auto-fix retries | 3 | Escalates to Tech Lead on failure |

## Rules

1. Lane 3 receives the GitHub issue spec independently and writes its test
   spec from the issue's acceptance criteria — **it must not read Lane 2's
   implementation first.** Reading the code before writing tests produces
   tests that describe what the code does, not what the ticket required
   (test collusion). The issue is the oracle.
2. The test spec goes to the Tech Lead for HITL approval (see
   `templates/hitl-test-review.md`) before any test executes.
3. After approval, Lane 3 executes tests against Lane 2's implementation.
   Live execution only — an "Evidence type: Source" citation (Lane 3 read
   the code and reasoned it should pass) does not satisfy this gate. Every
   check needs an actual run: a request/response, a log line, a before/after
   count.
4. If tests fail, Lane 3 may attempt up to 3 auto-fixes. A 4th consecutive
   failure on the same root cause escalates to the Tech Lead rather than
   retrying further.
5. Once tests pass, Lane 3 performs a style/refactor pass per the project's
   `.windsurfrules`, then is unblocked to commit. **This pass is
   report-only — Lane 3 identifies violations, it does not fix them,
   whether the violation is pre-existing or was introduced by the change
   just gated.** Implementing a fix (even a small one, even one that only
   compresses lines to get back under a cap) is Lane 2's job. If the
   gated change itself introduced a violation (e.g. pushed a file over the
   line cap), Lane 3 reports it as a gate finding for the Tech Lead to
   route back to Lane 1/Lane 2 — it does not edit the file itself to
   clear its own finding. See `rules/universal-agent.md`'s no-ad-hoc-fixes
   rule — this applies to Lane 3 exactly as it does to Lane 1.
6. If any check truly cannot be live-verified in the current environment
   (e.g. no browser available for a UI check), Lane 3 must say so explicitly
   rather than substituting a source-code citation — a partial, honest result
   is acceptable; a disguised one is not.
