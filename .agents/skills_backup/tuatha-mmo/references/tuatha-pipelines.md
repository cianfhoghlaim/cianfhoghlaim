# Tuath Data Pipelines

Data ingestion, transformation, and orchestration for the Celtic Educational MMO.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│    NCCA     │    SQA      │    WJEC     │   Dúchas    │  GeoJSON│
│  (Ireland)  │ (Scotland)  │   (Wales)   │ (Folklore)  │ (Maps)  │
└─────┬───────┴─────┬───────┴─────┬───────┴─────┬───────┴────┬────┘
      │             │             │             │            │
      └─────────────┴─────────────┴─────────────┴────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   DLT Sources     │
                    │ (data load tool)  │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│   DuckDB        │  │   CocoIndex     │  │   Graphiti     │
│ (Structured)    │  │  (Embeddings)   │  │ (Knowledge)    │
└────────┬────────┘  └────────┬────────┘  └────────┬───────┘
         │                    │                    │
         │           ┌────────▼────────┐           │
         │           │    LanceDB      │           │
         │           │ (Vector Store)  │           │
         │           └────────┬────────┘           │
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │      Dagster      │
                    │  (Orchestration)  │
                    └───────────────────┘
```

## DLT Sources

### Celtic Education Sources

**Location:** `dlt_sources/celtic_education/`

#### NCCA Irish Curriculum

**File:** `ncca_irish.py`

Ingests Irish curriculum from curriculumonline.ie:
- Junior Cycle specifications
- Leaving Certificate specifications
- Learning outcomes
- Assessment criteria

```python
@dlt.source
def ncca_curriculum():
    yield ncca_junior_cycle()
    yield ncca_leaving_cert()
    yield ncca_learning_outcomes()
```

#### SQA Scottish Gaelic

**File:** `sqa_gaelic.py`

Scottish Qualifications Authority content:
- National 5 Gaelic
- Higher Gaelic
- Advanced Higher

#### WJEC Welsh

**File:** `wjec_welsh.py`

Welsh curriculum standards:
- GCSE Welsh
- A Level Welsh

#### Dúchas Folklore

**File:** `duchas_folklore.py`

Irish folklore from duchas.ie:
- Schools' Collection
- Audio recordings
- Manuscript pages

### Geospatial Sources

**Location:** `dlt_sources/geospatial/`

#### Gaeltacht Boundaries

**File:** `gaeltacht_boundaries.py`

Irish-speaking region polygons:
- Gaeltacht zones
- Population statistics
- Language usage data

#### Welsh Language Areas

**File:** `welsh_language_areas.py`

Welsh-speaking communities:
- Fro Gymraeg boundaries
- Census language data

#### Scottish Gaelic Communities

**File:** `gaelic_communities.py`

Gàidhealtachd regions:
- Isle of Skye
- Outer Hebrides
- Other Gaelic areas

### Running DLT Pipelines

```bash
# Run single source
uv run python -m tuath.dlt_sources.celtic_education.ncca_irish

# Run all education sources
uv run python -m tuath.dlt_sources.celtic_education

# Run with custom destination
dlt run tuath.dlt_sources.celtic_education.ncca_irish --destination duckdb
```

## CocoIndex Embedding Flows

### Curriculum Embedding

**File:** `cocoindex_flows/curriculum_embedding.py`

Creates BGE-M3 embeddings for curriculum content:

```python
@cocoindex.flow
class CurriculumEmbeddingFlow:
    """Embed curriculum content for semantic search."""

    def source(self) -> Iterator[Document]:
        yield from load_curriculum_documents()

    def transform(self, doc: Document) -> list[Chunk]:
        return chunk_by_learning_outcome(doc)

    def embed(self, chunks: list[Chunk]) -> list[Embedding]:
        return embed_with_bge_m3(chunks, batch_size=100)

    def sink(self, embeddings: list[Embedding]):
        store_to_lancedb(embeddings, table="curriculum")
