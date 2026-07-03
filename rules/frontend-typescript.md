---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# Frontend TypeScript — Universal Hard Constraints

Applies to any TypeScript/React frontend across Vital Harmony projects.

## Type Safety

`any` is forbidden. Use `unknown` with type predicates, or an explicit
interface/type.

**Correct:**
```typescript
catch (err: unknown) {
  if (err instanceof Error) setError(err.message)
}
```

**Forbidden:**
```typescript
const data: any = await fetch(...)   // raw fetch + any — both violations
```

## API Calls

All backend calls go through the project's one designated HTTP client
module. No raw `fetch()`/axios calls anywhere else in application code.

## Graceful Degradation

Components must degrade to mock data or empty states when the backend is
offline — never crash or surface an unhandled error to the user.

## Async Cleanup

`useEffect` hooks that fire an API call must cancel on unmount via
`AbortController`.

**Correct:**
```typescript
useEffect(() => {
  const controller = new AbortController()
  apiClient.get<ProfileResponse>('/profiles/123', {
    signal: controller.signal,
  }).then(setProfile).catch(() => {})
  return () => controller.abort()
}, [id])
```

## Runtime Boundary Validation

TypeScript types API responses at compile time only — no runtime guarantee.
Validate required fields before writing a response into component props or
state; don't silently propagate `undefined`.

## 300-Line Cap

If an edit would push any `.ts`/`.tsx` file over 300 lines, decompose into
smaller modules before proceeding.
