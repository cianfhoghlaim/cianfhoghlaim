# Sruth - Data Flows

Dagster-orchestrated data pipelines for Celtic language education, crypto research, and portfolio management.

## Projects

| Project | Purpose | Status |
|---------|---------|--------|
| **oideachais** | Celtic education curriculum (NCCA, SEC, UK education) | Production |
| **crypteolas** | Crypto/DeFi research (GitHub, protocols, analytics) | Production |
| **tuath** | Celtic educational MMO (mythology, game assets) | Development |
| **aleyum** | Portfolio & dev dashboard (Spotify, GitHub) | Development |

## Oideachais (Education)

Unified Celtic education platform processing Irish, UK, and pan-Celtic curriculum.

```
sruth/oideachais/
├── dlt_sources/          # Ireland, UK, Celtic, geospatial sources
├── cocoindex_flows/      # Embedding pipelines
├── dagster_defs/         # Asset orchestration (6.2K LOC)
├── agents/               # ADK education agents
├── storage/              # DuckDB, LanceDB, Memgraph clients
├── observability/        # Datadog, MLflow, Langfuse, Ragas
├── ui/                   # TanStack Start frontend
└── datasets/             # UK education data (UCAS, DfE, ONS)
```

## Crypteolas (Crypto/DeFi)

GitHub intelligence and DeFi analytics platform.

```
sruth/crypteolas/
├── dlt_sources/          # GitHub, DeFi, documentation sources
├── cocoindex_flows/      # Code + document embeddings
├── dagster_assets/       # Pipeline orchestration
├── agents/               # ADK + HITL RAG agents
├── knowledge_graph/      # Graphiti + Cognee
├── transformations/      # Ibis-based analytics
├── api/                  # FastAPI with SIWE + x402
└── ui/                   # TanStack Start HITL interface
```

## Tuath (Celtic MMO)

Celtic educational MMO with mythology-driven content.

```
sruth/tuath/
├── dlt_sources/          # Mythology, geospatial sources
├── cocoindex_flows/      # Mythology embeddings
├── dagster_assets/       # Content orchestration
├── agents/               # ADK game agents
├── knowledge_graph/      # Graphiti hybrid search
├── game/                 # SpacetimeDB integration
└── ui/                   # TanStack Start game UI
```

## Aleyum (Portfolio)

Personal portfolio and developer dashboard.

```
sruth/aleyum/
├── pipelines/            # Spotify, GitHub data sources
├── cocoindex_flows/      # Artwork embeddings
├── dagster_assets/       # DLT + CocoIndex assets
├── services/             # Vision, image generation
└── portal/               # TanStack Start dashboard
```

## Serial Database Executor

**MANDATORY** for DuckDB operations (prevents segfaults). Each project has its own executor:

```python
# From any project's storage module
from sruth.oideachais.storage import run_serial
from sruth.crypteolas.storage import run_serial
from sruth.tuath.storage import run_serial

result = run_serial(lambda conn: conn.execute("SELECT * FROM table"))
```

## Constraints

See root `CLAUDE.md` for detailed constraints:
- **DuckDB:** Single-threaded only
- **Embeddings:** Batch minimum 100 texts
- **HNSW:** Drop before bulk inserts >50 rows

## Running

```bash
# Start Dagster UI for any project
cd oideachais && dagster dev -m sruth.oideachais.dagster_defs
cd crypteolas && dagster dev -m sruth.crypteolas
cd tuath && dagster dev -m sruth.tuath

# Start UI for any project
cd sruth/crypteolas/ui && pnpm dev
cd sruth/oideachais/ui && pnpm dev
cd aleyum/portal && pnpm dev
```

## Dependencies

| Resource | Used By |
|----------|---------|
| DuckDB | All projects (analytics) |
| LanceDB | All projects (embeddings) |
| Memgraph | oideachais, tuath (graphs) |
| FalkorDB | crypteolas (knowledge graph) |
| Graphiti | crypteolas, tuath (temporal) |
| Cognee | oideachais, crypteolas (memory) |
