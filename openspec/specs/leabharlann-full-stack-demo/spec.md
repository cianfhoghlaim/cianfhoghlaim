# `leabharlann-full-stack-demo` capability spec

## Purpose

`leabharlann-full-stack-demo` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `oideachais/dagster_defs/assets/leabharlann_demo_assets.py` and `oideachais/notebooks/leabharlann_full_stack_demo.py`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

A Dagster asset that processes 2 sample leabharlann PDFs end-to-end through the full stack (pymupdf → BAML → CocoIndex v1 → LanceDB), with asset checks and a Marimo notebook UI.

## Requirements

### Requirement: oideachais_cocoindex_leabharlann_full_stack_demo asset
The system SHALL register 1 new Dagster asset that takes 2 sample PDFs and processes them end-to-end.

#### Scenario: Sample PDFs
- **GIVEN** the asset is materialised
- **WHEN** it runs
- **THEN** the sample PDFs SHALL be:
  - `leabharlann/ollscoil_na_gaillimhe/irish/gaeilge.pdf` (Irish language exam, processed by `b.ExtractUoGArtifact`)
  - `leabharlann/zotero/Handwritten Text Recognition (HTR) for Irish-Langu.pdf` (processed by `b.ExtractZoteroMetadata`)

#### Scenario: 5-step pipeline
- **GIVEN** the asset is materialised
- **WHEN** it runs
- **THEN** the 5 steps SHALL execute in order:
  1. Extract text via pymupdf
  2. Call `b.ExtractUoGArtifact` and `b.ExtractZoteroMetadata` respectively
  3. Embed the chunks via the v1 CocoIndex Apps (`LeabharlannBooksEmbedding`, `LeabharlannZoteroEmbedding`)
  4. Store the embedded chunks in LanceDB (REST endpoint at `lance-api.cianfhoghlaim.ie`)
  5. Record the result metadata in a DuckDB table `leabharlann_full_stack_demo`

#### Scenario: Asset checks
- **GIVEN** the asset materialisation is complete
- **WHEN** the asset checks run
- **THEN** the following checks SHALL pass:
  - `pdf_extraction_status == "ok"`
  - `baml_extraction_status == "ok"`
  - `cocoindex_chunks_count > 10`
  - `lance_table_size_bytes > 1000`

### Requirement: Marimo notebook
The system SHALL provide a Marimo notebook that renders the 5-step pipeline as an interactive UI.

#### Scenario: Notebook renders
- **GIVEN** a user navigates to `/dashboards/leabharlann`
- **WHEN** the page loads
- **THEN** the Marimo notebook SHALL render the 5-step pipeline:
  - Step 1: Text extraction preview
  - Step 2: BAML extracted fields
  - Step 3: Top-5 similar chunks from LanceDB
  - Step 4: Cognee episode count (deferred to Feature 2 — returns 0 for now)
  - Step 5: Final status panel
