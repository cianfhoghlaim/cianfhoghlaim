---
name: dlt
description: Expert assistance for building data pipelines with dlt (data load tool). Use when users need ETL/ELT pipelines, REST API ingestion, incremental loading, schema inference, or loading data to warehouses and lakes.
---

# dlt - Data Load Tool

**Version:** >=1.4.0 | **Last Updated:** 2025-04

## Overview

dlt (data load tool) is a Python library for building production-ready data pipelines:

- **Declarative Loading**: Define resources and sources with decorators
- **Schema Inference**: Automatic schema detection and evolution
- **Incremental Loading**: Built-in cursor-based incremental extraction
- **Multiple Destinations**: DuckDB, BigQuery, Snowflake, Postgres, S3, and more
- **Normalization**: Automatic flattening of nested JSON structures
- **Pythonic Pipelines**: Clean, readable pipeline definitions
- **Streaming Support**: Real-time data streaming capabilities

**Documentation**: https://dlthub.com/docs

## When to Use This Skill

Activate when users need:

- "Load data from an API to a data warehouse"
- "Create incremental data pipelines"
- "Extract nested JSON to tables"
- "Build ETL pipelines in Python"
- "Sync data from REST APIs"

## Core Concepts

### 1. Resources and Sources

```python
import dlt
from typing import Iterator, Dict

@dlt.resource(
    write_disposition="merge",      # or "append" or "replace"
    primary_key="id",               # Required for merge
    table_name="users"              # Optional: override table name
)
def users() -> Iterator[Dict]:
    """Fetch users from API."""
    for user in fetch_api("/users"):
        yield user

@dlt.source
def my_api_source():
    """Source combining multiple resources."""
    return [
        users(),
        orders(),
        products()
    ]

# Run pipeline
pipeline = dlt.pipeline(
    pipeline_name="my_api",
    destination="duckdb",
    dataset_name="raw"
)

load_info = pipeline.run(my_api_source())
```

### 2. Write Dispositions

**Merge** - Upsert based on primary key:
```python
@dlt.resource(write_disposition="merge", primary_key="id")
def users():
    """User profiles that may be updated."""
    yield from fetch_users()
```

**Append** - Add new records only:
```python
@dlt.resource(write_disposition="append")
def events():
    """Immutable event log."""
    yield from fetch_events()
```

**Replace** - Full refresh:
```python
@dlt.resource(write_disposition="replace")
def daily_snapshot():
    """Complete snapshot each run."""
    yield from fetch_all_data()
```

### 3. Incremental Loading

```python
import pendulum

@dlt.resource(
    write_disposition="merge",
    primary_key="id"
)
def orders(
    updated_at=dlt.sources.incremental(
        "updated_at",
        initial_value=pendulum.parse("2024-01-01T00:00:00Z")
    )
):
    """Fetch orders incrementally by updated_at."""
    # First run: fetches from initial_value
    # Subsequent runs: fetches from last_value (max from previous run)

    params = {"since": updated_at.last_value.isoformat()}

    for order in fetch_api("/orders", params=params):
        # CRITICAL: Include cursor field in yielded data
        yield {
            "id": order["id"],
            "updated_at": order["updated_at"],  # Must include!
            "amount": order["amount"],
            "customer_id": order["customer_id"]
        }
```

### 4. Schema Inference

dlt automatically normalizes nested data:

```python
# Input: Nested JSON
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

**Schema Hints:**
```python
@dlt.resource(
    columns={
        "amount": {"data_type": "double"},
        "created_at": {"data_type": "timestamp"}
    }
)
def transactions():
    yield {"id": 1, "amount": 99.99, "created_at": "2024-01-15T10:30:00Z"}
```

### 5. Destinations

**DuckDB (Local Analytics):**
```python
pipeline = dlt.pipeline(
    pipeline_name="local_analysis",
    destination="duckdb",
    dataset_name="analytics"
)
# Creates: data/<pipeline_name>.duckdb
```

**BigQuery:**
```toml
# .dlt/secrets.toml
[destination.bigquery]
project_id = "my-project"
credentials = '{"type": "service_account", ...}'
```

```python
pipeline = dlt.pipeline(
    pipeline_name="bq_pipeline",
    destination="bigquery",
    dataset_name="raw_data"
)
```

**Snowflake:**
```toml
# .dlt/secrets.toml
[destination.snowflake]
account = "xxx.snowflakecomputing.com"
username = "user"
password = "pass"
database = "ANALYTICS"
warehouse = "COMPUTE_WH"
```

**PostgreSQL:**
```toml
# .dlt/secrets.toml
[destination.postgres]
credentials = "postgresql://user:pass@host:5432/database"
```

**Filesystem (S3/R2/GCS):**
```toml
# .dlt/secrets.toml
[destination.filesystem]
bucket_url = "s3://my-bucket/dlt-data"
aws_access_key_id = "..."
aws_secret_access_key = "..."
# For R2:
endpoint_url = "https://<account>.r2.cloudflarestorage.com"
```

### 6. REST API Source

```python
from dlt.sources.rest_api import rest_api_source

config = {
    "client": {
        "base_url": "https://api.example.com/v1",
        "auth": {
            "type": "bearer",
            "token": dlt.secrets["api_token"]
        }
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
                "paginator": {
                    "type": "page_number",
                    "page_param": "page",
                    "total_path": "meta.total_pages"
                }
            }
        },
        {
            "name": "user_orders",
            "endpoint": {
                "path": "users/{user_id}/orders",
                "params": {
                    "user_id": {
                        "type": "resolve",
                        "resource": "users",
                        "field": "id"
                    }
                }
            }
        }
    ]
}

