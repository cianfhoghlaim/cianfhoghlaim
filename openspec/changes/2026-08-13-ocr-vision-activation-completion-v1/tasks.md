# Tasks: OCR vision activation completion

## Phase A — Code-only stubs-to-real (no live services required)

- [ ] A1 Replace
  `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:266-283`
  (`_run_path_baml`) — replace the `NotImplementedError` with a real
  `b.Extract<Function>(text=_docling_text, ...)` call. Reuse the
  `baml_function` parameter that's already wired through. Guard the
  import with the existing `BAML_AVAILABLE` pattern.

- [ ] A2 Replace
  `meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py:472-494`
  (`_ragas_vote`) — call `evaluate_ensemble(ensemble_result)` from
  `meaisinfhoghlaim.evaluation.ragas_biiep_ensemble`. Refactor the
  helper signature to return
  `(voted_path, ragas_score, voted_output)` by selecting the winner
  from the `evaluate_ensemble()` return value (highest `composite`).

- [ ] A3 Fix the MLFLOW experiment-name inconsistency at
  `meaisinfhoghlaim/evaluation/ragas_biiep_ensemble.py:1` docstring —
  change `biiep_v2` → `biiep_v3` (the constant at line 49 is correct;
  this is docstring drift only).

## Phase B — Unit tests

- [ ] B1 Create
  `tests/meaisinfoghlaim/backends/test_scanned_detector.py` with
  fixture PDFs covering:
  - Text-rich PDF (chemistry syllabus) → `is_scanned=False`,
    `recommended_backend=""`
  - Scanned-image PDF (a 1-page PNG-only file) → `is_scanned=True`,
    `recommended_backend="qwen3-vl-8b"`
  - Blank/empty PDF → `is_scanned=True`, `recommended_backend=""`

- [ ] B2 `pytest tests/meaisinfoghlaim/backends/test_scanned_detector.py`
  passes locally.

## Phase C — Dagster scanned-PDF fanout

- [ ] C1 Create
  `orchestration/defs/2_materials/ocr_comparison/scanned_pdf_assets.py`
  with 6 per-LC6-subject `@asset`s
  (`scanned_pdf_chemistry`, `scanned_pdf_mathematics`, etc.) that
  call `is_scanned_pdf()` on every PDF in the subject's corpus and
  emit `(is_scanned, image_ratio, recommended_backend)` as the asset's
  MaterializeResult metadata.

- [ ] C2 Update
  `orchestration/defs/2_materials/meaisin_ocr_htr/ocr_model_assets.py`
  to add a `scan_metadata` side-output to the 19 per-model OCR asset
  bundles.

- [ ] C3 Register the new assets in
  `orchestration/defs/2_materials/ocr_comparison/scanned_pdf_assets.py`'s
  `__init__.py` so the dagster `load_defs` walker picks them up.

## Phase D — Validation (no live services required)

- [ ] D1 `mise run lint:registry` returns 0 hardcoded model strings.
- [ ] D2 `pytest tests/meaisinfoghlaim/backends/test_scanned_detector.py`
  passes (3 tests).
- [ ] D3 `mise run sync:dagster` reports the 6 new
  `scanned_pdf_<subject>` assets.
- [ ] D4 `openspec validate 2026-08-13-ocr-vision-activation-completion-v1
  --strict` returns 0 errors.

## Phase E — Live verification (gated on Plan V-A deployment)

- [ ] E1 (after V-A lands) `python scripts/run_biiep_ocr_ensemble.py
  --pdf <chemistry_syllabus.pdf>` returns
  `voted_path in {baml, unstract, qwen3_vl, gemma4}` with
  `ragas_score >= 0.70`.
- [ ] E2 (after V-A lands) `dagster asset materialize --select
  scanned_pdf_*` runs 6 successful materializations.
- [ ] E3 (after V-A lands) `SELECT COUNT(*) FROM
  md:cianfhoghlaim.ocr_results` returns ≥ 4 rows per PDF.

## Out of scope (flagged for follow-up)

- The litellm + llama-swap redeploy (gated on Plan V-A —
  `2026-08-13-biep-v3-orchestration-activation-v1`).
- The KCG Component factory for scanned-PDF assets (the openspec
  change's original `T4.2 + T4.3 deferral`); this change inlines the
  fanout as a plain Dagster asset (C1-C3) rather than waiting for the
  factory. If/when the factory lands, the fanout can be migrated to
  use it.
