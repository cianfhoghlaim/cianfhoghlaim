# Tasks: croilar-devtools-hub

## Phase 0 — OpenSpec setup

- [x] 0.1 Create change directory `openspec/changes/croilar-devtools-hub/`
- [x] 0.2 Write `proposal.md`
- [x] 0.3 Write `tasks.md`
- [x] 0.4 Write `specs/croilar-data-engineering/spec.md` (MODIFIED)
- [x] 0.5 Write `specs/croilar-portfolio/spec.md` (MODIFIED)
- [x] 0.6 Write `specs/croilar-devtools-hub/spec.md` (NEW)
- [ ] 0.7 Run `openspec validate croilar-devtools-hub --strict` until green

## Phase A — Convex observability of the web stack

- [ ] A.1 Add 9 tables to `croilar/convex/schema.ts`
- [ ] A.2 Create `croilar/convex/tanstack_routes.ts`
- [ ] A.2 Create `croilar/convex/convex_functions.ts`
- [ ] A.2 Create `croilar/convex/cloudflare_resources.ts`
- [ ] A.2 Create `croilar/convex/baml_schemas.ts`
- [ ] A.2 Create `croilar/convex/test_runs.ts`
- [ ] A.2 Create `croilar/convex/convex_function_calls.ts`
- [ ] A.2 Create `croilar/convex/convex_metrics.ts`
- [ ] A.2 Create `croilar/convex/marimo_notebooks.ts`
- [ ] A.2 Create `croilar/convex/glance_config.ts`
- [ ] A.3 Create `croilar/convex/_middleware.ts` with `loggedAction` helper
- [ ] A.4 Append 6 new cron entries to `croilar/convex/crons.ts`
- [ ] A.5 Write `croilar/scripts/analyze-web-stack.ts` (Bun)
- [ ] A.6 Add `CROILAR_CONVEX_DEPLOY_KEY` to `.infisical.env`
- [ ] A.7 Write `croilar/tests/test_web_analyzer.py` (analyzer fixtures)
- [ ] A.7 Write `croilar/tests/test_convex_modules.py` (schema + refreshAll)
- [ ] A.7 Write `croilar/tests/test_action_middleware.py` (loggedAction contract)

## Phase B — Live portal binding

- [ ] B.1 Rewrite `croilar/apps/portal/src/routes/_layout/data/pipelines.tsx`
- [ ] B.1 Rewrite `croilar/apps/portal/src/routes/_layout/monitoring/logs.tsx`
- [ ] B.1 Rewrite `croilar/apps/portal/src/routes/_layout/monitoring/metrics.tsx`
- [ ] B.2 Create `croilar/apps/portal/src/routes/_layout/web/index.tsx`
- [ ] B.2 Create `croilar/apps/portal/src/routes/_layout/web/$project.tsx`
- [ ] B.2 Add `currentRole` query to `croilar/convex/helpers.ts`
- [ ] B.3 Create `croilar/apps/portal/src/routes/_layout/notebooks/index.tsx`
- [ ] B.3 Create `croilar/apps/portal/src/routes/_layout/notebooks/$slug.tsx`
- [ ] B.4 Create `croilar/notebooks/streams/teaching/web_route_health.py`
- [ ] B.4 Create `croilar/notebooks/streams/teaching/convex_function_latency.py`
- [ ] B.4 Create `croilar/notebooks/streams/teaching/baml_extraction_quality.py`
- [ ] B.5 Extend `croilar/tests/test_smoke.py` with new portal page tests

## Phase C — Glance auto-generation + devtools MCP

- [ ] C.1 Write `croilar/scripts/regenerate-glance-config.ts` (Bun)
- [ ] C.2 Update `infrastructure/stacks/infrastructure/glance/pangolin.yaml` (add 4 sub-paths)
- [ ] C.2 Update `infrastructure/stacks/infrastructure/glance/blueprint.yaml` (add 4 sub-paths)
- [ ] C.3 Create `infrastructure/komodo/procedures/croilar-glance-regenerate.toml`
- [ ] C.4 Create `croilar/mcp/devtools/{package.json, src/index.ts, src/tools/*.ts}`
- [ ] C.4 Register `mcp.croilar-devtools` in `opencode.json`
- [ ] C.5 Write `croilar/tests/test_glance_regenerator.py`
- [ ] C.5 Write `croilar/tests/test_devtools_mcp.py`

## Phase 6 — Quality gates

- [ ] 6.1 `openspec validate croilar-devtools-hub --strict` — must pass
- [ ] 6.2 `bun run turbo typecheck` for `croilar/apps/{web,portal}` — must pass
- [ ] 6.3 `uv run pytest croilar/tests/` — all green
- [ ] 6.4 `bun run ccc:index` then `bun run ccc:search "devtools hub"` — confirm discoverability
- [ ] 6.5 `mise turbo build dagster` — code-location still loads

## Phase 7 — Commit, push, follow-up

- [ ] 7.1 `git add -A`
- [ ] 7.2 `git commit -m "feat(croilar): add devtools hub (Convex observability, live portal, Glance/MCP)"`
- [ ] 7.3 `git push --set-upstream origin feat/croilar-devtools-hub`
- [ ] 7.4 File follow-up issues (Phase D, Phase E, meaisínfhoghlaim web analyzer, test-runs CI ingest, cross-project BAML test corpus)
- [ ] 7.5 Update `croilar/README.md` and `stack.md` with the new hub
- [ ] 7.6 `openspec archive croilar-devtools-hub --yes` after deployment