source = rest_api_source(config)
pipeline.run(source)
```

## Common Patterns

### GitHub API Pipeline

```python
import dlt
from typing import Iterator, Dict

@dlt.resource(
    write_disposition="merge",
    primary_key="id"
)
def github_repos(
    org: str,
    updated_at=dlt.sources.incremental("updated_at")
) -> Iterator[Dict]:
    """Fetch GitHub repos for an organization."""
    import requests

    headers = {"Authorization": f"token {dlt.secrets['github_token']}"}
    params = {"sort": "updated", "direction": "desc"}

    if updated_at.last_value:
        params["since"] = updated_at.last_value.isoformat()

    response = requests.get(
        f"https://api.github.com/orgs/{org}/repos",
        headers=headers,
        params=params
    )

    for repo in response.json():
        yield {
            "id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "updated_at": repo["updated_at"],
            "stars": repo["stargazers_count"],
            "language": repo["language"]
        }

@dlt.source
def github_source(org: str):
    return [github_repos(org)]

# Run
pipeline = dlt.pipeline(
    pipeline_name="github",
    destination="duckdb",
    dataset_name="github"
)

load_info = pipeline.run(github_source(org="dagster-io"))
print(f"Loaded {len(load_info.loads_ids)} packages")
```

### Dagster Integration

```python
from dagster import asset, AssetExecutionContext
import dlt

@asset(compute_kind="dlt")
def dlt_github_repos(context: AssetExecutionContext):
    """DLT pipeline as Dagster asset."""
    pipeline = dlt.pipeline(
        pipeline_name="github_dagster",
        destination="duckdb",
        dataset_name="raw"
    )

    load_info = pipeline.run(github_source(org="dagster-io"))

    context.add_output_metadata({
        "rows_loaded": len(load_info.loads_ids),
        "destination": str(pipeline.destination)
    })

    return load_info
```

### Staging with Parquet

```python
pipeline = dlt.pipeline(
    pipeline_name="staged_load",
    destination="bigquery",
    staging="filesystem"  # Stage to S3/GCS first
)

# Run with Parquet format for better performance
load_info = pipeline.run(
    my_source(),
    loader_file_format="parquet"
)
```

### Multiple Sources to One Dataset

```python
pipeline = dlt.pipeline(
    pipeline_name="unified",
    destination="duckdb",
    dataset_name="warehouse"
)

# Load from multiple sources
pipeline.run(api_source())
pipeline.run(database_source())
pipeline.run(file_source())
```

## Configuration

### Project Structure

```
project/
├── .dlt/
│   ├── config.toml      # Non-sensitive config
│   └── secrets.toml     # Sensitive credentials
├── pipelines/
│   ├── __init__.py
│   └── github.py
└── main.py
```

### config.toml

```toml
[runtime]
log_level = "INFO"
dlthub_telemetry = false

[normalize]
max_nesting = 2
```

### secrets.toml

```toml
[sources.github]
api_token = "ghp_xxx"

[destination.bigquery]
project_id = "my-project"
credentials = '{"type": "service_account", ...}'
```

### Environment Variables

```bash
# Override secrets with env vars
export SOURCES__GITHUB__API_TOKEN=ghp_xxx
export DESTINATION__BIGQUERY__PROJECT_ID=my-project
```

## Error Handling

```python
load_info = pipeline.run(source)

# Check for failures
if load_info.has_failed_jobs:
    for package in load_info.load_packages:
        for job in package.jobs.values():
            if hasattr(job, 'failed') and job.failed:
                print(f"Failed: {job.file_path}")
                print(f"Error: {job.exception}")

# Get loaded table names
for package in load_info.load_packages:
    print(f"Tables: {list(package.jobs.keys())}")
```

## Performance Tips

1. **Use Parquet Format**
   ```python
   pipeline.run(source, loader_file_format="parquet")
   ```

2. **Stage Large Loads**
   ```python
   pipeline = dlt.pipeline(destination="bigquery", staging="filesystem")
   ```

3. **Stream Data**
   ```python
   @dlt.resource
   def large_data():
       for page in paginated_api():
           yield page  # Stream one page at a time
   ```

4. **Parallel Workers**
   ```toml
   # config.toml
   [extract]
   workers = 4
   ```

5. **Incremental Loading**
   Always use incremental for large datasets to avoid full refreshes.

## Troubleshooting

### "Column type conflict"
```python
@dlt.resource(columns={"amount": {"data_type": "double"}})
def data():
    yield {"amount": 99.99}
```

### "Incremental not working"
- Ensure cursor field is in yielded data
- Check initial_value format matches data

### "Out of memory"
- Stream data with generators
- Reduce batch sizes
- Use staging destination

### "Primary key required"
```python
@dlt.resource(write_disposition="merge", primary_key="id")
```

## Resources

- **Documentation**: https://dlthub.com/docs
- **API Reference**: https://dlthub.com/docs/api_reference
- **Examples**: https://dlthub.com/docs/examples
- **GitHub**: https://github.com/dlt-hub/dlt
- **Verified Sources**: https://dlthub.com/docs/dlt-ecosystem/verified-sources
