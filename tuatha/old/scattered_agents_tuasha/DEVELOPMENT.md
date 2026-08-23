# Tuath Development Guide

Complete development environment setup for the Celtic Educational MMO backend
(plus the consolidated codeolas, crypteolas, and apps/crypteolas demo
sub-packages — see [`README.md`](README.md) for the full structure).

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Python | 3.12+ | `brew install python@3.12` or `mise install python@3.12` |
| uv | 0.5+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker | 24+ | [Docker Desktop](https://docker.com) |
| Node.js | 22+ | `mise install node@22` or `brew install node@22` |
| Bun | 1.3+ | `mise install bun@1.3` or `curl -fsSL https://bun.sh/install \| bash` |

> Note: the `sruth/tuatha/ui/` Celtic-MMO frontend still uses `pnpm` historically,
> but the rest of the monorepo (including the new `apps/crypteolas demo/`
> TypeScript app) has standardised on `bun`. Run `bun install` in
> `apps/crypteolas demo/` and follow the local README for the legacy
> `sruth/tuatha/ui/` workspace.

## Environment Setup

### 1. Clone and Install

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway
uv sync                  # resolves all 8 workspace members (incl. codeolas, crypteolas, crypteolas-demo)
```

To sync just the tuath workspace member:

```bash
cd tuatha && uv sync
```

### 2. Environment Variables

The root `.env` is hydrated by the `mise` directory hook from the Infisical
`dev-baile` vault. Manual override: create `.env.local` in the project root.

```bash
# Required - Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
LANCEDB_PATH=./data/lancedb
DAGSTER_HOME=./.dagster_home

# Required - LLM
ANTHROPIC_API_KEY=your-anthropic-key
# OR use the LiteLLM gateway (recommended)
LITELLM_API_BASE=http://localhost:4000
LITELLM_API_KEY=your-litellm-key

# Optional - Embeddings (defaults to local)
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu  # or cuda, mps

# Optional - Auth
JWT_SECRET=your-jwt-secret
SIWE_DOMAIN=localhost

# Optional - Payments
X402_ENABLED=false
X402_ENDPOINT=http://localhost:4402

# Optional - Dagster observability
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=http://localhost:3000
```

### 3. Start Infrastructure

```bash
cd tuatha
docker compose up -d
```

This starts (per `sruth/tuatha/docker-compose.yaml` + `sruth/tuatha/compose.dev.yaml`):
- **FalkorDB** (port 7687) - Graphiti knowledge graph
- **LanceDB** - Vector store (file-based, no container)
- **Redis** (port 6379) - Session cache

Verify services:
```bash
docker compose ps
# All services should show "Up"
```

For the crypteolas sub-package (9-service dev stack: api, ui,
dagster-webserver, dagster-daemon, memgraph, memgraph-lab, dragonfly,
langfuse, lance-viewer):

```bash
cd sruth/tuatha/crypteolas
docker compose -f compose.yaml -f compose.dev.yaml up -d
```

## Running the APIs

### Celtic MMO API (port 8000)

```bash
cd tuatha
uv run uvicorn api.main:app --reload --port 8000
```

API available at: http://localhost:8000

### Crypteolas FastAPI backend (port 8001)

```bash
cd tuatha
uv run uvicorn crypteolas.api.main:app --port 8001
```

### Crypteolas AgentOS runtime (port 7771)

```bash
cd tuatha
uv run uvicorn crypteolas.agent_os.main:app --port 7771
```

### Production Mode (Celtic MMO)

```bash
cd tuatha
uv run uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints (Celtic MMO)

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI/Swagger UI |
| `/redoc` | ReDoc documentation |
| `/health` | Health check |
| `/auth/*` | SIWE authentication |
| `/curriculum/*` | Celtic curriculum content |
| `/mythology/*` | Celtic mythology |
| `/geospatial/*` | Celtic region GeoJSON |
| `/game/*` | Game state management |
| `/search/*` | Hybrid vector+graph search |
| `/copilotkit/*` | AG-UI agent streaming |
| `/payments/*` | x402 micropayments |

## Running Dagster Pipelines

### Start the unified Dagster UI (loads 3 code-locations)

```bash
cd tuatha
uv run dagster dev
```

Dagster UI at: http://localhost:3000 with three code-locations:
`tuath`, `crypteolas`, `crypteolas demo`.

### Materialize Assets (Celtic MMO)

```bash
# Single asset
cd tuatha
uv run dagster asset materialize -m dagster_assets.definitions --select celtic_curriculum

# All curriculum assets
uv run dagster asset materialize -m dagster_assets.definitions --select 'celtic_curriculum* mythology_content*'

# Full pipeline
uv run dagster job execute -m dagster_assets.definitions -j tuath_full_pipeline
```

Or via mise:

```bash
mise dagster:tuath
```

### Materialize Assets (Crypteolas)

```bash
cd tuatha
uv run dagster asset materialize -m crypteolas.definitions --select github_api_assets
uv run dagster job execute -m crypteolas.definitions -j ingestion_jobs
```

Or via mise:

```bash
mise dagster:crypteolas
```

### Materialize Assets (Crypteolas Demo)

```bash
cd sruth/tuatha/apps/crypteolas_demo
uv run dagster asset materialize -m definitions --select fibo_json_configs
```

Or via mise:

```bash
mise dagster:crypteolas_demo
```

### Available Assets

| Code-location | Asset | Description | Source |
|:--|:--|:--|:--|
| `tuath` | `celtic_curriculum` | NCCA/SQA/WJEC curriculum | DLT sources |
| `tuath` | `mythology_content` | Celtic myths and characters | DLT sources |
| `tuath` | `curriculum_embeddings` | BGE-M3 vectors | CocoIndex |
| `tuath` | `mythology_embeddings` | BGE-M3 vectors | CocoIndex |
| `tuath` | `knowledge_graph` | Graphiti temporal graph | FalkorDB |
| `tuath` | `exam_analysis` | Exam paper analysis | Dagster |
| `tuath` | `celtic_characters` | Celtic character knowledge | Dagster |
| `crypteolas` | `github_api_assets` | GitHub issues, PRs, commits, workflows | DLT |
| `crypteolas` | `defi_assets` | CoinGecko, DeFiLlama, Binance, subgraphs | DLT |
| `crypteolas` | `code_vector_index` | Code embeddings → LanceDB | CocoIndex |
| `crypteolas` | `docs_vector_index` | Doc embeddings → LanceDB | CocoIndex |
| `crypteolas` | `docs_graph_index` | Doc graph → Memgraph | Cognee |
| `crypteolas` | `cognee_knowledge_graph` | Static knowledge graph | Cognee |
| `crypteolas` | `graphiti_temporal_graph` | Temporal knowledge graph | Graphiti |
| `crypteolas demo` | `fibo_json_configs` | FIBO JSON config generation | FIBO + BAML |
| `crypteolas demo` | `generated_images` | FIBO image rendering | Bria FIBO MLX |
| `crypteolas demo` | `curriculum_metadata` | NCCA/SQA/WJEC metadata | DLT |
| `crypteolas demo` | `specification_pdfs` | Specification PDFs | DLT |
| `crypteolas demo` | `indexed_pages` | ColPali page indexing | ColPali |
| `crypteolas demo` | `extracted_concepts` | Qwen3-VL concept extraction | Qwen3-VL |
| `crypteolas demo` | `visualizable_concepts` | Filter for visual concepts | Dagster |
| `crypteolas demo` | `user_learning_activity` | Web3/XP event stream (mock) | Mock |
| `crypteolas demo` | `computed_xp_rewards` | XP reward computation | Mock |
| `crypteolas demo` | `pending_token_mints` | Token mint queue | Mock |
| `crypteolas demo` | `nft_evolution_queue` | NFT evolution queue | Mock |

## Testing

### Run All Tests

```bash
cd tuatha
uv run pytest tests/ -v
```

Or per-sub-package:

```bash
cd tuatha
uv run pytest sruth/codeolas/tests/ -v            # códeolas (35 unit + 31 integration)
uv run pytest sruth/crypteolas/tests/ -v         # crypteolas (61 passing + pre-existing failures)
```

Per-package mise aliases:

```bash
mise test:codeolas
mise test:crypteolas
mise test:crypteolas_demo
```

### Run with Coverage

```bash
cd tuatha
uv run pytest tests/ --cov=tuath --cov-report=html
open htmlcov/index.html
```

### Test Categories

```bash
# Unit tests only (Celtic MMO)
cd tuatha
uv run pytest tests/test_api_endpoints.py -v

# Integration tests (requires Docker)
uv run pytest tests/test_hybrid_search.py tests/test_graphiti_integration.py -v

# Run specific test
uv run pytest tests/test_api_endpoints.py::test_health_check -v

# códeolas unit tests only (skip integration)
uv run pytest sruth/codeolas/tests/ -v -m "not integration and not slow"
```

### Test Fixtures

The test suite uses `conftest.py` with fixtures for:
- FastAPI test client
- Mock LanceDB connection
- Mock FalkorDB connection
- Sample curriculum data

The `sruth/codeolas/tests/conftest.py` honours the `CODEOLAS_REPO_PATH` env var
(falls back to `os.getcwd()`) so the test runs on any machine layout.

## Running the Demo

Interactive demo showcasing all features:

```bash
cd tuatha
uv run python -m demo.run_demo
```

Features demonstrated:
1. Celtic curriculum search
2. Mythology knowledge queries
3. Agent multi-turn conversation
4. Hybrid search (vector + graph)
5. Geospatial region queries

## Frontend Development

### Celtic MMO UI (Vinxi + Babylon.js)

```bash
cd sruth/tuatha/ui
bun install
bun run dev
# → http://localhost:3000 (proxies to API at :8000)
```

### Crypteolas Demo (TanStack Start stub)

```bash
cd sruth/tuatha/apps/crypteolas_demo
bun install
bun run typecheck
bun run dev
# → http://localhost:3000 (proxies /api → localhost:8001)
```

### Crypteolas Demo Gradio UI (FIBO image gen)

```bash
cd sruth/tuatha/apps/crypteolas_demo
uv run python -m ui.app
```

## Code Analysis (codeolas)

### CLI

```bash
cd tuatha
uv run codeolas --help
uv run codeolas index --repo /path/to/repo
uv run codeolas search "auth" --limit 10
uv run codeolas research "How does the auth system work?"
uv run codeolas arch --output ARCHITECTURE.md
```

### MCP Server

```bash
cd tuatha
uv run codeolas-mcp    # stdio MCP server
```

### Crypteolas MCP Server

```bash
cd tuatha
uv run python -m crypteolas.mcp_server    # stdio MCP server
```

## IDE Configuration

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Even Better TOML (tamasfe.even-better-toml)
- BAML (boundary.baml-extension)

`.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "ruff.lint.args": ["--config=pyproject.toml"]
}
```

### Claude Code

The project includes `.claude/settings.local.json` for Claude Code integration:
- Task tool enabled for multi-step operations
- Custom skills for Celtic language patterns
- MCP servers configured for search
- The `codeolas-mcp` server is the recommended way to give Claude Code
  semantic search over the workspace.

## Troubleshooting

### FalkorDB Connection Error

```bash
# Check if container is running
docker ps | grep falkordb

# View logs
docker logs tuath-falkordb-1

# Restart
cd tuatha && docker compose restart falkordb
```

### LanceDB Lock Error

LanceDB requires single-threaded access. If you see lock errors:

```bash
# Remove stale lock files
rm -f ./data/lancedb/*.lock

# Or use environment variable
export LANCEDB_SERIALIZED=true
```

### Embedding Model OOM

For systems with limited RAM:

```bash
# Use smaller model
export EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Or reduce batch size
export EMBEDDING_BATCH_SIZE=32
```

### Dagster Asset Failure

```bash
# Check logs
cd tuatha
uv run dagster asset logs -m dagster_assets.definitions --select celtic_curriculum

# Reset asset state
uv run dagster asset wipe -m dagster_assets.definitions --select celtic_curriculum
```

### Dagster "Cannot annotate `context` parameter with type AssetExecutionContext"

This is a Dagster 1.12.6 vs prior-version compatibility issue in the crypteolas
assets. See `sruth/tuatha/crypteolas/STATUS.md` for the full list of pre-existing
issues; the structural refactor is complete but the asset-level API mismatch
needs separate fix.

### Crypteolas Demo TanStack app stubs

If `bun run dev` fails because of a missing dependency or import, check
`sruth/tuatha/apps/crypteolas_demo/STATUS.md` §"What was stubbed" for the list of
12 `src/lib/*` modules and 3 `models/*` modules. The shell is buildable but
the implementations are TODO.

## Project Structure

The full post-consolidation structure (see `README.md` for the narrative):

```
tuatha/
├── pyproject.toml                 # workspace member "tuath"
├── dg.toml                        # Dagster project (Celtic MMO code-location)
├── README.md                      # the file you are NOT reading right now
├── DEVELOPMENT.md                 # this file
├── anam.md                        # the Anam lore (Irish: "soul")
├── gaeilge.md                     # the Irish-language content (47 KB)
│
├── agents/                        # Celtic MMO: Google ADK + Agno + MCP
│   ├── adk/                       # root_agent, celtic_tutor, mythology_narrator,
│   │                              #   quest_guide, research_assistant
│   ├── callbacks/, mcp_server/, tools/
│   ├── config.py, orchestrator.py
├── api/                           # Celtic MMO: FastAPI (no __init__.py — namespace pkg)
│   ├── main.py, ag_ui_protocol.py
│   ├── routes/                    # auth, curriculum, mythology, geospatial,
│   │                              #   game_state, search, copilotkit, payments
│   └── services/
├── api-rs/                        # Rust API crate (axum + x402-rs)
├── asset_generation/              # Celtic MMO: LiteLLM image gen
├── baml_src/                      # Celtic MMO BAML (5 schemas + tuatha_clients.baml)
├── cocoindex_flows/               # Celtic MMO: mythology_embedding + celtic_multilingual
├── crates/                        # Rust workspace: stdb-modules, wgpu, solana
│   ├── services/nft-relayer/
│   ├── solana/programs/
│   ├── stdb-modules/{shared-types, tuath-game}/
│   └── wgpu/{celtic-shaders, particle-system}/
├── dagster_assets/                # Celtic MMO: definitions + assets + schedules
├── demo/                          # run_demo.py (mock data)
├── dlt_sources/                   # Celtic MMO: celtic_education, geospatial
├── dlt_utils/                     # destinations.py (NAMESPACE="tuath")
├── docker/                        # Dockerfile.api, Dockerfile.ui, Dockerfile.game
├── fibo_generation/               # FIBO image gen (SyllabusPage, FiboResource, etc.)
├── game/                          # Babylon.js game client (client/ + godot-client/)
├── knowledge_graph/               # graphiti/ + hybrid_search.py
├── notebooks/                     # marimo: speedrun/
├── storage/                       # serial_executor.py (deprecation shim)
├── tests/                         # conftest + 4 pytest files
├── ui/                            # TypeScript Vinxi + Babylon.js (bun workspace)
│
├── sruth/codeolas/                      # === CONSOLIDATED from códeolas_codebase_indexing/ ===
│   ├── STATUS.md                  # dedup + shim history
│   ├── __init__.py                # lazy public API
│   ├── cli.py, pyproject.toml
│   ├── chunking/, core/, storage/, search/, graph/, generators/
│   ├── mcp_server/                # stdio MCP server (typed Tool registry)
│   ├── dagster_assets/            # códeolas code-location
│   ├── cocoindex_flows/
│   ├── demo/
│   ├── tests/                     # 35 unit + 31 integration tests
│   ├── compose.yaml, compose.dev.yaml
│   └── .forgejo/workflows/        # CI/release (see STATUS.md re: nested workflow)
│
├── sruth/crypteolas/                    # === CONSOLIDATED from crypteolas_formative_assessment/ ===
│   ├── STATUS.md                  # drops, shims, BAML renames
│   ├── dg.toml                    # crypteolas Dagster project
│   ├── definitions.py             # Dagster code-location
│   ├── pyproject.toml             # name = "crypteolas"
│   ├── _shims/                    # compatibility shims (sruth.shared.* legacy)
│   ├── agent_os/                  # AgentOS production runtime
│   ├── agents/                    # ADK + Agno + HITL + MCP server
│   ├── api/                       # FastAPI backend (port 8001)
│   ├── baml_src/                  # 6 crypto BAML schemas (Crypteolas-prefixed clients)
│   ├── cocoindex_flows/           # unified_embedding, live_docs, protocol_graph
│   ├── config/, crates/           # crates/ = SpacetimeDB crypteolas-sync
│   ├── dagster_assets/            # github + defi + embedding + lakekeeper
│   ├── dagster_assets/components/ # YAML PipelineComponent loader
│   ├── demo/                      # mock data
│   ├── dlt_sources/               # defi/, github/, local/, documentation/
│   ├── dlt_utils/                 # NAMESPACE="crypteolas" destinations
│   ├── docker/                    # Dockerfile.api, Dockerfile.ui
│   ├── graphiti/                  # top-level Graphiti client
│   ├── knowledge_graph/           # cognee/ + graphiti/
│   ├── mcp_server/                # top-level MCP server
│   ├── notebooks/                 # 4 marimo (post-dedup)
│   ├── pipelines/                 # older Dagster pipelines (defs, dagster, etc.)
│   ├── storage/                   # LanceCatalog, Garage, DuckLake, Lakekeeper
│   ├── tests/                     # 61 passing + pre-existing failures
│   ├── transformations/           # Ibis-based crypto analytics
│   ├── ui/                        # TanStack Start (deferred to apps/crypteolas_demo)
│   ├── docs/                      # 7 historical design docs
│   ├── wrangler.toml              # Cloudflare Workers (TODO)
│   └── dagster.yaml.example
│
└── apps/                          # === CONSOLIDATED from sruth/tuatha/tuatha_1/ ===
    └── crypteolas_demo/           # flattened from tuatha_1/
        ├── STATUS.md              # TS app stub inventory
        ├── dg.toml                # crypteolas demo Dagster project
        ├── pyproject.toml         # name = "crypteolas-demo", root_module = "crypteolas_demo"
        ├── __init__.py            # lazy re-exports (CryptoResearchAgent, etc.)
        ├── crypto_agents.py, mcp_tools.py, definitions.py
        ├── anam-contracts/        # Foundry Solidity: AnamCaraDAO, CuchulainnNFT, TuathToken
        ├── db/                    # LanceDB + dataclass schemas (EduVision)
        ├── defs/                  # FIBO/EduVision Dagster code-location
        ├── foinse/                # YAML configs + LLM client (Irish: "source")
        ├── pipelines/             # Crypteolas Dagster code-location
        ├── scéimre/               # BAML schemas (Irish: "scheme")
        ├── src/                   # TanStack Start TypeScript (buildable shell)
        ├── ui/                    # Python Gradio app
        ├── models/                # ColPali, FIBO-MLX, Qwen3-VL stubs
        ├── anam-contracts/, db/, foinse/, scéimre/, ui/, models/
        ├── Dockerfile, docker-compose.yaml, nginx.conf
        ├── package.json, tsconfig.json, vite.config.ts, index.html
        ├── README.md, ANALYSIS.md
        └── .env.example
```

## Related Documentation

- [README.md](README.md) — the sub-package-level README (mirrors the root README)
- [sruth/codeolas/STATUS.md](sruth/codeolas/STATUS.md) — códeolas dedup + shim history
- [sruth/crypteolas/STATUS.md](sruth/crypteolas/STATUS.md) — crypteolas drops, shims, BAML renames
- [apps/crypteolas demo/STATUS.md](apps/crypteolas_demo/STATUS.md) — TS app stub inventory
- [`AGENTS.md`](../AGENTS.md) — agent protocols and guard rails
- [`openspec/changes/consolidate-external-libs-into-sruth/tuatha/`](../openspec/changes/consolidate-external-libs-into-sruth/tuatha/) — the change proposal
- [dg.toml](dg.toml) — Dagster project config (Celtic MMO code-location)
- [sruth/crypteolas/dg.toml](sruth/crypteolas/dg.toml) — crypteolas Dagster project config
- [apps/crypteolas demo/dg.toml](apps/crypteolas_demo/dg.toml) — demo Dagster project config
