# Cognee — AI Memory System with GraphRAG

## Overview

Cognee is an open-source AI memory and knowledge management framework that builds dynamic knowledge graphs from documents, conversations, and data pipelines. It supports multiple graph backends (Neo4j, Memgraph, FalkorDB), provides GraphRAG capabilities, and integrates with LLMs for semantic retrieval and reasoning over structured knowledge.

## Why This Matters for Kings' College Galway

Cognee is the primary knowledge graph builder for the curriculum extraction pipeline. When Dagster processes a Leaving Cert Mathematics syllabus, Cognee extracts entities (learning outcomes, prerequisite concepts, assessment criteria), builds a graph with weighted edges representing prerequisite relationships, and serves GraphRAG queries so the web app can answer "what do I need to understand before tackling differentiation?" This graph is the pedagogical backbone — it encodes the dependency structure that teachers use to sequence lessons, and it does so automatically from unstructured syllabus documents.

## Key Features

- **Multi-backend graphs** — Neo4j, Memgraph, FalkorDB (all three deployed in this infrastructure)
- **GraphRAG** — Retrieval-augmented generation over knowledge graphs
- **Document ingestion** — Automatic entity extraction and relationship inference
- **MCP integration** — Cognee MCP server for Cursor/Claude Desktop/VS Code integration
- **Temporal awareness** — Track how knowledge evolves as curricula change

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/cognee
docker compose up -d
```

### With Neo4j backend

```bash
docker compose --profile neo4j up -d
```

### WIth Frontend UI

```bash
docker compose --profile ui up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Locket resolves API keys and database passwords from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DEBUG` | No | Enable debug mode | `false` |
| `HOST` | No | API host | `0.0.0.0` |
| `ENVIRONMENT` | No | Runtime environment | `local` |
| `LOG_LEVEL` | No | Log verbosity | `ERROR` |
| `OPENAI_API_KEY` | Yes | LLM API key for entity extraction | — |
| `NEO4J_URI` | No | Neo4j Bolt URI | `bolt://neo4j:7687` |
| `NEO4J_USER` | No | Neo4j username | `neo4j` |
| `NEO4J_PASSWORD` | Yes | Neo4j password | — |
| `GRAPH_DATABASE_PROVIDER` | No | Graph backend | `neo4j` |

## Access

- **API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000` (profile: `ui`)
- **Debugger**: Port 5678
- **Auth**: API key-based (internal service)

## Upstream

- **Repository**: <https://github.com/topoteretes/cognee>
- **Documentation**: <https://cognee.ai>
- **Latest**: Active development (2025) — GraphRAG improvements, multi-model LLM support, MCP server integration

## Screenshot

Cognee's API is headless (REST/WebSocket). The optional frontend UI (profile: `ui`) at port 3000 provides a dashboard for browsing knowledge graphs, querying with natural language, and viewing entity-relationship visualisations. The MCP server enables integration with AI coding assistants for graph exploration.
