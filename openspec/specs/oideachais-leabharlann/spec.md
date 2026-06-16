# Oideachais Leabharlann Capability

## Purpose

`oideachais-leabharlann` is a capability of the Cianfhoghlaim platform.
The corresponding source code lives at
`oideachais/dlt_sources/author_archive/` (the 4 dlt sources: books,
zotero, takeout, UoG) and `oideachais/cocoindex_flows/leabharlann_embedding.py`
(the 3 v1 CocoIndex Apps). See `docs/00_index.md` for the quadrant map
and `docs/00-core/CLAUDE.md` for the project identity.

This spec was consolidated from the 110-line `leabharlann-ingestion` spec
and the 103-line `author-archive-baml-extraction` spec, plus the file-system
portion of the archived `author-archive-gemini-and-uos-ingestion` change.

## Background

The leabharlann (library) is the user's personal + academic archive
under `leabharlann/` in the repo root. The 4 subdirs are:

- `leabharlann/ollscoil_na_gaillimhe/` (2.2 GB, 5 subdirs: education,
  irish, mata, past, software_development) — the UoG artefacts
- `leabharlann/gemini_deep_research/` (79 MB) — Gemini deep research PDFs
  with inline citations
- `leabharlann/zotero/` (294 MB, 117 PDFs) — academic papers in real
  Zotero storage format (with `_.pdf` empty placeholders, `__dup0`
  duplicate markers, arXiv IDs)
- `leabharlann/gaeilge/` (40 PDFs + 2 MDs + 37 PNG previews) + `aigne/`
  (7 PDFs) — the books corpus
- `leabharlann/ollscoil_na_gaillimhe/previews/` — 37 PNG book covers

The 4 dlt sources scan these dirs, yield 6 resources each, and the
3 v1 CocoIndex Apps embed the chunks in LanceDB (BAAI/bge-large-en-v1.5
for English-only).

## Requirements

### Requirement: Generic leabharlann books source

The system SHALL provide a generic `leabharlann_books` dlt source that
scans `leabharlann/{gaeilge,aigne}/` with the `subject` partition key.

#### Scenario: Books source yields 6 resources

- **GIVEN** PDFs and DOCX files in `leabharlann/gaeilge/` and
  `leabharlann/aigne/`
- **WHEN** the `leabharlann_books_source()` source runs
- **THEN** the source yields 6 resources: `all_documents`,
  `pdf_documents`, `word_documents`, `epub_documents`, `md_documents`,
  `previews` (with the previews-path as a column, not a separate document)

### Requirement: Zotero source with arxiv_id detection

The system SHALL provide a `leabharlann_zotero` dlt source that
scans `leabharlann/zotero/` in real Zotero storage format and detects
arxiv IDs (both modern `2504.02890v2` and pre-DOI `2402`).

#### Scenario: Zotero arxiv_id detected

- **GIVEN** a file `Handwritten Text Recognition (HTR) for Irish-Langu.pdf`
  in `leabharlann/zotero/`
- **WHEN** the `zotero_source()` source runs
- **THEN** the `arxiv_id` column is NULL (no arxiv ID in the filename)
- **AND** the BAML `arxiv_papers_baml` resource invokes
  `b.ExtractZoteroMetadata` on arxiv-ID-bearing papers only

#### Scenario: Empty Zotero placeholder skipped

- **GIVEN** a `_.pdf` empty placeholder in `leabharlann/zotero/`
- **WHEN** the `zotero_source()` source runs
- **THEN** the placeholder is skipped (zero-byte file)

### Requirement: Google Takeout v1 source

The system SHALL provide a `leabharlann_takeout_v1` dlt source that
auto-discovers Google Takeout directories (with or without an account
prefix) and zip files at `~/Downloads/takeout-*.zip`.

#### Scenario: No-account-prefix Takeout layout

- **GIVEN** a directory `stedding/Takeout/Drive/` (no `<account>/` prefix)
- **WHEN** the `takeout_v1_source()` source runs
- **THEN** the `account_label` is auto-set to `stedding_takeout`
- **AND** all 64 docx files + 1 csv file in `Drive/` are loaded

#### Scenario: Multi-account Takeout layout

- **GIVEN** a directory `stedding/Takeout/<account>/Drive/` (with prefix)
- **WHEN** the `takeout_v1_source()` source runs
- **THEN** the `account_label` is set to the directory name

### Requirement: University of Galway artefacts source

The system SHALL provide a `leabharlann_university_of_galway` dlt
source that scans `leabharlann/ollscoil_na_gaillimhe/` for UoG artefacts.

#### Scenario: UoG artefact scan yields 6 resources

