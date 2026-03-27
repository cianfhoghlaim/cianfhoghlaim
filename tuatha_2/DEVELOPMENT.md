# Tuath Development Guide

Complete development environment setup for the Celtic Educational MMO backend.

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
# Required - Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
LANCEDB_PATH=./data/lancedb

# Required - LLM
ANTHROPIC_API_KEY=your-anthropic-key
# OR use LiteLLM gateway
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
```

### 3. Start Infrastructure

```bash
cd sruth/tuath
docker-compose up -d
```

This starts:
- **FalkorDB** (port 7687) - Graphiti knowledge graph
- **LanceDB** - Vector store (file-based, no container)
- **Redis** (port 6379) - Session cache

Verify services:
```bash
docker-compose ps
# All services should show "Up"
```

## Running the API

### Development Mode (with hot reload)

```bash
cd sruth/tuath
uv run uvicorn tuath.api.main:app --reload --port 8000
```

API available at: http://localhost:8000

### Production Mode

```bash
uv run uvicorn tuath.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### API Endpoints

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

### Start Dagster UI

```bash
cd sruth/tuath
dagster dev -m tuath.dagster_assets
```

Dagster UI at: http://localhost:3000

### Materialize Assets

```bash
# Single asset
dagster asset materialize -m tuath.dagster_assets --select celtic_curriculum

# All curriculum assets
dagster asset materialize -m tuath.dagster_assets --select 'celtic_curriculum* mythology_content*'

# Full pipeline
dagster job execute -m tuath.dagster_assets -j tuath_full_pipeline
```

### Available Assets

| Asset | Description | Source |
|-------|-------------|--------|
| `celtic_curriculum` | NCCA/SQA/WJEC curriculum | DLT sources |
| `mythology_content` | Celtic myths and characters | DLT sources |
| `curriculum_embeddings` | BGE-M3 vectors | CocoIndex |
| `mythology_embeddings` | BGE-M3 vectors | CocoIndex |
| `knowledge_graph` | Graphiti temporal graph | FalkorDB |

## Testing

### Run All Tests

```bash
cd sruth/tuath
uv run pytest tests/ -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=tuath --cov-report=html
open htmlcov/index.html
```

### Test Categories

```bash
# Unit tests only
uv run pytest tests/test_api_endpoints.py -v

# Integration tests (requires Docker)
uv run pytest tests/test_hybrid_search.py tests/test_graphiti_integration.py -v

# Run specific test
uv run pytest tests/test_api_endpoints.py::test_health_check -v
```

### Test Fixtures

The test suite uses `conftest.py` with fixtures for:
- FastAPI test client
- Mock LanceDB connection
- Mock FalkorDB connection
- Sample curriculum data

## Running the Demo

Interactive demo showcasing all features:

```bash
cd sruth/tuath
uv run python -m tuath.demo.run_demo
```

Features demonstrated:
1. Celtic curriculum search
2. Mythology knowledge queries
3. Agent multi-turn conversation
4. Hybrid search (vector + graph)
5. Geospatial region queries

## Frontend Development

### Install Frontend Dependencies

```bash
cd sruth/tuath/ui
pnpm install
```

### Run Frontend Dev Server

```bash
cd sruth/tuath/ui
pnpm dev
```

Frontend at: http://localhost:3000 (proxies to API at :8000)

## IDE Configuration

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Pylance (ms-python.vscode-pylance)
- Ruff (charliermarsh.ruff)
- Even Better TOML (tamasfe.even-better-toml)

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

## Troubleshooting

### FalkorDB Connection Error

```bash
# Check if container is running
docker ps | grep falkordb

# View logs
docker logs tuath-falkordb-1

# Restart
docker-compose restart falkordb
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
dagster asset logs -m tuath.dagster_assets --select celtic_curriculum

# Reset asset state
dagster asset wipe -m tuath.dagster_assets --select celtic_curriculum
```

## Project Structure

```
tuath/
├── api/
│   ├── main.py              # FastAPI app entrypoint
│   ├── routes/              # API route handlers
│   │   ├── auth.py          # SIWE authentication
│   │   ├── curriculum.py    # Curriculum endpoints
│   │   ├── mythology.py     # Mythology endpoints
│   │   ├── geospatial.py    # GeoJSON endpoints
│   │   ├── game_state.py    # Game state management
│   │   ├── search.py        # Hybrid search
│   │   ├── copilotkit.py    # AG-UI streaming
│   │   └── payments.py      # x402 micropayments
│   └── services/            # Business logic
├── agents/
│   ├── adk/                 # Google ADK agents
│   │   ├── root_agent.py    # Orchestrator
│   │   ├── celtic_tutor.py  # Language learning
│   │   ├── mythology_narrator.py
│   │   ├── quest_guide.py
│   │   └── research_assistant.py
│   └── tools/               # Agent tools
├── dlt_sources/             # DLT data ingestion
│   ├── celtic_education/    # NCCA, SQA, WJEC, Dúchas
│   ├── geospatial/          # Gaeltacht, Welsh areas
│   └── crypto/              # CoinGecko, DeFiLlama
├── cocoindex_flows/         # CocoIndex embeddings
│   ├── curriculum_embedding.py
│   ├── mythology_embedding.py
│   └── transforms/
├── knowledge_graph/         # Graphiti integration
│   ├── hybrid_search.py     # Vector + graph search
│   └── graphiti/
├── dagster_assets/          # Dagster orchestration
│   ├── definitions.py       # Repository definition
│   ├── curriculum_assets.py
│   ├── mythology_assets.py
│   ├── embedding_assets.py
│   └── schedules.py
├── asset_generation/        # LiteLLM image generation
│   ├── models.py
│   ├── prompts.py
│   └── service.py
├── tests/                   # pytest test suite
├── demo/                    # Interactive demos
└── docker-compose.yml       # Infrastructure
```

## Related Documentation

- [API Reference](docs/API.md)
- [Agent Architecture](docs/AGENTS.md)
- [Pipeline Guide](docs/PIPELINES.md)
- [QUICKSTART.md](QUICKSTART.md)