```

### Mythology Embedding

**File:** `cocoindex_flows/mythology_embedding.py`

Embeds mythology content with entity preservation:

```python
@cocoindex.flow
class MythologyEmbeddingFlow:
    """Embed mythology with character/location awareness."""

    def transform(self, doc: Document) -> list[Chunk]:
        chunks = semantic_chunk(doc)
        for chunk in chunks:
            chunk.metadata["entities"] = extract_celtic_entities(chunk)
        return chunks
```

### Multilingual Transform

**File:** `cocoindex_flows/transforms/celtic_multilingual.py`

Handles Celtic language specifics:

```python
def celtic_multilingual_transform(text: str, lang: str) -> str:
    """Normalize Celtic text for embedding."""
    # Handle fadas (Irish accents)
    # Handle Welsh mutations
    # Normalize Gaelic orthography
    return normalized_text
```

### Running CocoIndex

```bash
# Build embeddings
uv run cocoindex build curriculum_embedding

# Rebuild specific flow
uv run cocoindex build mythology_embedding --force

# Query embeddings
uv run cocoindex query "verb conjugation" --flow curriculum_embedding
```

## Dagster Orchestration

### Assets

**Location:** `dagster_assets/`

#### Curriculum Assets

**File:** `curriculum_assets.py`

```python
@asset(
    group_name="curriculum",
    partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"),
)
def celtic_curriculum(context) -> pd.DataFrame:
    """Ingest curriculum from all Celtic sources."""
    sources = ["ncca", "sqa", "wjec"]
    data = []
    for source in sources:
        data.extend(load_curriculum(source))
    return pd.DataFrame(data)


@asset(deps=[celtic_curriculum])
def curriculum_embeddings(context, celtic_curriculum) -> None:
    """Generate embeddings for curriculum content."""
    flow = CurriculumEmbeddingFlow()
    flow.run(celtic_curriculum)
```

#### Mythology Assets

**File:** `mythology_assets.py`

```python
@asset(group_name="mythology")
def mythology_content() -> pd.DataFrame:
    """Load Celtic mythology corpus."""
    return load_mythology_sources()


@asset(deps=[mythology_content])
def mythology_embeddings(context, mythology_content) -> None:
    """Embed mythology for search."""
    flow = MythologyEmbeddingFlow()
    flow.run(mythology_content)


@asset(deps=[mythology_content])
def knowledge_graph(context, mythology_content) -> None:
    """Build Graphiti knowledge graph."""
    graphiti = GraphitiClient()
    graphiti.build_from_corpus(mythology_content)
```

#### Embedding Assets

**File:** `embedding_assets.py`

```python
@asset(
    deps=[curriculum_embeddings, mythology_embeddings],
    group_name="search",
)
def search_index() -> None:
    """Create unified search index."""
    lancedb = get_lancedb()
    lancedb.create_index(
        tables=["curriculum", "mythology"],
        index_type="IVF_PQ",
        num_partitions=256,
    )
```

### Schedules

**File:** `schedules.py`

```python
# Daily curriculum refresh
curriculum_schedule = ScheduleDefinition(
    job=define_asset_job("curriculum_job", selection=["celtic_curriculum", "curriculum_embeddings"]),
    cron_schedule="0 2 * * *",  # 2 AM daily
)

# Weekly mythology rebuild
mythology_schedule = ScheduleDefinition(
    job=define_asset_job("mythology_job", selection=["mythology_content", "mythology_embeddings", "knowledge_graph"]),
    cron_schedule="0 3 * * 0",  # 3 AM Sunday
)
```

### Repository Definition

**File:** `definitions.py`

```python
from dagster import Definitions

