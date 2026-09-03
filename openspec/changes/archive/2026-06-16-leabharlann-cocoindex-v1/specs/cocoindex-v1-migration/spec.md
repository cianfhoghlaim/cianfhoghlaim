# Spec Delta — `cocoindex-v1-migration` (new capability)

## Purpose

`cocoindex-v1-migration` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives at `sruth/oideachais/cocoindex_flows/`. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

Migrate all CocoIndex flows in `sruth/oideachais/cocoindex_flows/` from the deprecated v0 API (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`, `cocoindex.sources.DuckDB`, `cocoindex.targets.lancedb`, `cocoindex.functions.SplitRecursively`, `cocoindex.functions.SentenceTransformerEmbed`) to the canonical v1 API (`@coco.fn`, `@coco.lifespan`, `coco.App`, `localfs.walk_dir`, `RecursiveSplitter`, `lancedb.mount_table_target`, `SentenceTransformerEmbedder`).

## ADDED Requirements

### Requirement: CocoIndex v1 App per Flow
The system SHALL expose every CocoIndex flow as a v1 `coco.App` instance with a `@coco.fn` `app_main` function and stable identity.

#### Scenario: App registration
- **GIVEN** an `sruth/oideachais/cocoindex_flows/<flow>.py` module
- **WHEN** the module is loaded
- **THEN** it SHALL declare `app = coco.App(coco.AppConfig(name="<UniqueName>"), app_main, ...)` at module level
- **AND** the `app_main` function SHALL be decorated with `@coco.fn`
- **AND** the app SHALL be invokable from the CLI as `cocoindex update <flow>:<app_name>`

#### Scenario: Live mode support
- **GIVEN** an `app_main` function
- **WHEN** the user runs `cocoindex update -L <flow>:<app_name>`
- **THEN** the app SHALL support `live=True` on its source
- **AND** the file-watcher SHALL be polled for changes by the local-filesystem source

### Requirement: Memoization on Expensive Functions
The system SHALL mark every function that performs an expensive operation (LLM call, embedding, OCR) with `@coco.fn(memo=True)`.

#### Scenario: Stable component path
- **GIVEN** a `@coco.fn(memo=True)` function with a file argument
- **WHEN** the function is called with the same file content twice
- **THEN** CocoIndex SHALL skip the second execution and reuse the cached target state
- **AND** the component path SHALL be derived from a stable identifier (filename, not object reference)

#### Scenario: Unstable path
- **GIVEN** a `@coco.fn(memo=True)` function with an index argument
- **WHEN** the index changes between runs
- **THEN** CocoIndex SHALL re-execute the function (the component path is unstable)

### Requirement: ContextKey for Shared Resources
The system SHALL share expensive resources (embedders, database pools) across components via `coco.ContextKey` and `@coco.lifespan`.

#### Scenario: Embedder context
- **GIVEN** an embedder back-end (e.g. `BAAI/bge-large-en-v1.5`)
- **WHEN** the App starts
- **THEN** the embedder SHALL be created in the `@coco.lifespan` function and provided via `builder.provide(EMBEDDER, ...)`
- **AND** processing functions SHALL access it via `await coco.use_context(EMBEDDER).embed(text)`
- **AND** the `EMBEDDER` ContextKey SHALL be declared with `detect_change=True` so a model swap auto-re-embeds

#### Scenario: LanceDB connection
- **GIVEN** a `LANCEDB_URI` environment variable
- **WHEN** the App starts
- **THEN** the LanceDB connection SHALL be created once in `@coco.lifespan` and provided via `builder.provide(LANCE_DB, conn)`
- **AND** all `mount_table_target` calls SHALL reference this shared connection

### Requirement: Live Filesystem Source
The system SHALL use `localfs.walk_dir(sourcedir, recursive=True, path_matcher=PatternFilePathMatcher(...), live=True)` for every personal-archive source.

#### Scenario: File discovery
- **GIVEN** a source directory and a `PatternFilePathMatcher` with `included_patterns=["**/*.pdf", "**/*.docx"]`
- **WHEN** the App runs in catch-up mode
- **THEN** the source SHALL walk the directory recursively and yield one entry per matching file
- **AND** hidden files (`.DS_Store`, `__pycache__`, etc.) SHALL be excluded via `excluded_patterns`

#### Scenario: Live watch
- **GIVEN** the App is in live mode
- **WHEN** a new file appears or an existing file's mtime changes
- **THEN** CocoIndex SHALL re-run the affected `process_file` component (memoized, so unchanged files are skipped)
- **AND** target states SHALL be updated atomically per component

### Requirement: LanceDB Table Target
The system SHALL write every CocoIndex flow's output to a LanceDB table declared via `lancedb.mount_table_target`.

#### Scenario: Table schema
- **GIVEN** a `MyRecord` dataclass with `id: int`, `filename: str`, `text: str`, `embedding: Annotated[NDArray, EMBEDDER]`
- **WHEN** the App mounts the table target
- **THEN** the table SHALL be created with the inferred schema (column types from the dataclass + the embedding dimension from `EMBEDDER`)
- **AND** the primary key SHALL be `id`
- **AND** the row identity SHALL be stable across re-runs (via `IdGenerator` + `await id_gen.next_id(...)`)

#### Scenario: Vector search query
- **GIVEN** a search query string
- **WHEN** the user invokes the App's `query(query_str)` function
- **THEN** the embedder SHALL embed the query
- **AND** LanceDB SHALL return the top-K rows by cosine distance
- **AND** the response SHALL be a list of dataclass instances with `score = 1.0 - _distance`

## MODIFIED Requirements

*(None — this is a new capability.)*

## REMOVED Requirements

### Requirement: v0 API (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`)

**Reason**: The venv has `cocoindex==1.0.9`. The v0 DSL is no longer importable. Migration is mandatory.

**Migration**:
- `sruth/oideachais/cocoindex_flows/*.py` (8 files) → v1 `coco.App` + `@coco.fn`
- `sruth/croilar/cocoindex_flows/cv_embedding.py` and `artwork_embedding.py` → v1 (deferred to a follow-up change)
