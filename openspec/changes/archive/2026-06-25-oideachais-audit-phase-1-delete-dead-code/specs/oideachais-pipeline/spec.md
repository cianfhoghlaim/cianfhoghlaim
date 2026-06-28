## ADDED Requirements

### Requirement: Round 11 Phase 1 — Confirmed-Dead Code Removed (2026-06-25)

The `oideachais-pipeline` capability spec MUST acknowledge that Round 11 of the
multi-quadrant sprawl audit (executed 2026-06-25) removed 14 confirmed-dead
items from `sruth/oideachais/`. The deletions were verified via pre-flight
grep across `sruth/oideachais/dagster_defs`, `sruth/oideachais/api`,
`sruth/oideachais/dlt_sources`, `sruth/oideachais/scripts`,
`sruth/oideachais/notebooks`, `sruth/oideachais/tests`,
`sruth/oideachais/cocoindex_flows`, `sruth/oideachais/cognee_integration`,
`sruth/oideachais/graph`, `sruth/oideachais/lancedb`, `sruth/oideachais/agents`,
`sruth/oideachais/alignment`, and `sruth/oideachais/ocr` (0 matches found for
each deleted item, excluding `__pycache__`).

#### Scenario: A developer queries the canonical layout

- **GIVEN** the openspec change `oideachais-audit-phase-1-delete-dead-code`
  is archived
- **WHEN** a developer runs `ls sruth/oideachais/`
- **THEN** the directory count is 55 (down from 61)
- **AND** the following paths no longer exist:
  - `sruth/oideachais/oideachais/` (nested legacy shim)
  - `sruth/oideachais/services/` (only contained the deleted embedding_service)
  - `sruth/oideachais/services/embedding_service/` (dead FastAPI)
  - `sruth/oideachais/marimo/` (dead 1-file stub)
  - `sruth/oideachais/exam_scraper/` (dead 2-script)
  - `sruth/oideachais/downloads/` (empty mount)
- **AND** the following root-level files no longer exist:
  - `sruth/oideachais/leaving_cert_timetable.pdf` (270 KB orphan)
  - `sruth/oideachais/PIPELINE_OPERATIONS.md` (orphaned doc)
  - `sruth/oideachais/test_api.py`
  - `sruth/oideachais/test_crawl.py`
  - `sruth/oideachais/test_crawl2.py`
  - `sruth/oideachais/test_full_crawl.py`
  - `sruth/oideachais/test_all_sources.py`

#### Scenario: Embedding service migration path

- **WHEN** any caller needs text embeddings after the deletion
- **THEN** they MUST use `sruth.oideachais.clients.embedding_client.EmbeddingClient`
  (the canonical in-process client with BGE-M3 fallback per the
  `embedding-pipeline` skill)
- **AND** NOT import from `sruth.oideachais.services.embedding_service`
  (the deleted module)

#### Scenario: OCR comparison migration path

- **WHEN** any caller needs OCR comparison outputs after the deletion
- **THEN** they MUST use `sruth/meaisinfhoghlaim/marimo/01_leabharlann_descriptive.py`
  (the canonical descriptive stats notebook)
- **OR** the Dagster asset at
  `sruth/oideachais/dagster_defs/assets/ocr_comparison_assets.py`
  (the canonical programmatic interface)
- **AND** NOT import from `sruth.oideachais.marimo.ocr_comparison_enhanced`
  (the deleted module)

#### Scenario: SEC exam paper ingestion migration path

- **WHEN** any caller needs SEC exam paper ingestion after the deletion
- **THEN** they MUST use the `ireland_examinations` DLT source via
  `sruth.oideachais.dlt_sources.ireland.examinations` and the
  `ireland/education/exam_materials_assets.py` Dagster asset group
- **AND** NOT import from `sruth.oideachais.exam_scraper.{retry_failed,scrape_exam_stats}`
  (the deleted modules)

#### Scenario: Test author path

- **WHEN** any test author writes a new test for the oideachais quadrant
- **THEN** they MUST place it under `sruth/oideachais/tests/` following the
  existing per-test-file or per-test-module pattern with `conftest.py` fixtures
- **AND** NOT place test scripts at the root of `sruth/oideachais/`
  (the 5 deleted root-level test scripts are the canonical example of the
  anti-pattern that has now been removed)
