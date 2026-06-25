# Oideachais Semantic Search Capability

## Purpose

`oideachais-semantic-search` is a capability of the Cianfhoghlaim platform. The
corresponding source code lives at `sruth/oideachais/cocoindex_flows/` (8 v0 flows +
the new v1 leabharlann flows) and `sruth/oideachais/api/routes/search.py`. See
`docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the
project identity.

## Background

Vector-based curriculum and corpus search via LanceDB HNSW (BAAI/bge-m3 or
BAAI/bge-large-en-v1.5 for English-only, 1024-d) with a FastAPI route at
`/search/*`. The full leabharlann corpus (books, zotero, takeout) is
indexed via the v1 CocoIndex Apps in
`sruth/oideachais/cocoindex_flows/leabharlann_embedding.py`.

This spec was renamed from `semantic-search` to disambiguate it from any
future non-oideachais semantic-search surfaces (e.g. a `tuatha` or `croilar`
semantic-search surface would have its own spec).
## Requirements
### Requirement: Bilingual + English-only search

The system SHALL support both bilingual (multilingual) and English-only
semantic search via two distinct embedding models, selected at the
CocoIndex flow level.

#### Scenario: Bilingual model selection

- **GIVEN** a CocoIndex v1 flow with `EMBEDDING_MODEL=BAAI/bge-m3`
- **WHEN** a query is embedded
- **THEN** the query is embedded with the BGE-M3 multilingual model (1024-d)
- **AND** the result includes the top-10 closest chunks across all corpora

#### Scenario: English-only model selection

- **GIVEN** a CocoIndex v1 flow with `EMBEDDING_MODEL=BAAI/bge-large-en-v1.5`
- **WHEN** a query is embedded
- **THEN** the query is embedded with the BGE-large-en-v1.5 model (1024-d, English-tuned)
- **AND** the result includes the top-10 closest chunks across all corpora

### Requirement: Cross-corpus search

The system SHALL support cross-corpus search across the oideachais
leabharlann corpora (books, zotero, takeout) and the curriculum corpora
(NCCA, SEC, examinations).

#### Scenario: Cross-corpus query

- **GIVEN** a search request `q="handwritten text recognition for Irish"`
- **WHEN** the user issues a search via `/search/semantic`
- **THEN** the system returns the top-10 results from BOTH the zotero
  corpus and the leabharlann books corpus
- **AND** the result includes a `corpus` field per hit for routing

### Requirement: Search API

The system SHALL expose a FastAPI route at `/search/semantic` for
semantic search.

#### Scenario: API returns 200

- **GIVEN** a user issues `GET /search/semantic?q=irish+gaelic`
- **WHEN** the request is processed
- **THEN** the route returns HTTP 200 with `{"results": [...], "total": N}`

### Requirement: LanceDB time-travel RAG

The system SHALL support time-travel / versioned RAG via
`table.checkout(version)` and `table.version`, enabling A/B testing
of embedding models and version-anchored retrieval.

#### Scenario: Query a historical version

- **GIVEN** a LanceDB table at `sruth/oideachais/lancedb_data/leabharlann_books`
  with N versions (one per re-index)
- **WHEN** the user calls `table.checkout(version=2).search(...)`
- **THEN** the search returns rows from version 2 only
- **AND** the engine does not re-embed against the current model

#### Scenario: A/B test two embedding models

- **GIVEN** two LanceDB tables `leabharlann_books_v1` (BGE-large-en-v1.5)
  and `leabharlann_books_v2` (BGE-M3)
- **WHEN** the user runs the same query against both tables
- **THEN** the side-by-side comparison is returned
- **AND** the `model_name` column distinguishes the source table

### Requirement: Embeddings Registry (10+ providers)

The system SHALL use the LanceDB embeddings registry via
`embedding.get_registry().get("<provider>")` to support 10+ providers
(OpenAI, Cohere, HuggingFace, Sentence-Transformers, ColBERT, Gemini,
Bedrock, Ollama, OpenCLIP), with `LanceModel` + `SourceField()` +
`VectorField()` for the declarative schema.

#### Scenario: Provider selection

- **GIVEN** a `Document(LanceModel)` with
  `text: str = model.SourceField()` and
  `vector: Vector(model.ndims()) = model.VectorField()`
- **WHEN** `model = get_registry().get("openai").create(name="text-embedding-3-small")`
  is called
- **THEN** the embedding is generated via OpenAI
- **AND** swapping `get_registry().get("cohere")` swaps the provider
  with no other code change

### Requirement: Context Enrichment Window RAG

The system SHALL support the neighbour-window chunking pattern
(Advanced_RAG_Context_Enrichment_Window) for long-doc RAG: each
chunk is augmented with N neighbouring chunks before embedding, and
the search re-ranks the results by group.

#### Scenario: Windowed RAG on long doc

- **GIVEN** a doc with 50 chunks and `window_size=3`
- **WHEN** the chunker runs
- **THEN** each chunk is augmented with its ±3 neighbours
- **AND** the search returns the augmented chunks, then the
  re-ranker groups them by parent chunk
- **AND** the result includes the full context window, not just
  the matched chunk

### Requirement: Multimodal "fat table" BLOB+vector schema

The system SHALL support a single LanceDB table with text + image
BLOB + vector + metadata columns, with the BLOB stored as a
range-readable `LargeList` (avoiding full-row reads).

#### Scenario: Multimodal recipe search

- **GIVEN** a `Recipe` table with `name: str`, `image_blob: LargeList[uint8]`,
  `image_embedding: FixedSizeList[uint8, 768]`, `description: str`
- **WHEN** the user runs an image-similarity search
- **THEN** the engine reads the `image_blob` only for the top-K rows
  (range-read), not the full table
- **AND** the result is returned as a Pydantic dataclass

### Requirement: LanceDB Cloud regions + auto-compaction

The system SHALL use LanceDB Cloud for the production semantic
search sink, with the 4 supported regions (`us-east-1`, `us-west-2`,
`eu-west-1`, `ap-south-1`), and the cloud-managed auto-compaction +
auto-reindexing features enabled.

#### Scenario: Cloud connection

- **GIVEN** `LANCEDB_URI=db://leabharlann` and `LANCEDB_API_KEY=<...>`
- **WHEN** `lancedb.connect(LANCEDB_URI, api_key=LANCEDB_API_KEY,
  region="eu-west-1")` is called
- **THEN** the engine connects to the `eu-west-1` region
- **AND** auto-compaction runs every 5 minutes
- **AND** auto-reindexing runs on every 1k writes

### Requirement: Lance + Iceberg (companion table pattern)

The system SHALL support the `lance.namespace.connect("iceberg", ...)`
companion-table pattern, where a LanceDB table is exposed as an
Iceberg table to consumers (e.g. DuckDB `ATTACH iceberg_attach`,
PyIceberg).

#### Scenario: Lance table queryable as Iceberg

- **GIVEN** a Lance table at `lance://s3://lance/leabharlann_books`
- **WHEN** the user calls
  `lance.namespace.connect("iceberg", REST_URL=..., S3_ENDPOINT=...)`
  and registers the table
- **THEN** the table is queryable via PyIceberg as a standard Iceberg
  table
- **AND** ACID transactions on the Lance side are visible from
  Iceberg-side readers

### Requirement: Ibis + DuckDB `lance_scan()` integration

The system SHALL support `INSTALL lance; LOAD lance;` in DuckDB and
use `lance_scan('<lance-table-path>')` as a view for federated SQL
queries over Lance tables from marimo notebooks.

#### Scenario: SQL over Lance

- **GIVEN** a marimo notebook connected to the MotherDuck `oideachais`
  database
- **WHEN** the user runs
  `SELECT * FROM lance_scan('s3://lance/leabharlann_books') WHERE ...`
- **THEN** DuckDB reads the Lance table via the lance extension
- **AND** the SQL query joins with the DuckDB tables without an
  explicit ETL step

### Requirement: Modern TypeScript LanceDB API

The system SHALL use the modern TypeScript LanceDB API
(`embedding.getRegistry()`, `LanceSchema`, `sourceField`,
`vectorField`, `search()` (NOT deprecated `vectorSearch()`),
`rerankers`, RRF rerankers).

#### Scenario: TS hybrid search

- **GIVEN** a TypeScript app with `lancedb` + `transformers`
  + `rerankers` installed
- **WHEN** the user calls
  `table.search(queryType="hybrid").vector(emb).text(query).rerank(method="rrf")`
- **THEN** the engine returns hybrid (vector + FTS) results, re-ranked
  by Reciprocal Rank Fusion
- **AND** the deprecated `vectorSearch(...)` API is NOT used anywhere
  in the codebase

### Requirement: Lance-Ray distributed indexing

The system SHALL use `lance-ray` (`lr.create_scalar_index`,
`lr.read_lance`, `lr.write_lance`, `lr.add_columns`) for any
re-indexing operation > 1M rows on the `bunchloch` workstation.

#### Scenario: Distributed re-index

- **GIVEN** a Lance table with 2M rows on `bunchloch`
- **WHEN** the user calls `lr.read_lance(...)` then transforms via Ray
  actors and writes back with `lr.write_lance(...)`
- **THEN** the operation completes in O(N/num_workers) wall time
- **AND** the workers do not corrupt the Lance metadata
  (Lance's MVCC safety holds under Ray concurrency)

### Requirement: Geospatial + FTS combo

The system SHALL support FTS + geospatial compound queries via the
LanceDB `_distance` operator and the `prefilter=False` option for
non-selective filters.

#### Scenario: Geo + FTS

- **GIVEN** a `places` table with `name: str`, `description: str`,
  `lat: float32`, `lon: float32`
- **WHEN** the user runs
  `table.search(q, query_type="hybrid").where("distance(...) < 5km")`
- **THEN** the results are filtered to within 5 km of the query
  point AND matched by FTS
- **AND** `prefilter=False` is set so the geo filter is applied AFTER
  the FTS retrieval (since the geo filter is non-selective)

