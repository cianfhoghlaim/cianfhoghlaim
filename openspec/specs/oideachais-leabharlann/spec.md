# Oideachais Leabharlann Capability

## Purpose

`oideachais-leabharlann` is a capability of the Cianfhoghlaim platform.
The corresponding source code lives at
`sruth/oideachais/dlt_sources/author_archive/` (the 4 dlt sources: books,
zotero, takeout, UoG) and `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`
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

### Requirement: CocoIndex v1 App conventions (every flow)

The system SHALL expose every CocoIndex flow as a v1 `coco.App`
instance with a `@coco.fn` `app_main` function, a stable name, and
a single-source-of-truth configuration.

#### Scenario: App registration

- **GIVEN** an `sruth/oideachais/cocoindex_flows/<flow>.py` module
- **WHEN** the module is loaded
- **THEN** it SHALL declare
  `app = coco.App(coco.AppConfig(name="<UniqueName>"), app_main, ...)`
  at module level
- **AND** the `app_main` function SHALL be decorated with `@coco.fn`
- **AND** the app SHALL be invokable from the CLI as
  `cocoindex update <flow>:<app_name>`

#### Scenario: Live mode

- **GIVEN** an `app_main` function
- **WHEN** the user runs `cocoindex update -L <flow>:<app_name>`
- **THEN** the app SHALL support `live=True` on its source
- **AND** the file-watcher SHALL be polled for changes by the
  local-filesystem source

### Requirement: Memoization on expensive `@coco.fn` calls

The system SHALL mark every function that performs an expensive
operation (LLM call, embedding, OCR) with `@coco.fn(memo=True)`.

#### Scenario: Stable component path

- **GIVEN** a `@coco.fn(memo=True)` function with a file argument
- **WHEN** the function is called with the same file content twice
- **THEN** CocoIndex SHALL skip the second execution and reuse the
  cached target state
- **AND** the component path SHALL be derived from a stable identifier
  (filename, not object reference)

#### Scenario: Unstable path re-runs

- **GIVEN** a `@coco.fn(memo=True)` function with an index argument
- **WHEN** the index changes between runs
- **THEN** CocoIndex SHALL re-execute the function (the component
  path is unstable)

### Requirement: `ContextKey` for shared resources

The system SHALL share expensive resources (embedders, database
pools) across components via `coco.ContextKey` and `@coco.lifespan`.

#### Scenario: Embedder context

- **GIVEN** an embedder back-end (e.g. `BAAI/bge-large-en-v1.5`)
- **WHEN** the App starts
- **THEN** the embedder SHALL be created in the `@coco.lifespan`
  function and provided via `builder.provide(EMBEDDER, ...)`
- **AND** processing functions SHALL access it via
  `await coco.use_context(EMBEDDER).embed(text)`
- **AND** the `EMBEDDER` ContextKey SHALL be declared with
  `detect_change=True` so a model swap auto-re-embeds

#### Scenario: LanceDB connection context

- **GIVEN** a `LANCEDB_URI` environment variable
- **WHEN** the App starts
- **THEN** the LanceDB connection SHALL be created once in
  `@coco.lifespan` and provided via
  `builder.provide(LANCE_DB, conn)`
- **AND** all `mount_table_target` calls SHALL reference this
  shared connection

### Requirement: `mount_table_target` + `declare_row` (no v0 collectors)

The system SHALL use the v1 `mount_table_target` API for every
LanceDB / Postgres / Neo4j / FalkorDB target. The v0 `add_collector()`
+ `collector.export(...)` pattern SHALL NOT be used.

#### Scenario: LanceDB target

- **GIVEN** a `MyRecord` dataclass with
  `id: int`, `filename: str`, `text: str`,
  `embedding: Annotated[NDArray, EMBEDDER]`
- **WHEN** the App mounts the table target via
  `await lancedb.mount_table_target(LANCE_DB, table_name=...,
  table_schema=await lancedb.TableSchema.from_class(MyRecord,
  primary_key=["id"]))`
- **THEN** the table SHALL be created with the inferred schema
  (column types from the dataclass + the embedding dimension from
  `EMBEDDER`)
- **AND** the primary key SHALL be `id`
- **AND** the row identity SHALL be stable across re-runs (via
  `IdGenerator` + `await id_gen.next_id(...)`)

#### Scenario: declare_row emits one row

- **GIVEN** a `target_table: lancedb.TableTarget[MyRecord]`
- **WHEN** the per-chunk `@coco.fn` calls
  `target_table.declare_row(row=MyRecord(...))`
- **THEN** the row SHALL be queued for the LanceDB target
- **AND** the row's `embedding` field SHALL be the embedded chunk

#### Scenario: declare_vector_index

- **GIVEN** a `target_table` with an `embedding` column of type
  `Annotated[NDArray, EMBEDDER]`
- **WHEN** the App calls
  `target_table.declare_vector_index(column="embedding")`
- **THEN** the engine SHALL create a vector index on the column
  (L2 / cosine inferred from the `EMBEDDER` type)
