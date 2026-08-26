# Tasks: 2026-08-25-post-cascade-followups

## Phase 1: Real Convex schema (1 task)

- [x] **T1.1**: Replace the Wave 6 stub with the 7-table schema at `web/packages/db/convex/schema.ts`

## Phase 2: Real AG-UI SSE handler (1 task)

- [x] **T2.1**: Replace the Wave 6 hello-event stub with the streaming implementation at `web/hono-api/src/routes/agui/index.ts` (4 endpoints)

## Phase 3: .env.example wire-up (1 task)

- [x] **T3.1**: Append the 4 missing env vars to `.env.example` (`CIANFHOGHLAIM_MOTHERDUCK_TOKEN`, `CONVEX_URL`, `CIANFHOGHLAIM_RUNTIME_URL`, `MLFLOW_TRACKING_URI`)

## Phase 4: Openspec change (3 tasks)

- [x] **T4.1**: Create `openspec/changes/2026-08-25-post-cascade-followups/proposal.md`
- [x] **T4.2**: Create `openspec/changes/2026-08-25-post-cascade-followups/tasks.md` (this file)
- [x] **T4.3**: Create `openspec/changes/2026-08-25-post-cascade-followups/specs/post-cascade-followups/spec.md`

## Phase 5: Verification + commit + push + tag (3 tasks)

- [ ] **T5.1**: `uv run python scripts/lint_drift_docs.py --dry-run` exits 0
- [ ] **T5.2**: Commit + push
- [ ] **T5.3**: Tag `v2026.08.25-post-cascade-followups`

## Total: 9 tasks across 5 phases

Estimated effort: ~1 day. This PR delivers the 3 highest-impact
follow-ups from the Wave 8 deferred list.
