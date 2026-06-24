# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: V1 unified embedding App (unified_embeddings asset)

The system SHALL run a v1-native CocoIndex App for unified document
embedding, reading from any DuckDB-compatible source and writing to
the `unified_embeddings` LanceDB table. The App uses:

- Configurable DuckDB connection (default:
  `crypteolas_catalog.docs.scraped_documents`).
- `asyncio.to_thread` to read the DuckDB rows (does not block the event loop).
- `RecursiveSplitter` (markdown) for chunking, with a paragraph+char
  fallback when cocoindex is unavailable.
- `get_content_hash` (sha256 prefix) for per-chunk deduplication.
- `classify_content` (v0 parity) to tag each chunk as `documentation` or `code`.
- 1 `UnifiedDocumentRow` dataclass with BGE-M3 embedding on `text`
  (1024 dims) and stable IDs of the form
  `unified:<doc_id>:<chunk_index>:<content_hash>`.

The Dagster asset `unified_embeddings` (group `embedding`) lives in
`oideachais/dagster_defs/assets/unified_embedding_assets.py` and
kicks the v1 App via
`cocoindex update oideachais.cocoindex_flows.unified_embedding:unified_app`.

#### Scenario: A developer searches unified documents by source type

- **GIVEN** the `unified_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await unified_search("SpacetimeDB reducer", source_types=["protocol_docs"])`
- **THEN** the v1 App returns the top-10 rows from the `unified_embeddings`
  LanceDB table, filtered by `source_type IN ('protocol_docs')`,
  ranked by BGE-M3 cosine similarity to the query

#### Scenario: A developer filters by protocol

- **GIVEN** the `unified_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await unified_search("reducer", protocol="spacetimedb")`
- **THEN** the v1 App returns only rows where `protocol = 'spacetimedb'`,
  ranked by BGE-M3 cosine similarity

### Requirement: V1 code embedding App (code_embeddings asset)

The system SHALL run a v1-native CocoIndex App for local code file
embedding, walking a configurable directory and writing to the
`code_embeddings` LanceDB table. The App uses:

- `UNIFIED_CODE_ROOT` env var (default:
  `crypteolas/storage/data/code/`).
- `localfs.walk_dir(code_root, recursive=True, live=True, refresh_interval=3600s)`
  with the codebase_indexing.py excludes.
- 8 file extensions: `*.py`, `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.rs`,
  `*.go`, `*.sol`.
- `RecursiveSplitter` with `detect_code_language` for chunking
  (the canonical v1 pattern from `codebase_indexing.py`).
- 1 `CodeChunkRow` dataclass with BGE-M3 embedding on `text` and
  stable IDs of the form `code:<filename>:<chunk_index>`.

The Dagster asset `code_embeddings` (group `embedding`) lives in
`oideachais/dagster_defs/assets/unified_embedding_assets.py` and
kicks the v1 App via
`cocoindex update oideachais.cocoindex_flows.unified_embedding:code_app`.

#### Scenario: A developer searches code embeddings by language

- **GIVEN** the `code_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await code_search("reducer", language="rust")`
- **THEN** the v1 App returns the top-10 rows from the `code_embeddings`
  LanceDB table, filtered by `language = 'rust'`,
  ranked by BGE-M3 cosine similarity to the query

#### Scenario: A developer filters by chunk type

- **GIVEN** the `code_embeddings` Dagster asset has materialised
- **WHEN** a developer runs `await code_search("function", chunk_type="block")`
- **THEN** the v1 App returns only rows where `chunk_type = 'block'`,
  ranked by BGE-M3 cosine similarity

## REMOVED Requirements

(None.)
