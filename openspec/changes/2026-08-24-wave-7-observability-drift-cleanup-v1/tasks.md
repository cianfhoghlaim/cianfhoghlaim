# Tasks: 2026-08-24-wave-7-observability-drift-cleanup-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-7-observability-drift-cleanup-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-7-observability-drift-cleanup-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-7-observability-drift-cleanup-v1/specs/observability-drift-cleanup/spec.md`

## Phase 2: MlflowBackend (2 tasks)

- [x] **T2.1**: Add `MlflowBackend` class to `observability/unified_tracer.py` (~line 270, before `UnifiedTracer`)
- [x] **T2.2**: Update `UnifiedTracer.__init__` to accept `mlflow_enabled=True` and instantiate `MlflowBackend()`

## Phase 3: OTel semantic conventions (2 tasks)

- [x] **T3.1**: Add `apply_otel_semantic_conventions(span, kind)` helper to `observability/unified_tracer.py` (~line 275)
- [x] **T3.2**: Call `apply_otel_semantic_conventions` from `UnifiedTracer.trace` (mapping `db` → `db`, `llm` → `gen_ai`, `tool` → `object_store`)

## Phase 4: lint:drift-docs fixes (5 tasks)

- [x] **T4.1**: Fix `AGENTS.md:120` — claimed 65 skills, actual 166
- [x] **T4.2**: Fix `bonneagar/AGENTS.md:29,89,155` — claimed 94 stacks, actual 99
- [x] **T4.3**: Fix `notebooks/AGENTS.md:239` — claimed 59 notebooks, actual 67
- [x] **T4.4**: Run `mise run lint:drift-docs` (exits 0)
- [x] **T4.5**: Verify `git diff --stat AGENTS.md` shows the 5 file updates

## Phase 5: Verification (2 tasks)

- [x] **T5.1**: `grep -c "class.*Backend" observability/unified_tracer.py` returns 4
- [x] **T5.2**: OTel convention helpers all pass the unit-test assertions

## Phase 6: Commit + push (2 tasks)

- [ ] **T6.1**: Stage only Wave 7 files
- [ ] **T6.2**: Commit + push

## Total: 16 tasks across 6 phases

Estimated effort: ~2 weeks (per the master plan's Wave 7 estimate).
This PR delivers the framework (MlflowBackend + OTel conventions + drift
fixes). MLflow production wire-up lands in a Wave 7 follow-up PR.
