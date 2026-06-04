# Crypteolas - GitHub Intelligence + DeFi Analytics

Cross-domain crypto research platform combining GitHub development activity
with DeFi metrics. This package lives at `tuatha/crypteolas/` after the
[consolidation refactor](../../../../openspec/changes/consolidate-external-libs-into-tuatha/).
See [`../STATUS.md`](../STATUS.md) for the full dedup + shim + BAML rename
history.

## Prerequisites

- Python 3.11+
- Node.js 20+ (for the TanStack UI — the new frontend is at
  `tuatha/apps/crypteolas_demo/`; this directory still has a `ui/` subdir
  that is no longer the canonical frontend)
- Docker & Docker Compose
- uv (Python package manager)
- Bun 1.3+ (for the new crypteolas_demo frontend at `tuatha/apps/crypteolas_demo/`)

## Quick Start

### 1. Start Infrastructure

```bash
cd tuatha/crypteolas
docker compose -f compose.yaml up -d
```

This starts:
- FalkorDB (Knowledge graph)
- LanceDB (Vector store via volume)
- Redis (Caching)
- Memgraph + Memgraph Lab
- Langfuse (LLM observability)
- Lance viewer

Or for the dev overlay (hot-reload + Langfuse/FalkorDB integration):

```bash
cd tuatha/crypteolas
docker compose -f compose.yaml -f compose.dev.yaml up -d
```

### 2. Install Dependencies

```bash
# From the tuatha/ root (which resolves the crypteolas workspace member)
cd tuatha && uv sync

# TypeScript frontend (now lives at tuatha/apps/crypteolas demo/)
cd ../tuatha/apps/crypteolas demo && bun install
```

### 3. Run the API

```bash
cd tuatha
uv run uvicorn crypteolas.api.main:app --port 8001 --reload
```

API available at: http://localhost:8001

### 4. Run the Frontend (TanStack Start stub)

```bash
cd tuatha/apps/crypteolas demo
bun install
bun run dev
```

Frontend available at: http://localhost:3000 (proxies `/api` to the crypteolas
FastAPI at :8001)

> The TanStack app is currently a buildable shell of stubs. See
> [`../../../tuatha/apps/crypteolas demo/STATUS.md`](../../../../tuatha/apps/crypteolas_demo/STATUS.md).

### 5. Run the Demo

```bash
cd tuatha/crypteolas
uv run python -m demo.run_demo
```

### 6. Run the AgentOS runtime

```bash
cd tuatha
uv run uvicorn crypteolas.agent_os.main:app --port 7771
```

### 7. Start the MCP server

```bash
cd tuatha
uv run python -m crypteolas.mcp_server
```

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI documentation |
| `/health` | Health check |
| `/github/*` | GitHub intelligence |
| `/defi/*` | DeFi protocol analytics |
| `/search/*` | Hybrid search (LanceDB + Memgraph) |
| `/copilotkit/*` | AI research agent |
| `/auth/*` | SIWE authentication |
| `/payments/*` | x402 micropayments |
| `/agents/*` | AgentOS endpoints |

## Testing

```bash
# From the tuatha/ root
cd tuatha

# Run all crypteolas tests
uv run pytest crypteolas/tests/ -v

# Or via mise
mise test:crypteolas
```

## Dagster Pipelines

```bash
# Start the unified Dagster UI (loads all 3 code-locations)
cd tuatha
uv run dagster dev
# → http://localhost:3000

# Or run crypteolas in isolation
cd tuatha
uv run dagster dev -m crypteolas.definitions
# → http://localhost:3000 (just the crypteolas code-location)

# Or via mise
mise dagster:crypteolas
```

### Available Assets

| Code-location | Asset | Description |
|:--|:--|:--|
| `crypteolas` | `github_api_assets` | GitHub issues, PRs, commits, workflows |
| `crypteolas` | `defi_assets` | CoinGecko, DeFiLlama, Binance, Aave/Pendle subgraphs |
| `crypteolas` | `code_vector_index` | Code embeddings → LanceDB |
| `crypteolas` | `docs_vector_index` | Doc embeddings → LanceDB |
| `crypteolas` | `docs_graph_index` | Doc graph → Memgraph |
| `crypteolas` | `cognee_knowledge_graph` | Static knowledge graph |
| `crypteolas` | `graphiti_temporal_graph` | Temporal knowledge graph (FalkorDB) |
| `crypteolas` | `embedding_assets` | Embedding pipelines (multiple) |
| `crypteolas` | `lakekeeper_examples` | LakeKeeper resource examples |

## Project Structure

