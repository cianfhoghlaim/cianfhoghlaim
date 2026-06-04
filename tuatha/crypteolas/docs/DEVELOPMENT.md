# Crypteolas Development Guide

Complete development environment setup for the GitHub Intelligence + DeFi
Analytics platform. Crypteolas lives at `tuatha/crypteolas/` after the
[consolidation refactor](../../../../openspec/changes/consolidate-external-libs-into-tuatha/).
See [`../STATUS.md`](../STATUS.md) for the full refactor history.

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | `brew install python@3.12` or `mise install python@3.12` |
| uv | 0.5+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | 24+ | [Docker Desktop](https://docker.com) |
| Node.js | 22+ | `mise install node@22` or `brew install node@22` |
| Bun | 1.3+ | `mise install bun@1.3` (for the new frontend at `tuatha/apps/crypteolas demo/`) |

> The new TypeScript frontend at `tuatha/apps/crypteolas demo/` has
> standardised on **bun** (replacing the prior `pnpm` setup).

## Environment Setup

### 1. Clone and Install

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway
uv sync
```

### 2. Environment Variables

The root `.env` is hydrated by the `mise` directory hook from the
Infisical `dev-baile` vault. Manual override: create `.env.local` in the
project root.

```bash
# Required - GitHub
GITHUB_ACCESS_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_TOKEN=ghp_xxxxxxxxxxxx   # legacy alias

# Required - Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
LANCEDB_PATH=./data/lancedb
DUCKDB_PATH=./data/crypteolas.duckdb
REDIS_URL=redis://localhost:6379

# Required - LLM
ANTHROPIC_API_KEY=your-anthropic-key
# OR use the LiteLLM gateway (recommended)
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

# Optional - Observability
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=http://localhost:3000
```

### 3. Start Infrastructure

```bash
cd tuatha/crypteolas
docker compose -f compose.yaml up -d
```

Or with the dev overlay (hot-reload + Langfuse/FalkorDB integration):

```bash
cd tuatha/crypteolas
docker compose -f compose.yaml -f compose.dev.yaml up -d
```

This starts:
- **FalkorDB** (port 7687) - Graphiti knowledge graph
- **Memgraph** (port 7687) - Cognee static knowledge graph
- **LanceDB** - Vector store (file-based, no container)
- **Redis/Dragonfly** (port 6379) - Caching and rate limiting
- **Langfuse** (port 3000) - LLM observability

Verify services:
```bash
cd tuatha/crypteolas
docker compose -f compose.yaml ps
# All services should show "Up"
```

## Running the API

### Development Mode (with hot reload)

```bash
cd tuatha
uv run uvicorn crypteolas.api.main:app --reload --port 8001
```

API available at: http://localhost:8001

### Production Mode

```bash
cd tuatha
uv run uvicorn crypteolas.api.main:app --host 0.0.0.0 --port 8001 --workers 4
```

### Crypteolas AgentOS Runtime (port 7771)

```bash
cd tuatha
uv run uvicorn crypteolas.agent_os.main:app --port 7771
```

### Crypteolas MCP Server (stdio)

```bash
cd tuatha
uv run python -m crypteolas.mcp_server
```

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI/Swagger UI |
| `/health` | Health check |
| `/api/agent/*` | AG-UI streaming |
| `/api/analytics/*` | DeFi protocol analytics |
| `/api/search/*` | Hybrid code/doc search |
| `/api/github/*` | GitHub intelligence |
| `/api/auth/*` | SIWE authentication |
| `/api/payments/*` | x402 micropayments |
| `/api/agents/*` | AgentOS endpoints |

## Running Dagster Pipelines

### Start the unified Dagster UI (loads 3 code-locations)

```bash
cd tuatha
uv run dagster dev
# → http://localhost:3000
# → Code locations: tuath, crypteolas, crypteolas demo
```

### Materialize Assets (crypteolas)

```bash
cd tuatha
uv run dagster asset materialize -m crypteolas.definitions --select github_api_assets

# All DeFi data
uv run dagster asset materialize -m crypteolas.definitions --select defi_assets

# Full pipeline
uv run dagster job execute -m crypteolas.definitions -j ingestion_jobs
```

Or via mise:

```bash
mise dagster:crypteolas
```

### Available Assets

| Code-location | Asset | Description | Source |
|:--|:--|:--|:--|
| `crypteolas` | `github_api_assets` | GitHub issues, PRs, commits, workflows | GitHub API |
| `crypteolas` | `crawl_assets` | Documentation crawling | Firecrawl |
| `crypteolas` | `files_assets` | Local file processing | DLT |
| `crypteolas` | `defi_assets` | CoinGecko, DeFiLlama, Binance, subgraphs | DLT |
| `crypteolas` | `code_vector_index` | Code embeddings → LanceDB | CocoIndex |
| `crypteolas` | `docs_vector_index` | Doc embeddings → LanceDB | CocoIndex |
| `crypteolas` | `docs_graph_index` | Doc graph → Memgraph | Cognee |
| `crypteolas` | `cognee_knowledge_graph` | Static knowledge graph | Cognee |
| `crypteolas` | `graphiti_temporal_graph` | Temporal knowledge graph | Graphiti |
| `crypteolas` | `embedding_assets` | Embedding pipelines (multiple) | CocoIndex |
| `crypteolas` | `lakekeeper_examples` | LakeKeeper resource examples | Dagster |

## Testing

### Run All Tests

```bash
cd tuatha
uv run pytest crypteolas/tests/ -v
```

Or via mise:

```bash
mise test:crypteolas
```

### Run with Coverage

```bash
cd tuatha
uv run pytest crypteolas/tests/ --cov=crypteolas --cov-report=html
open htmlcov/index.html
```

### Test Categories

```bash
# Unit tests (61 pass, pre-existing failures are out of scope)
cd tuatha
uv run pytest crypteolas/tests/test_api_endpoints.py -v
uv run pytest crypteolas/tests/test_dlt_sources.py -v
uv run pytest crypteolas/tests/test_defi_analytics.py -v

# GitHub integration tests
uv run pytest crypteolas/tests/test_github_intelligence.py -v

# Knowledge graph tests
uv run pytest crypteolas/tests/test_knowledge_graph.py -v
```

## Running the Demo

Interactive demo showcasing features:

```bash
cd tuatha/crypteolas
uv run python -m demo.run_demo
```

Features demonstrated:
1. GitHub repository search
2. Code semantic search
3. DeFi protocol analytics
4. Protocol comparison
5. Agent research queries

## Frontend Development

The TanStack Start frontend has been moved to
`tuatha/apps/crypteolas demo/`. The legacy `tuatha/crypteolas/ui/` is
no longer the canonical frontend.

### New Frontend (tuatha/apps/crypteolas demo/)

```bash
cd tuatha/apps/crypteolas demo
bun install
bun run dev
# → http://localhost:3000 (proxies /api → localhost:8001)
```

> The TanStack app is currently a buildable shell of stubs. See
> [`../../apps/crypteolas demo/STATUS.md`](../../apps/crypteolas_demo/STATUS.md).

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
- MCP servers for code search (the `codeolas-mcp` server is recommended for semantic search over the workspace)
- Custom skills for DeFi patterns

## Troubleshooting

### GitHub Rate Limiting

```bash
# Check remaining rate limit
curl -H "Authorization: token $GITHUB_ACCESS_TOKEN" https://api.github.com/rate_limit

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
cd tuatha/crypteolas
docker compose restart falkordb
```

### Redis Connection Error

```bash
# Test connection
redis-cli ping

# If using Docker
docker exec -it crypteolas-dragonfly-1 redis-cli ping
```

### Embedding Model OOM

```bash
# Use smaller model for development
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Or reduce batch size
export EMBEDDING_BATCH_SIZE=32
```

### Dagster `Cannot annotate context parameter with type AssetExecutionContext`

This is a Dagster 1.12.6 vs prior-version compatibility issue in the
crypteolas assets. See `../STATUS.md` for the full list of pre-existing
issues; the structural refactor is complete but the asset-level API
mismatch needs separate fix.

## Project Structure

```
tuatha/crypteolas/
├── STATUS.md                          # the refactor history (read this first)
├── definitions.py                     # Dagster code-location
├── pyproject.toml                     # name = "crypteolas"
├── dg.toml                            # Dagster project config
├── compose.yaml, compose.dev.yaml
├── docker/                            # Dockerfile.api, Dockerfile.ui
├── _shims/                            # sruth.shared.* compatibility shims
├── agent_os/                          # AgentOS production runtime
├── agents/                            # ADK + Agno + HITL + MCP server
├── api/                               # FastAPI backend
│   ├── main.py
│   ├── routes/                        # agent, search, analytics, github, auth, payments
│   ├── services/                      # code_search, defi_analytics, etc.
│   └── lib/                           # x402 stubs
├── baml_src/                          # 6 crypto BAML schemas
├── cocoindex_flows/                   # unified_embedding, live_docs, protocol_graph
├── config/                            # repos.yaml, protocol configs
├── crates/                            # SpacetimeDB crypteolas-sync
├── dagster_assets/                    # github + defi + embedding + lakekeeper
├── dagster_assets/components/         # YAML PipelineComponent loader
├── demo/                              # mock data
├── dlt_sources/                       # defi/, github/, local/, documentation/
├── dlt_utils/                         # destinations
├── graphiti/                          # top-level Graphiti client
├── knowledge_graph/                   # cognee/ + graphiti/
├── mcp_server/                        # top-level MCP server
├── notebooks/                         # 4 marimo (post-dedup)
├── pipelines/                         # older Dagster pipelines
├── storage/                           # LanceCatalog, Garage, DuckLake, Lakekeeper
├── tests/                             # 61 passing + pre-existing failures
├── transformations/                   # Ibis-based crypto analytics
├── ui/                                # legacy TanStack (deferred to apps/crypteolas demo/)
├── docs/                              # 7 historical design docs
├── wrangler.toml                      # Cloudflare Workers (TODO)
└── dagster.yaml.example
```

## Data Sources

| Source | Data | Update Frequency | API Limits |
|--------|------|------------------|------------|
| GitHub API | Repos, commits, contributors, workflows | Hourly | 5000/hour |
| DeFiLlama | Protocols, TVL, yields | 15 min | None |
| CoinGecko | Prices, market data | 1 min | 50/min free |
| Binance | Funding rates, derivatives | Real-time | 1200/min |
| Bybit | Funding rates, OI | Real-time | 600/min |
| OKX | Funding rates, OI | Real-time | 600/min |
| Aave v3 subgraph | Reserves, positions | Daily | 1000 req/5min |
| Pendle subgraph | Markets, swaps | Daily | 1000 req/5min |
| Firecrawl | Web scraping | On-demand | per plan |
| Beaconcha.in | ETH staking, validators | 5 min | 200/min |

## Related Documentation

- [`../STATUS.md`](../STATUS.md) — the refactor history (drops, shims, BAML renames)
- [`../QUICKSTART.md`](../QUICKSTART.md) — quickstart for local dev
- [`../SETUP.md`](../SETUP.md) — detailed setup
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) — 25 KB architecture deep-dive
- [`../../README.md`](../../README.md) — the tuath workspace README
- [`../../DEVELOPMENT.md`](../../DEVELOPMENT.md) — workspace-level dev guide
