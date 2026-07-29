# 2026-08-08-biep-v3-production-readiness-v1 — Tasks

## Pre-implementation
- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1

## Stage 1 — Real OCR ensemble wiring
- [ ] Edit `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:160-219`
  - replace `_call_docling` with real httpx POST
  - replace `_call_unstract` with real httpx POST
  - replace `_call_qwen3_vl` with real httpx POST
  - replace `_call_gemma4` with real httpx POST
- [ ] Add `tenacity` retry + circuit breaker per path

## Stage 2 — Real RAGAS evaluation
- [ ] Edit `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py:122-130`
  - replace `_heuristic_score` with `ragas.metrics.{faithfulness,...}.single_turn_score(...)`
  - Rename `MLFLOW_EXPERIMENT_NAME = "biiep_v2"` → `"biiep_v3"`

## Stage 3 — Real DuckLake writes
- [ ] Edit `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:266-300`
  - implement real `_land_paths_in_ducklake`
  - atomic `BEGIN; ...; COMMIT;` writes

## Stage 4 — Subject-scoped backfill job
- [ ] Create `orchestration/defs/2_materials/{jurisdiction}_education/backfill_job.py`

## Stage 5 — Daily 8-jurisdiction declarative automation
- [ ] Create `orchestration/automation/biiep_daily_automation.py`
- [ ] Retire the dangling 6-hour `ScheduleDefinition` at `biiep_ocr_ensemble.py:126-132`

## Stage 6 — CocoIndex consumes voted DuckLake output
- [ ] Create `cocoindex/subjects/education_subject_embedding.py`

## Stage 7 — Spec delta + validation
- [ ] Write spec delta to `openspec/changes/2026-08-08-biep-v3-production-readiness-v1/specs/infrastructure-stacks/spec.md`
- [ ] `openspec validate 2026-08-08-biep-v3-production-readiness-v1 --strict`
- [ ] Commit + push
- [ ] Archive after merge

## Post-implementation
- [ ] File any remaining bugs
- [ ] Run `./scripts/sync_agent_docs.sh`