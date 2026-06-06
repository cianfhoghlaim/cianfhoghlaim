# oideachais - Unified Celtic Education Platform

A unified data platform for Celtic language education, covering 6 nations and 6 Celtic languages with comprehensive observability and AI agent capabilities.

## Overview

This project merges three sruth pipelines into a single, observable platform:
- **oideachas**: Irish education curriculum (NCCA, SEC, curriculumonline.ie)
- **teanga**: Celtic language processing (Irish, Welsh, Scottish Gaelic, Manx, Cornish, Breton)
- **oideachas_oileáin**: British Isles education statistics (England, Scotland, Wales, NI)

## Features

| Category | Features |
|----------|----------|
| **Data Assets** | 37+ Dagster assets across 4 domains (Ireland, UK, Celtic, Geospatial) |
| **Data Sources** | 30+ DLT sources for curriculum, statistics, and language data |
| **Geospatial** | DuckDB Spatial with 60k+ statistical area boundaries |
| **Vector Search** | LanceDB semantic search across curriculum content |
| **LLM Extraction** | BAML schemas for type-safe structured outputs |
| **AI Agents** | ADK-based multi-agent system with domain routing |
| **Observability** | Full Datadog, MLflow, Langfuse, Ragas, Kafka integration |

## Architecture

```
                    ┌─────────────────────────────────────────────────────────────┐
                    │                    Celtic Education Platform                  │
                    └─────────────────────────────────────────────────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌─────────────────┐              ┌─────────────────────┐              ┌─────────────────┐
│   DLT Sources   │              │   Dagster Assets    │              │   ADK Agents    │
│                 │              │                     │              │                 │
│ • Ireland (8)   │──────────────│ • ireland_education │──────────────│ • RootAgent     │
│ • UK (12)       │              │ • uk_education      │              │ • Curriculum    │
│ • Celtic (6)    │              │ • celtic_language   │              │ • Geospatial    │
│ • Geospatial(4) │              │ • geospatial        │              │ • Translation   │
└─────────────────┘              │ • embeddings        │              │ • Corpus        │
                                 │ • evaluation        │              │ • Statistics    │
                                 └─────────────────────┘              └─────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         │                                    │                                    │
         ▼                                    ▼                                    ▼
┌─────────────────┐              ┌─────────────────────┐              ┌─────────────────┐
│    Storage      │              │   CocoIndex Flows   │              │  Observability  │
│                 │              │                     │              │                 │
│ • DuckDB        │◄─────────────│ • curriculum_embed  │─────────────►│ • Datadog APM   │
│ • LanceDB       │              │ • translation       │              │ • Datadog LLMObs│
│ • Memgraph      │              │ • geospatial_index  │              │ • MLflow        │
└─────────────────┘              └─────────────────────┘              │ • Langfuse      │
                                                                      │ • Ragas         │
                                                                      │ • Kafka         │
                                                                      └─────────────────┘
```

## Directory Structure

```
sruth/oideachais/
├── api/                  # FastAPI application with Datadog APM
│   ├── main.py           # App with observability lifespan
│   └── routes/           # API endpoints
├── agents/               # ADK-based AI agents
│   ├── adk/
│   │   ├── root_agent.py # Orchestrator with query routing
│   │   ├── curriculum_agent.py
│   │   ├── geospatial_agent.py
│   │   ├── translation_agent.py
│   │   ├── corpus_agent.py
│   │   └── statistics_agent.py
│   └── tools/            # Agent tools for search/retrieval
├── cocoindex_flows/      # Vector embedding pipelines
│   ├── curriculum_embedding.py  # Batch embedding (100+ min)
│   ├── curriculum_translation.py
│   └── geospatial_indexing.py
├── dagster_defs/         # Dagster asset orchestration
│   ├── assets/
│   │   ├── ie_education_assets.py
│   │   ├── uk_education_assets.py
│   │   ├── celtic_language_assets.py
│   │   ├── geospatial_assets.py
│   │   ├── embedding_assets.py
│   │   └── search_assets.py
│   ├── resources.py
│   └── schedules.py
├── dlt_sources/          # Data ingestion sources
│   ├── ireland/          # NCCA, SEC, curriculumonline
│   ├── uk/               # England, Scotland, Wales, NI
│   ├── celtic/           # Language resources (Dúchas, Tearma)
│   └── geospatial/       # Boundaries and locations
├── kafka/                # Event streaming
│   ├── producer.py       # Confluent Kafka producer
│   ├── consumer.py       # Consumer with observability
│   ├── topics.py         # 25+ topic configurations
│   └── schema_registry.py # Avro schemas
├── observability/        # Unified observability stack
│   ├── __init__.py       # All exports
│   ├── agent_tracing.py  # Datadog LLMObs decorators
│   ├── mlflow_config.py  # MLflow experiments
│   ├── langfuse_config.py # LLM cost tracking
│   ├── ragas_evaluator.py # RAG quality evaluation
│   └── fastapi_middleware.py # Datadog APM
├── storage/              # Database configurations
│   ├── duckdb.py         # Single-threaded executor
│   └── lancedb.py        # Vector store
└── alignment/            # Bilingual en/ga alignment
```

