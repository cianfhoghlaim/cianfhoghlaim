# Graphiti — Temporal Knowledge Graph

## Overview

Graphiti is an open-source temporal knowledge graph system that builds and queries bi-temporal graphs — tracking not just what is true now, but what was true at any point in time. It supports Neo4j and FalkorDB as graph backends, embeddings for semantic search, and incremental updates as new information arrives.

## Why This Matters for Kings' College Galway

Graphiti's bi-temporal model is uniquely suited to curriculum data, which changes on two time axes: the "valid time" (when a syllabus was in effect for students) and the "transaction time" (when the syllabus document was published/ingested). When the Irish government reforms the Leaving Cert Maths syllabus in 2027, Graphiti records the 2023 syllabus as valid from 2023 to 2027 and the new syllabus from 2027 onward — both are queryable. This temporal awareness makes it possible to ask "what were the prerequisite chains for differentiation in the 2023 syllabus?" and get an accurate answer even after the syllabus has changed.

## Key Features

- **Bi-temporal model** — Separate valid time and transaction time for every fact
- **Episodic memory** — Track knowledge across multiple syllabus versions
- **Incremental updates** — Add new curriculum documents without rebuilding the graph
- **Semantic search** — Embedding-based retrieval of related learning outcomes
- **Multi-backend** — Neo4j (default) and FalkorDB

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/graphiti
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Requires a running Neo4j instance. Locket resolves `OPENAI_API_KEY` and `NEO4J_PASSWORD` from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `OPENAI_API_KEY` | Yes | LLM API key for entity extraction | — |
| `NEO4J_URI` | No | Neo4j Bolt URI | `bolt://neo4j:7687` |
| `NEO4J_USER` | No | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Yes | Neo4j password | — |
| `PORT` | No | API port | `8000` |
| `db_backend` | No | Graph database backend | `neo4j` |

## Access

- **API**: `http://localhost:8000`
- **Healthcheck**: `http://localhost:8000/healthcheck`
- **Neo4j Browser**: `http://localhost:7474`
- **Auth**: API key (internal); Neo4j credentials for graph browser

## Upstream

- **Repository**: <https://github.com/getzep/graphiti>
- **Documentation**: <https://help.getzep.com/graphiti>
- **Latest**: Active development (2025) — bi-temporal search improvements, FalkorDB backend support, incremental ingestion performance

## Screenshot

Graphiti serves a headless REST API at port 8000. The Neo4j Browser at port 7474 provides a graph visualisation interface for exploring knowledge graphs directly — nodes represent learning outcomes and concepts, edges represent prerequisite and related-to relationships with validity timestamps.
