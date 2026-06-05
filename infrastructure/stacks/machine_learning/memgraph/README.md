# Memgraph — In-Memory Graph Database with MAGE

## Overview

Memgraph is a high-performance, in-memory graph database compatible with the Cypher query language (Neo4j's query language). It includes MAGE (Memgraph Advanced Graph Extensions) — a library of graph algorithms for pathfinding, community detection, centrality analysis, and more. The Lab UI provides a browser-based graph exploration and query interface.

## Why This Matters for Kings' College Galway

Memgraph is the fastest graph database in the platform, used for real-time prerequisite chain queries. When a student is working through a learning outcome and the web app needs to compute "what are the immediate next steps after mastering this concept?" Memgraph traverses the knowledge graph in microseconds — faster than Neo4j (which is disk-based) or FalkorDB (which is Redis-based but adds network overhead). The MAGE algorithm library enables graph analytics like finding the most central concepts in the curriculum or detecting circular prerequisites that indicate a syllabus error.

## Key Features

- **In-memory Cypher** — Full Cypher compatibility with sub-millisecond queries
- **MAGE algorithms** — BFS/DFS, PageRank, betweenness centrality, community detection
- **Lab UI** — Browser-based graph visualisation and query IDE
- **Stream processing** — Real-time graph updates via Kafka/Pulsar streams
- **Durability** — Periodic snapshots and WAL for crash recovery

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/memgraph
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Locket resolves `MEMGRAPH_PASSWORD` from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `MEMGRAPH_BOLT_PORT` | No | Bolt protocol port | `7687` |
| `MEMGRAPH_HTTP_PORT` | No | HTTP port (for Lab) | `7444` |
| `MEMGRAPH_LAB_PORT` | No | Lab UI port | `3000` |
| `MEMGRAPH_USER` | No | Database user | `memgraph` |
| `MEMGRAPH_PASSWORD` | Yes | Database password | — |
| `MEMGRAPH_LOG_LEVEL` | No | Log verbosity | `WARNING` |

## Access

- **Bolt Protocol**: `bolt://localhost:7687`
- **Lab UI**: `https://memgraph-lab.cianfhoghlaim.ie` (private, Member role)
- **Auth**: Username/password (Bolt); Pocket ID SSO (Lab)

## Upstream

- **Repository**: <https://github.com/memgraph/memgraph>
- **Documentation**: <https://memgraph.com/docs>
- **Latest**: v3.x (2025) — MAGE library expansion, Lab UI rewrite, stream processing improvements, ARM64 support

## Screenshot

![Memgraph Documentation](https://storage.googleapis.com/firecrawl-scrape-media/screenshot-d159a896-6723-4bc3-8daa-35f271b6283f.png)

Memgraph's documentation at [memgraph.com/docs](https://memgraph.com/docs) covers graph algorithms and Cypher. Memgraph Lab provides a graph visualisation interface: nodes rendered with customisable colours and sizes, edges showing relationship types, a Cypher query editor with autocomplete, and query result tables with zoom, pan, and force-directed layout.
