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
