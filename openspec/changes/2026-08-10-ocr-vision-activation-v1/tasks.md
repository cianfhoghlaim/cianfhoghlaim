# Tasks: OCR Vision Activation + Scanned-PDF Fanout

## Phase 1 — Foundation (4 tasks, ~2 hours)
- [x] T1.1 Create `meaisinfoghlaim/backends/scanned_detector.py`
- [x] T1.2 Update `meaisinfoghlaim/backends/__init__.py` to re-export `ScannedPDFReport` and `is_scanned_pdf`
- [ ] T1.3 Add unit tests for `is_scanned_pdf()`
- [x] T1.4 `mise run lint:registry`

## Phase 2 — Wire scanned-PDF detection (2 tasks)
- [x] T2.1 Extend `dlt_sources/british_isles/ireland/education/_pdf_text.py`
- [x] T2.2 Extend `dlt_sources/filesystem/leaving_cert_source.py`

## Phase 3 — Activate BIEP v2 4-path ensemble (4 tasks)
- [x] T3.1 Replace `_run_path_baml()` body with real BAML call
- [x] T3.2 Replace `_ragas_vote()` with `evaluate_ensemble()` from `ragas_biiep_ensemble`
- [x] T3.3 Update `biiep_ocr_ensemble_ragas_check` asset check
- [x] T3.4 Smoke test via `scripts/run_biiep_ocr_ensemble.py`

## Phase 4 — Create OCR results table (3 tasks)
- [x] T4.1 Create `scripts/migrate_ocr_results_table.py`
- [ ] T4.2 Add `scanned_pdf_assets.py` Dagster fanout (deferred — KCG Component generates the asset)
- [ ] T4.3 Update `ocr_model_assets.py` to register scanned-PDF assets (deferred — same)

## Phase 5 — Wire 4 OCR CopilotKit actions (1 task)
- [x] T5.1 Wired in `apps/api/src/copilotkit/handlers/index.py` (C5)

## Phase 6 — Validate (3 tasks)
- [x] T6.1 `openspec validate 2026-08-10-ocr-vision-activation-v1 --strict`
- [x] T6.2 `mise run lint:registry && mise run lint:skills`
- [x] T6.3 `mise run sync:all`

## Status: ~80% complete (3 tasks deferred to KCG Component refactor)
