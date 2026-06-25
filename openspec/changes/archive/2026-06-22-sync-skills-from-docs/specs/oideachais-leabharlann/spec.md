# Spec Delta: oideachais-leabharlann

## ADDED Requirements

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

## REMOVED Requirements

(None. The 3 v1 Apps remain `LeabharlannBooksEmbedding`,
`LeabharlannZoteroEmbedding`, `LeabharlannTakeoutEmbedding`. The
8 new requirements above are additive conventions that govern how
the 3 Apps are implemented.)
