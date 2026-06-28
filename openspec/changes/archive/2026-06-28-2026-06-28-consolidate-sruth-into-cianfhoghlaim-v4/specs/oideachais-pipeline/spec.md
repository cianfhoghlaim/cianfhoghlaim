# Spec Delta — oideachais-pipeline

## ADDED Requirements

### Requirement: Ireland Education Asset Location (v4)

The system SHALL store Ireland early-childhood, primary, junior-cycle, senior-cycle, and Leaving-Cert assets under `cianfhoghlaim/assets/` keyed by `ireland.education.{stage}.{language}`, where `stage ∈ {aistear, primary, junior_cycle, senior_cycle, leaving_cert_syllabus, leaving_cert_exam_paper, leaving_cert_marking_scheme}` and `language ∈ {english, gaeilge}`. Dagster asset key prefix changes from `oideachais.*` to `ireland.education.*`.

#### Scenario: Dagster asset resolution

- **WHEN** Dagster materialises an Ireland syllabus asset
- **THEN** the asset key is `ireland_education_leaving_cert_syllabus_english` (snake_case of `ireland.education.leaving_cert_syllabus.english`)
- **AND** the source module is `cianfhoghlaim.sources.nations.ie.education.leaving_cert.english`
- **AND** the BAML function is `cianfhoghlaim.core.baml.curriculum.ExtractLeavingCertSyllabus`
- **AND** the CocoIndex embedding flow is `cianfhoghlaim.core.cocoindex.ocr_aware_flow`

### Requirement: Leabharlann Asset Location (v4)

The system SHALL store leabharlann (personal archive) assets under `cianfhoghlaim/assets/leabharlann.py` keyed by `leabharlann.{corpus}.{document}`, where `corpus ∈ {aigne, gaeilge, gemini_deep_research, mata, ollscoil_na_gaillimhe, zotero}`. The physical corpus directory moves from `/leabharlann/` at repo root to `cianfhoghlaim/leabharlann/`.

#### Scenario: Leabharlann DAG asset resolution

- **WHEN** Dagster materialises a Zotero asset
- **THEN** the asset key is `leabharlann_zotero_paper`
- **AND** the source module is `cianfhoghlaim.pipelines.ingest.leabharlann.zotero`
- **AND** the CocoIndex flow is `cianfhoghlaim.core.cocoindex.leabharlann_flow`
- **AND** the destination is `ducklake://oideachais.leabharlann.zotero`

### Requirement: 16 Core Stack Packages (v4)

The system SHALL organise stack concerns under 16 `cianfhoghlaim/core/` packages: `dlt`, `duckdb`, `ducklake`, `lancedb`, `motherduck`, `cocoindex`, `baml`, `marimo`, `browser`, `cognee`, `obs`, `rag`, `search`, `curriculum`, `config`, `memory`.

#### Scenario: Cross-package import

- **WHEN** a developer imports `from cianfhoghlaim.core.lancedb import HnswConfig`
- **THEN** the import resolves to `cianfhoghlaim/core/lancedb/hnsw.py` (the canonical home, formerly at `sruth/oideachais/lancedb/indexing.py`)

### Requirement: 5-Stage Pipeline Spine (v4)

The system SHALL organise pipeline code under 5 `cianfhoghlaim/pipelines/` stages: `browser`, `ingest`, `distribute`, `process`, `expose`. Each stage is independently runnable from Dagster.

#### Scenario: Stage composition

- **WHEN** Dagster materialises an Ireland Leaving Cert paper
- **THEN** stage `browser` loads the PDF via `core/browser/sruth_browser/`
- **AND** stage `ingest` writes to local DuckDB via `core/duckdb/`
- **AND** stage `distribute` writes to DuckLake via `core/ducklake/`
- **AND** stage `process` runs CocoIndex OCR-aware flow via `core/cocoindex/`
- **AND** stage `expose` queries via `core/motherduck/` + `notebooks/ireland_curriculum_analysis.py`