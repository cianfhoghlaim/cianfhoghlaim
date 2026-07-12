# LanceDB — Embedded Vector Database

## Overview

LanceDB is an open-source embedded vector database built on the Lance columnar format. It provides serverless, embedded vector search with HNSW indexing, MVCC safety for concurrent reads/writes, and hybrid search combining vector similarity with full-text and metadata filtering. Unlike server-based vector databases, LanceDB runs in-process with zero infrastructure overhead.

## Why This Matters for Kings' College Galway

LanceDB is the primary vector store for curriculum embeddings. When the Dagster pipeline extracts learning outcomes from a syllabus, it embeds them using BGE-M3 and stores the vectors in LanceDB. The Lance format's columnar design means vector search is fast (HNSW) and the data is directly queryable by DuckDB — no ETL step between the vector store and the analytics engine. The Lance Namespace sidecar (in the lakehouse stack) registers LanceDB tables as Iceberg tables, unifying vector and structured data under one catalog. MVCC safety means the web app can serve search results while the Dagster pipeline ingests new embeddings concurrently.

## Key Features

- **Embedded/serverless** — No separate database server; runs in-process with Python
- **HNSW indexing** — Configurable M and ef parameters for speed/accuracy
- **MVCC safety** — Concurrent readers and writers without locking
- **Hybrid search** — Vector + full-text + metadata filtering in one query
- **DuckDB integration** — Lance format is directly readable by DuckDB
- **Iceberg integration** — Registered as Iceberg tables via Lance Namespace

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/lancedb
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. LanceDB's data viewer provides a web UI for browsing collections and running queries.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LANCEDB_PORT` | No | Data viewer port | `8080` |
| `LANCEDB_STORAGE_PATH` | No | Data storage path | `/data/lancedb` |
| `S3_ENDPOINT` | No | Garage S3 endpoint for cloud storage | — |

## Access

- **Python API**: Embedded (no server — `import lancedb`)
- **Data Viewer**: `http://localhost:8080`
- **Auth**: Internal (no authentication for embedded mode)

## Upstream

- **Repository**: <https://github.com/lancedb/lancedb>
- **Documentation**: <https://lancedb.github.io/lancedb/>
- **Latest**: v0.15.x (2025) — MVCC improvements, HNSW index persistence, hybrid search with full-text, Iceberg table registration

## Screenshot

LanceDB's data viewer at port 8080 provides a table browser showing collection schemas, sample rows, and query execution. The embedded nature means most interaction is through Python code (`lancedb.connect()`) rather than a UI. The Lance Namespace sidecar in the lakehouse stack provides Iceberg-compatible table discovery.