defs = Definitions(
    assets=[
        celtic_curriculum,
        curriculum_embeddings,
        mythology_content,
        mythology_embeddings,
        knowledge_graph,
        search_index,
    ],
    schedules=[
        curriculum_schedule,
        mythology_schedule,
    ],
    resources={
        "duckdb": DuckDBResource(database="./data/tuath.duckdb"),
        "lancedb": LanceDBResource(uri="./data/lancedb"),
        "graphiti": GraphitiResource(neo4j_uri=os.getenv("NEO4J_URI")),
    },
)
```

### Running Dagster

```bash
# Start Dagster UI
dagster dev -m tuath.dagster_assets

# Materialize single asset
dagster asset materialize -m tuath.dagster_assets --select celtic_curriculum

# Materialize with dependencies
dagster asset materialize -m tuath.dagster_assets --select curriculum_embeddings+

# Run scheduled job manually
dagster job execute -m tuath.dagster_assets -j curriculum_job
```

### Asset Graph

```
celtic_curriculum ──┬──► curriculum_embeddings ──┐
                    │                            │
mythology_content ──┼──► mythology_embeddings ───┼──► search_index
                    │                            │
                    └──► knowledge_graph ────────┘
```

## Database Configuration

### DuckDB (Structured Data)

Single-threaded access required:

```python
# Use SerialDatabaseExecutor
from tuath.db import get_duckdb_connection

with get_duckdb_connection() as conn:
    df = conn.execute("SELECT * FROM curriculum").fetchdf()
```

### LanceDB (Vector Store)

MVCC-safe for reads, single-writer for mutations:

```python
from lancedb import connect

db = connect("./data/lancedb")
table = db.open_table("curriculum")

# Search
results = table.search(query_vector).limit(10).to_list()
```

### FalkorDB/Graphiti (Knowledge Graph)

```python
from graphiti_core import Graphiti

graphiti = Graphiti(
    neo4j_uri=os.getenv("NEO4J_URI"),
    neo4j_user=os.getenv("NEO4J_USER"),
    neo4j_password=os.getenv("NEO4J_PASSWORD"),
)

# Query temporal knowledge
results = graphiti.search(
    "Cú Chulainn training",
    group_ids=["ulster_cycle"],
)
```

## Embedding Best Practices

### Batch Processing

Always batch embeddings (100x performance):

```python
# Good
embeddings = embed_batch(texts, batch_size=100)

# Bad
embeddings = [embed_single(t) for t in texts]
```

### Index Management

Drop indexes for bulk inserts:

```python
# Before bulk insert
db.execute("DROP INDEX IF EXISTS idx_curriculum_embedding")

# Bulk insert
db.insert_many(embeddings)

# After insert
db.execute("CREATE INDEX idx_curriculum_embedding ON curriculum USING HNSW (embedding)")
```

### Memory Management

For large corpora:

```python
# Stream processing
for batch in chunk_iterator(documents, size=1000):
    embeddings = embed_batch(batch)
    store_batch(embeddings)
    gc.collect()  # Free memory
```

## Monitoring

### Dagster UI

Access at http://localhost:3000 during development.

Features:
- Asset lineage visualization
- Run history
- Schedule status
- Resource utilization

### Logs

```bash
# Asset logs
dagster asset logs -m tuath.dagster_assets --select celtic_curriculum

# Run logs
dagster run logs -m tuath.dagster_assets --run-id <run_id>
```

### Metrics

Pipeline metrics exposed at `/metrics`:
- `tuath_assets_materialized_total`
- `tuath_embedding_batch_duration_seconds`
- `tuath_curriculum_records_processed`

---

## Related Documentation

- [Adding Data Sources](./guides/ADDING_DATA_SOURCES.md) - Step-by-step source creation
- [Performance Tuning](./guides/PERFORMANCE_TUNING.md) - Embedding optimization
- [Celtic Languages](./guides/CELTIC_LANGUAGES.md) - Language processing patterns
- [Architecture](./ARCHITECTURE.md) - System overview
- [Deployment](./DEPLOYMENT.md) - Production pipeline setup