## Quick Start

### 1. Install Dependencies

```bash
# Clone and navigate
cd sruth/oideachais

# Install with uv
uv sync

# Install with observability extras
uv sync --extra observability

# Install with Kafka
uv sync --extra kafka
```

### 2. Configure Environment

```bash
# Copy example environment
cp .env.local.example .env.local

# Edit with your credentials
# Required: DATADOG, MLFLOW, LANGFUSE, KAFKA configs
```

### 3. Initialize Storage

```bash
# Create database schemas
python -m storage.init_schemas

# Initialize LanceDB tables
python -m storage.init_lancedb
```

### 4. Start Services

```bash
# Start Dagster UI (asset orchestration)
dagster dev -m dagster_defs.definitions

# Start FastAPI (in another terminal)
uvicorn api.main:app --reload

# Start Kafka consumers (optional)
python -m kafka.consumer
```

## Observability Stack

### Datadog APM & LLMObs

Full distributed tracing and LLM observability:

```python
from observability import (
    setup_datadog_apm,
    trace_adk_agent,
    GeminiLLMSpan,
    annotate_span,
)

# Instrument FastAPI
app = FastAPI()
setup_datadog_apm(app)

# Trace agents
@trace_adk_agent("curriculum_search")
async def search_curriculum(query: str):
    with GeminiLLMSpan("gemini-2.0-flash", query) as span:
        response = await llm.generate(query)
        span.set_response(response, input_tokens=100, output_tokens=200)
        return response

# Annotate spans with metadata
annotate_span(
    input_data=query,
    output_data=response,
    metadata={"domain": "curriculum"},
    metrics={"latency_ms": 150.0}
)
```

### MLflow Experiment Tracking

Track model experiments and metrics:

```python
from observability import mlflow_run, log_agent_metrics

with mlflow_run("curriculum_embedding", tags={"nation": "ireland"}):
    # Run embedding pipeline
    result = flow.run()

    # Log metrics
    log_agent_metrics(
        agent_name="embedding",
        query="ireland_curriculum",
        response_length=result["chunks"],
        latency_ms=1500,
        token_count=50000,
    )
```

### Langfuse LLM Cost Tracking

Track LLM costs and traces:

```python
from observability import langfuse_trace, create_generation

with langfuse_trace("agent_query", user_id="user123") as trace:
    response = await agent.process(query)

    create_generation(
        trace,
        name="curriculum_search",
        model="gemini-2.0-flash",
        input_messages=[{"role": "user", "content": query}],
        output=response.content,
        usage={"prompt_tokens": 100, "completion_tokens": 200},
    )
```

### Ragas RAG Evaluation

Evaluate RAG quality:

```python
from observability import RagasEvaluator, EvaluationSample

evaluator = RagasEvaluator()

samples = [
    EvaluationSample(
        question="What are Junior Cycle learning outcomes?",
        answer=generated_answer,
        contexts=retrieved_contexts,
        ground_truth="Expected answer",
    )
]

results = await evaluator.evaluate(samples)
# Returns: faithfulness, answer_relevancy, context_precision
```

### Confluent Kafka Streaming

Stream events to Kafka:

```python
from kafka import get_producer, AGENT_QUERIES, AGENT_RESPONSES

producer = get_producer()

# Publish query event
producer.produce(
    AGENT_QUERIES.name,
    key=session_id,
    value={
        "query_id": query_id,
        "query": user_query,
        "agent_name": "root_agent",
    }
)

# Publish response event
producer.produce(
    AGENT_RESPONSES.name,
    key=session_id,
    value={
        "response_id": response_id,
        "content": response.content[:2000],
        "latency_ms": latency,
    }
)
producer.flush()
```

## Critical Constraints

### DuckDB Single-Threaded Access

DuckDB MUST use single-threaded access to prevent segfaults:

```python
from storage import SerialDatabaseExecutor

executor = SerialDatabaseExecutor()
result = await executor.execute(query)
```

### Embedding Batch Minimum

Embeddings MUST be batched with minimum 100 per call:

```python
from cocoindex_flows import MIN_EMBEDDING_BATCH_SIZE, HNSW_DROP_THRESHOLD

# MANDATORY: Batch minimum 100 (100x performance difference)
# Unbatched 1000 texts: ~100s
# Batched 1000 texts: ~1s

config = EmbeddingConfig(
    batch_size=100,  # MANDATORY minimum
)
```

### HNSW Index Management

Drop indexes before bulk inserts >50 rows:

