## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-08-08-biep-v3-production-readiness-v1

## Why

The P2 layer makes the BIEP v3 stack production-ready by replacing
the OCR ensemble stubs with real HTTP/BAML calls + real RAGAS evaluation +
real DuckLake writes + subject-scoped backfill + daily declarative
automation + CocoIndex consuming the voted DuckLake output. 6 items.

Lives in the `cianfhoghlaim` repo.

## What changes

### 1. Real OCR ensemble wiring

`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:160-219` —
replace all 4 `_run_path_*` stubs with real `httpx.AsyncClient` calls:
- `_call_docling` → POST `http://localhost:5001/v1/convert`
- `_call_unstract` → POST `http://localhost:8002/api/v1/deployment/{workflow_id}/process`
- `_call_qwen3_vl` → POST `http://localhost:4000/v1/chat/completions` (LiteLLM)
- `_call_gemma4` → POST `http://localhost:8080/completion` (llama-swap)

Add `tenacity` retry + circuit breaker per path.

### 2. Real RAGAS evaluation

`meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py:122-130` —
replace `_heuristic_score` with `ragas.metrics.{faithfulness,
answer_relevance,context_precision}.single_turn_score(...)`.

Rename `MLFLOW_EXPERIMENT_NAME = "biiep_v2"` → `"biiep_v3"`.

### 3. Real DuckLake writes

`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:266-300` —
implement real `_land_paths_in_ducklake` using `dlt.common.
destinations_cianfhoghlaim.get_dlt_destination(use_ducklake=True)` +
atomic `BEGIN; ...; COMMIT;` writes.

### 4. Subject-scoped backfill job

`orchestration/defs/2_materials/{jurisdiction}_education/backfill_job.py`
(new, ~60 LOC) — `define_asset_job(name=f"{jurisdiction}_lc_mathematics_backfill", selection=[...])`.

### 5. Daily 8-jurisdiction declarative automation

`orchestration/automation/biiep_daily_automation.py` (new, ~30 LOC) —
`AutomationCondition.cron("@daily")` on the partitioned ingestion root.

Retire the dangling 6-hour `ScheduleDefinition` at `biiep_ocr_ensemble.py:126-132`.

### 6. CocoIndex consumes voted DuckLake output

`cocoindex_flows/subjects/education_subject_embedding.py` (new, ~80 LOC)
— a registry-driven app that reads typed/voted output from DuckLake
tables and exports to consistent LanceDB tables.

## Dependencies

```yaml
Blocked by: 2026-08-07-biep-v3-hardening-v1
Affected repos: cianfhoghlaim
```

## Acceptance gates

- The PDF → BAML → DuckLake → CocoIndex chain works end-to-end for one test PDF
- `EnsembledExtractor._call_*` methods return real responses (not sentinels)
- RAGAS scores reflect actual extraction quality (not hard-coded 0.85)
- The 8-jurisdiction declarative automation triggers at midnight UTC
- CocoIndex reads from the DuckLake voted-canonical table

## Cross-references
- `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`
- `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py`
- `orchestration/automation/biiep_daily_automation.py`