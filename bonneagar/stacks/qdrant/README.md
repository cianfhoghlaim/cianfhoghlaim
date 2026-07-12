# Qdrant — Vector Similarity Search Engine

## Overview

Qdrant is a high-performance open-source vector database written in Rust, designed for similarity search, recommendation, and semantic retrieval. It supports HNSW indexing, payload filtering, quantization, and multi-tenant collections — making it suitable for both development and production-scale vector search workloads.

## Why This Matters for Kings' College Galway

Qdrant provides high-performance vector search for the curriculum content. While LanceDB handles the primary curriculum embedding storage (with Iceberg integration), Qdrant serves as the low-latency search layer for the web app — when a student types "product rule differentiation example" into the search bar, Qdrant returns the top-K semantically similar learning outcomes and study assets in under 10ms. Its payload filtering enables scoped searches ("only show me senior cycle, higher level results"), and quantization keeps memory usage reasonable on the Hetzner node despite millions of embeddings.

## Key Features

- **Rust-native performance** — Sub-10ms search latency at million-vector scale
- **HNSW indexing** — Configurable M and ef parameters for speed/recall tradeoff
- **Payload filtering** — Filter by metadata (subject, cycle, level) during search
- **Quantization** — Scalar and product quantization for memory efficiency
- **Multi-tenant** — Isolated collections per subject or user group

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/qdrant
docker compose up -d
```

### Production (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `QDRANT_HTTP_PORT` | No | REST API port | `6333` |
| `QDRANT_GRPC_PORT` | No | gRPC API port | `6334` |
| `QDRANT_API_KEY` | Yes | API key for authentication | — |
| `QDRANT_LOG_LEVEL` | No | Log verbosity | `INFO` |

## Access

- **REST API**: `http://localhost:6333`
- **gRPC API**: `http://localhost:6334`
- **Web Dashboard**: Bundled at port 6333 (`/dashboard`)
- **Auth**: API key

## Upstream

- **Repository**: <https://github.com/qdrant/qdrant>
- **Documentation**: <https://qdrant.tech/documentation/>
- **Latest**: v1.13.x (2025) — full-text search integration, sparse vectors, geo-radius filtering, improved quantization

## Screenshot

![Qdrant Documentation](https://storage.googleapis.com/firecrawl-scrape-media/screenshot-97d683b2-6514-4d13-aad6-494f8acaefbe.png)

Qdrant's documentation at [qdrant.tech/documentation](https://qdrant.tech/documentation) covers vector search patterns. The built-in web dashboard provides a collections browser, visual search interface (nearest neighbours with similarity scores), and a telemetry panel showing index size, memory usage, and query throughput.
