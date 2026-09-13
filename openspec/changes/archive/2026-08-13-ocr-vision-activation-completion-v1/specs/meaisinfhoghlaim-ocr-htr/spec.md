## ADDED Requirements

### Requirement: 4-path BIEP v2 ensemble — 4 real paths

The system SHALL ensure that `EnsembledExtractor.extract()` in
`meaisinfhoghlaim/ocr/ensemble/ensembled_extractor.py` produces a
real output for all 4 paths (BAML, Unstract, qwen3-vl, gemma4). No
path SHALL raise `NotImplementedError` or return a `[<PATH>_PATH]`
placeholder string. The `_ragas_vote` helper SHALL delegate to the
canonical `evaluate_ensemble()` function in
`meaisinfhoghlaim.evaluation.ragas_biiep_ensemble`, not to inline
scoring.

#### Scenario: All 4 paths produce real outputs for the chemistry syllabus

- **GIVEN** the chemistry syllabus PDF at
  `stedding/ingest_queue/chemistry/SCSEC09_Chemistry_syllabus_Eng.pdf`
- **WHEN** `EnsembledExtractor.extract(pdf_path=...)` runs
- **THEN** the returned `EnsembleResult.paths` list has exactly 4
  `EnsemblePathOutput` records (one per path)
- **AND** no record has `error="baml path pending Phase B1"` or any
  `NotImplementedError`-derived error message
- **AND** `voted_path in {"baml", "unstract", "qwen3_vl", "gemma4"}`
- **AND** `ragas_score >= 0.70`

#### Scenario: RAGAS vote delegates to evaluate_ensemble

- **GIVEN** `_ragas_vote(paths)` is called with a non-empty `paths`
  list
- **WHEN** the helper executes
- **THEN** the helper calls
  `meaisinfhoghlaim.evaluation.ragas_biiep_ensemble.evaluate_ensemble(ensemble_result)`
  to compute per-path scores
- **AND** the helper does not reimplement the scoring inline (no
  separate `sum(subs) / max(len(subs), 1)` block)

### Requirement: Scanned-PDF detector unit-tested

The system SHALL provide a pytest suite at
`tests/meaisinfoghlaim/backends/test_scanned_detector.py` that
exercises the 3 main detection thresholds
(`TEXT_DENSITY_THRESHOLD = 50`, `BLANK_PAGE_RATIO_THRESHOLD = 0.8`,
`IMAGE_HEAVY_THRESHOLD = 0.5`) against fixture PDFs covering the 3
canonical detection outcomes (text-rich, scanned-image, blank/empty).

#### Scenario: Text-rich PDF returns `is_scanned=False`

- **GIVEN** a fixture PDF with > 200 chars of text on every page
  (e.g. chemistry syllabus)
- **WHEN** `is_scanned_pdf(pdf_path)` runs
- **THEN** the returned `ScannedPDFReport.is_scanned` is `False`
- **AND** `recommended_backend` is `""` (text layer is sufficient)

#### Scenario: Scanned-image PDF returns `is_scanned=True` with qwen3-vl

- **GIVEN** a fixture PDF with 1 page of pure PNG content (no
  selectable text)
- **WHEN** `is_scanned_pdf(pdf_path)` runs
- **THEN** the returned `ScannedPDFReport.is_scanned` is `True`
- **AND** `recommended_backend` is `"qwen3-vl-8b"` (the image-heavy
  workhorse)

#### Scenario: Blank/empty PDF returns `is_scanned=True` without backend

- **GIVEN** a fixture PDF with 0 pages of text and 0 images
- **WHEN** `is_scanned_pdf(pdf_path)` runs
- **THEN** the returned `ScannedPDFReport.is_scanned` is `True`
- **AND** `recommended_backend` is `""` (no backend can extract
  useful content from a blank page)
