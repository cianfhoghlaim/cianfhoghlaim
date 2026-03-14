# Tuath Celtic Educational MMO - Quick Start

Celtic language learning through mythology - a gamified educational platform.

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- uv (Python package manager)

## Quick Start

### 1. Start Infrastructure

```bash
cd sruth/tuath
docker-compose up -d
```

This starts:
- FalkorDB (Graphiti knowledge graph)
- LanceDB (Vector store via volume)

### 2. Install Dependencies

```bash
# Python backend
uv sync

# TypeScript frontend
cd ui && pnpm install
```

### 3. Run the API

```bash
uv run uvicorn tuath.api.main:app --reload
```

API available at: http://localhost:8000

### 4. Run the Frontend

```bash
cd ui
pnpm dev
```

Frontend available at: http://localhost:3000

### 5. Run the Demo

```bash
uv run python -m tuath.demo.run_demo
```

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `/docs` | OpenAPI documentation |
| `/health` | Health check |
| `/auth/*` | SIWE authentication |
| `/search/*` | Hybrid search (vector + graph) |
| `/curriculum/*` | Celtic curriculum content |
| `/mythology/*` | Celtic mythology content |
| `/copilotkit/*` | AI agent (A2UI) |
| `/game/*` | Game state management |
| `/payments/*` | x402 micropayments |

## Testing

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=tuath --cov-report=html
```

## Dagster Pipelines

```bash
# Start Dagster UI
dagster dev -m tuath.dagster_assets

# Access at http://localhost:3000
```

### Available Assets

- `celtic_curriculum` - Curriculum from NCCA, WJEC, SQA
- `mythology_content` - Mythological characters, stories, locations
- `curriculum_embeddings` - BGE-M3 vectors for search
- `mythology_embeddings` - BGE-M3 vectors for search

## Project Structure

```
tuath/
├── api/
│   ├── main.py           # FastAPI app
│   └── routes/           # API endpoints
├── services/
│   ├── curriculum.py     # Curriculum service
│   ├── mythology.py      # Mythology service
│   ├── game_state.py     # Game state management
│   ├── embedding.py      # BGE-M3 embeddings
│   └── siwe_auth.py      # SIWE authentication
├── knowledge_graph/
│   ├── hybrid_search.py  # Vector + Graph search
│   └── graphiti/         # Temporal knowledge graph
├── dagster_assets/       # Dagster pipeline definitions
├── agents/               # ADK agents & tools
├── ui/                   # TanStack Start frontend
├── tests/                # pytest tests
└── demo/                 # Demo scripts
```

## Environment Variables

```bash
# Required
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Optional
ANTHROPIC_API_KEY=your-key
LANCEDB_PATH=./data/lancedb
```

## Features

- **SIWE Authentication**: Sign-In With Ethereum
- **x402 Micropayments**: Pay-per-query model
- **Hybrid Search**: Vector similarity + knowledge graph
- **A2UI Protocol**: Generative UI components
- **Celtic Curriculum**: Ireland, Wales, Scotland, Cornwall, Brittany, Isle of Man
- **Mythology Database**: Characters, stories, locations across traditions
