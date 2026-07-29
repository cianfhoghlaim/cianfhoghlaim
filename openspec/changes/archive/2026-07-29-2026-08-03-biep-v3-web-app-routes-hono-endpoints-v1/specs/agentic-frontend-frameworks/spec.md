## MODIFIED Requirements

### Requirement: 6 BIEP v3 TanStack routes + 5 BIEP v3 Hono endpoints + per-jurisdiction ACL

The system SHALL provide the 6 BIEP v3 TanStack routes, the 5 BIEP v3
Hono endpoints, the mount of the 3 BIEP v2 + 5 BIEP v3 Hono endpoints,
AND the per-jurisdiction ACL on the BIEP v3 endpoints.

#### Scenario: 6 BIEP v3 TanStack routes exist

- **WHEN** `marimo run` runs against the renamed `apps/web/src/routes/biep-v2/index.tsx`
- **THEN** TanStack SHALL regenerate `routeTree.gen.ts` to include
  the `/biep-v2` route
- **AND** all 6 BIEP v3 routes SHALL be registered in the route tree

#### Scenario: 5 BIEP v3 Hono endpoints mounted

- **WHEN** `curl localhost:8000/api/v1/biep-v3/ireland` runs
- **THEN** the response SHALL be 200 OK with paginated rows from the registry
- **AND** all 5 BIEP v3 endpoints SHALL be mounted (ireland, england,
  sct_wls_ni, crown, registry)
- **AND** the 3 BIEP v2 endpoints (lc, jc, england) SHALL also be
  mounted (they're orphaned today)

#### Scenario: Per-jurisdiction ACL on BIEP v3 endpoints

- **WHEN** an unauthenticated request hits any BIEP v3 endpoint
- **THEN** the response SHALL be 401 Unauthorized
- **WHEN** an authenticated request lacks the required jurisdiction claim
- **THEN** the response SHALL be 403 Forbidden

#### Scenario: Cache-Control header on BIEP v3 responses

- **WHEN** any BIEP v3 response is returned
- **THEN** the `Cache-Control` header SHALL be
  `private, max-age=60, stale-while-revalidate=300`