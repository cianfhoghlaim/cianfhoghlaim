# 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1

## Why

The BIEP v3 batch shipped 5 generic jurisdiction pipelines covering
~1,560 cohorts across 8 British Isles jurisdictions, but the web
app surface is incomplete:

- The `/biep-v2` page sits at the wrong TanStack depth (should be
  `apps/web/src/routes/biep-v2/index.tsx`, not `src/routes/biep-v2/`)
  so TanStack's route generator never picks it up
- The 3 BIEP v2 Hono endpoints are written but never mounted in
  `web/hono-api/src/index.ts:34-41`
- 0 of 6 BIEP v3 TanStack routes exist (`/biep-v3`,
  `/biep-v3/{ireland,england,sct-wls-ni,crown}`, `/registry`)
- 0 of 5 BIEP v3 Hono endpoints exist
- No per-jurisdiction ACL or rate limiting on the BIEP endpoints

This is the B4 change. It lives in the **cianfhoghlaim repo** (the
web app + Hono API are at `web/apps/cianfhoghlaim-web/` +
`web/hono-api/`).

## What changes

### 1. Move the orphaned `/biep-v2` page

- `git mv web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx
  web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v2/index.tsx`
- Delete the empty `web/apps/cianfhoghlaim-web/src/routes/biep-v2/__init__.tsx`

### 2. Mount the 3 BIEP v2 Hono endpoints + create 5 BIEP v3 Hono endpoints

- Edit `web/hono-api/src/index.ts:34-41` — add the 8 route mounts
- Create `web/hono-api/src/routes/biep-v3/{index,ireland,england,sct_wls_ni,crown,registry}.ts` (6 new files)

### 3. Create 6 BIEP v3 TanStack routes

- `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/index.tsx` (new) — 8-jurisdiction overview
- `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/ireland.tsx` (new) — 544 Ireland cohorts
- `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/england.tsx` (new) — 276 England cohorts
- `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/sct-wls-ni.tsx` (new) — 380 SCT/WLS/NI cohorts
- `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/crown.tsx` (new) — 360 Crown cohorts
- `web/apps/cianfhoghlaim-web/apps/web/src/routes/registry.tsx` (new) — embeds companion notebook

### 4. Auth + per-jurisdiction ACL

- Edit `web/hono-api/src/middleware.ts:29-46` — add `requireClaim(claim)`
  helper for the 8 jurisdiction slugs

## Dependencies

```yaml
Blocked by: 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `bun run web:dev` serves `/biep-v3`, `/biep-v3/ireland`, `/registry`
- `curl localhost:8000/api/v1/biep-v3/ireland` returns 200 OK with paginated rows
- `dg check yaml` passes
- `openspec validate 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 --strict` passes

## Cross-references

- `web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx` (orphaned page)
- `web/hono-api/src/routes/biep-v2/{lc,jc,england}.ts` (orphaned Hono endpoints)
- `web/hono-api/src/middleware.ts:29-46` (the auth middleware)
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` — the TanStack + Hono conventions