- **AND** the index SHALL be auto-rebuilt by the engine on the
  next catch-up run

### Requirement: `mount_each` + `map` for fan-out and parallelism

The system SHALL use `coco.mount_each(fn, source.items(), *extra_args)`
to fan out a `@coco.fn` across source items, and `coco.map(fn, items,
*extra_args)` for parallel processing of in-memory lists.

#### Scenario: Per-file mount_each

- **GIVEN** a `files = localfs.walk_dir(...)` source and a
  `@coco.fn(memo=True) async def process_file(file, table)` function
- **WHEN** the App calls
  `await coco.mount_each(process_file, files.items(), target_table)`
- **THEN** `process_file` SHALL be called once per source item
- **AND** the calls SHALL be parallelised (no manual
  `asyncio.gather` needed)
- **AND** memoisation SHALL skip unchanged files

#### Scenario: Per-chunk map

- **GIVEN** a list of `chunks: list[Chunk]` and a
  `@coco.fn async def process_chunk(chunk, ...)` function
- **WHEN** the App calls `await coco.map(process_chunk, chunks, ...)`
- **THEN** `process_chunk` SHALL be called once per chunk
- **AND** the calls SHALL be parallelised

### Requirement: `Annotated[NDArray, EMBEDDER]` vector dimension source

The system SHALL type every embedding column on a `LanceModel` /
`@dataclass` row as `Annotated[NDArray, EMBEDDER]` so the dimension
is inferred from the `EMBEDDER` `ContextKey` (not hard-coded).

#### Scenario: Dimension inferred

- **GIVEN** `embedding: Annotated[NDArray, EMBEDDER]` on a `MyRecord`
  dataclass, and an `EMBEDDER = coco.ContextKey[BgeEmbedder]("embedder", detect_change=True)`
  with `ndims=1024`
- **WHEN** the App mounts the target
- **THEN** the `embedding` column SHALL be `FixedSizeList[uint8, 1024]`
  (or `float32`, per the EMBEDDER type)
- **AND** swapping the EMBEDDER to a 768-d model SHALL auto-trigger
  a re-embed (because `detect_change=True`)

### Requirement: `IdGenerator` for stable row identity

The system SHALL use `IdGenerator` from `cocoindex.resources.id` to
generate stable, deterministic primary keys per (file, content) pair,
so the same chunk re-emitted by `process_chunk` re-uses the same `id`.

#### Scenario: Stable id

- **GIVEN** a `process_chunk(chunk, ..., id_gen: IdGenerator, table)` fn
- **WHEN** the fn calls `await id_gen.next_id(chunk.text)`
- **THEN** the returned `int` SHALL be a deterministic hash of
  `chunk.text`
- **AND** the same `chunk.text` SHALL produce the same `id` across
  re-runs (so the LanceDB `merge` write disposition is correct)

### Requirement: `localfs.walk_dir` + `PatternFilePathMatcher`

The system SHALL use the v1 `localfs.walk_dir(sourcedir, recursive=True,
path_matcher=PatternFilePathMatcher(included_patterns=[...],
excluded_patterns=[...]), live=True)` API for every personal-archive
source.

#### Scenario: File discovery

- **GIVEN** `localfs.walk_dir("leabharlann/gaeilge", recursive=True,
  path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf",
  "**/*.docx"], excluded_patterns=["**/previews", "**/.*"]))`
- **WHEN** the App runs in catch-up mode
- **THEN** the source SHALL yield one entry per matching file
- **AND** hidden files (`.DS_Store`, `__pycache__`) SHALL be excluded
  via `excluded_patterns`

## Cross-references

- [`sruth/oideachais/dlt_sources/author_archive/`](../../sruth/oideachais/dlt_sources/author_archive/) (the 4 dlt sources)
- [`sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`](../../sruth/oideachais/cocoindex_flows/leabharlann_embedding.py) (the 3 v1 Apps)
- [`sruth/oideachais/dagster_defs/assets/leabharlann_assets.py`](../../sruth/oideachais/dagster_defs/assets/leabharlann_assets.py) (the 7 Dagster assets)
- [`sruth/oideachais/dagster_defs/assets/leabharlann_full_stack_demo.py`](../../sruth/oideachais/dagster_defs/assets/leabharlann_full_stack_demo.py) (the demo asset)
- [`sruth/oideachais/dagster_defs/sensors/leabharlann_sensors.py`](../../sruth/oideachais/dagster_defs/sensors/leabharlann_sensors.py) (the sensor)
- [`openspec/specs/oideachais-baml-schemas/spec.md`](oideachais-baml-schemas/spec.md) (the upstream BAML extraction)
- [`openspec/specs/oideachais-cognify-knowledge-graph/spec.md`](oideachais-cognify-knowledge-graph/spec.md) (the downstream cognify + edges)
- [`openspec/specs/oideachais-marimo-dashboards/spec.md`](oideachais-marimo-dashboards/spec.md) (the full-stack demo dashboard)