- **GIVEN** PDFs + DOCX + Apple Pages files in `leabharlann/ollscoil_na_gaillimhe/`
- **WHEN** the `university_of_galway_source()` source runs
- **THEN** the source yields 6 resources with the `domain` partition
  key (education | irish | mata | past | software_development)

### Requirement: Gemini deep research source with citation extraction

The system SHALL provide a `leabharlann_gemini_deep_research` dlt
source that scans `leabharlann/gemini_deep_research/` for Gemini
deep-research PDFs and extracts inline citations via PyMuPDF.

#### Scenario: Gemini citations extracted

- **GIVEN** a Gemini deep research PDF with N inline citations
- **WHEN** the `gemini_deep_research_source()` source runs
- **THEN** the `gemini_citations` column contains N rows (one per
  citation, with `url` + `source_file_hash`)

### Requirement: 3 v1 CocoIndex Apps

The system SHALL provide 3 CocoIndex v1 Apps that embed the leabharlann
corpora into LanceDB: `LeabharlannBooksEmbedding`,
`LeabharlannZoteroEmbedding`, `LeabharlannTakeoutEmbedding`.

#### Scenario: v1 App embeds chunks

- **GIVEN** the books dlt source has materialised N rows
- **WHEN** the `LeabharlannBooksEmbedding` App runs (`cocoindex update`)
- **THEN** the App embeds the chunks with BAAI/bge-large-en-v1.5 (1024-d)
- **AND** the embeddings are written to LanceDB (REST or blob)
- **AND** the App uses `IdGenerator()` for stable IDs

### Requirement: Dagster asset group

The system SHALL register 7 Dagster assets in the
`leabharlann_ingestion` group: 3 raw ingest (books, zotero, takeout) +
1 BAML metadata extraction + 3 CocoIndex v1 embedding updates.

#### Scenario: 7 assets register

- **GIVEN** the 4 dlt sources + the 3 CocoIndex Apps are configured
- **WHEN** the Dagster code-location is loaded
- **THEN** 7 assets appear in the `leabharlann_ingestion` group

### Requirement: Full-stack demo asset

The system SHALL provide a `leabharlann_full_stack_demo` Dagster asset
that exercises the entire stack on 2 sample PDFs (1 UoG + 1 Zotero).

#### Scenario: Full-stack demo runs

- **GIVEN** the 2 sample PDFs are present in `leabharlann/`
- **WHEN** the `leabharlann_full_stack_demo` asset materialises
- **THEN** the asset:
  1. Extracts text via pymupdf
  2. Calls `b.ExtractUoGArtifact` and `b.ExtractZoteroMetadata`
  3. Triggers the books + zotero CocoIndex v1 updates
  4. Adds the demo text to Cognee
  5. Writes the metadata to DuckDB
- **AND** 4 asset checks pass (extraction OK, BAML OK, CocoIndex OK, full pipeline OK)

### Requirement: Directory-watch sensor

The system SHALL provide a `leabharlann_sensors` directory-watch sensor
that polls every 60 seconds and emits `RunRequest`s for the affected
partitions.

#### Scenario: Sensor fires on new file

- **GIVEN** a new PDF lands in `leabharlann/gaeilge/`
- **WHEN** the sensor polls
- **THEN** a `RunRequest` is emitted for the `leabharlann_books_raw`
  asset with the affected `subject` partition

## Cross-references

- [`oideachais/dlt_sources/author_archive/`](../../oideachais/dlt_sources/author_archive/) (the 4 dlt sources)
- [`oideachais/cocoindex_flows/leabharlann_embedding.py`](../../oideachais/cocoindex_flows/leabharlann_embedding.py) (the 3 v1 Apps)
- [`oideachais/dagster_defs/assets/leabharlann_assets.py`](../../oideachais/dagster_defs/assets/leabharlann_assets.py) (the 7 Dagster assets)
- [`oideachais/dagster_defs/assets/leabharlann_full_stack_demo.py`](../../oideachais/dagster_defs/assets/leabharlann_full_stack_demo.py) (the demo asset)
- [`oideachais/dagster_defs/sensors/leabharlann_sensors.py`](../../oideachais/dagster_defs/sensors/leabharlann_sensors.py) (the sensor)
- [`openspec/specs/oideachais-baml-schemas/spec.md`](oideachais-baml-schemas/spec.md) (the upstream BAML extraction)
- [`openspec/specs/oideachais-cognify-knowledge-graph/spec.md`](oideachais-cognify-knowledge-graph/spec.md) (the downstream cognify + edges)
- [`openspec/specs/oideachais-marimo-dashboards/spec.md`](oideachais-marimo-dashboards/spec.md) (the full-stack demo dashboard)
