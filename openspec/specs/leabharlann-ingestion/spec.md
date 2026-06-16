# `leabharlann-ingestion` capability spec

## Purpose

`leabharlann-ingestion` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `oideachais/dlt_sources/author_archive/`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

Ingest the `leabharlann/` personal-archive tree: `ollscoil_na_gaillimhe/` (renamed university archive), `gemini_deep_research/` (renamed Gemini archive), `zotero/` (117 PDFs in real Zotero storage format), `gaeilge/` (40 PDFs + MDs + `previews/`), `aigne/` (7 books), and `stedding/Takeout/` (sample googletakeout, 64 .docx + 1 .csv).
## Requirements
### Requirement: Leabharlann Books Source
The system SHALL discover and ingest every supported file in `leabharlann/gaeilge/` and `leabharlann/aigne/` into the `leabharlann_books` DuckLake table.

#### Scenario: Multi-format discovery
- **GIVEN** the `leabharlann_books_raw` Dagster asset is materialised
- **WHEN** the source walks the directories
- **THEN** it SHALL yield one row per supported file (`.pdf`, `.docx`, `.epub`, `.md`, plus existing types)
- **AND** each row SHALL be tagged with `subject="gaeilge" | "aigne" | "epub" | "md"` and `account="leabharlann"`

#### Scenario: Preview pairing
- **GIVEN** a book PDF at `leabharlann/gaeilge/foo.pdf`
- **AND** a preview PNG at `leabharlann/gaeilge/previews/foo_preview.png`
- **WHEN** the source yields the row
- **THEN** the row SHALL include `preview_path = "leabharlann/gaeilge/previews/foo_preview.png"`
- **AND** the preview PNG SHALL NOT be indexed as a separate document

#### Scenario: EPUB extraction
- **GIVEN** a `.epub` file is scanned
- **WHEN** the `epub_documents` resource yields the row
- **THEN** the row SHALL include `epub_chapters: list[dict]` (chapter title + text per chapter)
- **AND** the extractor SHALL be `ebooklib` (try-import; graceful degradation if not installed)

### Requirement: Zotero Source
The system SHALL discover and ingest every PDF in `leabharlann/zotero/` into the `leabharlann_zotero` DuckLake table.

#### Scenario: Zotero storage format discovery
- **GIVEN** `leabharlann/zotero/` contains 117 PDFs (e.g. `Barry et al. - 2022 - gaBERT -- an Irish Language Model.pdf`)
- **WHEN** the `leabharlann_zotero_raw` Dagster asset is materialised
- **THEN** the source SHALL yield one row per non-empty PDF
- **AND** the empty `_.pdf` placeholder SHALL be skipped
- **AND** each row SHALL be tagged with `account="leabharlann_zotero"`, `arxiv_id` (when extractable from the filename), and `duplicate_marker` (e.g. `__dup0`, `_(1)`)

#### Scenario: SHA-256 deduplication
- **GIVEN** two Zotero PDFs with the same content (e.g. `2025.cltw-1.pdf` and `2025.cltw-1__dup0.pdf`)
- **WHEN** the source yields the rows
- **THEN** the rows SHALL have distinct `file_hash` values (because the file paths differ)
- **AND** the dlt primary key (`file_hash`) SHALL prevent the same file from being loaded twice on re-runs
- **AND** a downstream BAML extractor MAY collapse the two rows into a single `ZoteroPaper` via content-hash dedup

#### Scenario: arXiv ID extraction
- **GIVEN** a Zotero PDF named `2504.02890v2.pdf` (arXiv ID with version)
- **WHEN** the source yields the row
- **THEN** the `arxiv_id` column SHALL be populated as `2504.02890` (version stripped)
- **AND** the `arxiv_version` column SHALL be populated as `v2`

### Requirement: Takeout v1 Source (Phase 1 filesystem)
The system SHALL auto-discover Google Takeout directories and zips in three layouts, without manual YAML editing.

#### Scenario: No-account-prefix layout
- **GIVEN** `stedding/Takeout/Drive/*.docx` exists (no `<account>/` wrapper)
- **WHEN** the `leabharlann_takeout_v1_raw` Dagster asset is materialised
- **THEN** the source SHALL walk the directory and yield one row per file
- **AND** every row SHALL be tagged with `account="stedding_takeout"` (the fallback label)
- **AND** the `domain` column SHALL be derived from the top-level subdirectory (`Drive`, `Gmail`, `Gemini Apps`, etc.)

#### Scenario: Account-prefix layout
- **GIVEN** `stedding/Takeout/<account>/Drive/*.docx` exists
- **WHEN** the source walks
- **THEN** every row SHALL be tagged with `account=<account>` (the directory name)

#### Scenario: ZIP auto-discovery
- **GIVEN** `~/Downloads/takeout-*.zip` exists
- **WHEN** the `leabharlann_directory_sensor` polls
- **THEN** the sensor SHALL emit a `RunRequest` with `partition_key` = the zip file's stem
- **AND** the asset materialisation SHALL mark the zip for extraction (Phase 1: manifest only; Phase 2 OAuth: actual extraction)

### Requirement: CocoIndex v1 Embedding for Leabharlann
The system SHALL run a v1 CocoIndex App per leabharlann source, embedding documents into LanceDB.

#### Scenario: Books CocoIndex App
- **GIVEN** the `leabharlann_books_raw` asset has materialised
- **WHEN** the `leabharlann_cocoindex_books_update` asset materialises
- **THEN** the `leabharlann_books_embedding` CocoIndex App SHALL run (catch-up mode)
- **AND** a LanceDB table `leabharlann_books` SHALL be populated with embedded chunks
- **AND** the asset metadata SHALL include `embedding_model` and `embedding_dim`

#### Scenario: Zotero CocoIndex App
- **GIVEN** the `leabharlann_zotero_raw` asset and the `leabharlann_paper_metadata` asset have materialised
- **WHEN** the `leabharlann_cocoindex_zotero_update` asset materialises
- **THEN** the `leabharlann_zotero_embedding` CocoIndex App SHALL run
- **AND** it SHALL call `b.ExtractZoteroMetadata` per row (BAML memoised by `file_hash`)
- **AND** a LanceDB table `leabharlann_zotero` SHALL be populated with embedded abstract chunks + metadata

#### Scenario: Takeout CocoIndex App
- **GIVEN** the `leabharlann_takeout_v1_raw` asset has materialised
- **WHEN** the `leabharlann_cocoindex_takeout_update` asset materialises
- **THEN** the `leabharlann_takeout_embedding` CocoIndex App SHALL run
- **AND** a LanceDB table `leabharlann_takeout` SHALL be populated

### Requirement: Source default paths MUST point at `leabharlann/`
The dlt source modules `oideachais/dlt_sources/author_archive/{university_of_galway,gemini_deep_research}.py` MUST define `DEFAULT_UOG_PATH` and `DEFAULT_GEMINI_PATH` pointing at `leabharlann/ollscoil_na_gaillimhe/` and `leabharlann/gemini_deep_research/` respectively. The source factories SHALL continue to accept any `base_path` argument so callers can pass the old `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/` path explicitly for back-compat.

#### Scenario: Default path under leabharlann
- **GIVEN** the `university_of_galway_source()` factory is called without arguments
- **WHEN** the path is inspected
- **THEN** the path SHALL end with `leabharlann/ollscoil_na_gaillimhe`

#### Scenario: Backwards-compatible explicit path
- **GIVEN** an existing caller passes an explicit `base_path=...` to `university_of_galway_source(base_path=...)`
- **WHEN** the source runs
- **THEN** the `account` column SHALL be the value passed in `base_path`

