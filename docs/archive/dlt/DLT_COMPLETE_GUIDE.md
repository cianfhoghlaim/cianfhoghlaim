# DLT (Data Load Tool) — Complete Reference Guide

> **Merged From:** `docs/data_engineering/dlt/` (22 files)
> Consolidated: dlthub.md, dlthub-codebase-analysis.md, dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md, dlt-SQLMesh.md, Transformations, Kafka, Deploy guides (Cloud Run, Cloud Functions, Webhooks), Explore with marimo, Load Datadog, github_api_init/, small-data-sf-2025/, dlt_modal/

---

## Table of Contents

1. [Overview & Core Concepts](#overview--core-concepts)
2. [Resource & Source Patterns](#resource--source-patterns)
3. [Incremental Loading](#incremental-loading)
4. [Schema Management & Normalization](#schema-management--normalization)
5. [REST API Source Framework](#rest-api-source-framework)
6. [Destination Configuration](#destination-configuration)
7. [DLT Transformations (Hub)](#dlt-transformations-hub)
8. [SQLMesh Integration](#sqlmesh-integration)
9. [Kafka Integration](#kafka-integration)
10. [Marimo Data Exploration](#marimo-data-exploration)
11. [Deployment Patterns](#deployment-patterns)
12. [Orchestrator Integration](#orchestrator-integration)
13. [Type-Safe Pipeline (BAML + oRPC)](#type-safe-pipeline-baml--orpc)
14. [Codebase Design Patterns](#codebase-design-patterns)
15. [Troubleshooting & Best Practices](#troubleshooting--best-practices)

---

## Overview & Core Concepts

DLT (Data Load Tool) is a Python library for declarative data loading and ELT pipelines. It handles schema inference, normalization, incremental loading, and destination management automatically.

### Key Principles

1. **Declarative Over Imperative** — Configuration in YAML/decorators, not boilerplate code
2. **Schema Evolution** — Automatic handling of schema changes
3. **Incremental by Default** — Only process changed data
4. **Type Safety** — Pydantic integration for runtime validation

### Quick Start

```python
import dlt

@dlt.resource(write_disposition="merge", primary_key="id")
def my_data():
    yield {"id": 1, "name": "Alice"}

pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",
    dataset_name="data",
    progress="log"
)
load_info = pipeline.run(my_data())
```

---

## Resource & Source Patterns

### Resource Definition

```python
@dlt.resource(
    write_disposition="merge",      # "merge" | "append" | "replace"
    primary_key="id",               # Required for merge
    table_name="custom_name"        # Optional: override table name
)
def my_resource(
    updated_at=dlt.sources.incremental("updated_at")
) -> Iterator[Dict]:
    data = fetch_api(since=updated_at.last_value)
    for record in data:
        yield record
```

### Write Disposition Selection

| Disposition | Use Case | Requires |
|-------------|----------|----------|
| **merge** | Dimension tables, slowly changing data | `primary_key` |
| **append** | Immutable event logs, fact tables | — |
| **replace** | Full refresh snapshots | — |

### Source Composition

```python
@dlt.source
def github_source():
    return [
        github_repositories(),
        github_issues(),
        github_pull_requests(),
    ]
```

---

## Incremental Loading

### Basic Pattern

```python
import pendulum

@dlt.resource(write_disposition="merge", primary_key="id")
def incremental_data(
    updated_at=dlt.sources.incremental(
        "updated_at",
        initial_value=pendulum.parse("2024-01-01T00:00:00Z")
    )
):
    api_params = {"since": updated_at.last_value}
    for record in fetch_api(api_params):
        yield {
            "id": record["id"],
            "updated_at": record["updated_at"],  # Must include cursor field
            "data": record["data"]
        }
```

### Critical Rules

1. **Always include the cursor field** in yielded data
2. **Define primary_key** for merge operations
3. **Use initial_value** for first-run baseline
4. **Stream data** — yield pages, not full datasets

---

## Schema Management & Normalization

### Automatic Normalization

```python
# Input: Nested structure
data = {
    "id": 1,
    "user": {"name": "Alice", "email": "alice@example.com"},
    "tags": ["python", "data"]
}

# Results in 3 tables:
# 1. main_table (id, _dlt_id, _dlt_load_id)
# 2. main_table__user (name, email, _dlt_parent_id)
# 3. main_table__tags (value, _dlt_parent_id)
```

### Schema Hints

```python
@dlt.resource(
    columns={"amount": {"data_type": "double"}}
)
def transactions():
    yield {"id": 1, "amount": 99.99}
```

### Pydantic Integration

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True

@dlt.resource(name="users", columns=User)
def load_users():
    yield {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

Available functions in `dlt.common.libs.pydantic`:
- `pydantic_to_table_schema_columns()` — Convert model to table schema
- `apply_schema_contract_to_model()` — Configure schema evolution modes
- `create_list_model()` — Generate batch validation models
- `validate_and_filter_items()` — Validate data against models

---

## REST API Source Framework

### Basic Configuration

```python
from dlt.sources.rest_api import rest_api_source

config = {
    "client": {
        "base_url": "https://api.example.com",
        "auth": {"token": dlt.secrets["api_token"]}
    },
    "resource_defaults": {
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {
            "params": {"per_page": 100}
        }
    },
    "resources": [
        {
            "name": "users",
            "endpoint": {
                "path": "users",
                "paginator": "json_response"
            }
        }
    ]
}

source = rest_api_source(config)
pipeline.run(source)
```

### Authentication Methods

**API Key:**
```python
"auth": {
    "type": "api_key",
    "name": "api_key",
    "api_key": dlt.secrets["api_key"],
    "location": "query"  # or "header"
}
```

**Bearer Token:**
```python
"auth": {
    "type": "bearer",
    "token": dlt.secrets["bearer_token"]
}
```

**OAuth2:**
```python
"auth": {
    "type": "oauth2",
    "token_url": "https://auth.example.com/oauth/token",
    "client_id": dlt.secrets["client_id"],
    "client_secret": dlt.secrets["client_secret"],
    "scopes": ["read", "write"]
}
```

### Pagination Types

| Type | Description | Key Parameters |
|------|-------------|----------------|
| `json_link` | Next URL in response JSON | `next_url_path` |
| `header_link` | Link header with rel="next" | `links_next_key` |
| `offset` | Numeric offset/limit | `limit`, `offset_param`, `total_path` |
| `page_number` | Page index | `page_param`, `total_path`, `base_page` |
| `cursor` | Continuation token in JSON | `cursor_path`, `cursor_param` |
| `single_page` | No pagination | — |

### Incremental Loading in REST API

```python
{
    "path": "posts",
    "data_selector": "results",
    "params": {
        "created_since": "{incremental.start_value}",
    },
    "incremental": {
        "cursor_path": "created_at",
        "initial_value": "2024-01-25T00:00:00Z",
    },
}
```

### Secret Handling Patterns

**Pattern 1: Decorator (Recommended)**
```python
@dlt.source
def my_api_source(api_key: str = dlt.secrets.value):
    config = {
        "client": {
            "auth": {"type": "api_key", "api_key": api_key}
        }
    }
    yield rest_api_source(config)
```

**Pattern 2: Direct Call**
```python
def my_api_source_direct():
    actual_key = dlt.secrets["my_api_key"]  # Resolve explicitly
    config = {"client": {"auth": {"type": "api_key", "api_key": actual_key}}}
    return rest_api_source(config)
```

### GitHub API Example (32 Endpoints)

The `github_api_init` template provides a production-ready REST API connector covering:

| Category | Endpoints |
|----------|-----------|
| Organization/User | organizations, users, teams, repositories |
| Repository Metadata | assignees, branches, labels, tags, workflows |
| Issues | issues, events, milestones, comments, reactions |
| Pull Requests | pulls, commits, reviews, comments, reactions |
| Commits & Code | commits, comments, reactions |
| Releases | releases, deployments |
| Activity | events, stargazers |
| Projects | projects, columns, cards |
| CI/CD | workflow_runs, workflow_jobs |

---

## Destination Configuration

### DuckDB (Local Analytics)

```python
pipeline = dlt.pipeline(
    pipeline_name="local_analysis",
    destination="duckdb",
    dataset_name="analytics"
)
```

### BigQuery

```toml
# .dlt/secrets.toml
[destination.bigquery]
project_id = "my-project"
dataset_id = "analytics"
credentials = '{"type": "service_account", ...}'
```

### Cloudflare R2 (Filesystem)

```toml
# .dlt/secrets.toml
[destination.filesystem]
bucket_url = "s3://my-r2-bucket"
aws_access_key_id = "..."
aws_secret_access_key = "..."
endpoint_url = "https://<account>.r2.cloudflarestorage.com"
```

### Staging for Large Loads

```python
pipeline = dlt.pipeline(
    destination="bigquery",
    staging="filesystem"  # Faster for large data
)
```

---

## DLT Transformations (Hub)

`dlt transformations` build new tables from already-ingested data. They use the `@dlt.hub.transformation` decorator.

### Use Cases

- Build reporting tables from raw data
- Clean/anonymize data before downstream access
- Normalize JSON into 3NF
- Create dimensional (star-schema) models
- Generate ML feature sets
- Merge heterogeneous sources

### Basic Transformation

```python
@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    customers_table = dataset["customers"]
    yield customers_table.order_by("name").limit(5)

pipeline.run(copied_customers(pipeline.dataset()))
```

### SQL-Based Transformation

```python
@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    customers_table = dataset("""
        SELECT * FROM customers ORDER BY name LIMIT 5
    """)
    yield customers_table
```

### Advanced: Aggregation with Ibis

```python
@dlt.hub.transformation(name="orders_per_user", write_disposition="merge")
def orders_per_user(dataset: dlt.Dataset) -> Any:
    purchases = dataset.table("purchases").to_ibis()
    # Ibis expressions for aggregation
    yield purchases.group_by("user_id").aggregate(
        total=purchases.amount.sum(),
        count=purchases.id.count()
    )
```

---

## SQLMesh Integration

### Getting Started

```bash
# Within dlt project root
sqlmesh init -t dlt --dlt-pipeline <pipeline-name> duckdb
```

This generates:
- `config.yaml` — Project configuration
- `./models` — Auto-generated incremental models
- `./seeds`, `./audits`, `./tests`, `./macros`

### Refresh Models

```bash
# Generate all missing tables
sqlmesh dlt_refresh <pipeline-name>

# Force overwrite existing
sqlmesh dlt_refresh <pipeline-name> --force

# Specific table
sqlmesh dlt_refresh <pipeline-name> --table <dlt-table>
```

### Run Plan

```bash
sqlmesh plan
```

---

## Kafka Integration

### Setup

```bash
dlt init kafka duckdb
```

### Configuration

```toml
# .dlt/secrets.toml
[sources.kafka.credentials]
bootstrap_servers = "web.address.gcp.confluent.cloud:9092"
group_id = "test_group"
security_protocol = "SASL_SSL"
sasl_mechanisms = "PLAIN"
sasl_username = "example_username"
sasl_password = "example_secret"
```

### Resource

```python
@dlt.resource(name="kafka_messages", table_name=lambda msg: msg["_kafka"]["topic"])
def kafka_consumer(
    topics: Union[str, List[str]],
    credentials: Union[KafkaCredentials, Consumer] = dlt.secrets.value,
    msg_processor: Optional[Callable] = default_msg_processor,
    batch_size: Optional[int] = 3000,
    batch_timeout: Optional[int] = 3,
    start_from: Optional[TAnyDateTime] = None,
) -> Iterable[TDataItem]:
    ...
```

---

## Marimo Data Exploration

### Setup

```bash
pip install marimo "ibis-framework[duckdb]"
marimo edit my_notebook.py
```

### DLT Widgets

```python
import marimo as mo
from dlt.helpers.marimo import render, load_package_viewer

await render(load_package_viewer)
```

### Access Data via Ibis

```python
# Access loaded data
dataset = pipeline.dataset()
tables = dataset.table("my_table").to_ibis()
df = tables.execute()
```

---

## Deployment Patterns

### Google Cloud Run

```bash
gcloud run jobs deploy notion-pipeline-job \
    --source . \
    --tasks 1 \
    --max-retries 5 \
    --cpu 4 \
    --memory 4Gi \
    --region us-central1 \
    --project my-project
```

**Environment Variables:** Set via Cloud Run UI or GCP Secret Manager. Capitalize variable names: `sources.notion.api_key` → `SOURCES__NOTION__API_KEY`.

### Google Cloud Functions

```bash
gcloud functions deploy pipeline_notion \
    --runtime python310 \
    --trigger-http \
    --allow-unauthenticated \
    --source . \
    --timeout 300
```

### GCP Webhook (Event-Driven)

```python
import dlt
from google.cloud import bigquery

def your_webhook(request):
    data = request.get_json()
    Event = [data]
    pipeline = dlt.pipeline(
        pipeline_name='platform_to_bigquery',
        destination='bigquery',
        dataset_name='webhooks',
    )
    pipeline.run(Event, table_name='webhook')
    return 'Event received and processed successfully.'
```

---

## Orchestrator Integration

### Dagster

```python
from dagster import asset, AssetExecutionContext
import dlt

@asset(compute_kind="dlt")
def dlt_ingestion(context: AssetExecutionContext):
    pipeline = dlt.pipeline(
        pipeline_name="data_ingest",
        destination="duckdb",
        dataset_name="raw"
    )
    load_info = pipeline.run(my_source())
    context.add_output_metadata({
        "rows_loaded": len(load_info.loads_ids),
        "tables": list(load_info.load_packages[0].jobs.keys())
    })
    return load_info
```

### Airflow

```python
from airflow.decorators import dag, task
import dlt

@dag(schedule="@daily")
def dlt_dag():
    @task
    def run_dlt_pipeline():
        pipeline = dlt.pipeline(
            pipeline_name="airflow_pipeline",
            destination="bigquery"
        )
        return pipeline.run(my_source())

    run_dlt_pipeline()
```

---

## Type-Safe Pipeline (BAML + oRPC)

### Architecture

```
DLT (ingestion) → BAML (schema bridge) → Pydantic (Python) + Zod (TypeScript) → oRPC/MCP API
```

### BAML Schema Definition

```baml
class DocumentChunk {
  id string                 @description("Unique chunk identifier")
  repo string               @description("Repository name or ID")
  file_path string?         @description("Source file path")
  content string            @description("Text content of the chunk")
  embedding float[]         @description("Embedding vector")
}
```

### Generated Pydantic

```python
class DocumentChunk(BaseModel):
    id: str
    repo: str
    file_path: Optional[str] = None
    content: str
    embedding: List[float]
```

### Generated TypeScript + Zod

```typescript
export interface DocumentChunk {
  id: string;
  repo: string;
  file_path?: string;
  content: string;
  embedding: number[];
}

export const DocumentChunkSchema = z.object({
  id: z.string(),
  repo: z.string(),
  file_path: z.string().optional(),
  content: z.string(),
  embedding: z.array(z.number())
});
```

---

## Codebase Design Patterns

### Decorator Pattern
Used extensively in DLT and Dagster for declaring resources and assets.

### Factory Pattern
Creating destinations and clients dynamically:
```python
def create_r2_destination(bucket_name=None, endpoint_url=None, ...):
    return dlt.destinations.filesystem(
        bucket_url=f"s3://{bucket_name}",
        credentials={...}
    )
```

### Repository/Client Pattern
Encapsulating external service interactions (R2Client, GitHubClient).

### Strategy Pattern
Different processing strategies for cloning, uploading, indexing, and scraping.

---

## Troubleshooting & Best Practices

### Common Issues

| Issue | Solution |
|-------|----------|
| "Column type conflict" | Provide schema hints via `columns=` |
| "Incremental not working" | Ensure cursor field is in yielded data |
| "Out of memory" | Stream pages, don't load all at once |
| "Primary key required for merge" | Add `primary_key=` to resource |

### Best Practices

1. **Always define primary keys** for merge operations
2. **Use incremental loading** for large datasets
3. **Use Parquet format** for better performance: `pipeline.run(source, loader_file_format="parquet")`
4. **Stage large loads** via S3/R2 for warehouse destinations
5. **Monitor runs**: Check `load_info.has_failed_jobs`
6. **Validate data** before yielding
7. **Set dev_mode=True** during development
8. **Use `.dlt/secrets.toml`** for credentials (never hardcode)

### Performance Optimization

```python
# Use Parquet
pipeline.run(source, loader_file_format="parquet")

# Stream data in batches
@dlt.resource
def large_dataset():
    for page in paginated_api():
        yield page  # Not: all_data = fetch_all()
```

### Full Pipeline Example

```python
import dlt
from typing import Iterator, Dict

@dlt.resource(
    write_disposition="merge",
    primary_key="id",
    table_name="github_repos"
)
def github_repositories(
    updated_at=dlt.sources.incremental("updated_at")
) -> Iterator[Dict]:
    import requests
    headers = {"Authorization": f"token {dlt.secrets['github_token']}"}
    params = {
        "since": updated_at.last_value.isoformat() if updated_at.last_value else "2024-01-01"
    }
    response = requests.get(
        "https://api.github.com/orgs/dlt-hub/repos",
        headers=headers, params=params
    )
    for repo in response.json():
        yield {
            "id": repo["id"],
            "name": repo["name"],
            "updated_at": repo["updated_at"],
            "stars": repo["stargazers_count"],
            "language": repo["language"]
        }

@dlt.source
def github_source():
    return [github_repositories()]

pipeline = dlt.pipeline(
    pipeline_name="github_ingest",
    destination="duckdb",
    dataset_name="github",
    progress="log"
)

load_info = pipeline.run(github_source())

if load_info.has_failed_jobs:
    for job in load_info.load_packages[0].jobs.values():
        if job.failed:
            print(f"Failed: {job.exception}")
else:
    print("All jobs completed successfully")
```

---

## Quick Reference

```python
# Create pipeline
pipeline = dlt.pipeline(pipeline_name="x", destination="duckdb", dataset_name="data")

# Define resource
@dlt.resource(write_disposition="merge", primary_key="id")
def my_data(): yield {"id": 1}

# Incremental
updated_at=dlt.sources.incremental("updated_at", initial_value="2024-01-01")

# Run
load_info = pipeline.run(my_source())

# Check results
if load_info.has_failed_jobs:
    print([j for j in load_info.load_packages[0].jobs.values() if j.failed])
```
