# `oideachais-cocoindex-v1-migration` capability spec — leabharlann-email-inbox-pipeline delta

The `oideachais-cocoindex-v1-migration` capability spec governs
the v1 `coco.App` instances across the oideachais lakehouse. The
leabharlann sub-tree currently has 3 v1 Apps
(`leabharlann_books_embedding`, `leabharlann_zotero_embedding`,
`leabharlann_takeout_embedding`).

This delta adds a 4th v1 App
`leabharlann_inbox_embedding` for the new email-inbox pipeline.

## ADDED Requirements

### Requirement: `leabharlann_inbox_embedding` v1 App

The system SHALL expose a v1 `coco.App` named
`leabharlann_inbox_embedding` that reads MBOX files from
`/srv/mailcow-exports/` (populated by Mailcow's
`dovecot_imapsync_runner` + the `mailcow-export` companion
container), chunks each message, embeds with
BAAI/bge-large-en-v1.5 (1024-d), and writes to the
`oideachais_inbox_messages` LanceDB table.

#### Scenario: App registration

- **GIVEN** an `embeddings/_oideachais_src/leabharlann_embedding.py`
  module with the 4th App declared
- **WHEN** the module is loaded
- **THEN** it SHALL declare
  `app = coco.App(coco.AppConfig(name="LeabharlannInboxEmbedding"), app_main, ...)`
  at module level
- **AND** the `app_main` function SHALL be decorated with
  `@coco.fn`

#### Scenario: App invoked from CLI

- **GIVEN** the App is registered
- **WHEN** the user runs `cocoindex update
  leabharlann_inbox_embedding`
- **THEN** the App processes every MBOX file in
  `/srv/mailcow-exports/` (recursive, excluding hidden files)

#### Scenario: Live mode supports hot-reload

- **WHEN** the user runs `cocoindex update -L
  leabharlann_inbox_embedding`
- **THEN** the App's source SHALL be in `live=True` mode
- **AND** the file-watcher SHALL be polled for new MBOX files

#### Scenario: Embedder + LanceDB shared via ContextKey

- **GIVEN** the App's `@coco.lifespan` function
- **WHEN** the App starts
- **THEN** the embedder SHALL be created in `@coco.lifespan`
  and provided via `builder.provide(EMBEDDER, ...)`
- **AND** the LanceDB connection SHALL be created once in
  `@coco.lifespan` and provided via `builder.provide(LANCE_DB,
  conn)`
- **AND** all `mount_table_target` calls SHALL reference this
  shared connection

#### Scenario: Cosine + FTS indexes declared

- **GIVEN** the mounted `oideachais_inbox_messages` table with
  an `embedding` column of type
  `Annotated[NDArray, EMBEDDER]`
- **WHEN** the App calls `target_table.declare_vector_index(column="embedding")`
- **THEN** the engine SHALL create a vector index on the
  column (cosine, 1024-d)

- **WHEN** the App calls `target_table.declare_fts_index(columns=["subject", "body_excerpt"])`
- **THEN** the engine SHALL create a full-text-search index on
  those columns for the `@query_handler search_inbox` RRF
  fusion

### Requirement: `search_inbox` query handler

The system SHALL expose a `@query_handler` named
`search_inbox(query, account=None, year=None, baml_class=None,
urgency_min=None, limit=20)` that returns ranked rows from the
`oideachais_inbox_messages` table using RRF-fused cosine + BM25
scoring.

#### Scenario: Hybrid search returns 20 rows

- **GIVEN** 1,000 vectors in the table
- **WHEN** `search_inbox("HSE Ireland malpractice appeal",
  baml_class="legal_case", limit=20)` runs
- **THEN** it returns 20 rows ranked by RRF-fused cosine +
  BM25 score
- **AND** every returned row has `baml_class == "legal_case"`

## MODIFIED Requirements

*(None — the change only ADDS the 4th v1 App; the 3 existing
Apps are unchanged.)*

## REMOVED Requirements

*(None.)*
