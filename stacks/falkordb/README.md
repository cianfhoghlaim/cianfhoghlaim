# FalkorDB — Vector + Graph Hybrid Database

## Overview

FalkorDB is a Redis-compatible graph database that combines graph queries (Cypher/OpenCypher) with vector similarity search in a single engine. Built on Redis, it provides ultra-low latency graph traversal and HNSW-powered vector search within the same database — enabling hybrid queries like "find learning outcomes similar to this one AND trace their prerequisite chain."

## Why This Matters for Kings' College Galway

FalkorDB fills the gap between pure vector databases (Qdrant, LanceDB) and pure graph databases (Neo4j, Memgraph) by doing both in one engine. For the curriculum platform, this means a single query can semantically search for related learning outcomes AND traverse their prerequisite graph simultaneously. This hybrid capability is essential for the study recommendation engine: "given the student is struggling with outcome 3.2, find similar outcomes they should review AND show the prerequisite chain that leads to the next topic" — all in one database call.

## Key Features

- **Cypher + vectors** — Graph queries and vector search in the same engine
- **Redis-compatible** — Works with existing Redis clients and tools
- **HNSW indexing** — Configurable for speed/recall tradeoff
- **Ultra-low latency** — Sub-millisecond graph traversals
- **Full-text search** — Integrated with vector search for hybrid retrieval

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/falkordb
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Redis-compatible port exposed for application connections.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `FALKORDB_PORT` | No | Redis-compatible port | `6379` |
| `FALKORDB_HTTP_PORT` | No | HTTP API port | `3000` |
| `FALKORDB_PASSWORD` | Yes | Authentication password | — |

## Access

- **Redis API**: `redis://localhost:6379`
- **HTTP API**: `http://localhost:3000`
- **Auth**: Password (Redis AUTH)

## Upstream

- **Repository**: <https://github.com/falkordb/falkordb>
- **Documentation**: <https://docs.falkordb.com>
- **Latest**: v4.x (2025) — vector search integration, hybrid query support, improved Cypher compatibility, Redis 7.4 compatibility

## Screenshot

FalkorDB is primarily a headless database engine accessed via Redis clients. The HTTP API at port 3000 provides a RESTful interface for graph and vector queries. Some community tools provide graph visualisation over the Redis protocol, rendering nodes and edges in a browser-based interface.
