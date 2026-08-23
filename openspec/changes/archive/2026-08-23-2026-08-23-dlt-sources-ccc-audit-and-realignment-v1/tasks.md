# Tasks: 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-23-dlt-sources-ccc-audit-and-realignment-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-23-dlt-sources-ccc-audit-and-realignment-v1/tasks.md` (this file)
- [x] **T1.3**: Create `specs/british-isles-education-pipeline-v3/spec.md` (2 ADDED Requirements)

## Phase 2: CCC audit (1 task, ~1 hr) [DONE]

- [x] **T2.1**: CCC audit ALL of `dlt_sources/` (1,957 files) — map @dlt.source + @dlt.resource decorators per subtree (completed in proposal)

## Phase 3: Realignment (4 tasks, ~3-4 hrs)

- [x] **T3.1**: Add 1-line AGENTS.md to each of the 14 sub-trees (gap-fill documentation) — 14 files
- [x] **T3.2**: Wire `british_isles/ireland/education/university_of_galway_deep.py` into BIEP v3 5-phase pattern (1 Dagster asset + 1 CocoIndex App + 1 MotherDuck table)
- [x] **T3.3**: Add `dlt_sources/api_sources/leabharlann_education_notes.py` (the cross-repo bridge for leabharlann maths + CS notes)
- [x] **T3.4**: Update `dlt_sources/DATA_PLATFORM_ROUTER.md` to reflect the audit + the 14 new AGENTS.md files

## Phase 4: Dagster improvements (2 tasks, ~1 hr)

- [x] **T4.1**: Wire `dagster-mlflow` plugin for native MLflow tracing (add to pyproject.toml + update `orchestration/definitions.py`)
- [x] **T4.2**: Add `cognee_health_check` Dagster sensor (per `indexing-and-cognition` spec)

## Phase 5: Validate (1 task, ~5 min)

- [ ] **T5.1**: Run `openspec validate 2026-08-23-dlt-sources-ccc-audit-and-realignment-v1 --strict`

## Phase 6: Commit + push (3 tasks, ~10 min)

- [ ] **T6.1**: Stage only the openspec change files (NOT the 14 AGENTS.md files which are a separate change)
- [ ] **T6.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`
- [ ] **T6.3**: Verify the audit is visible in `openspec list`

## Total: 14 tasks across 6 phases

Estimated effort: ~4-6 hours (the audit is the biggest task; the realignment is mechanical).