# 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify A1 merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Move the orphaned `/biep-v2` page

- [ ] `git mv web/apps/cianfhoghlaim-web/src/routes/biep-v2/index.tsx
  web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v2/index.tsx`
- [ ] `git rm web/apps/cianfhoghlaim-web/src/routes/biep-v2/__init__.tsx`

## Stage 2 — Create the 5 BIEP v3 Hono endpoints

- [ ] Create `web/hono-api/src/routes/biep-v3/index.ts` (barrel)
- [ ] Create `web/hono-api/src/routes/biep-v3/ireland.ts` — paginated Ireland
  cohorts from `dlt.british_isles._cross.registry_api.query_by_jurisdiction("ireland")`
- [ ] Create `web/hono-api/src/routes/biep-v3/england.ts`
- [ ] Create `web/hono-api/src/routes/biep-v3/sct_wls_ni.ts`
- [ ] Create `web/hono-api/src/routes/biep-v3/crown.ts`
- [ ] Create `web/hono-api/src/routes/biep-v3/registry.ts` — full registry
  + 12 cross-jurisdiction bridges (with rate limiting per IP)

## Stage 3 — Mount the 3 BIEP v2 + 5 BIEP v3 Hono endpoints

- [ ] Edit `web/hono-api/src/index.ts:34-41` — add:
  ```ts
  import biepV2 from "./routes/biep-v2";
  import biepV3 from "./routes/biep-v3";
  app.route("/", biepV2.lc);
  app.route("/", biepV2.jc);
  app.route("/", biepV2.england);
  app.route("/", biepV3.ireland);
  app.route("/", biepV3.england);
  app.route("/", biepV3.sct_wls_ni);
  app.route("/", biepV3.crown);
  app.route("/", biepV3.registry);
  ```

## Stage 4 — Create 6 BIEP v3 TanStack routes

- [ ] Create `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/index.tsx`
- [ ] Create `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/ireland.tsx`
- [ ] Create `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/england.tsx`
- [ ] Create `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/sct-wls-ni.tsx`
- [ ] Create `web/apps/cianfhoghlaim-web/apps/web/src/routes/biep-v3/crown.tsx`
- [ ] Create `web/apps/cianfhoghlaim-web/apps/web/src/routes/registry.tsx`

## Stage 5 — Auth + per-jurisdiction ACL

- [ ] Edit `web/hono-api/src/middleware.ts:29-46` — add a `requireClaim(claim)`
  helper for the 8 jurisdiction slugs
- [ ] Add `Cache-Control: private, max-age=60` headers to all BIEP v3
  responses

## Stage 6 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1/specs/agentic-frontend-frameworks/spec.md`
- [ ] Run `openspec validate 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-03-biep-v3-web-app-routes-hono-endpoints-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol