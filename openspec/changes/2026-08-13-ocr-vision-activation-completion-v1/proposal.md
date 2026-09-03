# Change: OCR vision activation completion (close the 3 stubbed paths + scanned-PDF fanout)

## Why

The `2026-08-10-ocr-vision-activation-v1` change shipped the
foundation for BIEP v2's 4-path OCR/VLM ensemble, but **3 of its 17
tasks remain incomplete** and **2 tasks are flagged "marked-done but
actually still stubbed"**:

1. **T3.1 — `_run_path_baml()` is still a stub.** The task is marked
   `[x]` in `tasks.md:Phase 3` but the code at
   `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:283` still
   raises `NotImplementedError("BAML path pending Phase B1")`. Path 1
   of the 4-path ensemble is therefore unreachable — every
   `EnsembledExtractor.extract()` invocation logs
   `EnsemblePathOutput(error="baml path pending Phase B1")` and the
   `_ragas_vote` scores the path at 0.0 (because `_heuristic_score`
   returns 0.0 for any path with an `error` attribute).

2. **T3.2 — `_ragas_vote()` doesn't use `evaluate_ensemble()`.** The
   task is marked `[x]` but the code at
   `ensembled_extractor.py:472-494` uses inline scoring, not the
   canonical `evaluate_ensemble()` from
   `meaisinfhoghlaim.evaluation.ragas_biiep_ensemble`. The MLflow
   observability hook (which only fires when `evaluate_ensemble()` is
   called) is therefore never reached.

3. **T1.3 — Unit tests for `is_scanned_pdf()` don't exist.** The
   scanned-PDF detector at
   `meaisinfoghlaim/backends/scanned_detector.py:118` is wired into
   `dlt_sources/british_isles/ireland/education/_pdf_text.py` and
   `dlt_sources/filesystem/leaving_cert_source.py` per the openspec
   change's Phase 2, but no test suite covers it.

4. **T4.2 + T4.3 — Dagster fanout is deferred to the KCG Component
   factory.** The change notes these tasks are "deferred — KCG
   Component generates the asset" but no such generation has happened.
   `scanned_pdf_assets.py` and `ocr_model_assets.py` updates remain
   outstanding.

5. **Discovered inconsistency**: the docstring at
   `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py:1` says "logged
   to MLflow experiment `biiep_v2`" but the constant at line 49 is
   `MLFLOW_EXPERIMENT_NAME = "biiep_v3"`. Pre-existing drift that
   this change corrects as a bonus.

## What Changes

- **Replace `_run_path_baml()` stub** at
  `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:266-283`
  with a real BAML call against the docling-extracted text. The
  `baml_function` parameter is already wired through; the new body
  imports `baml_client.baml_client.sync_client` and calls
  `b.Extract<Function>(text=docling_text, ...)` against the canonical
  LC5 / LC6 extraction functions.
- **Replace `_ragas_vote()` inline scoring** at
  `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:472-494`
  with a real `evaluate_ensemble(ensemble_result)` call. Refactor the
  helper signature to return `(voted_path, ragas_score, voted_output)`
  by selecting the winner from the `evaluate_ensemble()` return value.
- **Fix the MLFLOW experiment name inconsistency** —
  `MLFLOW_EXPERIMENT_NAME = "biiep_v3"` is correct (per the
  `register_biiep_v3_metrics()` function name); update the
  `evaluate_ensemble()` docstring from `biiep_v2` to `biiep_v3`.
- **Add unit tests** for `is_scanned_pdf()` at
  `tests/meaisinfoghlaim/backends/test_scanned_detector.py` — covers
  the 3 main thresholds (`TEXT_DENSITY_THRESHOLD = 50`,
  `BLANK_PAGE_RATIO_THRESHOLD = 0.8`, `IMAGE_HEAVY_THRESHOLD = 0.5`)
  with fixture PDFs.
- **Add Dagster scanned-PDF fanout** at
  `orchestration/defs/2_materials/ocr_comparison/scanned_pdf_assets.py`
  — one asset per LC6 subject that calls `is_scanned_pdf()` on every
  PDF and routes to `recommended_backend` via `select_ocr_backend()`.
- **Wire scanned-PDF detection into `ocr_model_assets.py`** — the 19
  per-model OCR asset bundles gain a `scan_metadata` side-output that
  exposes `is_scanned` + `image_ratio` columns.
- Add 2 new Requirements to the `meaisinfhoghlaim-ocr-htr` spec
  formalising the "4-path ensemble MUST have 4 real paths" and the
  "scanned-PDF detector MUST be unit-tested" invariants.

## Dependencies

`Blocked by: none`. `Blocked by (soft):
2026-08-13-biep-v3-orchestration-activation-v1` (Plan V-A — the
4-path ensemble can only fully run end-to-end once litellm + llama-swap
are redeployed; this change fixes the code paths but the live
end-to-end round-trip is gated on V-A's deployment work).
`Affected repos: cianfhoghlaim (single repo)`.

## Impact

- Capabilities: MODIFIED `meaisinfhoghlaim-ocr-htr` (2 ADDED
  Requirements).
- Code: `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py`
  (~100 LOC) + `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py`
  (~10 LOC) + new
  `tests/meaisinfoghlaim/backends/test_scanned_detector.py` (~80
  LOC) + new
  `orchestration/defs/2_materials/ocr_comparison/scanned_pdf_assets.py`
  (~200 LOC) + `orchestration/defs/2_materials/meaisin_ocr_htr/ocr_model_assets.py`
  (~50 LOC).
- Risk: medium — touching the 4-path ensemble is the most
  load-bearing OCR code in the platform; unit tests + the canonical
  chemistry-pilot smoke test reduce risk.