```python
from cocoindex_flows import HNSW_DROP_THRESHOLD

if row_count > HNSW_DROP_THRESHOLD:
    # Drop index before insert
    table.drop_index("vector_idx")

    # Bulk insert
    table.add(embeddings)

    # Recreate index
    table.create_index("vector_idx", index_type="IVF_HNSW")
```

## Kafka Topics

| Topic | Purpose | Key |
|-------|---------|-----|
| `edu.curriculum.pages` | Curriculum page events | document_id |
| `edu.curriculum.updates` | Curriculum update notifications | source |
| `edu.exams.papers` | Exam paper events | exam_id |
| `celtic.language.translations` | Translation events | source_lang |
| `celtic.folklore.documents` | Folklore document events | collection |
| `celtic.terminology.updates` | Terminology updates | term_id |
| `geo.boundaries.updates` | Boundary data updates | nation |
| `geo.schools.locations` | School location events | school_id |
| `ai.embeddings.created` | Embedding creation events | table_name |
| `ai.agent.queries` | Agent query events | session_id |
| `ai.agent.responses` | Agent response events | session_id |
| `eval.rag.scores` | RAG evaluation scores | evaluation_id |
| `eval.agent.metrics` | Agent performance metrics | agent_name |

## Environment Variables

See `.env.local.example` for complete reference. Key variables:

### Datadog
```bash
DD_API_KEY=your-api-key
DD_SITE=datadoghq.eu
DD_SERVICE=oideachais
DD_LLMOBS_ENABLED=1
DD_LLMOBS_ML_APP=celtic-education
```

### MLflow
```bash
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=oideachais
```

### Langfuse
```bash
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...
```

### Kafka
```bash
CONFLUENT_BOOTSTRAP_SERVERS=pkc-xxx.region.cloud:9092
CONFLUENT_API_KEY=your-api-key
CONFLUENT_API_SECRET=your-api-secret
CONFLUENT_SCHEMA_REGISTRY_URL=https://psrc-xxx.region.cloud
```

### Google Cloud (ADK)
```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

## ADK Agents

### Root Agent

The root agent orchestrates queries to specialized domain agents:

```python
from agents import create_root_agent, AgentContext

agent = create_root_agent()

context = AgentContext(
    query="What are the learning outcomes for Junior Cycle Irish?",
    language="en",
    nation="ireland",
)

response = await agent.process(context)
print(f"Domain: {response.domain}")  # curriculum
print(f"Response: {response.content}")
print(f"Sources: {len(response.sources)}")
```

### Domain Agents

| Agent | Domain | Capabilities |
|-------|--------|--------------|
| CurriculumAgent | curriculum | Search learning outcomes, subjects, exams |
| GeospatialAgent | geospatial | Map queries, school locations, boundaries |
| TranslationAgent | translation | Celtic language translation |
| CorpusAgent | corpus | Folklore, stories, cultural content |
| StatisticsAgent | statistics | Education statistics, comparisons |

### Query Routing

Queries are routed based on keywords and LLM classification:

```python
# Keyword routing (fast)
"curriculum" -> CurriculumAgent
"map", "location" -> GeospatialAgent
"translate" -> TranslationAgent
"folklore", "story" -> CorpusAgent
"statistics", "compare" -> StatisticsAgent

# LLM routing (fallback for ambiguous queries)
Gemini 2.0 Flash classifies intent
```

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=oideachais

# Run specific test
uv run pytest tests/test_agents.py -k "test_root_agent"
```

### Linting

```bash
# Run ruff
uv run ruff check .

# Auto-fix
uv run ruff check --fix .
```

### Type Checking

```bash
uv run mypy oideachais/
```

## Deployment

### Docker

```bash
# Build image
docker build -t oideachais:latest .

# Run with environment
docker run -d \
  --env-file .env.local \
  -p 8000:8000 \
  oideachais:latest
```

### Kubernetes

See `bonneagar/oideachais/` for Kubernetes manifests.

## Credits & Resources

| Resource | Credits | Use For |
|----------|---------|---------|
| Modal | $280 | Serverless fine-tuning |
| HuggingFace | Pro + $50 | Model hosting |
| Google Cloud | £200 + $100 | Gemini API, compute |
| Confluent | $400/mo | Kafka streaming |
| Datadog | Trial | APM, LLMObs |

## Related Documentation

- [NCCA Curriculum](https://curriculumonline.ie)
- [SEC Examinations](https://examinations.ie)
- [Dúchas.ie Folklore](https://duchas.ie)
- [Tearma.ie Terminology](https://tearma.ie)
- [TanStack Start](https://tanstack.com/start)
- [Google ADK](https://developers.google.com/agent-developer-kit)

## Local Deployment UI Screenshots
### Dagster Local Pipeline
![Dagster UI](/docs/images/dagster_ui.png)

### MotherDuck Integration
![MotherDuck UI](/docs/images/motherduck_ui.png)