```
tuatha/crypteolas/
├── __init__.py                 # package marker
├── definitions.py              # Dagster code-location entry point
├── pyproject.toml              # name = "crypteolas"
├── dg.toml                     # Dagster project config
├── STATUS.md                   # dedup + shim + BAML rename history
│
├── _shims/                     # compatibility shims (sruth.shared.* legacy)
├── agent_os/                   # AgentOS production runtime
├── agents/                     # ADK + Agno + HITL + MCP server
├── api/                        # FastAPI backend (routes/ + services/ + lib/)
├── baml_src/                   # 6 crypto BAML schemas (Crypteolas-prefixed clients)
├── cocoindex_flows/            # unified_embedding, live_docs, protocol_graph
├── config/                     # repos.yaml, protocol configs
├── crates/                     # SpacetimeDB crypteolas-sync
├── dagster_assets/             # github + defi + embedding + lakekeeper assets
├── dagster_assets/components/  # YAML PipelineComponent loader
├── demo/                       # mock data
├── dlt_sources/                # defi/, github/, local/, documentation/
├── dlt_utils/                  # NAMESPACE="crypteolas" destinations
├── docker/                     # Dockerfile.api, Dockerfile.ui
├── graphiti/                   # top-level Graphiti client
├── knowledge_graph/            # cognee/ + graphiti/
├── mcp_server/                 # top-level MCP server (TOOL_REGISTRY)
├── notebooks/                  # 4 marimo (post-dedup)
├── pipelines/                  # older Dagster pipelines
├── storage/                    # LanceCatalog, Garage, DuckLake, Lakekeeper
├── tests/                      # 61 passing + pre-existing failures
├── transformations/            # Ibis-based crypto analytics
├── ui/                         # TanStack Start (deferred to apps/crypteolas_demo)
├── docs/                       # 7 historical design docs
├── wrangler.toml               # Cloudflare Workers (TODO)
└── dagster.yaml.example
```

## Environment Variables

```bash
# Required
GITHUB_TOKEN=your-github-pat
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Optional
ANTHROPIC_API_KEY=your-key
DEFILLAMA_API_KEY=your-key
LANCEDB_PATH=./data/lancedb
REDIS_URL=redis://localhost:6379

# Langfuse (LLM observability)
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=http://localhost:3000
```

## Features

- **GitHub Intelligence**
  - Repository search and analysis
  - Commit history tracking
  - Contributor pattern analysis
  - Development velocity metrics

- **DeFi Analytics**
  - Protocol TVL tracking (DeFiLlama)
  - Yield opportunity comparison
  - Chain distribution analysis
  - Risk metric calculation
  - Funding-rate analysis (Binance, Bybit, OKX)
  - Subgraph data (Aave v3, Pendle)

- **Cross-Domain Correlation**
  - Dev activity ↔ TVL correlation
  - Contributor expertise mapping
  - Protocol health scoring

- **AI Research Agent**
  - Natural language queries
  - A2UI generative components
  - Multi-tool reasoning
  - Citation support
  - Agno-based agent team (research, analysis, pipeline triggering)

- **Knowledge Graph**
  - Cognee static graph (Memgraph)
  - Graphiti temporal graph (FalkorDB)
  - Hybrid vector + graph search

## Data Sources

| Source | Data | Update Frequency |
|--------|------|------------------|
| GitHub API | Repos, commits, contributors, workflows | Hourly |
| DeFiLlama | Protocols, TVL, yields | 15 min |
| CoinGecko | Token prices, market cap | 5 min |
| Binance / Bybit / OKX | Funding rates, open interest | Hourly |
| Aave v3 subgraph | Reserves, user positions | Daily |
| Pendle subgraph | Markets, swaps | Daily |
| Documentation | README, whitepapers, audit reports | Daily |
| Firecrawl | Web scraping | On-demand |

## See Also

- [`../STATUS.md`](../STATUS.md) — the full refactor history (drops, shims, BAML renames, dedup)
- [`../baml_src/clients.baml`](../baml_src/clients.baml) — the crypteolas BAML clients (with `Crypteolas`-prefixed names to avoid colliding with the Celtic MMO clients)
- [`../wrangler.toml`](../wrangler.toml) — the Cloudflare Workers config (with TODO for the missing `workers/index.ts`)
- [`../docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) — 25 KB architecture deep-dive
- [`../docs/SETUP.md`](../docs/SETUP.md) — detailed setup
- [`../docs/DEVELOPMENT.md`](../docs/DEVELOPMENT.md) — development workflow
- [`../../README.md`](../../README.md) — the tuath workspace README
