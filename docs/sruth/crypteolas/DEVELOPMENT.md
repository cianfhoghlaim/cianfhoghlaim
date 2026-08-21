# Crypteolas Development Guide

Complete development environment setup for the GitHub Intelligence + DeFi Analytics platform.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | `brew install python@3.12` |
| uv | 0.5+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | 24+ | [Docker Desktop](https://docker.com) |
| Node.js | 22+ | `mise install node@22` or `brew install node@22` |
| pnpm | 9+ | `npm install -g pnpm` |

## Environment Setup

### 1. Clone and Install

```bash
cd /Users/cliste/dev/cianfhoghlaim
uv sync
```

### 2. Environment Variables

Create `.env.local` in the project root:

```bash
# Required - GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx

# Required - Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
LANCEDB_PATH=./data/lancedb
REDIS_URL=redis://localhost:6379

# Required - LLM
ANTHROPIC_API_KEY=your-anthropic-key
# OR use LiteLLM gateway
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=your-litellm-key

# Optional - DeFi Data
DEFILLAMA_API_KEY=your-key          # Higher rate limits
COINGECKO_API_KEY=your-key          # Pro features
BINANCE_API_KEY=your-key            # Derivatives data
BINANCE_API_SECRET=your-secret

# Optional - Embeddings
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu  # or cuda, mps

# Optional - Auth
JWT_SECRET=your-jwt-secret
SIWE_DOMAIN=localhost
```

### 3. Start Infrastructure

```bash
cd sruth/crypteolas
docker-compose up -d
```

This starts:
- **FalkorDB** (port 7687) - Graphiti knowledge graph
- **Redis** (port 6379) - Caching and rate limiting
- **LanceDB** - Vector store (file-based, no container)

Verify services:
```bash
docker-compose ps
# All services should show "Up"
```

## Running the API

### Development Mode (with hot reload)

```bash
cd sruth/crypteolas
uv run uvicorn crypteolas.api.main:app --reload --port 8001
```

API available at: http://localhost:8001

### Production Mode

```bash
uv run uvicorn crypteolas.api.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI/Swagger UI |
| `/health` | Health check |
| `/api/github/*` | GitHub intelligence |
| `/api/analytics/*` | DeFi protocol analytics |
| `/api/search/*` | Hybrid code/doc search |
| `/api/agent/*` | AG-UI agent streaming |
| `/auth/*` | SIWE authentication |

## Running Dagster Pipelines

### Start Dagster UI

```bash
cd sruth/crypteolas
dagster dev -m crypteolas.dagster_assets
```

Dagster UI at: http://localhost:3000

### Materialize Assets

```bash
# GitHub data
dagster asset materialize -m crypteolas.dagster_assets --select github_repositories

# DeFi data
dagster asset materialize -m crypteolas.dagster_assets --select defi_protocols

# Full pipeline
dagster job execute -m crypteolas.dagster_assets -j crypteolas_full_pipeline
```

### Available Assets

| Asset | Description | Source |
|-------|-------------|--------|
| `github_repositories` | DeFi repo metadata | GitHub API |
| `github_commits` | Commit history | GitHub API |
| `github_contributors` | Developer activity | GitHub API |
| `defi_protocols` | Protocol TVL | DeFiLlama |
| `defi_pools` | Yield opportunities | DeFiLlama |
| `repository_embeddings` | Code vectors | CocoIndex |
| `protocol_embeddings` | Doc vectors | CocoIndex |

## Testing

### Run All Tests

```bash
cd sruth/crypteolas
uv run pytest tests/ -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=crypteolas --cov-report=html
open htmlcov/index.html
```

### Test Categories

```bash
# Unit tests
uv run pytest tests/test_api_endpoints.py -v

# GitHub integration tests
uv run pytest tests/test_github_intelligence.py -v

# DeFi analytics tests
uv run pytest tests/test_defi_analytics.py -v
```

## Running the Demo

Interactive demo showcasing features:

```bash
cd sruth/crypteolas
uv run python -m crypteolas.demo.run_demo
```

Features demonstrated:
1. GitHub repository search
2. Code semantic search
3. DeFi protocol analytics
4. Protocol comparison
5. Agent research queries

## Frontend Development

### Install Frontend Dependencies

```bash
cd sruth/crypteolas/ui
pnpm install
```

### Run Frontend Dev Server

```bash
cd sruth/crypteolas/ui
pnpm dev
```

Frontend at: http://localhost:3000 (proxies to API at :8001)

## IDE Configuration

### VS Code

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true
  }
}
```

### Claude Code

Project includes Claude Code configuration for:
- Task tool for multi-step analysis
- MCP servers for code search
- Custom skills for DeFi patterns

## Troubleshooting

### GitHub Rate Limiting

```bash
# Check remaining rate limit
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Use Redis cache to reduce API calls
export GITHUB_CACHE_ENABLED=true
export GITHUB_CACHE_TTL=3600
```

### FalkorDB Connection Error

```bash
# Check container
docker ps | grep falkordb

# View logs
docker logs crypteolas-falkordb-1

# Restart
docker-compose restart falkordb
```

### Redis Connection Error

```bash
# Test connection
redis-cli ping

# If using Docker
docker exec -it crypteolas-redis-1 redis-cli ping
```

### Embedding Model OOM

```bash
# Use smaller model for development
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Or reduce batch size
export EMBEDDING_BATCH_SIZE=32
```

## Project Structure

```
crypteolas/
├── api/
│   ├── main.py              # FastAPI app entrypoint
│   ├── routes/              # API route handlers
│   │   ├── agent.py         # AG-UI streaming
│   │   ├── search.py        # Hybrid search
│   │   ├── analytics.py     # DeFi analytics
│   │   ├── github.py        # GitHub intelligence
│   │   └── auth.py          # SIWE authentication
│   └── services/            # Business logic
│       ├── code_search_service.py
│       ├── defi_analytics_service.py
│       ├── document_search_service.py
│       └── knowledge_graph_service.py
├── agents/
│   ├── adk/                 # Google ADK agents
│   │   ├── root_agent.py    # Orchestrator
│   │   ├── protocol_research.py
│   │   ├── code_analysis.py
│   │   ├── defi_analytics.py
│   │   └── documentation_agent.py
│   └── tools/               # Agent tools
│       ├── code_search.py
│       ├── document_search.py
│       └── defi_metrics.py
├── dlt_sources/             # DLT data ingestion
│   ├── github/              # GitHub API source
│   ├── defi/                # DeFiLlama, CoinGecko, Binance
│   └── documentation/       # Protocol docs
├── cocoindex_flows/         # CocoIndex embeddings
│   ├── code_embedding.py
│   ├── document_embedding.py
│   └── transforms/
│       └── code_chunking.py
├── knowledge_graph/         # Graph databases
│   ├── graphiti/            # Temporal protocol graph
│   └── cognee/              # Static knowledge
├── dagster_assets/          # Dagster orchestration
│   ├── definitions.py
│   ├── github_assets.py
│   ├── defi_assets.py
│   ├── embedding_assets.py
│   └── schedules.py
├── tests/                   # pytest test suite
├── demo/                    # Interactive demos
└── docker-compose.yml       # Infrastructure
```

## Data Sources

| Source | Data | Update Frequency | API Limits |
|--------|------|------------------|------------|
| GitHub API | Repos, commits, contributors | Hourly | 5000/hour |
| DeFiLlama | Protocols, TVL, yields | 15 min | None |
| CoinGecko | Prices, market data | 1 min | 50/min free |
| Binance | Funding rates, derivatives | Real-time | 1200/min |

## Related Documentation

- [API Reference](docs/API.md)
- [Agent Architecture](docs/AGENTS.md)
- [Pipeline Guide](docs/PIPELINES.md)
- [QUICKSTART.md](QUICKSTART.md)
