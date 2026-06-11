---
title: 'Pattern: Data Pipeline (DLT → Dagster → CocoIndex)'
domain: 'patterns'
status: 'stable'
description: '| Constraint | Description | Violation Consequence | |------------|-------------|----------------------| | **Incremental loading** | Track cursor/offset for resumable extraction | Re-processing entire dataset on each run | | **Schema validation** | Validate data before loading |'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/DATA_PIPELINE.md
ccc_query_hints:
  - pattern: data pipeline (dlt → dagster → 
---

# Pattern: Data Pipeline (DLT → Dagster → CocoIndex)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **Incremental loading** | Track cursor/offset for resumable extraction | Re-processing entire dataset on each run |
| **Schema validation** | Validate data before loading | Schema drift, type errors in downstream |
| **Idempotency** | Use merge/upsert with natural keys | Duplicate records |
| **Secret management** | Use `dlt.secrets.value`, never hardcode | Credential leaks |
| **Rate limiting** | Implement backoff for API calls | API bans, failed extractions |

---

## Architecture Overview

```
REST APIs / Files / Databases
           ↓
    DLT (Extraction)
    ├── REST API configuration (YAML)
    ├── Pagination handling (6 types)
    └── Incremental state tracking
           ↓
    Dagster (Orchestration)
    ├── Asset-based DAGs
    ├── DagsterDltResource wrapper
    ├── Schedules & sensors
    └── Data quality checks
           ↓
    CocoIndex (Transformation)
    ├── Chunking & embedding
    ├── LLM extraction
    └── Vector/graph exports
           ↓
    Storage (LanceDB / PostgreSQL / Graph DBs)
```

---

## DLT Patterns

### Pattern 1: REST API Configuration (YAML)

**When to use**: Any REST API data extraction.

**Implementation** (`source-config.yaml`):
```yaml
source_name: github_api
client:
  base_url: https://api.github.com
  auth:
    type: bearer
    token: dlt.secrets.value  # Resolved at runtime
  headers:
    Accept: application/vnd.github.v3+json
  paginator:
    type: header_link        # Uses Link header
    # Other types: page, offset, cursor, json_link, single_page

resources:
  - name: repositories
    endpoint:
      path: /user/repos
      params:
        per_page: 100
      incremental:
        cursor_path: updated_at
        initial_value: "2024-01-01"
    primary_key: id
    write_disposition: merge   # Upsert behavior

  - name: issues
    endpoint:
      path: /repos/{owner}/{repo}/issues
      params:
        state: all
      incremental:
        cursor_path: updated_at
        initial_value: "2024-01-01"
    primary_key: id
    write_disposition: merge
```

### Pattern 2: Minimal DLT Pipeline (Python)

**When to use**: Quick implementation from YAML config.

**Implementation**:
```python
import dlt
from dlt.sources.rest_api import rest_api_source, RESTAPIConfig

@dlt.source(name="github_api")
def github_source(access_token=dlt.secrets.value):
    """GitHub API source with incremental loading."""
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.github.com",
            "auth": {"type": "bearer", "token": access_token},
        },
        "resources": [
            {
                "name": "repositories",
                "endpoint": {
                    "path": "/user/repos",
                    "params": {"per_page": 100},
                    "incremental": {
                        "cursor_path": "updated_at",
                        "initial_value": "2024-01-01",
                    },
                },
                "primary_key": "id",
                "write_disposition": "merge",
            },
        ],
    }
    yield from rest_api_source(config)

# Run pipeline
pipeline = dlt.pipeline(
    pipeline_name="github_pipeline",
    destination="duckdb",
    dataset_name="github_data",
)
load_info = pipeline.run(github_source())
print(load_info)
```

### Pattern 3: Pagination Types

| Type | When to Use | Configuration |
|------|-------------|---------------|
| **page** | `?page=1&per_page=100` | `{type: page, page_param: page, page_size_param: per_page}` |
| **offset** | `?offset=0&limit=100` | `{type: offset, offset_param: offset, limit: 100}` |
| **cursor** | `?after=cursor_token` | `{type: cursor, cursor_path: pagination.next, cursor_param: after}` |
| **header_link** | HTTP `Link` header | `{type: header_link}` |
| **json_link** | Response contains next URL | `{type: json_link, next_url_path: pagination.next}` |
| **single_page** | No pagination needed | `{type: single_page}` |

### Pattern 4: Incremental Loading

**When to use**: Any source with timestamps/versions.

**Implementation**:
```python
# DLT tracks state automatically
"incremental": {
    "cursor_path": "updated_at",     # Field to track
    "initial_value": "2024-01-01",   # Starting point
    "start_param": "since",          # Optional: query parameter
}

# On subsequent runs, DLT automatically:
# 1. Reads last cursor value from state
# 2. Adds since=<last_value> to API calls
# 3. Only fetches new/updated records
# 4. Saves new cursor value to state
```

---

## Dagster Patterns

### Pattern 5: DagsterDltResource Integration

**When to use**: Wrap DLT sources as Dagster assets.

**Implementation**:
```python
from dagster import Definitions, asset, AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt

# Define DLT pipeline
@dlt.source
def education_source():
    yield from rest_api_source(config)

education_pipeline = dlt.pipeline(
    pipeline_name="education",
    destination="duckdb",
    dataset_name="education_data",
)

# Wrap as Dagster assets
@dlt_assets(
    dlt_source=education_source(),
    dlt_pipeline=education_pipeline,
    group_name="ingestion",
)
def education_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)

# Definitions
defs = Definitions(
    assets=[education_assets],
    resources={"dlt": DagsterDltResource()},
)
```

### Pattern 6: Multi-Dimensional Partitioning

**When to use**: Parallel processing by time/domain/region.

**Implementation**:
```python
from dagster import (
    Definitions,
    asset,
    MultiPartitionsDefinition,
    StaticPartitionsDefinition,
    DailyPartitionsDefinition,
)

# Define partition dimensions
domain_partitions = StaticPartitionsDefinition(
    ["curriculum", "language", "statistics", "geospatial"]
)
nation_partitions = StaticPartitionsDefinition(
    ["ireland", "scotland", "wales", "england", "ni"]
)
time_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

# Combined partitions
multi_partitions = MultiPartitionsDefinition({
    "domain": domain_partitions,
    "nation": nation_partitions,
    "date": time_partitions,
})

@asset(partitions_def=multi_partitions)
def partitioned_education_data(context):
    partition_key = context.partition_key
    domain = partition_key.keys_by_dimension["domain"]
    nation = partition_key.keys_by_dimension["nation"]
    date = partition_key.keys_by_dimension["date"]

    # Process specific partition
    return extract_data(domain=domain, nation=nation, date=date)
```

### Pattern 7: Asset Checks for Data Quality

**When to use**: Validate data before downstream consumption.

**Implementation**:
```python
from dagster import asset, asset_check, AssetCheckResult

@asset
def raw_curriculum_data():
    return load_curriculum_data()

@asset_check(asset=raw_curriculum_data)
def check_curriculum_not_empty(raw_curriculum_data):
    count = len(raw_curriculum_data)
    return AssetCheckResult(
        passed=count > 0,
        metadata={"row_count": count},
        description="Curriculum data should not be empty",
    )

@asset_check(asset=raw_curriculum_data)
def check_no_null_titles(raw_curriculum_data):
    null_count = sum(1 for r in raw_curriculum_data if r["title"] is None)
    return AssetCheckResult(
        passed=null_count == 0,
        metadata={"null_title_count": null_count},
    )
```

### Pattern 8: Schedules and Sensors

**When to use**: Automate pipeline runs.

**Implementation**:
```python
from dagster import (
    ScheduleDefinition,
    sensor,
    RunRequest,
    SensorEvaluationContext,
)

# Cron-based schedule
daily_curriculum_schedule = ScheduleDefinition(
    job=curriculum_sync_job,
    cron_schedule="0 2 * * *",  # 2 AM daily
    execution_timezone="Europe/Dublin",
)

# Event-driven sensor
@sensor(job=embedding_pipeline_job)
def new_documents_sensor(context: SensorEvaluationContext):
    """Trigger embedding when new documents arrive."""
    new_docs = check_for_new_documents(context.cursor)

    if new_docs:
        yield RunRequest(
            run_key=f"embed_{context.cursor}",
            run_config={"ops": {"embed": {"config": {"doc_ids": new_docs}}}},
        )
        context.update_cursor(str(max(new_docs)))
```

---

## CocoIndex Patterns

### Pattern 9: Core Flow Definition

**When to use**: Any data transformation with embedding/extraction.

**Implementation**:
```python
import cocoindex
from cocoindex.sources import LocalFile
from cocoindex.functions import SplitRecursively, SentenceTransformerEmbed
from cocoindex.storages import LanceDB

@cocoindex.flow_def(name="DocumentEmbedding")
def document_embedding_flow(flow_builder, data_scope):
    # 1. Source: Watch directory for files
    data_scope["documents"] = flow_builder.add_source(
        LocalFile(
            path="./documents",
            glob_pattern="**/*.{md,txt,pdf}",
        )
    )

    # 2. Transform: Chunk and embed
    with data_scope["documents"].row() as doc:
        # Parse content based on file type
        doc["parsed"] = doc["content"].transform(ParseDocument())

        # Split into chunks
        doc["chunks"] = doc["parsed"].transform(
            SplitRecursively(
                chunk_size=800,
                chunk_overlap=150,
                language="markdown",
            )
        )

        # Embed each chunk
        with doc["chunks"].row() as chunk:
            chunk["embedding"] = chunk["text"].transform(
                SentenceTransformerEmbed(
                    model="BAAI/bge-m3",
                    normalize=True,
                )
            )

    # 3. Export: Store in LanceDB with indexes
    embeddings = data_scope["documents"]["chunks"].collector()

    embeddings.export(
        "document_embeddings",
        LanceDB(uri="./lancedb"),
        vector_indexes=[
            cocoindex.VectorIndexDef(
                field_name="embedding",
                metric=cocoindex.VectorSimilarityMetric.COSINE,
            )
        ],
        fts_indexes=["text"],  # Full-text search on content
    )
```

### Pattern 10: LLM Extraction with BAML

**When to use**: Structured data extraction from unstructured content.

**Implementation**:
```python
import cocoindex
from cocoindex.functions import BAMLExtract

@cocoindex.flow_def(name="CurriculumExtraction")
def curriculum_extraction_flow(flow_builder, data_scope):
    data_scope["documents"] = flow_builder.add_source(LocalFile(path="./curriculum"))

    with data_scope["documents"].row() as doc:
        # Extract structured data using BAML schema
        doc["extracted"] = doc["content"].transform(
            BAMLExtract(
                schema="CurriculumDocument",  # Defined in baml_src/
                model="gemini-2.0-flash",
            )
        )

        # Flatten extracted fields
        doc["learning_outcomes"] = doc["extracted"]["learning_outcomes"]
        doc["prerequisites"] = doc["extracted"]["prerequisites"]
        doc["assessment_criteria"] = doc["extracted"]["assessment_criteria"]

    # Export to structured storage
    data_scope["documents"].export(
        "curriculum_structured",
        PostgreSQL(connection_string=os.getenv("DATABASE_URL")),
    )
```

### Pattern 11: Knowledge Graph Construction

**When to use**: Build entity-relationship graphs from documents.

**Implementation**:
```python
import cocoindex
from cocoindex.functions import LLMExtractEntities, LLMExtractRelations
from cocoindex.storages import Neo4j

@cocoindex.flow_def(name="KnowledgeGraph")
def knowledge_graph_flow(flow_builder, data_scope):
    data_scope["documents"] = flow_builder.add_source(LocalFile(path="./docs"))

    with data_scope["documents"].row() as doc:
        # Extract entities
        doc["entities"] = doc["content"].transform(
            LLMExtractEntities(
                entity_types=["Person", "Organization", "Concept", "Location"],
                model="gemini-2.0-flash",
            )
        )

        # Extract relationships
        doc["relations"] = doc["content"].transform(
            LLMExtractRelations(
                relation_types=["WORKS_FOR", "LOCATED_IN", "RELATED_TO", "PREREQUISITE_OF"],
                entities=doc["entities"],
                model="gemini-2.0-flash",
            )
        )

    # Export to graph database
    data_scope["documents"].export(
        "knowledge_graph",
        Neo4j(uri=os.getenv("NEO4J_URI")),
    )
```

---

## Integration Points

| Component | Connects To | Pattern |
|-----------|-------------|---------|
| **DLT** | Dagster | `DagsterDltResource` wraps sources as assets |
| **Dagster** | CocoIndex | Assets trigger CocoIndex flows |
| **CocoIndex** | LanceDB | Vector export with indexes |
| **CocoIndex** | BAML | Type-safe extraction |
| **CocoIndex** | Graph DBs | Entity-relationship export |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Hardcoded API tokens | Use `dlt.secrets.value` or environment variables |
| Missing incremental config | Always add `incremental` for timestamp fields |
| Wrong pagination type | Check API docs for Link header vs cursor |
| No primary key | Define `primary_key` for merge/upsert |
| Large chunk sizes | Keep chunks 500-1000 tokens for embedding quality |
| Missing vector indexes | Always create HNSW index for search |
| Blocking CocoIndex flows | Use async transforms for I/O |

---

## Pipeline Template

```python
# Complete pipeline: DLT → Dagster → CocoIndex

# 1. DLT Source (dlt_sources/api_source.py)
@dlt.source
def api_source():
    yield from rest_api_source(config)

# 2. Dagster Assets (dagster_assets/ingestion.py)
@dlt_assets(dlt_source=api_source(), dlt_pipeline=pipeline)
def ingestion_assets(context, dlt):
    yield from dlt.run(context=context)

# 3. CocoIndex Flow (cocoindex_flows/embedding.py)
@cocoindex.flow_def(name="Embedding")
def embedding_flow(flow_builder, data_scope):
    # Read from DuckDB (populated by DLT)
    data_scope["data"] = flow_builder.add_source(
        DuckDB(query="SELECT * FROM raw_data")
    )
    # Transform and export...

# 4. Dagster Definition (definitions.py)
defs = Definitions(
    assets=[ingestion_assets, embedding_assets],
    schedules=[daily_schedule],
    resources={"dlt": DagsterDltResource()},
)
```

---

## References

- Source: `taighde/dlt/github_api_init/`, `taighde/dagster/dagster-dspy/`, `taighde/cocoindex/`
- Skills: `.claude/skills/dlt/`, `.claude/skills/dagster/`, `.claude/skills/cocoindex/`
- Examples: `sruth/oideachais/dlt_sources/`, `sruth/oideachais/dagster_defs/`
