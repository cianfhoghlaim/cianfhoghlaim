# Crypteolas - GitHub Intelligence + DeFi Analytics

Cross-domain crypto research platform combining GitHub development activity with DeFi metrics.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- uv (Python package manager)

## Quick Start

### 1. Start Infrastructure

```bash
cd sruth/crypteolas
docker-compose up -d
```

This starts:
- FalkorDB (Knowledge graph)
- LanceDB (Vector store via volume)
- Redis (Caching)

### 2. Install Dependencies

```bash
# Python backend
uv sync

# TypeScript frontend
cd ui && pnpm install
```

### 3. Run the API

```bash
uv run uvicorn crypteolas.api.main:app --port 8001 --reload
```

API available at: http://localhost:8001

### 4. Run the Frontend

```bash
cd ui
pnpm dev
```

Frontend available at: http://localhost:3000

### 5. Run the Demo

```bash
uv run python -m crypteolas.demo.run_demo
```

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI documentation |
| `/health` | Health check |
| `/github/*` | GitHub intelligence |
| `/defi/*` | DeFi protocol analytics |
| `/search/*` | Hybrid search |
| `/copilotkit/*` | AI research agent |
| `/auth/*` | SIWE authentication |
| `/payments/*` | x402 micropayments |

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=crypteolas --cov-report=html
```

## Dagster Pipelines

```bash
# Start Dagster UI
dagster dev -m crypteolas.dagster_assets

# Access at http://localhost:3000
```

### Available Assets

- `github_repositories` - DeFi repository data
- `github_commits` - Commit history analysis
- `github_contributors` - Developer activity
- `defi_protocols` - Protocol TVL from DeFiLlama
- `defi_pools` - Yield opportunity data
- `repository_embeddings` - Search vectors
- `protocol_embeddings` - Search vectors

## Project Structure

```
crypteolas/
├── api/
│   ├── main.py           # FastAPI app
│   └── routes/           # API endpoints
├── services/
│   ├── github.py         # GitHub API service
│   ├── defi.py           # DeFi data service
│   ├── embedding.py      # BGE-M3 embeddings
│   └── siwe_auth.py      # SIWE authentication
├── dlt_sources/
│   ├── github/           # GitHub DLT pipeline
│   ├── defi/             # DeFi DLT pipeline
│   └── documentation/    # Docs pipeline
├── knowledge_graph/
│   ├── hybrid_search.py  # Vector + Graph search
│   └── graphiti/         # Protocol relationships
├── dagster_assets/       # Dagster definitions
├── agents/               # ADK research agents
├── ui/                   # TanStack Start frontend
├── tests/                # pytest tests
└── demo/                 # Demo scripts
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

- **Cross-Domain Correlation**
  - Dev activity ↔ TVL correlation
  - Contributor expertise mapping
  - Protocol health scoring

- **AI Research Agent**
  - Natural language queries
  - A2UI generative components
  - Multi-tool reasoning
  - Citation support

## Data Sources

| Source | Data | Update Frequency |
|--------|------|------------------|
| GitHub API | Repos, commits, contributors | Hourly |
| DeFiLlama | Protocols, TVL, yields | 15 min |
| Documentation | README, docs | Daily |
