<!-- Tech Lead approval checklist for a Lane 3 test spec. Complete before Lane 3
     executes any test against Lane 2's implementation. -->

## HITL Test Spec Review: [Issue #N — Short Title]

- [ ] Test cases cover all acceptance criteria stated in the issue
- [ ] No test is trivially easy (e.g. `assert True`, a test that can't fail)
- [ ] Edge cases are represented (empty input, boundary values, error paths)
- [ ] Coverage scope is appropriate to the ticket type (standard vs. UI
      golden path — see `rules/testing-gate.md` / `rules/frontend-ui-golden-path.md`)
- [ ] Test spec was written from the issue alone — confirm Lane 3 did not
      cite Lane 2's implementation as the basis for any test case

**Approved:** _______  **Date:** _______

**Notes / requested changes before approval:**
