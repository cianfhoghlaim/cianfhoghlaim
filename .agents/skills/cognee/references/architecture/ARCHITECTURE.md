# Architecture — Documentation Cognition Pipeline

## High-Level Architecture

The cognition pipeline transforms scattered `.md` documentation into a queryable knowledge graph that agents (via MCP servers) and applications (via REST APIs) can use for semantic retrieval, relationship discovery, and consolidation planning.

```
                              ┌──────────────────────────────────┐
                              │        .md Documentation         │
                              │   docs/agents/ docs/bonneagar/    │
                              │   docs/data_engineering/ ...      │
                              └──────────────┬───────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │     Cognee       │  Port 8100
                                    │  (ingest + KG)   │  Docker
                                    │  DeepSeek V4 Pro │
                                    └────────┬────────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          │                  │                  │
                 ┌────────▼────────┐ ┌──────▼───────┐ ┌───────▼────────┐
                 │    Graphiti     │ │   FalkorDB   │ │    Langfuse    │
                 │  (temporal KG)  │ │ (hybrid srch)│ │ (trace all ops)│
                 │    Port 8000    │ │  Port 6379   │ │   Port 3000    │
                 └────────┬────────┘ └──────┬───────┘ └───────┬────────┘
                          │                  │                  │
                          └──────────────────┼──────────────────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    │                        │                        │
           ┌───────▼────────┐    ┌──────────▼──────────┐    ┌───────▼────────┐
           │      CCC       │    │     Lakehouse        │    │    LakeFS      │
           │  (code search) │    │  (Garage S3 + Iceberg│    │  (data version) │
           │  .cocoindex_   │    │   + Lance Namespace) │    │   Port 8000    │
           └────────────────┘    └─────────────────────┘    └────────────────┘
                                             │
                                    ┌────────▼────────┐
                                    │    Monitoring    │
                                    │  Dozzle (logs)   │
                                    │  Beszel (metrics)│
                                    └─────────────────┘
```

## Component Roles

### Cognee — Primary Ingestion Engine
- **Input**: `.md` files via HTTP API (`POST /api/v1/add`) or Python SDK (`cognee.add()`)
- **Processing**: `cognify()` triggers LLM-based entity extraction and relationship inference using DeepSeek V4 Pro
- **Output**: Knowledge graph in Neo4j, vector embeddings in LanceDB
- **MCP**: `cognee-mcp` server for agent queries via `SearchType.GRAPH_COMPLETION`

### Graphiti — Temporal Layer
- **Input**: Same Neo4j instance as Cognee (shared backend)
- **Processing**: Adds bi-temporal metadata (valid time + transaction time) to knowledge graph nodes
- **Output**: Versioned knowledge graph — query curriculum data as it existed at any point in time
- **MCP**: `graphiti_core.mcp` for temporal queries from agents

### FalkorDB — Hybrid Search
- **Input**: Redis-compatible protocol on port 6379
- **Processing**: Combines Cypher graph queries with HNSW vector search in a single engine
- **Output**: Sub-millisecond hybrid queries: "find similar concepts AND traverse prerequisites"

### Langfuse — Observability Layer
- **Input**: Traces from Cognee's `cognify()` operations, CCC indexing runs, Graphiti temporal updates
- **Processing**: ClickHouse columnar storage for fast trace aggregation
- **Output**: Per-operation cost, latency, token usage — critical for tracking cognition pipeline costs

### CCC (CocoIndex Code) — Codebase Semantic Search
- **Input**: The entire monorepo source code (Python, TypeScript, BAML, Rust, Go)
- **Processing**: `bun run ccc:index` builds semantic index in `.cocoindex_code/target_sqlite.db`
- **Output**: `bun run ccc:search "query"` returns ranked code snippets with file paths
- **MCP**: `ccc mcp` server for agent tool calling

### Lakehouse — Storage Backend
- **Input**: Parquet files, LanceDB vectors, Iceberg table metadata
- **Processing**: Garage S3 provides S3-compatible storage; Lakekeeper provides Iceberg catalog; Lance Namespace bridges LanceDB → Iceberg
- **Output**: ACID-transactional, time-travel-capable, queryable from DuckDB and Python

### LakeFS — Data Versioning
- **Input**: All data writes to Garage S3 buckets
- **Processing**: Git-like branching/committing/merging of data at the S3 layer
- **Output**: `production` branch (current curriculum), `2023-reform` branch (historical), per-experiment branches

### Dozzle — Container Logs
- **Monitors**: Cognee container logs, Graphiti container logs, FalkorDB logs
- **Value**: Debug failed cognition runs, LLM API errors, Neo4j connection issues

### Beszel — Server Metrics
- **Monitors**: CPU/memory/disk/network across arm1-oci, cax41-hetzner, bunchloch
- **Value**: Alert when cognition pipeline saturates memory (Neo4j graph size, LanceDB index build)

## Data Flow — End to End

```
1. INDEX:  ccc:index → .cocoindex_code/target_sqlite.db
2. INGEST: Cognee POST /api/v1/add → documents stored in LanceDB
3. COGNIFY: Cognee POST /api/v1/cognify → LLM extracts entities/relationships → Neo4j KG
4. TEMPORAL: Graphiti records valid/transaction times → bi-temporal layer
5. HYBRID: FalkorDB indexes vectors + graph → sub-ms hybrid queries
6. TRACE: Langfuse captures all LLM calls → cost/latency/token analytics
7. STORE: Lakehouse persists Parquet/LanceDB files on Garage S3
8. VERSION: LakeFS branches/commits/merges data at S3 layer
9. MONITOR: Dozzle shows real-time logs; Beszel alerts on resource saturation
```

## Agent Access

All components are accessible to agents via MCP servers in `opencode.json`:

| Agent tool | Backend | MCP server |
|:--|:--|:--|
| `cognee_search("query")` | Cognee GraphRAG | `cognee` |
| `cocoindex-code_search("query")` | CCC semantic index | `cocoindex-code` |
| `graphiti_search("query")` | Graphiti temporal KG | `graphiti` |
| `langfuse_get_trace(id)` | Langfuse traces | `langfuse` |
| `motherduck_execute_query(sql)` | MotherDuck analytics | `motherduck` |
| `firecrawl_scrape(url)` | Web scraping | `firecrawl` |
