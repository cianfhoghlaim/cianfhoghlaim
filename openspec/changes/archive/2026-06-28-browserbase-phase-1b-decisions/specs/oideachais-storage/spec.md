# oideachais-storage (delta: Phase 1B research findings)

> Filled by Phase 1B research agent (5/5 prompts complete).
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-1b/`.

## ADDED Requirements

### Requirement: LanceDB v2 (.lance format) with Lance Namespace REST Catalog

The system SHALL use LanceDB v2 (`.lance` format) for all vector + blob
hybrid storage, with the Lance Namespace REST Catalog (port 8182)
bridging LanceDB to the lakehouse (Iceberg + Garage S3).

#### Scenario: LanceDB mount via Namespace

- **GIVEN** a LanceDB Python client connecting to `http://lakehouse-lance:8182`
- **WHEN** the client opens a table (e.g., `codebase_chunks`)
- **THEN** the table resolves to its `.lance` files on Garage S3
- **AND** HNSW index queries return ranked results

### Requirement: FalkorDB is the canonical vector+graph hybrid database

The system SHALL use FalkorDB as the primary vector+graph hybrid
database for cross-archive knowledge graph queries (edge types: cites,
builds-on, contradicts).

#### Scenario: FalkorDB vector + graph query

- **GIVEN** a FalkorDB driver connected at `falkordb:6379` with
  `vector.so` loadable loaded
- **WHEN** a Cypher query combines graph traversal (e.g.,
  `MATCH (a:Paper)-[:CITES]->(b:Paper)`) with vector search (e.g.,
  `CALL db.idx.vector.queryNodes('paper_embedding', 10, $query_vector)`)
- **THEN** the query returns the top 10 most relevant papers

### Requirement: Graphiti uses FalkorDB for persistence + Dragonfly for episode cache

The system SHALL use Graphiti (via `graphiti-core`) with FalkorDB for
persistent graph storage and Dragonfly (Redis-compatible) for the
bi-temporal episode cache.

#### Scenario: Graphiti add_episode

- **GIVEN** Graphiti initialized with FalkorDB + Dragonfly
- **WHEN** `await graphiti.add_episode(...)` is called with Irish OCR data
- **THEN** the episode is stored in Dragonfly (for fast query)
- **AND** the entities + edges are persisted to FalkorDB

### Requirement: Garage S3 + Lakekeeper is the canonical object storage + catalog

The system SHALL use Garage S3 (S3-compatible, 3-node cluster) as the
canonical object storage, with Lakekeeper (Iceberg REST Catalog) on
port 8181 as the metadata layer.

#### Scenario: Garage 3-node HA

- **GIVEN** the Garage cluster has 3 nodes (replication factor 3)
- **WHEN** one node fails
- **THEN** the cluster continues serving reads + writes from the
  remaining 2 nodes
- **AND** no data loss (replication factor 3)

### Requirement: Cognee is the canonical knowledge graph memory layer

The system SHALL use Cognee for the knowledge graph memory layer,
indexing all `.md` documentation + BAML-extracted structured data into
6 typed datasets (aistear, primary, junior_cycle, senior_cycle,
tertiary, cross_stage) with Postgres unified provider (Neo4j fallback
for prod).

#### Scenario: Cognee cognify across 6 datasets

- **GIVEN** the Cognee stack is up at `http://cognee:8100`
- **WHEN** `await cognee.cognify()` runs against the 6 typed datasets
- **THEN** each dataset's docs are extracted → embedded → graphed
- **AND** the resulting knowledge graph is queryable via
  `cognee.search(query_type=GRAPH_COMPLETION)`

### Requirement: Cloudflare R2 + Workers + D1 is the canonical edge stack

The system SHALL use Cloudflare R2 (S3-compatible object storage for
public assets), Cloudflare Workers (edge compute for BAML extraction),
and Cloudflare D1 (serverless SQLite for OAuth sessions) as the
canonical edge stack.

#### Scenario: R2 + Workers + D1 integration

- **GIVEN** a TanStack Start route at `/api/extract` deployed to Workers
- **WHEN** the route receives a request with an R2 PDF key
- **THEN** it fetches the PDF from the `LEABHARLANN_BUCKET` R2 bucket
- **AND** runs BAML extraction via LiteLLM `minimax` alias
- **AND** looks up the OAuth session in D1 via `env.DB.prepare(...).bind(...)`

### Requirement: LanceDB IVF_HNSW_SQ is the canonical vector index (Wave 2 drift fix)

The system SHALL use **`IVF_HNSW_SQ`** as the default vector index for
all LanceDB tables (HNSW is a **sub-index** inside IVF partitions in
v0.33+, not a top-level type — the Wave-1 P1B-06 standalone HNSW
config is not creatable). For large tables (>1 M rows) the system
SHALL use `IVF_PQ` (or `IVF_RQ` when `dim <= 256`).

