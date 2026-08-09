# Proposal: OCR Vision Activation + Scanned-PDF Fanout

**Change ID:** `2026-08-10-ocr-vision-activation-v1`
**Date:** 2026-08-10
**Author:** Build agent
**Status:** Draft

## Why

The BIEP v2 4-path OCR/VLM ensemble has been architecturally complete since the 2026-07-22 trilogy but the production wiring is **stubbed in 3 critical places**:

1. `orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py` — the asset body returns `rows_landed: 0` without invoking any of the 4 paths
2. `meaisinfoghlaim/ocr/ensemble/ensembled_extractor.py` — `_run_path_baml()` raises `NotImplementedError`
3. `dlt_sources/british_isles/ireland/education/_pdf_text.py` — the shared `extract_pdf_text()` returns `[PDF_TEXT_STUB]` placeholder when `pymupdf.get_text()` returns empty (the scanned-PDF signal)

This change activates the ensemble end-to-end with real VLM calls + adds scanned-PDF detection at the file level + writes the canonical `ocr_results` table to MotherDuck.

## What changes

### Code (4 new + 6 modified)

| File | Status | What |
|---|---|---|
| `meaisinfoghlaim/backends/scanned_detector.py` | **NEW** | `ScannedPDFReport` dataclass + `is_scanned_pdf()` function |
| `scripts/migrate_ocr_results_table.py` | **NEW** | CREATE TABLE IF NOT EXISTS `md:cianfhoghlaim.ocr_results` |
| `scripts/run_biiep_ocr_ensemble.py` | **NEW** | CLI runner for `EnsembledExtractor.extract()` |
| `dlt_sources/british_isles/ireland/education/_pdf_text.py` | modified | Call `is_scanned_pdf()` before stub fallback |
| `dlt_sources/filesystem/leaving_cert_source.py` | modified | `_row()` emits `is_scanned` + `image_ratio` columns |
| `meaisinfoghlaim/ocr/ensemble/ensembled_extractor.py` | modified | `_run_path_baml()` calls real BAML; `_ragas_vote()` uses `evaluate_ensemble()` |

### Spec (1 spec delta, +4 ADDED Requirements)

- `openspec/specs/meaisinfoghlaim-ocr-htr/spec.md` — 4 new Requirements

## Success criteria

1. `openspec validate 2026-08-10-ocr-vision-activation-v1 --strict` returns 0 errors
2. `mise run lint:registry` returns 0 hardcoded model strings
3. `python scripts/migrate_ocr_results_table.py` creates the table
