# Cognee Setup — Docker + DeepSeek + Neo4j + MCP

Complete setup guide for running Cognee v1.1 as a Docker container with DeepSeek API, Neo4j graph backend, LanceDB vector storage, and MCP server activation.

## Prerequisites

- Docker + Docker Compose
- DeepSeek API key (`$DEEPSEEK_API_KEY` in environment, hydrated from Infisical)
- Neo4j running (from Graphiti stack or standalone)

## Quick Setup

```bash
# 1. Ensure Neo4j is running
cd infrastructure/stacks/graphiti
docker compose up neo4j -d
# Verify: curl -s http://localhost:7474 | head -5

# 2. Start Cognee with DeepSeek API
cd ../cognee
DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" docker compose up -d
# Wait 10s for migrations to complete
sleep 10

# 3. Verify
curl -s http://localhost:8100/docs | head -5
# Should return Swagger HTML
```

## Docker Compose Configuration

The compose.yaml at `infrastructure/stacks/cognee/compose.yaml`:

```yaml
services:
  cognee:
    image: cognee/cognee:latest  # Docker Hub: v1.1.2
    ports:
      - "8100:8000"  # Host 8100 → Container 8000
    environment:
      - LLM_API_KEY=${DEEPSEEK_API_KEY}
      - LLM_PROVIDER=openai       # DeepSeek is OpenAI-compatible
      - LLM_MODEL=deepseek-chat    # DeepSeek V4 Pro via API
      - LLM_ENDPOINT=https://api.deepseek.com/v1
      - EMBEDDING_PROVIDER=openai
      - EMBEDDING_MODEL=text-embedding-3-small
      - GRAPH_DATABASE_PROVIDER=neo4j
      - GRAPH_DATABASE_URL=bolt://host.docker.internal:7687
      - GRAPH_DATABASE_USERNAME=neo4j
      - GRAPH_DATABASE_PASSWORD=devpassword
      - VECTOR_DATABASE_PROVIDER=lancedb
      - ENABLE_BACKEND_ACCESS_CONTROL=false
      - CACHING=false
    volumes:
      - cognee_data:/data
```

## Cognee API Endpoints

| Method | Endpoint | Purpose |
|:--|:--|:--|
| `POST` | `/api/v1/auth/register` | Register user |
| `POST` | `/api/v1/auth/login` | Login (returns access token) |
| `POST` | `/api/v1/add` | Add documents (multipart form data) |
| `POST` | `/api/v1/cognify` | Build knowledge graph from added docs |
| `POST` | `/api/v1/search` | Search the knowledge graph |
| `GET` | `/api/v1/search` | Get search history |
| `GET` | `/docs` | Swagger API documentation |

## Adding Documents

### Via HTTP API (recommended for batch ingestion)

```bash
# Upload a single file
curl -X POST http://localhost:8100/api/v1/add \
  -F "data=@document.md" \
  -F "datasetName=docs-agents"

# Upload multiple files
for f in docs/agents/*.md; do
  curl -X POST http://localhost:8100/api/v1/add \
    -F "data=@$f" \
    -F "datasetName=docs-agents"
done
```

### Via Python Script (batch processing)

```bash
# Using our custom ingestion script
cd oideachais
uv run python scripts/cognee_http_ingest.py ../docs/agents docs-agents
uv run python scripts/cognee_http_ingest.py ../docs/bonneagar docs-bonneagar
```

## Building the Knowledge Graph (Cognify)

```bash
# Cognify a single dataset
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{"datasets": ["docs-agents"]}'

# Cognify all datasets
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{"datasets": ["docs-agents", "docs-bonneagar", "docs-data-eng", "docs-ml", "docs-web", "docs-context"]}'

# Cognify in background (async)
curl -X POST http://localhost:8100/api/v1/cognify \
  -H "Content-Type: application/json" \
  -d '{"datasets": ["docs-agents"], "runInBackground": true}'
```

## Searching the Graph

```bash
# Graph completion (most powerful — uses LLM reasoning)
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "searchType": "GRAPH_COMPLETION",
    "query": "what are the key patterns for BAML extraction in curriculum documents?",
    "datasets": ["docs-agents"]
  }'

# Chunks (fast semantic search)
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "searchType": "CHUNKS",
    "query": "Pangolin Traefik middleware configuration"
  }'

# Summaries (topical overview)
curl -X POST http://localhost:8100/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "searchType": "SUMMARIES",
    "query": "what are the main topics in the infrastructure documentation?"
  }'
```

## MCP Server Setup

The Cognee MCP server is configured in `opencode.json`:

```json
{
  "mcp": {
    "cognee": {
      "type": "local",
      "command": ["uvx", "cognee-mcp"],
      "env": {
        "COGNEE_API_URL": "http://localhost:8100",
        "COGNEE_API_KEY": "infisical://dev-baile/cognee/api_key",
        "LLM_API_KEY": "infisical://dev-baile/deepseek/api_key"
      },
      "enabled": true
    }
  }
}
```

This exposes Cognee's knowledge graph search to agents via the `cognee_search` tool.

## Troubleshooting

### Container won't start
```bash
docker logs cognee | tail -20
# Common issues: Neo4j unreachable, API key not set
```

### Cognify hangs
```bash
# Check Neo4j is healthy
curl -s http://localhost:7474 | head -3
# Check LLM API key
docker exec cognee env | grep LLM_API_KEY
# Ensure key is not empty
```

### Search returns no results
```bash
# Verify documents were added
curl http://localhost:8100/api/v1/search?dataset_name=docs-agents
# Re-run cognify if documents were added after last cognify
```
