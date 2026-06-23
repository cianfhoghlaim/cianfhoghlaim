# Cognee — Knowledge & Cognition Integration Hub

Cognition pipeline for documentation processing, knowledge graph construction, and agent-accessible semantic search across the Kings' College Galway project.

## What This Directory Covers

| File | Purpose |
|:--|:--|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Full cognition pipeline architecture — how Cognee, Graphiti, FalkorDB, Langfuse, CCC, Lakehouse, LakeFS, Dozzle, Beszel connect |
| [COGNEE_SETUP.md](./COGNEE_SETUP.md) | Step-by-step Cognee Docker setup with DeepSeek API, Neo4j backend, MCP server activation |
| [COGNEE_INTEGRATION.md](./COGNEE_INTEGRATION.md) | Dagster asset pipeline for document ingestion, GraphRAG query patterns, remember/cognify/search API |
| [CCC_INTEGRATION.md](./CCC_INTEGRATION.md) | CocoIndex + CCC MCP setup, codebase indexing strategy, `ccc:index`/`ccc:search` commands |
| [MCP_SERVERS.md](./MCP_SERVERS.md) | Full `opencode.json` MCP config reference for all cognition, search, and observability servers |
| [WORKFLOW.md](./WORKFLOW.md) | End-to-end documentation cognition workflow: index → cognify → analyze → merge → monitor |
| [INFRASTRUCTURE.md](./INFRASTRUCTURE.md) | Supporting stacks: Lakehouse (storage), LakeFS (versioning), Dozzle (logs), Beszel (metrics) |
| [LANGFUSE_OBSERVABILITY.md](./LANGFUSE_OBSERVABILITY.md) | Langfuse MCP setup, tracing cognition operations, cost tracking |

## The 8-Stack Cognition Pipeline

```
.md files ──▶ Cognee (ingest + cognify) ──▶ Graphiti (temporal KG)
                   │                              │
                   ▼                              ▼
              Langfuse ◀── trace all ───▶ FalkorDB (hybrid search)
                   │
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
  CCC          Lakehouse       LakeFS
(search)      (storage)       (version)
    │              │              │
    └──────────────┼──────────────┘
                   ▼
            Dozzle + Beszel
            (monitor pipeline)
```

## Quick Start

```bash
# 1. Start the cognition infrastructure
cd infrastructure/stacks/cognee
docker compose -f compose.yaml up -d  # Cognee on :8100

cd ../graphiti
docker compose up neo4j -d  # Neo4j on :7687, Graphiti on :8000

cd ../falkordb
docker compose up -d  # FalkorDB on :6379

# 2. Index the codebase
bun run ccc:index

# 3. Cognify documentation
cd oideachais
uv run python scripts/cognee_setup.py
uv run python scripts/cognee_http_ingest.py ../docs/agents docs-agents
uv run python scripts/cognee_http_ingest.py ../docs/data_engineering docs-data-eng
uv run python scripts/cognee_http_ingest.py ../docs/bonneagar docs-bonneagar

# 4. Build knowledge graph (triggers LLM entity extraction)
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{"datasets": ["docs-agents", "docs-data-eng", "docs-bonneagar"]}'

# 5. Query the graph via MCP (available to agents in opencode.json)
```

## MCP Servers Configured

| Server | Port | Purpose |
|:--|:--|:--|
| `cognee` | 8100 | Document ingestion, GraphRAG queries |
| `cocoindex-code` | local | Semantic code search |
| `graphiti` | 8000 | Temporal knowledge graph |
| `langfuse` | 3000 | LLM trace observability |
| `firecrawl` | cloud | Web scraping for docs |
| `browserbase` | cloud | Browser automation |
| `chrome` | local | Local Chrome DevTools |
| `motherduck` | cloud | SQL analytics |
| `infisical` | 8081 | Secret management |
