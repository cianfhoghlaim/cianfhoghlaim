# Oideachas Demo

Standalone demonstration of the Celtic Education Curriculum Processing platform.

## Quick Start

```bash
cd sruth/oideachais
python demo/run_demo.py
```

## What This Demo Demonstrates

### 1. DLT Data Sources
- **Ireland**: NCCA curriculum, SEC exams, curriculumonline.ie
- **UK**: GOV.UK, Education Scotland, Welsh Government
- **Celtic**: Dúchas.ie folklore, Tearma.ie terminology
- **Geospatial**: School locations, regional boundaries

### 2. Document Processing
- PDF extraction from curriculum documents
- HTML cleaning and parsing
- Semantic chunking by learning outcomes
- BGE-M3 batch embeddings (minimum 100 chunks)

### 3. Semantic Search
- Hybrid vector + keyword search
- Multilingual support (Irish, Welsh, Scottish Gaelic, Breton)
- Reranking with Jina API (15-20% precision boost)

### 4. BAML Extraction
- Type-safe LLM extraction for curriculum entities
- Structured learning outcomes
- Subject and strand classification

### 5. Knowledge Graph
- Geospatial queries (schools by region)
- Curriculum relationships (subjects, strands, outcomes)
- Neo4j/Cypher support

### 6. Dagster Assets
- 37+ assets across 4 domains
- Scheduled data refreshes
- Asset dependency graphs

### 7. Celtic Languages
- Irish (Gaeilge) - 1.7M speakers
- Welsh (Cymraeg) - 880k speakers
- Scottish Gaelic (Gàidhlig) - 60k speakers
- Breton (Brezhoneg) - 200k speakers

### 8. Observability
- Datadog APM (distributed tracing)
- Datadog LLMObs (LLM monitoring)
- MLflow (experiment tracking)
- Langfuse (cost tracking)
- Ragas (RAG evaluation)
- Kafka (event streaming)

## Requirements

This demo uses mock data and requires minimal dependencies:

```bash
pip install httpx
```

For the full platform, see the main [README](../README.md).

## Demo Structure

```
demo/
├── __init__.py
├── run_demo.py       # Main demo script
└── README.md         # This file
```

## Running the Demo

The demo runs entirely offline with mock data. No API keys or external services required.

```bash
# From the sruth/oideachais directory
python demo/run_demo.py
```

The demo will showcase:
- All 10 major features
- Mock data for curriculum, geospatial, and Celtic language content
- Code examples for DLT sources, Dagster assets, and API endpoints

## Full Platform Setup

To run the complete platform with real data:

```bash
# Install dependencies
uv sync

# Configure environment
cp .env.local.example .env.local
# Edit .env.local with your credentials

# Initialize storage
python -m storage.init_schemas
python -m storage.init_lancedb

# Start Dagster UI (asset orchestration)
dagster dev -m dagster_defs.definitions

# Start FastAPI (in another terminal)
uvicorn api.main:app --reload

# Run data pipelines
python -m dlt_sources.ireland.ncca
python -m dlt_sources.uk.gov_uk
python -m dlt_sources.celtic.duchas

# Create embeddings
python -m cocoindex_flows.curriculum_embedding

# Query with agents
python -m agents.adk.root_agent
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Celtic Education Platform                  │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ DLT Sources │──────│ Dagster     │──────│ ADK Agents  │
│             │      │ Assets      │      │             │
│ • Ireland   │      │ • 37 assets │      │ • Root      │
│ • UK        │      │ • 4 domains │      │ • Domain    │
│ • Celtic    │      │ • Schedules │      │ • Routing   │
└─────────────┘      └─────────────┘      └─────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Storage     │      │ CocoIndex   │      │ Observabil- │
│             │      │ Flows       │      │ ity         │
│ • DuckDB    │◄─────│ • Embed     │─────►│ • Datadog   │
│ • LanceDB   │      │ • Translate │      │ • MLflow    │
│ • Memgraph  │      │ • Index     │      │ • Langfuse  │
└─────────────┘      └─────────────┘      └─────────────┘
```

## Key Features

### Critical Constraints

**DuckDB Single-Threaded Access**
- DuckDB MUST use single-threaded access
- Use `SerialDatabaseExecutor` wrapper
- Prevents segfaults and corruption

**Embedding Batch Minimum**
- Minimum 100 embeddings per API call
- Unbatched: ~100s for 1000 texts
- Batched: ~1s for 1000 texts (100x faster)

**HNSW Index Management**
- Drop indexes before bulk inserts >50 rows
- Recreate after insert complete
- 20x speedup for bulk operations

## Data Sources

### Ireland Education
- **NCCA**: ncca.ie (curriculum specifications)
- **SEC**: examinations.ie (exam papers, marking schemes)
- **Curriculumonline**: curriculumonline.ie (teacher resources)

### UK Education
- **GOV.UK**: national-curriculum.service.gov.uk
- **Education Scotland**: educationscotland.gov.uk
- **Welsh Government**: hwb.gov.wales
- **Northern Ireland**: ccea.org.uk

### Celtic Languages
- **Dúchas.ie**: duchas.ie (Irish folklore collection)
- **Tearma.ie**: tearma.ie (Irish terminology)
- **Gaelic Portraits**: gaelicportraits.org
- **Welsh Books Council**: llyfrgell.cymru

## API Endpoints

When running the full platform:

- `GET /health` - Health check
- `GET /curriculum/search` - Semantic search
- `GET /curriculum/:nation/:subject` - Get curriculum by subject
- `POST /curriculum/embed` - Embed document
- `GET /geospatial/schools` - Query schools by location
- `GET /celtic/languages` - List Celtic languages
- `POST /celtic/translate` - Translate text
- `GET /knowledge/graph/query` - Cypher graph query

## Observability

The full platform integrates:

- **Datadog APM**: Distributed tracing for API endpoints
- **Datadog LLMObs**: LLM token usage and costs
- **MLflow**: Experiment tracking for embeddings
- **Langfuse**: Per-query cost tracking
- **Ragas**: RAG quality evaluation
- **Kafka**: Real-time event streaming (25+ topics)

## Support

For issues or questions:
- Main README: [sruth/oideachais/README.md](../README.md)
- Project docs: [CLAUDE.md](../../../CLAUDE.md)
- Celtic language AI: [.claude/skills/celtic-language-ai](../../../.claude/skills/celtic-language-ai)