#### Scenario: IVF_HNSW_SQ build

- **GIVEN** a LanceDB `codebase_chunks` table with 50,000 rows and
  1024-dim BGE-M3 embeddings
- **WHEN** `table.create_index("vector", config=IvfHnswSq(
  num_partitions=4, metric="cosine", ef_construction=150))` runs
- **THEN** LanceDB builds an IVF_HNSW_SQ index (HNSW sub-graph inside
  4 IVF partitions + scalar quantisation)
- **AND** recall@10 ≥ 0.95 at p50 latency ≤ 200 ms

### Requirement: LanceDB Blob v2 is the canonical large-object store for PDFs + images

The system SHALL use **LanceDB Blob v2** (`pa.large_binary()` + Arrow
field metadata `{"lance-encoding:blob": "true"}`) for storing >1 MB
PDFs and high-res images directly inside LanceDB tables, with three
materialisation modes (`lazy`, `bytes`, `descriptions`).

#### Scenario: Blob v2 lazy materialisation of exam PDFs

- **GIVEN** a LanceDB `examination_papers` table with a `pdf_blob`
  column declared as `pa.large_binary()` with
  `lance-encoding:blob=true`
- **WHEN** a query reads 1000 rows via `.to_pandas(mode="lazy")`
- **THEN** the DataFrame loads with column metadata only
- **AND** the PDF bytes are NOT read from S3 until
  `.pdf_bytes[row_idx]` is accessed
- **AND** peak memory stays below 50 MB regardless of total table size

### Requirement: Graphiti bi-temporal tracking with FalkorDB + Dragonfly is canonical (Wave 2 verified)

The system SHALL use **Graphiti (`graphiti-core >= 0.29.2`)** for
bi-temporal context-graph storage, backed by **FalkorDB 1.1.2** (with
`vector.so` loadable) for the persistent graph and **Dragonfly**
(Redis-compatible) for the bi-temporal episode cache. Wave 2
benchmarks: **94.7% LoCoMo @ 155 ms, 90.2% LongMemEval @ 162 ms**.

#### Scenario: Bi-temporal fact invalidation

- **GIVEN** Graphiti is initialised with `FalkorDriver` + Dragonfly
  cache
- **WHEN** `await graphiti.add_episode(name="correction",
  episode_body="Taoiseach is no longer Leo Varadkar",
  reference_time=now)` runs after an earlier episode that said
  "Taoiseach is Leo Varadkar"
- **THEN** the earlier `EntityEdge` gets `invalid_at = reference_time`
  (auto-closed, not deleted)
- **AND** a point-in-time query for the first episode's date still
  returns "Taoiseach = Leo Varadkar"
- **AND** a query for today's date returns "Taoiseach = (new name)"

### Requirement: LanceDB embedding registry with 15+ providers is canonical (Wave 2)

The system SHALL use the **LanceDB embedding registry** (15+ providers:
OpenAI, HF, Sentence Transformers, Cohere, Jina, VoyageAI, OpenCLIP,
ImageBind, AWS Bedrock, Gemini, Ollama, IBM watsonx, ColPali,
Instructor, Superlinked) for every table that embeds at ingest time,
with provider secrets injected via `registry.set_var("api_key", ...)`
+ `$var:api_key` config placeholders.

#### Scenario: BGE-M3 embedding via the registry

- **GIVEN** a LanceDB table `codebase_chunks` is created with
  `embedding=registry.get("sentence-transformers").create(
  name="BAAI/bge-m3", dim=1024)`
- **WHEN** a row is added with raw text
- **THEN** the registry auto-embeds the text via the BGE-M3 model
- **AND** the `vector` column is populated with a 1024-dim float32
  array

### Requirement: Cognee 7-cluster knowledge graph with Postgres unified provider (Wave 2 confirmed)

The system SHALL run **Cognee 0.1.22+** with the **Postgres unified
provider** (relational + vector + graph in one Postgres instance,
Neo4j fallback for prod scale) and the canonical 7-cluster ontology
(aistear, primary, junior_cycle, senior_cycle, tertiary, leabharlann,
cross_stage) — one cluster per `cognee.datasets.add(...)` call.

#### Scenario: Cognee cognify on 7 clusters

- **GIVEN** the Cognee stack is up at `http://cognee:8100` with the
  Postgres unified provider
- **WHEN** `await cognee.cognify(datasets=["aistear", "primary",
  "junior_cycle", "senior_cycle", "tertiary", "leabharlann",
  "cross_stage"])` runs
- **THEN** each dataset's docs are extracted → embedded (BGE-M3) →
  graphed (entity + edge + community)
- **AND** the resulting knowledge graph is queryable via
  `cognee.search("What is the primary maths curriculum for 2026?",
  query_type=GRAPH_COMPLETION)`
