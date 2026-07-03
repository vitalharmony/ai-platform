---
paths:
  - "**/*.py"
---

# Backend Python — Universal Hard Constraints

Applies to any Python backend across Vital Harmony projects. Project-specific
addenda (e.g. a Cypher/Neo4j-specific rule file) live in the project's own
`.claude/rules/` and layer on top of this file — they are not part of the
platform sync since they don't apply universally.

## Type Hints

Every function carries an explicit return type hint.

## Pydantic Payloads

All inbound write/update payloads use explicit Pydantic models with
`model_config = ConfigDict(extra="forbid")`. No `dict`, `Any`, or open-ended
types at API boundaries.

**Correct:**
```python
class UpdateProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    location: str | None = None
```

## Query Injection Safety

Any query language with injection risk (SQL, Cypher, etc.) must be
parameterized. f-strings/concatenation to build query bodies are forbidden.

**Correct:**
```python
records = session.run(
    "MATCH (p:Person) WHERE elementId(p) = $person_id RETURN p",
    person_id=person_id,
).data()
```

**Forbidden:**
```python
session.run(f"MATCH (p:Person) WHERE elementId(p) = '{person_id}' RETURN p")
```

## Single-Instance Resources

Any driver/connection-pool singleton (DB driver, cache client) is
instantiated exactly once, in one designated module, at process lifespan.
Never instantiate a second one elsewhere — inject/depend on the singleton.

## LLM Gateway

If the project makes LLM calls, all of them route through one designated
gateway module (`complete()`-style entrypoint). No other module constructs a
provider client directly or hardcodes a model ID. Structured output: use the
gateway's schema-validated entrypoint if one exists rather than hand-rolling
`json.loads(strip_fences(...))` call sites — that pattern is fragile and
silently returns empty results on malformed output.

## Layering

- **Routers/controllers** are thin HTTP layers — validation in/out, no
  business logic.
- **Services** hold business logic.
- Reusable queries live in a dedicated queries module, not inline in
  services or routers.

## Observability

Use the structured logger (`logging.getLogger(__name__)` or project
equivalent) — never `print()` in production paths.

## Async Safety

Never call blocking I/O inside an `async def` without offloading it to a
thread pool. Sync DB drivers, PDF/image libraries, and `requests` all block
the event loop — one slow call starves every concurrent request.

**Correct:**
```python
from starlette.concurrency import run_in_threadpool

result = await run_in_threadpool(session.run, query, **params)
```

## Pre-Submit Checklist

- [ ] Every query call uses parameterized inputs (no f-strings)
- [ ] No new singleton-resource instantiation outside its designated module
- [ ] No new raw `json.loads(strip_fences(...))` call sites for LLM output
- [ ] Every `async def` calling blocking I/O wraps it in a thread-pool offload
