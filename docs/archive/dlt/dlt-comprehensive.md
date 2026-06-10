# dlt (Data Load Tool) Comprehensive Guide

> Merged from 23 source files in `dlt/` — dltHub expert skill, GitHub API init research, deployment patterns, and tool integrations.

---

## Core dlt Skill & Reference


> Source: `docs/data_engineering/dlt/dlthub.md`

---
name: dlthub Expert
description: Expert assistance for building data pipelines with dlthub (DLT). Provides guidance on resources, sources, incremental loading, schema inference, and destination configuration.
category: Data Engineering
tags: [dlthub, dlt, data-pipeline, etl, elt, data-engineering]
---

# dlthub Expert Skill

You are an expert in dlthub (DLT), the Python library for declarative data loading and ELT pipelines. You help users design, implement, debug, and optimize DLT pipelines.

## Core Capabilities

When users ask for help with dlthub, you should:

1. **Design Pipelines**: Help architect data pipelines using DLT's resource and source patterns
2. **Implement Resources**: Write `@dlt.resource` and `@dlt.source` decorators with proper configurations
3. **Configure Incremental Loading**: Set up `dlt.sources.incremental()` for efficient data sync
4. **Schema Management**: Guide users on schema inference, hints, and evolution
5. **Debug Issues**: Troubleshoot common problems like schema conflicts, incremental loading issues, and memory problems
6. **Optimize Performance**: Suggest performance improvements (Parquet format, batching, parallel workers)
7. **Integrate with Orchestrators**: Help integrate DLT with Dagster, Airflow, or Prefect

## Key Principles

### 1. Resource Definition Pattern

Always define resources with proper metadata:

```python
import dlt
from typing import Iterator, Dict

@dlt.resource(
    write_disposition="merge",      # or "append" or "replace"
    primary_key="id",               # Required for merge
    table_name="custom_name"        # Optional: override table name
)
def my_resource(
    updated_at=dlt.sources.incremental("updated_at")  # For incremental
) -> Iterator[Dict]:
    """Resource docstring."""
    # Fetch data
    data = fetch_api(since=updated_at.last_value)

    # Yield records
    for record in data:
        yield record
```

### 2. Write Disposition Selection

Guide users to choose the right write disposition:

- **merge**: For dimension tables, slowly changing data, or when updates are needed
  - Requires `primary_key` to be defined
  - Performs UPSERT operations
  - Example: user profiles, product catalogs

- **append**: For immutable event logs or fact tables
  - No deduplication
  - Faster than merge
  - Example: clickstream events, transactions, logs

- **replace**: For full refresh snapshots
  - Truncates table on each run
  - Example: daily snapshots, small reference tables

### 3. Incremental Loading Pattern

Always suggest incremental loading for large datasets:

```python
import pendulum

@dlt.resource(
    write_disposition="merge",
    primary_key="id"
)
def incremental_data(
    updated_at=dlt.sources.incremental(
        "updated_at",
        initial_value=pendulum.parse("2024-01-01T00:00:00Z")
    )
):
    """Only fetch data since last run."""
    # First run: fetches from initial_value
    # Subsequent runs: fetches from last_value (max cursor from previous run)

    api_params = {"since": updated_at.last_value}

    for record in fetch_api(api_params):
        # Ensure cursor field is present in yielded data
        yield {
            "id": record["id"],
            "updated_at": record["updated_at"],  # Critical: include cursor field
            "data": record["data"]
        }
```

### 4. Schema Inference and Normalization

Explain how DLT handles nested data:

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

Guide users to:
- Let DLT normalize automatically (recommended for most cases)
- Pre-flatten data if they need specific control over schema
- Use schema hints for type enforcement

### 5. Destination Configuration

Help users configure destinations properly:

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
dataset_id = "analytics"
credentials = '{"type": "service_account", ...}'
```

**Cloudflare R2 (Filesystem):**
```toml
# .dlt/secrets.toml
[destination.filesystem]
bucket_url = "s3://my-r2-bucket"
aws_access_key_id = "..."
aws_secret_access_key = "..."
endpoint_url = "https://<account>.r2.cloudflarestorage.com"
```

### 6. REST API Integration

For REST APIs, recommend the `rest_api_source`:

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

### 7. Pipeline Orchestration

Help integrate with orchestrators:

**Dagster:**
```python
from dagster import asset, AssetExecutionContext
import dlt

@asset(compute_kind="dlt")
def dlt_ingestion(context: AssetExecutionContext):
    """DLT pipeline as Dagster asset."""
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

**Airflow:**
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

## Common Issues and Solutions

### Issue: "Column type conflict"

**Problem:**
```
Column 'amount' has type 'bigint' but received 'double'
```

**Solution:**
Provide schema hints:
```python
@dlt.resource(
    columns={"amount": {"data_type": "double"}}
)
def transactions():
    yield {"id": 1, "amount": 99.99}
```

### Issue: "Incremental loading not working"

**Problem:** All data reloaded every time

**Solution:** Ensure cursor field is present in yielded data:
```python
@dlt.resource(primary_key="id")
def data(updated_at=dlt.sources.incremental("updated_at")):
    for item in fetch_api():
        yield {
            "id": item["id"],
            "updated_at": item["updated_at"]  # ✓ Must include cursor field
        }
```

### Issue: "Out of memory"

**Problem:** Loading millions of rows causes OOM

**Solution:** Stream data in batches:
```python
@dlt.resource
def large_dataset():
    # Stream one page at a time
    for page in paginated_api():
        yield page

    # Avoid: all_data = fetch_all()  # ❌ Loads everything
```

### Issue: "Primary key required for merge"

**Problem:**
```
Write disposition 'merge' requires primary_key
```

**Solution:**
```python
@dlt.resource(
    write_disposition="merge",
    primary_key="id"  # Add this
)
def my_resource():
    yield {"id": 1, "data": "..."}
```

## Best Practices to Recommend

1. **Always define primary keys for merge operations**
   ```python
   @dlt.resource(write_disposition="merge", primary_key="id")
   ```

2. **Use incremental loading for large datasets**
   ```python
   updated_at=dlt.sources.incremental("updated_at")
   ```

3. **Use Parquet for better performance**
   ```python
   pipeline.run(source, loader_file_format="parquet")
   ```

4. **Stage large warehouse loads via S3/R2**
   ```python
   pipeline = dlt.pipeline(
       destination="bigquery",
       staging="filesystem"  # Faster for large data
   )
   ```

5. **Monitor and log pipeline runs**
   ```python
   load_info = pipeline.run(source)

   if load_info.has_failed_jobs:
       for job in load_info.load_packages[0].jobs.values():
           if job.failed:
               print(f"Failed: {job.exception}")
   ```

6. **Validate data quality**
   ```python
   @dlt.resource
   def validated_data():
       for record in fetch_api():
           if not record.get("id"):
               raise ValueError("Missing ID")
           yield record
   ```

## Example Workflows

### Full Pipeline Example

```python
import dlt
from typing import Iterator, Dict

# 1. Define resource
@dlt.resource(
    write_disposition="merge",
    primary_key="id",
    table_name="github_repos"
)
def github_repositories(
    updated_at=dlt.sources.incremental("updated_at")
) -> Iterator[Dict]:
    """Fetch GitHub repos incrementally."""
    import requests

    headers = {"Authorization": f"token {dlt.secrets['github_token']}"}
    params = {
        "since": updated_at.last_value.isoformat() if updated_at.last_value else "2024-01-01"
    }

    response = requests.get(
        "https://api.github.com/orgs/dlt-hub/repos",
        headers=headers,
        params=params
    )

    for repo in response.json():
        yield {
            "id": repo["id"],
            "name": repo["name"],
            "updated_at": repo["updated_at"],
            "stars": repo["stargazers_count"],
            "language": repo["language"]
        }

# 2. Define source
@dlt.source
def github_source():
    """GitHub data source."""
    return [
        github_repositories(),
        # Add more resources as needed
    ]

# 3. Create and run pipeline
pipeline = dlt.pipeline(
    pipeline_name="github_ingest",
    destination="duckdb",
    dataset_name="github",
    progress="log"
)

load_info = pipeline.run(github_source())

# 4. Inspect results
print(f"Pipeline: {load_info.pipeline.pipeline_name}")
print(f"Destination: {load_info.pipeline.destination}")
print(f"Tables created: {list(load_info.load_packages[0].jobs.keys())}")

if load_info.has_failed_jobs:
    print("⚠️  Some jobs failed")
else:
    print("✓ All jobs completed successfully")
```

## Response Guidelines

When helping users with dlthub:

1. **Ask clarifying questions** about:
   - Data source type (API, database, files)
   - Expected data volume and update frequency
   - Target destination (DuckDB, BigQuery, S3, etc.)
   - Need for incremental loading vs. full refresh

2. **Provide complete, working examples** with:
   - Proper imports
   - Decorator configurations
   - Error handling
   - Logging/monitoring

3. **Explain trade-offs** between:
   - merge vs. append vs. replace
   - Incremental vs. full refresh
   - Direct loading vs. staging
   - Schema inference vs. explicit hints

4. **Reference documentation** when needed:
   - Main docs: https://dlthub.com/docs/intro
   - API reference: https://dlthub.com/docs/api_reference/
   - Examples: https://dlthub.com/docs/examples/

5. **Suggest optimizations** for:
   - Performance (Parquet, batching, parallel workers)
   - Cost (incremental loading, staging)
   - Reliability (retry logic, validation)
   - Maintainability (code organization, testing)

## Integration with This Codebase

This project uses dlthub in several pipelines:

- **GitHub Pipeline** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/`):
  - DLT resources for GitHub metadata
  - DuckDB destination for tracking
  - Integration with Dagster

- **Documentation Pipeline** (`/home/user/hackathon/data-unified/pipelines/docs_to_knowledge/`):
  - DLT for documentation ingestion
  - Integration with Firecrawl and Cognee

- **Shared Utilities** (`/home/user/hackathon/data-unified/pipelines/shared/`):
  - `dlt_sources.py`: R2 and DuckDB destination factories
  - `config.py`: Configuration management

Reference these implementations when helping users build similar pipelines.

## Quick Reference

**Create a pipeline:**
```python
pipeline = dlt.pipeline(pipeline_name="my_pipeline", destination="duckdb", dataset_name="data")
```

**Define a resource:**
```python
@dlt.resource(write_disposition="merge", primary_key="id")
def my_data(): yield {"id": 1}
```

**Incremental loading:**
```python
updated_at=dlt.sources.incremental("updated_at", initial_value="2024-01-01")
```

**Run pipeline:**
```python
load_info = pipeline.run(my_source())
```

**Check results:**
```python
if load_info.has_failed_jobs:
    print("Failed jobs:", [j for j in load_info.load_packages[0].jobs.values() if j.failed])
```

---

Use this skill to provide expert-level guidance on building production-ready data pipelines with dlthub.


## KCG Summary


> Source: `docs/data_engineering/dlt/KCG_SUMMARY.md`

# dlt (Data Load Tool) — KCG Summary

## What It Is
dlt (Data Load Tool / dlthub) is a Python library for declarative ELT pipelines that infers schemas, normalizes nested JSON, and supports incremental loading into DuckDB, MotherDuck, BigQuery, Snowflake, and more. This directory contains the dlt expert agent documentation, GitHub API research pipeline (multi-source init from API → dlt), dlt + SQLMesh transformation patterns, Small Data SF 2025 workshop materials, BAML + oRPC + MCP typesafe pipeline analysis, and deployment docs for Google Cloud Functions/Run.

## Why This Matters for Kings' College Galway
dlt is the ingestion backbone of the oideachais platform — it loads Leaving Cert examination data from filesystem or REST sources into DuckDB/MotherDuck staging tables. The GitHub API research pipeline provides reusable patterns for `dlt init` source generation and incremental loading configuration. The SQLMesh integration docs show the DLT → SQLMesh transformation handoff. The deployment patterns (Cloud Run, Cloud Functions) inform production pipeline deployment on the Komodo+Pangolin infrastructure.

## Key Patterns Preserved
22 .md files remain, including:
- `dlthub.md` — Full dlt expert agent instruction (501 lines)
- `dlthub-codebase-analysis.md` — Deep analysis of dlt internals
- `dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md` — BAML + oRPC + MCP for typesafe dlt pipelines
- `dlt - SQLMesh.md` — DLT to SQLMesh transformation patterns
- `github_api_init/` (7 .md files) — Comprehensive GitHub API source research: pipeline analysis, comparison with source init, quick reference, executive summary
- `dlt_modal/README.md` — Modal cloud deployment
- `small-data-sf-2025/` (3 files) — Workshop materials: basics, presentation, README
- Deployment docs: Cloud Functions webhook, Cloud Functions deploy, Cloud Run (3 files)
- `Explore data with marimo _ dlt Docs.md` — dlt + marimo data exploration
- `Kafka _ dlt Docs.md` — dlt + Kafka streaming
- `Load Datadog data in Python using dltHub.md` — Observability pipeline
- `Transformations _ dlt Docs.md` — dlt transformation patterns

## Source Files
Full source removed (2026-06-06). Available at https://github.com/dlt-hub/dlt

## What Was Removed
Python source (.py), TOML/JSON/YAML configs, lock files, .gitignore, SQL files, shell scripts, CSV data, Jupyter notebooks


## Codebase Analysis


> Source: `docs/data_engineering/dlt/dlthub-codebase-analysis.md`

# DLT Hub Codebase Analysis

## Overview
The dlthub codebase in `/home/user/hackathon/data-unified` is a sophisticated data engineering platform that integrates multiple data pipelines and orchestration frameworks. It demonstrates advanced Python patterns for building scalable, extensible data platforms.

## 1. Design Patterns

### 1.1 Decorator Pattern

**Usage**: Extensively used in DLT and Dagster for declaring resources and assets.

**Key Examples**:

```python
# DLT Resource Decorator
@dlt.resource(write_disposition="merge", primary_key="full_name")
def github_repos_resource(repos=None, github_token=None):
    # Resource implementation
    yield data

# DLT Source Decorator
@dlt.source
def github_repos_source(repos=None, github_token=None):
    return github_repos_resource(repos=repos, github_token=github_token)

# Dagster Asset Decorator
@asset(
    description="...",
    group_name="github_pipeline",
    deps=[github_repos],
)
def r2_uploaded_repos(context: AssetExecutionContext, github_repos):
    # Asset implementation
    return result
```

**File Locations**:
- `/home/user/hackathon/data-unified/pipelines/github_to_r2/clone_repo.py` (lines 53-144)
- `/home/user/hackathon/data-unified/pipelines/github_to_r2/upload_r2.py` (lines 116-159)
- `/home/user/hackathon/data-unified/pipelines/docs_to_knowledge/scrape_docs.py` (lines 76-128)
- `/home/user/hackathon/data-unified/pipelines/github_to_r2/dagster_assets.py` (lines 16-135)

### 1.2 Builder Pattern

**Usage**: Used for configuring complex flows and pipelines.

**Key Example**: `CodeIndexConfig` dataclass

```python
@dataclass
class CodeIndexConfig:
    """Configuration for code indexing."""
    repo_owner: str
    repo_name: str
    branch: str
    r2_object_prefix: str
    path: Optional[str] = None
    included_patterns: Optional[list[str]] = None
    excluded_patterns: Optional[list[str]] = None
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/github_to_r2/index_cocoindex.py` (lines 21-32)

### 1.3 Factory Pattern

**Usage**: Creating destinations and clients dynamically.

```python
def create_r2_destination(bucket_name=None, endpoint_url=None, ...):
    """Create a DLT destination for Cloudflare R2."""
    return dlt.destinations.filesystem(
        bucket_url=f"s3://{bucket_name}",
        credentials={...}
    )

def create_duckdb_destination(database_path=None):
    """Create a DLT destination for DuckDB."""
    return dlt.destinations.duckdb(database_path)
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/shared/dlt_sources.py` (lines 7-59)

### 1.4 Repository/Client Pattern

**Usage**: Encapsulating external service interactions.

```python
class R2Client:
    """Client for interacting with Cloudflare R2 storage."""
    
    def __init__(self, access_key_id=None, ...):
        self.s3_client = boto3.client("s3", ...)
    
    def upload_file(self, file_path, object_name=None, ...):
        # Implementation
        
    def download_file(self, object_name, file_path, ...):
        # Implementation
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/shared/r2_client.py` (lines 11-196)

### 1.5 Strategy Pattern

**Usage**: Different ways to process and index data.

- **GitHub cloning strategy**: `clone_github_repo()` function
- **Upload strategy**: `upload_repo_to_r2()` function
- **Indexing strategy**: `index_from_r2()` function
- **Documentation scraping strategy**: `scrape_documentation()` function

**File Locations**:
- `/home/user/hackathon/data-unified/pipelines/github_to_r2/clone_repo.py` (lines 15-50)
- `/home/user/hackathon/data-unified/pipelines/github_to_r2/upload_r2.py` (lines 35-108)
- `/home/user/hackathon/data-unified/pipelines/docs_to_knowledge/scrape_docs.py` (lines 13-73)

---

## 2. Data Ontology & Schema System

### 2.1 Type System Foundation

The codebase uses Pydantic v2 for runtime type validation and schema definition.

**Base Type Definitions** (`/home/user/hackathon/data-unified/models/classes.py`):

```python
# Source type literals
SourceType = Literal[
    "github_api",
    "repository_clone",
    "docs_site",
    "issue_thread",
    "release",
    "workflow_run",
]

# Collection method literals
CollectionMethod = Literal[
    "rest_api",
    "graphql_api",
    "git_clone",
    "local_file",
    "manual_upload",
]
```

### 2.2 Core Data Models

**SourceInfo** - Metadata about data source:
```python
class SourceInfo(BaseModel):
    type: SourceType
    collection_method: CollectionMethod
    owner: Optional[str]
    repository: Optional[str]
    ref: Optional[str]  # branch, tag, or commit SHA
    api_endpoint: Optional[str]
    doc_url: Optional[str]
    path: Optional[str]
    description: Optional[str]
```

**RetrievalMetadata** - Tracking retrieval information:
```python
class RetrievalMetadata(BaseModel):
    ingested_at: Optional[datetime]
    sha: Optional[str]
    etag: Optional[str]
    size_bytes: Optional[int]
    content_type: Optional[str]
    toolchain: Optional[str]
```

**RepositoryAnalysis** - Repository intelligence:
```python
class RepositoryAnalysis(BaseModel):
    primary_language: Optional[str]
    languages: Optional[List[LanguageStat]]
    dependency_files: Optional[List[str]]
    services_detected: Optional[List[str]]
    key_workflows: Optional[List[str]]
    risk_flags: Optional[List[str]]
    notes: Optional[str]
```

**DataItem** - Unified data representation:
```python
class DataItem(BaseModel):
    id: Optional[str]
    source: SourceInfo
    retrieval: RetrievalMetadata
    endpoint: Optional[EndpointDescriptor]
    repository: Optional[RepositoryAnalysis]
    documentation: Optional[DocumentationNode]
    semantic: SemanticInfo
    content: Optional[str]
```

**File Location**: `/home/user/hackathon/data-unified/models/classes.py`

### 2.3 Pipeline Configuration Models

**Priority Enum** - Processing priority levels:
```python
class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

**GitHubRepoConfig** - GitHub repository configuration:
```python
class GitHubRepoConfig(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    path: Optional[str] = None
    included_patterns: Optional[List[str]] = None
    excluded_patterns: Optional[List[str]] = None
    enabled: bool = True
    priority: Priority = Priority.MEDIUM
    
    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.repo}"
```

**PipelineConfig** - Global pipeline settings:
```python
class PipelineConfig(BaseModel):
    incremental: bool = True
    batch_size: int = 10
    max_concurrent: int = 5
    rate_limit_per_second: float = 1.0
```

**IndexingResult** - Code indexing pipeline results:
```python
class IndexingResult(BaseModel):
    repo_name: str
    indexed_files: int
    total_chunks: int
    embeddings_generated: int
    storage_location: str
    index_location: str
    metadata: Dict[str, Any]
    started_at: datetime
    completed_at: datetime
    success: bool
    errors: List[str]
```

**File Location**: `/home/user/hackathon/data-unified/models/schemas.py`

### 2.4 Configuration-Driven Schema

Configuration is loaded from YAML and merged with Pydantic models:

```python
def load_config(config_path: str = "config/sources.yaml"):
    """Load configuration from YAML file."""
    config_file = project_root / config_path
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    return config

def get_sources_config() -> dict[str, Any]:
    """Get software sources configuration."""
    config = load_config("config/sources.yaml")
    return config.get("sources", {})
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/shared/config.py`

---

## 3. Resource Patterns

### 3.1 DLT Resource Pattern

DLT resources are the fundamental unit of data extraction. They follow a consistent pattern:

**Pattern Structure**:
```python
@dlt.resource(write_disposition="merge", primary_key="id")
def my_resource(params=None):
    """DLT resource implementation.
    
    Args:
        params: Optional configuration parameters
        
    Yields:
        Data items to be loaded
    """
    # 1. Handle configuration
    if params is None:
        params = load_config()
    
    # 2. Implement extraction logic
    for item in extract_data(params):
        # 3. Transform if needed
        transformed = transform(item)
        # 4. Yield results
        yield transformed
```

**Real Examples**:

**GitHub Repos Resource** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/clone_repo.py:53-127`):
```python
@dlt.resource(write_disposition="merge", primary_key="full_name")
def github_repos_resource(repos=None, github_token=None):
    """Fetches repository metadata from GitHub API."""
    github_token = github_token or get_env("GITHUB_API_KEY")
    if repos is None:
        repos = get_github_repos_config()
    
    auth = BearerTokenAuth(github_token) if github_token else None
    
    for repo_config in repos:
        if not repo_config.get("enabled", True):
            continue
        
        owner = repo_config["owner"]
        repo = repo_config["repo"]
        
        try:
            response = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                headers={"Authorization": f"Bearer {github_token}"}
            )
            response.raise_for_status()
            repo_data = response.json()
            
            yield {
                "full_name": repo_data["full_name"],
                "owner": owner,
                "repo": repo,
                "stars": repo_data.get("stargazers_count"),
                # ... more fields
            }
        except Exception as e:
            print(f"Error fetching {owner}/{repo}: {e}")
            yield {"full_name": f"{owner}/{repo}", "error": str(e)}
```

**R2 Upload Resource** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/upload_r2.py:116-146`):
```python
@dlt.resource(write_disposition="merge", primary_key="full_name")
def r2_upload_resource(cloned_repos):
    """Resource for uploading repos to R2."""
    r2_client = R2Client()
    
    for repo_info in cloned_repos:
        if not repo_info.get("success", False):
            continue
        
        result = upload_repo_to_r2(
            repo_path=Path(repo_info["clone_path"]),
            owner=repo_info["owner"],
            repo=repo_info["repo"],
            branch=repo_info["branch"],
            r2_client=r2_client,
        )
        
        yield result
```

**Docs Scraper Resource** (`/home/user/hackathon/data-unified/pipelines/docs_to_knowledge/scrape_docs.py:76-111`):
```python
@dlt.resource(write_disposition="merge", primary_key="name")
def docs_scraper_resource(sources=None, max_urls_per_source=50):
    """Resource for scraping documentation sources."""
    if sources is None:
        all_sources = get_sources_config()
        sources = [
            {"name": name, **config}
            for name, config in all_sources.items()
            if config.get("enabled", True) and config.get("docs_url")
        ]
    
    for source in sources:
        result = scrape_documentation(
            name=source["name"],
            docs_url=source["docs_url"],
            max_urls=max_urls_per_source,
        )
        yield result
```

### 3.2 DLT Source Pattern

Sources wrap resources and enable composition:

```python
@dlt.source
def github_repos_source(repos=None, github_token=None):
    """DLT source for GitHub repositories."""
    return github_repos_resource(repos=repos, github_token=github_token)

@dlt.source
def r2_upload_source(cloned_repos):
    """DLT source for R2 uploads."""
    return r2_upload_resource(cloned_repos=cloned_repos)

@dlt.source
def docs_scraper_source(sources=None, max_urls_per_source=50):
    """DLT source for documentation scraping."""
    return docs_scraper_resource(
        sources=sources, 
        max_urls_per_source=max_urls_per_source
    )
```

### 3.3 Write Disposition Pattern

DLT supports different write behaviors:

```python
# Merge (upsert): Update existing records or insert new ones
@dlt.resource(write_disposition="merge", primary_key="full_name")
def mergeable_resource():
    yield data

# Replace: Truncate and reload entire table
pipeline.run(source, write_disposition="replace")

# Append: Only insert new records
pipeline.run(source, write_disposition="append")
```

### 3.4 State Management Pattern

DLT resources can use incremental state:

```python
# Pseudo-pattern from dlt documentation
@dlt.resource
def incremental_resource(
    cursor: dlt.sources.incremental[str] = 
        dlt.sources.incremental("updated_at", initial_value="2024-01-01")
):
    """Resource with incremental loading."""
    # dlt automatically tracks the cursor
    # and restarts from last value on subsequent runs
    yield data
```

**File Location in Examples**: `/home/user/hackathon/data/examples/dlt/notebooks/dlt_sentry.py:70`

---

## 4. Pipeline Patterns

### 4.1 Orchestration Pipeline Pattern

Pipelines combine sources with destinations and configuration:

**Pattern**:
```python
pipeline = dlt.pipeline(
    pipeline_name="my_pipeline",
    destination="duckdb",  # or "postgres", etc.
    dataset_name="my_dataset",
)

load_info = pipeline.run(my_source())
```

**Real Examples** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/dagster_assets.py`):

```python
# GitHub Pipeline
pipeline = dlt.pipeline(
    pipeline_name="github_repos",
    destination=create_duckdb_destination(),
    dataset_name="github_metadata",
)
load_info = pipeline.run(github_repos_source(github_token=get_env("GITHUB_API_KEY")))

# R2 Upload Pipeline
pipeline = dlt.pipeline(
    pipeline_name="r2_uploads",
    destination=create_duckdb_destination(),
    dataset_name="r2_uploads",
)
load_info = pipeline.run(r2_upload_source(cloned_repos=github_repos))

# Documentation Pipeline
pipeline = dlt.pipeline(
    pipeline_name="docs_scraper",
    destination=create_duckdb_destination(),
    dataset_name="docs_metadata",
)
load_info = pipeline.run(docs_scraper_source(max_urls_per_source=50))
```

### 4.2 Dagster Asset Composition Pattern

Dagster assets compose pipelines into DAGs with dependencies:

**Pattern**:
```python
@asset(
    description="...",
    group_name="pipeline_group",
    deps=[upstream_asset],
)
def downstream_asset(context: AssetExecutionContext, upstream_asset: List[Dict]):
    """Asset that depends on upstream."""
    context.log.info(f"Processing {len(upstream_asset)} items")
    
    # Process upstream data
    result = process(upstream_asset)
    
    # Optional: Emit events or metadata
    context.log.info(f"Produced result: {result}")
    
    return result
```

**Real Example - GitHub Pipeline** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/dagster_assets.py:16-44`):

```python
@asset(
    description="Fetch GitHub repository metadata and clone repositories",
    group_name="github_pipeline",
)
def github_repos(context: AssetExecutionContext) -> List[Dict[str, Any]]:
    """Clone configured GitHub repositories."""
    context.log.info("Cloning GitHub repositories...")
    
    cloned_repos = clone_all_repos(github_token=get_env("GITHUB_API_KEY"))
    
    pipeline = dlt.pipeline(
        pipeline_name="github_repos",
        destination=create_duckdb_destination(),
        dataset_name="github_metadata",
    )
    load_info = pipeline.run(github_repos_source(github_token=get_env("GITHUB_API_KEY")))
    
    context.log.info(f"Cloned {len(cloned_repos)} repositories")
    return cloned_repos
```

**Real Example - R2 Upload** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/dagster_assets.py:47-89`):

```python
@asset(
    description="Upload cloned repositories to Cloudflare R2",
    group_name="github_pipeline",
    deps=[github_repos],
)
def r2_uploaded_repos(
    context: AssetExecutionContext,
    github_repos: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Upload cloned repositories to R2."""
    context.log.info(f"Uploading {len(github_repos)} repositories to R2...")
    
    pipeline = dlt.pipeline(
        pipeline_name="r2_uploads",
        destination=create_duckdb_destination(),
        dataset_name="r2_uploads",
    )
    load_info = pipeline.run(r2_upload_source(cloned_repos=github_repos))
    context.log.info(f"Upload complete: {load_info}")
    
    upload_results = []
    for repo in github_repos:
        if repo.get("success"):
            upload_results.append({
                "full_name": repo["full_name"],
                "owner": repo["owner"],
                "repo": repo["repo"],
                "branch": repo["branch"],
                "success": True,
            })
    
    return upload_results
```

### 4.3 Job and Schedule Pattern

Dagster jobs group related assets:

```python
github_pipeline_job = define_asset_job(
    name="github_pipeline",
    selection=["github_repos", "r2_uploaded_repos", "indexed_code"],
    description="Complete GitHub → R2 → CocoIndex pipeline",
)

docs_pipeline_job = define_asset_job(
    name="docs_pipeline",
    selection=["scraped_docs", "r2_uploaded_docs", "knowledge_graphs"],
    description="Complete Docs → R2 → Cognee pipeline",
)

full_pipeline_job = define_asset_job(
    name="full_pipeline",
    selection="*",
    description="Run both GitHub and Docs pipelines",
)

# Scheduling
github_daily_schedule = ScheduleDefinition(
    job=github_pipeline_job,
    cron_schedule="0 2 * * *",  # 2 AM daily
    name="github_daily",
)

docs_weekly_schedule = ScheduleDefinition(
    job=docs_pipeline_job,
    cron_schedule="0 3 * * 0",  # Sundays at 3 AM
    name="docs_weekly",
)
```

**File Location**: `/home/user/hackathon/data-unified/dagster_project/definitions.py`

### 4.4 Multi-Stage Pipeline Pattern

Pipelines typically follow: Extract → Transform → Load (ETL)

**Example - GitHub Code Indexing**:
1. **Extract**: `github_repos` asset - fetches metadata from GitHub API
2. **Transform**: Upload to R2, transform to storage format
3. **Load**: Index with CocoIndex, store vectors in LanceDB

**Example - Documentation Pipeline**:
1. **Extract**: `scraped_docs` - Firecrawl scrapes documentation
2. **Transform**: Generate llms.txt and llms-full.txt files
3. **Load**: Upload to R2, process with Cognee, store in Memgraph

---

## 5. Error Handling

### 5.1 Exception Handling Pattern

The codebase uses consistent exception handling:

**Pattern**:
```python
try:
    # Attempt operation
    result = operation()
    return {"success": True, "result": result}
except SpecificException as e:
    # Log error
    logger.error(f"Specific error: {e}")
    # Return error result
    return {"success": False, "error": str(e)}
except Exception as e:
    # Catch-all for unexpected errors
    logger.error(f"Unexpected error: {e}")
    return {"success": False, "error": str(e)}
```

**Real Examples**:

**GitHub Clone Error Handling** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/clone_repo.py:174-198`):
```python
def clone_all_repos(target_base_dir=None, github_token=None):
    """Clone all configured GitHub repositories."""
    results = []
    
    for repo_config in repos:
        try:
            repo_dir = target_base_dir / f"{owner}_{repo}"
            clone_path = clone_github_repo(owner, repo, branch, repo_dir, github_token)
            
            results.append({
                "full_name": f"{owner}/{repo}",
                "success": True,
                "clone_path": str(clone_path),
            })
        except Exception as e:
            print(f"Error cloning {owner}/{repo}: {e}")
            results.append({
                "full_name": f"{owner}/{repo}",
                "success": False,
                "error": str(e),
            })
    
    return results
```

**R2 Upload Error Handling** (`/home/user/hackathon/data-unified/pipelines/github_to_r2/upload_r2.py:35-108`):
```python
def upload_repo_to_r2(repo_path, owner, repo, branch="main", r2_client=None):
    """Upload a repository to Cloudflare R2."""
    try:
        archive_path = create_repo_archive(repo_path)
        
        object_name = f"repos/{owner}/{repo}/{branch}/archive.tar.gz"
        r2_client.upload_file(file_path=archive_path, object_name=object_name)
        
        return {
            "full_name": f"{owner}/{repo}",
            "success": True,
            "archive_object": object_name,
        }
    except Exception as e:
        return {
            "full_name": f"{owner}/{repo}",
            "error": str(e),
            "success": False,
        }
    finally:
        if archive_path.exists():
            archive_path.unlink()
```

### 5.2 AWS/R2 Exception Handling

```python
class R2Client:
    def upload_file(self, file_path, object_name=None, ...):
        """Upload a file to R2."""
        try:
            self.s3_client.upload_file(str(file_path), bucket, object_name)
            return object_name
        except ClientError as e:
            raise Exception(f"Failed to upload file to R2: {e}")
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/shared/r2_client.py:74-78`

### 5.3 Configuration Error Handling

```python
def get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """Get environment variable with optional default and required check."""
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required environment variable {key} not set")
    return value or ""
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/shared/config.py:13-30`

### 5.4 Firecrawl/OpenAI Error Handling

**Example** (`/home/user/hackathon/data-unified/pipelines/docs_to_knowledge/generate_llmstxt.py:49-77`):

```python
def map_website(self, url: str, limit: int = 100) -> List[str]:
    """Map a website to get all URLs."""
    try:
        response = requests.post(
            f"{self.firecrawl_base_url}/map",
            headers=self.headers,
            json={"url": url, "limit": limit}
        )
        response.raise_for_status()
        
        data = response.json()
        if data.get("success") and data.get("links"):
            return data["links"]
        else:
            logger.error(f"Failed to map website: {data}")
            return []
    except Exception as e:
        logger.error(f"Error mapping website: {e}")
        return []
```

### 5.5 Logging Pattern

The codebase uses Python's standard logging module:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Usage
logger.info("Starting process...")
logger.error("Error occurred: {e}")
logger.debug("Debug information")
```

**File Location**: `/home/user/hackathon/data-unified/pipelines/docs_to_knowledge/generate_llmstxt.py:29-33`

---

## 6. Testing Patterns

### 6.1 Test Structure

Testing examples found in the codebase use pytest:

```python
# From /home/user/hackathon/infrastructure/compose/agno/tests/
import pytest
from conftest import setup_fixtures

@pytest.fixture
def client():
    """Fixture for API client."""
    return create_test_client()

def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
```

### 6.2 Conftest Pattern

Pytest conftest.py for shared fixtures:

```python
# conftest.py
import pytest

@pytest.fixture(scope="session")
def setup_database():
    """Setup database for tests."""
    db = create_test_db()
    yield db
    db.cleanup()

@pytest.fixture
def client(setup_database):
    """Create test client."""
    return create_client(setup_database)
```

**File Location**: `/home/user/hackathon/infrastructure/compose/agno/tests/conftest.py`

### 6.3 Integration Testing Pattern

The codebase suggests integration test patterns for pipelines:

```python
def test_github_pipeline():
    """Test complete GitHub pipeline."""
    # Setup
    repos = [{"owner": "test", "repo": "repo"}]
    
    # Execute
    result = clone_all_repos()
    
    # Assert
    assert result[0]["success"] == True
    assert len(result) > 0

def test_dlt_pipeline():
    """Test DLT pipeline integration."""
    pipeline = dlt.pipeline(
        pipeline_name="test_pipeline",
        destination="duckdb",
    )
    
    load_info = pipeline.run(test_source())
    
    assert load_info.has_successfully_loaded == True
```

---

## 7. Extension Points

### 7.1 Configuration-Driven Extensions

**Pattern**: Load pipelines from configuration files

```yaml
# config/sources.yaml
sources:
  dagster:
    github_url: https://github.com/dagster-io/dagster
    docs_url: https://docs.dagster.io/
    enabled: true
    priority: high
  
  dbt:
    github_url: https://github.com/dbt-labs/dbt-core
    docs_url: https://docs.getdbt.com/
    enabled: true
    priority: high
```

**File Location**: `/home/user/hackathon/data-unified/config/`

### 7.2 Custom Resource Extension

**Pattern**: Create new DLT resources

```python
# In pipelines/custom/my_source.py
@dlt.resource(write_disposition="merge", primary_key="id")
def my_custom_resource(config=None):
    """Custom data source."""
    if config is None:
        config = get_config("custom/my_source")
    
    for item in extract_data(config):
        yield transform(item)

@dlt.source
def my_custom_source(config=None):
    return my_custom_resource(config)
```

### 7.3 Custom Destination Extension

**Pattern**: Create new DLT destination

```python
def create_custom_destination(connection_string):
    """Create custom destination."""
    return dlt.destinations.custom_sql(
        connection_string=connection_string,
        schema_inference=True
    )
```

### 7.4 Custom Dagster Asset Extension

**Pattern**: Add new assets to the pipeline

```python
# In pipelines/custom/dagster_assets.py
from dagster import asset

@asset(
    group_name="custom_pipeline",
)
def my_custom_asset(context: AssetExecutionContext):
    """Custom processing asset."""
    context.log.info("Processing custom data...")
    return result
```

### 7.5 Custom Client Pattern

**Pattern**: Extend R2Client for new storage

```python
class CustomStorageClient:
    """Client for custom storage backend."""
    
    def __init__(self, config):
        self.config = config
        self.client = initialize_client(config)
    
    def upload_file(self, file_path, object_name):
        """Upload file implementation."""
        pass
    
    def download_file(self, object_name, file_path):
        """Download file implementation."""
        pass
```

### 7.6 Data Model Extension

**Pattern**: Extend Pydantic models

```python
# Extend existing models
class CustomDataItem(DataItem):
    """Extended data item with custom fields."""
    custom_field: str
    custom_metadata: Dict[str, Any]

class CustomSourceInfo(SourceInfo):
    """Extended source info."""
    custom_source_type: str
```

### 7.7 Hook/Middleware Pattern

**Pattern**: DLT event hooks (pseudo-pattern)

```python
# Example pattern from dlt capabilities
def on_pipeline_run(context):
    """Hook called before/after pipeline run."""
    logger.info(f"Pipeline running: {context.pipeline_name}")

pipeline.on_before_load(on_pipeline_run)
pipeline.on_load_complete(on_pipeline_run)
```

### 7.8 CLI Command Extension

**Pattern**: Add new CLI commands

```python
# In cli/custom_commands.py
import typer

custom_app = typer.Typer()

@custom_app.command()
def custom_operation(
    param1: str = typer.Argument(..., help="Parameter 1"),
    param2: str = typer.Option("default", help="Parameter 2")
):
    """Custom operation command."""
    console.print(f"Running custom operation: {param1}, {param2}")
    result = execute_operation(param1, param2)
    console.print(f"[green]Success![/green]")

# In cli/main.py
app.add_typer(custom_app, name="custom", help="Custom commands")
```

**File Location**: `/home/user/hackathon/data-unified/cli/main.py:18-21`

### 7.9 Notebook Extension

**Pattern**: Add interactive notebooks

```python
# In notebooks/custom_analysis.py
import marimo

app = marimo.App()

@app.cell
def setup():
    import pandas as pd
    return pd,

@app.cell
def analyze_data(pd):
    """Custom analysis."""
    data = load_data()
    return pd.DataFrame(data)

if __name__ == "__main__":
    app.run()
```

---

## 8. Key Architectural Components

### 8.1 Shared Utilities Layer

**Location**: `/home/user/hackathon/data-unified/pipelines/shared/`

- **config.py**: Environment variable and YAML configuration management
- **dlt_sources.py**: Factory functions for DLT destinations
- **r2_client.py**: Cloudflare R2 S3-compatible client wrapper

### 8.2 Models Layer

**Location**: `/home/user/hackathon/data-unified/models/`

- **classes.py**: Data type definitions (SourceInfo, DataItem, etc.)
- **schemas.py**: Pipeline configuration models (GitHubRepoConfig, etc.)

### 8.3 Pipeline Layers

**Location**: `/home/user/hackathon/data-unified/pipelines/`

```
pipelines/
├── github_to_r2/          # Code indexing pipeline
│   ├── clone_repo.py      # GitHub API & cloning
│   ├── upload_r2.py       # R2 upload logic
│   ├── index_cocoindex.py # CocoIndex integration
│   └── dagster_assets.py  # Orchestration
│
├── docs_to_knowledge/     # Documentation pipeline
│   ├── scrape_docs.py     # Firecrawl scraping
│   ├── generate_llmstxt.py # llms.txt generation
│   ├── upload_r2.py       # R2 upload
│   ├── cognify.py         # Cognee integration
│   └── dagster_assets.py  # Orchestration
│
└── shared/                # Reusable components
    ├── config.py
    ├── dlt_sources.py
    └── r2_client.py
```

### 8.4 Interfaces Layer

**Location**: `/home/user/hackathon/data-unified/`

```
├── cli/                   # Typer CLI interface
│   ├── main.py
│   ├── github_commands.py
│   ├── docs_commands.py
│   └── query_commands.py
│
├── notebooks/            # Marimo interactive notebooks
│   ├── github_pipeline.py
│   ├── docs_pipeline.py
│   └── unified_dashboard.py
│
└── dagster_project/      # Dagster orchestration
    └── definitions.py
```

---

## 9. Summary Table: Design Patterns Used

| Pattern | Purpose | Location | Key Files |
|---------|---------|----------|-----------|
| **Decorator** | Declare resources, sources, assets | DLT & Dagster | clone_repo.py, upload_r2.py, dagster_assets.py |
| **Builder** | Configure complex flows | CodeIndexConfig | index_cocoindex.py |
| **Factory** | Create destinations & clients | Destinations | dlt_sources.py |
| **Repository** | Encapsulate external services | R2Client | r2_client.py |
| **Strategy** | Different processing approaches | Pipelines | github_to_r2/, docs_to_knowledge/ |
| **Iterator** | Yield data items from resources | DLT Resources | github_repos_resource, r2_upload_resource |
| **Composition** | Combine assets into DAGs | Dagster | dagster_assets.py, definitions.py |
| **Configuration** | YAML-driven extensibility | Config management | config.py, sources.yaml |
| **Exception Handler** | Graceful error handling | Error handling | Throughout codebase |

---

## 10. Data Flow Architecture

```
GitHub API ──→ Clone Local ──→ Archive ──→ R2 ──→ CocoIndex ──→ LanceDB
                                              ├──→ PostgreSQL
                                              └──→ DuckDB (metadata)

Documentation URL ──→ Firecrawl ──→ llms.txt ──→ R2 ──→ Cognee ──→ Memgraph
                                      │
                                      └──→ OpenAI (LLM processing)
```

---

## 11. Configuration-Driven Design

The platform is highly configurable through:

1. **Environment Variables** (.env)
2. **YAML Configuration** (config/sources.yaml)
3. **Pydantic Models** (type validation & defaults)
4. **Runtime Parameters** (function arguments)

This allows users to:
- Add new sources by editing YAML
- Change processing parameters via env vars
- Extend models without code changes
- Create new pipelines via composition

---

## 12. Extensibility Summary

### How to Extend

1. **Add New Source**: Create new resource + source in `pipelines/*/`
2. **Add New Destination**: Use `create_*_destination()` factory
3. **Add New Asset**: Define `@asset` in `dagster_assets.py`
4. **Add New CLI Command**: Create command in `cli/` and register in `main.py`
5. **Add New Data Model**: Extend Pydantic models in `models/`
6. **Add New Configuration**: Update YAML in `config/`
7. **Add New Interface**: Create notebook or Typer command

### Key Extension Points

- **DLT Resources**: Reusable data extraction units
- **Dagster Assets**: Composable pipeline units
- **Shared Utilities**: R2Client, Config, DLT factories
- **Data Models**: Type-safe schema definitions
- **CLI Commands**: User-facing operations
- **Notebooks**: Interactive exploration



## Typesafe Pipeline Analysis (BAML/ORPC/MCP)


> Source: `docs/data_engineering/dlt/dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md`

# DLT → BAML → oRPC/OpenAPI: Type-Safe Pipeline Analysis

## Executive Summary

This research analyzes how dlthub's auto-generated schemas can be leveraged with BAML to create a fully type-safe pipeline spanning data ingestion to API/MCP endpoints. The key insight is that **BAML serves as the schema bridge** that generates both Pydantic (Python) and Zod (TypeScript) schemas from a single source of truth, enabling seamless integration across the entire stack.

---

## 1. DLT Schema Generation & Pydantic Integration

### 1.1 How DLT Auto-Generates Schemas

DLT automatically infers schemas during the normalization process:

```python
import dlt

@dlt.resource
def users():
    yield {"id": 1, "name": "Alice", "email": "alice@example.com"}
    yield {"id": 2, "name": "Bob", "email": "bob@example.com"}

# DLT automatically creates schema:
# - id: bigint
# - name: text
# - email: text
```

**Key capabilities:**
- Automatic type inference from Python data structures
- Schema evolution (adding columns, changing types)
- Export to YAML format for inspection/modification
- Incremental loading with state tracking

### 1.2 Current Pydantic Integration (Input Direction)

DLT supports using Pydantic models as schema definitions:

```python
from pydantic import BaseModel
import dlt

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True

@dlt.resource(name="users", columns=User)
def load_users():
    yield {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

**Available functions in `dlt.common.libs.pydantic`:**
- `pydantic_to_table_schema_columns()` - Convert Pydantic model to table schema
- `apply_schema_contract_to_model()` - Configure model for schema evolution modes
- `create_list_model()` - Generate batch validation models
- `validate_and_filter_items()` - Validate data against models

### 1.3 The Export Gap (Schema → Pydantic)

**Current limitation**: DLT does not yet export inferred schemas to Pydantic models.

**2025 Roadmap**: DLT is "experimenting with different ways to represent schemas, ie. instead of yaml we want to offer the option to store dlt schemas as Pydantic models or data classes."

**Workaround strategies:**
1. **BAML as schema source** (recommended) - Define schemas in BAML, generate Pydantic
2. **Manual schema definition** - Define Pydantic models and use with DLT
3. **YAML → Code generation** - Parse exported YAML and generate Pydantic

---

## 2. BAML: The Schema Bridge

### 2.1 What BAML Does

BAML (Boundary AI Markup Language) provides:
- Single source of truth for type definitions
- Code generation for multiple languages (Python, TypeScript, Ruby, Go, Java, C#, Rust)
- Schema-Aligned Parsing (SAP) for robust LLM output parsing
- 60% token efficiency compared to JSON schemas

### 2.2 Schema Definition in BAML

```baml
// baml_src/domain.baml

class DocumentChunk {
  id string                 @description("Unique chunk identifier")
  repo string               @description("Repository name or ID")
  file_path string?         @description("Source file path (if applicable)")
  content string            @description("Text content of the chunk")
  embedding float[]         @description("Embedding vector of the content")
}

class ApiResponse {
  success bool
  data DocumentChunk[]
  error string?
  timestamp datetime
}

enum ProcessingStatus {
  PENDING
  PROCESSING
  COMPLETED
  FAILED
}
```

### 2.3 Generated Pydantic Models

Running `baml-cli generate` produces:

```python
# baml_client/types.py (auto-generated)

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class DocumentChunk(BaseModel):
    id: str
    repo: str
    file_path: Optional[str] = None
    content: str
    embedding: List[float]

class ApiResponse(BaseModel):
    success: bool
    data: List[DocumentChunk]
    error: Optional[str] = None
    timestamp: datetime
```

### 2.4 Generated TypeScript Types

```typescript
// baml_client/types.ts (auto-generated)

export type ProcessingStatus = "PENDING" | "PROCESSING" | "COMPLETED" | "FAILED";

export interface DocumentChunk {
  id: string;
  repo: string;
  file_path?: string;
  content: string;
  embedding: number[];
}

export interface ApiResponse {
  success: boolean;
  data: DocumentChunk[];
  error?: string;
  timestamp: string;
}
```

### 2.5 Generated Zod Schemas

For runtime validation in TypeScript, create Zod schemas from the types:

```typescript
// schemas.ts

import { z } from 'zod';

export const ProcessingStatusSchema = z.enum([
  "PENDING", "PROCESSING", "COMPLETED", "FAILED"
]);

export const DocumentChunkSchema = z.object({
  id: z.string(),
  repo: z.string(),
  file_path: z.string().optional(),
  content: z.string(),
  embedding: z.array(z.number())
});

export const ApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.array(DocumentChunkSchema),
  error: z.string().optional(),
  timestamp: z.string().datetime()
});

// Type inference
export type DocumentChunk = z.infer<typeof DocumentChunkSchema>;
export type ApiResponse = z.infer<typeof ApiResponseSchema>;
```

**Automation options:**
- `pydantic2zod` - Convert Pydantic models to Zod schemas
- Custom BAML generator plugin for Zod
- JSON Schema as intermediate format

---

## 3. oRPC: Type-Safe API Contracts

### 3.1 What oRPC Provides

oRPC is a TypeScript RPC framework with:
- **Contract-first development** - Define API once, generate clients
- **100% type safety** - Shared contracts between server and clients
- **Automatic OpenAPI generation** - First-class OpenAPI 3.1.1 support
- **Schema validation** - Works with Zod, Valibot, ArkType

### 3.2 Contract Definition with Zod

```typescript
// contracts/api.ts

import { oc } from '@orpc/contract';
import { DocumentChunkSchema, ApiResponseSchema } from './schemas';
import { z } from 'zod';

// Query contract
export const searchChunks = oc
  .input(z.object({
    query: z.string(),
    repo: z.string().optional(),
    limit: z.number().default(10)
  }))
  .output(ApiResponseSchema);

// Mutation contract
export const indexRepository = oc
  .input(z.object({
    repo_url: z.string().url(),
    branch: z.string().default('main')
  }))
  .output(z.object({
    job_id: z.string(),
    status: ProcessingStatusSchema
  }));

// Contract bundle
export const contract = oc.router({
  search: searchChunks,
  index: indexRepository
});
```

### 3.3 Server Implementation

```typescript
// server/router.ts

import { os } from '@orpc/server';
import { contract } from '../contracts/api';
import { searchMemory, startIndexJob } from './services';

export const router = os.contract(contract).router({
  search: os.search.handler(async ({ input }) => {
    const chunks = await searchMemory(input.query, input.repo, input.limit);
    return {
      success: true,
      data: chunks,
      timestamp: new Date().toISOString()
    };
  }),

  index: os.index.handler(async ({ input }) => {
    const job = await startIndexJob(input.repo_url, input.branch);
    return {
      job_id: job.id,
      status: job.status
    };
  })
});
```

### 3.4 OpenAPI Generation

```typescript
// server/openapi.ts

import { OpenAPIGenerator } from '@orpc/openapi';
import { ZodToJsonSchemaConverter } from '@orpc/zod';
import { router } from './router';

const generator = new OpenAPIGenerator({
  schemaConverters: [new ZodToJsonSchemaConverter()]
});

export const openApiSpec = await generator.generate(router, {
  info: {
    title: 'Document Chunk API',
    version: '1.0.0',
    description: 'Type-safe API for document indexing and search'
  },
  servers: [
    { url: 'https://api.example.com', description: 'Production' }
  ]
});
```

### 3.5 Type-Safe Client

```typescript
// client/api.ts

import { createORPCClient } from '@orpc/client';
import { createORPCReactQueryUtils } from '@orpc/tanstack-query';
import { contract } from '../contracts/api';

// Create typed client
const client = createORPCClient<typeof contract>({
  baseURL: 'https://api.example.com'
});

// TanStack Query integration
export const orpc = createORPCReactQueryUtils(client);

// Usage in React component
function SearchComponent() {
  const { data, isLoading } = orpc.search.useQuery({
    input: { query: 'authentication', limit: 5 }
  });

  // data is fully typed as ApiResponse
  return (
    <div>
      {data?.data.map(chunk => (
        <div key={chunk.id}>{chunk.content}</div>
      ))}
    </div>
  );
}
```

---

## 4. MCP: Type-Safe Tool Endpoints

### 4.1 MCP Protocol Overview

Model Context Protocol (MCP) provides:
- Standardized way for AI agents to access external tools
- Three primitives: Resources (GET), Tools (POST), Prompts (templates)
- JSON-RPC 2.0 protocol
- Multiple transports: stdio, HTTP, SSE, WebSocket

### 4.2 Pydantic AI + MCP Integration

```python
# mcp_server/tools.py

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel
from baml_client.types import DocumentChunk, ApiResponse

# Type-safe tool input/output with Pydantic
class SearchInput(BaseModel):
    query: str
    repo: str | None = None
    limit: int = 10

server = Server("document-search")

@server.tool()
async def search_chunks(input: SearchInput) -> list[DocumentChunk]:
    """Search for document chunks matching the query."""
    # Pydantic validates input automatically
    results = await perform_search(input.query, input.repo, input.limit)
    # Return type is validated against DocumentChunk schema
    return results

@server.tool()
async def get_chunk_by_id(chunk_id: str) -> DocumentChunk | None:
    """Retrieve a specific document chunk by ID."""
    return await fetch_chunk(chunk_id)
```

### 4.3 Exposing oRPC Endpoints as MCP Tools

```python
# mcp_server/orpc_bridge.py

from mcp.server import Server
from pydantic import BaseModel
import httpx

# Mirror oRPC contracts as MCP tools
class SearchRequest(BaseModel):
    query: str
    repo: str | None = None
    limit: int = 10

class IndexRequest(BaseModel):
    repo_url: str
    branch: str = "main"

server = Server("orpc-bridge")

@server.tool()
async def api_search(request: SearchRequest):
    """Search documents via oRPC API (type-safe)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/search",
            json=request.model_dump()
        )
        # Response validated against ApiResponse schema
        return ApiResponse.model_validate(response.json())

@server.tool()
async def api_index(request: IndexRequest):
    """Index a repository via oRPC API (type-safe)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/index",
            json=request.model_dump()
        )
        return response.json()
```

### 4.4 TypeScript MCP Server with Zod

```typescript
// mcp-server/tools.ts

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DocumentChunkSchema } from './schemas';
import { z } from 'zod';

const server = new McpServer({
  name: 'document-search',
  version: '1.0.0'
});

// Define tool with Zod schema validation
server.tool(
  'search_chunks',
  z.object({
    query: z.string(),
    repo: z.string().optional(),
    limit: z.number().default(10)
  }),
  async (input) => {
    const results = await performSearch(input.query, input.repo, input.limit);
    // Validate output
    const validated = z.array(DocumentChunkSchema).parse(results);
    return { content: [{ type: 'text', text: JSON.stringify(validated) }] };
  }
);
```

---

## 5. Complete Type-Safe Pipeline Architecture

### 5.1 Schema Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BAML Schema Definitions                   │
│                   (Single Source of Truth)                   │
│                                                              │
│   class DocumentChunk { id: string, content: string, ... }   │
└────────────────────────┬────────────────────────────────────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
              ▼          │          ▼
     ┌────────────┐      │      ┌────────────┐
     │  Pydantic  │      │      │ TypeScript │
     │   Models   │      │      │   Types    │
     └─────┬──────┘      │      └─────┬──────┘
           │             │            │
     ┌─────▼──────┐      │      ┌─────▼──────┐
     │    DLT     │      │      │    Zod     │
     │  Pipeline  │      │      │  Schemas   │
     └─────┬──────┘      │      └─────┬──────┘
           │             │            │
           │             │      ┌─────▼──────┐
           │             │      │   oRPC     │
           │             │      │ Contracts  │
           │             │      └─────┬──────┘
           │             │            │
     ┌─────▼─────────────┼────────────▼──────┐
     │           Shared Data Layer            │
     │   (Database, Vector Store, Graph)      │
     └─────┬─────────────┬────────────┬──────┘
           │             │            │
           ▼             ▼            ▼
     ┌──────────┐  ┌──────────┐  ┌──────────┐
     │   MCP    │  │ OpenAPI  │  │  Client  │
     │  Tools   │  │   Spec   │  │   SDK    │
     └──────────┘  └──────────┘  └──────────┘
```

### 5.2 Data Flow Example

**Step 1: Define Schema in BAML**
```baml
class CodeSnippet {
  id string
  repo string
  file_path string
  language string
  content string
  embedding float[]
  created_at datetime
}
```

**Step 2: Use Pydantic in DLT Pipeline**
```python
from baml_client.types import CodeSnippet
import dlt

@dlt.resource(columns=CodeSnippet)
def extract_code_snippets(repo_path: str):
    for file in scan_repository(repo_path):
        snippet = CodeSnippet(
            id=generate_id(file),
            repo=repo_path,
            file_path=file.path,
            language=detect_language(file),
            content=file.content,
            embedding=embed(file.content),
            created_at=datetime.now()
        )
        yield snippet.model_dump()
```

**Step 3: Define oRPC Contract with Zod**
```typescript
import { CodeSnippetSchema } from './schemas';

export const getSnippets = oc
  .input(z.object({ repo: z.string(), language: z.string().optional() }))
  .output(z.array(CodeSnippetSchema));
```

**Step 4: Expose as MCP Tool**
```python
@server.tool()
async def search_code(query: str, language: str = None) -> list[CodeSnippet]:
    """Search code snippets with semantic similarity."""
    return await vector_search(query, language)
```

### 5.3 Type Safety Benefits

| Layer | Validation Type | Technology |
|-------|----------------|------------|
| ETL Input | Runtime | DLT + Pydantic |
| LLM Output | Runtime + Parse | BAML SAP |
| API Request | Runtime | Zod + oRPC |
| API Response | Runtime | Zod + oRPC |
| Client Call | Compile-time | TypeScript + oRPC |
| MCP Tool | Runtime | Pydantic/Zod |

---

## 6. Implementation Strategy

### 6.1 Recommended Approach

1. **Start with BAML** - Define all domain types in `.baml` files
2. **Generate code** - Run `baml-cli generate` for both Python and TypeScript
3. **Create Zod schemas** - Use `pydantic2zod` or manual definition
4. **Define oRPC contracts** - Use Zod schemas for input/output
5. **Implement servers** - Both API (oRPC) and MCP tools
6. **Generate OpenAPI** - For external integrations and documentation

### 6.2 Build Pipeline

```yaml
# .github/workflows/schema-sync.yml

name: Schema Synchronization

on:
  push:
    paths:
      - 'baml_src/**/*.baml'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Generate Python/TS from BAML
        run: baml-cli generate

      - name: Generate Zod from Pydantic
        run: python scripts/pydantic_to_zod.py

      - name: Generate OpenAPI from oRPC
        run: npm run generate:openapi

      - name: Type check
        run: |
          mypy baml_client/
          npx tsc --noEmit

      - name: Commit generated code
        run: |
          git add baml_client/ src/schemas/
          git commit -m "chore: regenerate schemas from BAML"
```

### 6.3 Version Control Strategy

```baml
// Include version in schemas for evolution tracking
class CodeSnippet {
  _schema_version int = 2  // Increment on breaking changes
  id string
  // ... fields
}
```

---

## 7. Current Limitations & Workarounds

### 7.1 DLT Schema Export Gap

**Problem**: DLT doesn't export inferred schemas to Pydantic yet.

**Workarounds**:
1. Define schemas in BAML first, then use with DLT
2. Export DLT schema to YAML, convert to Pydantic manually
3. Use `datamodel-code-generator` to convert JSON Schema to Pydantic

### 7.2 BAML → Zod Generation

**Problem**: BAML doesn't directly generate Zod schemas.

**Solutions**:
1. Use `pydantic2zod` on generated Pydantic models
2. Use JSON Schema as intermediate format
3. Write custom BAML generator plugin

### 7.3 oRPC SSL Issues

**Problem**: Some oRPC documentation endpoints have SSL issues.

**Solution**: Use npm packages directly and community examples.

---

## 8. Production Considerations

### 8.1 Error Handling

```typescript
// Graceful validation errors
const result = ApiResponseSchema.safeParse(data);
if (!result.success) {
  logger.error('Schema validation failed', {
    errors: result.error.issues,
    data
  });
  throw new ValidationError(result.error);
}
```

### 8.2 Performance

- **Pydantic v2** - Rust-based validation, 5-50x faster than v1
- **Zod** - Efficient parsing with early termination
- **oRPC** - Lightweight, works on edge runtimes

### 8.3 Monitoring

```python
# Track schema validation failures
@metrics.counter("schema_validation_errors")
def validate_chunk(data: dict) -> DocumentChunk:
    try:
        return DocumentChunk.model_validate(data)
    except ValidationError as e:
        metrics.increment("schema_validation_errors", tags={"type": "DocumentChunk"})
        raise
```

---

## 9. Conclusion

The combination of **DLT + BAML + oRPC + MCP** creates a powerful type-safe pipeline:

1. **BAML** serves as the single source of truth for schemas
2. **Pydantic** provides runtime validation in Python (DLT, MCP tools)
3. **Zod** provides runtime validation in TypeScript (oRPC, MCP servers)
4. **oRPC** generates OpenAPI specs automatically from contracts
5. **MCP** exposes tools with type-safe inputs/outputs

This architecture ensures that data flowing from ingestion (DLT) through processing to APIs and AI tools maintains type consistency at every boundary, catching errors early and improving developer experience through IDE autocompletion and compile-time checks.

---

## References

- [DLT Documentation - Schema](https://dlthub.com/docs/general-usage/schema)
- [DLT Pydantic Integration](https://dlthub.com/docs/api_reference/dlt/common/libs/pydantic)
- [BAML Documentation](https://docs.boundaryml.com)
- [oRPC Documentation](https://orpc.unnoq.com/docs)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Pydantic AI MCP Guide](https://ai.pydantic.dev/mcp/overview/)
- [pydantic2zod](https://github.com/argyle-engineering/pydantic2zod)


## Small Data SF 2025 Patterns


> Source: `docs/data_engineering/dlt/small-data-sf-2025/README.md`

# Keep It Simple and Scalable

> This repository hosts the material for a workshop given at [Small Data SF 2025]([https://www.smalldatasf.com/](https://www.smalldatasf.com/#agenda-hands-on-workshops-keep-it-simple-and-scalable-pythonic-extract-load-transform-elt-using-dlthub)).

During this workshop, you will use the Python library [dlt](https://github.com/dlt-hub/dlt) to build an extract, load, transform (ELT) pipeline for the [official GitHub REST API](https://docs.github.com/en/rest?apiVersion=2022-11-28).

We'll go through the full lifecyle of a data project:
1. Load data from a REST API
2. Ensure data quality via manual exploration and checks
3. Transform raw data into clean data and metrics 
4. Build a data product (e.g., report, web app)
5. Deploy the pipeline and data product

We'll introduce and suggest several tools throughout the workshop: dlt, [LLM scaffolding](https://dlthub.com/workspace), [Continue](https://github.com/continuedev/continue), [duckdb](https://github.com/duckdb/duckdb), [Motherduck](https://motherduck.com/), [marimo](https://github.com/marimo-team/marimo/tree/main), [ibis](https://github.com/ibis-project/ibis), and more!

## Workshop format

This workshop will alternate between:
- **Tutorial**: speakers explain and demonstrate concepts
- **Exercise**: participants code to solve a task

Most exercises are open-ended and participants are invited to explore their own path (e.g., ingest data from different endpoints). It's also possible to follow along the speaker during exercise segments.

To avoid getting stuck, this repository includes several checkpoints to resume from.

## Repository structure

All of the workshop material is in this repository. A brief overview:

- `README.md` contains all of the written instructions for the workshop. See the `## Setup` section for installation instructions 
- `pyproject.toml` and `uv.lock` define Python dependencies
- `.continue/` contains MCP configuration for the Continue IDE extension
- `.cursor/` contains MCP configuration for the Cursor IDE
- `.vscode/` contains MCP configuration for the GitHub Copilot extension


## Setup
1. Start by cloning this repository on your local machine

  ```shell
  git clone https://github.com/dlt-hub/small-data-sf-2025
  ```

2. Move to the repository directory

  ```shell
  cd small-data-sf-2025
  ```

### Python environment
1. Create a virtual Python environment and active it

    ```shell
    # on Linux & MacOS
    python -m venv .venv && .venv/bin/activate
    ```

    ```shell
    # on Windows
    python -m venv .venv && .venv/Scripts/activate
    ```

2. Install Python dependencies

    ```shell
    pip install -r requirements.txt
    ```

### dltHub
During the workshop, we will use the Python library [dlt](https://github.com/dlt-hub/dlt). It is open source and under the Apache 2.0 license. We will also use the Python library dlthub, which includes paid features. A 30-day trial license can be self-issued anonymously for development, education, and CI operations purposes.

0. Setup the Python environment, which includes `dlt` and `dlthub`
1. Self-issue a license for `dlthub` and the specified features: 
  ```shell
  dlt license issue dlthub.transformation
  ```
2. It should automatically store the token. If it prints a warning, follow the instructions.
3. Verify the token is properly set: `dlt license info`. The result should look like
   ```shell
   Searching dlt license in environment or secrets toml
   License found

   License Id: 736xxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxx
   Licensee: machine:4366xxxxxxxxxxxxxxxxxxxxxxxxxxxx
   Issuer: dltHub Inc.
   License Type: self-issued-trial
   Issued: 2025-11-xx xx:xx:xx
   Scopes: dlthub.transformation
   Valid Until: 2025-12-xx xx:xx:xx
   ```

### GitHub REST API
The workshop will focus on using public data from the official [GitHub REST API](https://docs.github.com/en/rest?apiVersion=2022-11-28). The REST API is free to use, but you need a GitHub token to make requests to most endpoints.

1. Login on GitHub
2. Go to [https://github.com/settings/apps](https://github.com/settings/apps)
3. Select `Personal access tokens > Tokens (classic)`
4. Click `Generate new token > Generate new token (classic)`
5. Set a `note`. You don't need to select any `scope`.
6. Click `Generate token`
7. Store the token value securely. We will add it to `.dlt/secrets.toml` during the workshop.

References:
- [Authenticating with a personal token](https://docs.github.com/en/rest/authentication/authenticating-to-the-rest-api?apiVersion=2022-11-28#authenticating-with-a-personal-access-token)

### Motherduck
The vast majority of the workshop will be happening on your local machine. We'll be using [Motherduck](https://motherduck.com/) during the later steps to show how to go from local development to production. You can signup via email, Google, or GitHub. The free tier is sufficient for the workshop (you might receive a free business trial on first signup).

1. Login / signup to Motherduck [https://app.motherduck.com/](https://app.motherduck.com/)
2. (on signup) Go through onboarding flow. Look out for the `Skip` button.
3. Go to [https://app.motherduck.com/settings/tokens](https://app.motherduck.com/settings/tokens)
4. Click `Create token` to generate a `Read/Write Token`
5. Store the token value securely. We will add it to `.dlt/secrets.toml` during the workshop.

### Continue
During the workshop, we will use the [VSCode](https://code.visualstudio.com/) extension [Continue](https://github.com/continuedev/continue) to build data pipelines using `dlt`, LLMs, and MCP servers. It is open source and under the Apache 2.0 license. You will need an LLM API key to use it (OpenAI, Anthropic, Mistral, etc.). Using self-hosted LLMs is also possible.

> Note. If you already have a subscription with Cursor, Copilot, Windsurf, etc., you will be able to follow along with these tools. The interface and configuration will differ slightly though.

1. Install VSCode [https://code.visualstudio.com/](https://code.visualstudio.com/)
2. Inside VSCode, go to the `Extensions` tab
3. Search for `continue` and install the extension (by `continue.dev`, identifier is `continue.continue`)
4. Go to the Continue chat panel. You can find it by doing `CTRL + P` (command palette) and execute `Continue: Focus Continue Chat`
5. Under `Models`, set your LLM API key. We suggest select models X or Y `TODO complete steps`
6. Under `Tools`, you should see the MCP server loaded with some tools if you properly setup your Python environment.


> Source: `docs/data_engineering/dlt/small-data-sf-2025/1_basics/README.md`

# 1. Basics: ELT and dlt


## Directory content
- `1_rest_api_pipeline.py` A script that shows a typical `dlt` pipeline to load data from a REST API. It will load Jaffleshop data from our REST API and ingest it in a local duckdb. Run it via:

    ```shell
    python 1_rest_api_pipeline.py
    ```

- `2_files_pipeline.py` A script that shows a typical `dlt` pipeline to load data from an object store / filesystem. It will load Jaffleshop data from a local file (found in `./data` and ingest it in a local duckdb (the same where REST API data was loaded). Run it via:

    ```shell
    python 2_files_pipeline.py
    ```

- `3_jaffleshop_notebook.py` A notebook tutorial showing the full ELT life cycle and some convenience method for interactive development. Run it via

    ```shell
    marimo edit 3_jaffleshop_notebook.py
    ```

## GitHub API Source Pattern


> Source: `docs/data_engineering/dlt/github_api_init/EXECUTIVE_SUMMARY.md`

# github_api_init: Executive Summary

## What You Have

A **production-ready template** for building REST API data pipelines using dlt's REST API framework. This demonstrates dlt's best practice for declarative, configuration-driven API connectors.

## The Three Core Files

### 1. **github-docs.yaml** (The API Specification)
- 32 GitHub REST API endpoints fully defined
- Declarative YAML format (not code)
- Includes client config, auth, pagination, and error handling
- Can be auto-generated from OpenAPI specs

**Key sections:**
```yaml
client:                    # Global HTTP client settings
  base_url: https://api.github.com
  auth: { type: apikey, location: header }
  paginator: { type: page, per_page: 30 }

resources: [...]          # Individual endpoint definitions
```

### 2. **github_pipeline.py** (The Executor)
- Minimal template showing dlt pattern
- Uses `@dlt.source` decorator
- Calls `rest_api_resources()` with config
- Injects secrets via function parameters

**Pattern:**
```python
@dlt.source
def github_source(access_token=dlt.secrets.value):
    config = { "client": {...}, "resources": [...] }
    yield from rest_api_resources(config)

pipeline = dlt.pipeline(...).run(github_source())
```

### 3. **.dlt/** Configuration Directory
- `secrets.toml` - Credential templates (not committed)
- `config.toml` - Runtime settings (logging, telemetry)
- `.sources` - Version tracking metadata

## 32 Endpoints Categories

| Category | Count | Examples |
|----------|-------|----------|
| Organization/User | 4 | organizations, users, teams, repositories |
| Repository Metadata | 6 | assignees, branches, labels, tags, workflows |
| Issues | 6 | issues, events, milestones, comments, reactions |
| Pull Requests | 6 | pulls, commits, reviews, comments, reactions |
| Commits & Code | 3 | commits, comments, reactions |
| Releases | 2 | releases, deployments |
| Activity | 2 | events, stargazers |
| Projects | 3 | projects, columns, cards |
| CI/CD | 2 | workflow_runs, workflow_jobs |

## Key Architectural Decisions

### 1. **Declarative Over Imperative**
- Configuration in YAML, not Python code
- Non-developers can understand/modify endpoints
- AI-friendly for code generation

### 2. **Authentication Security**
- Never hardcode credentials
- Secrets injected via `dlt.secrets.value`
- Per-environment configuration via `.dlt/secrets.toml`

### 3. **Pagination Handled Automatically**
```yaml
paginator:
  type: page           # Handles page-based pagination
  page_size_param: per_page
  default_page_size: 30
```
Framework manages iteration, no manual pagination code.

### 4. **Data Extraction via JSONPath**
```yaml
data_selector: results    # Unwraps nested response data
```
Framework extracts data from any response structure.

### 5. **Minimal Code Boilerplate**
- Rest API framework handles pagination, errors, retries
- Developer only defines config, not implementation
- Single entry point: `github_pipeline.py`

## Pagination Support

The framework automatically handles 6 pagination types:

1. **Page-based** - `/endpoint?page=1&per_page=30`
2. **Offset-based** - `/endpoint?offset=0&limit=100`
3. **Cursor-based** - `/endpoint?after=cursor_token`
4. **Link headers** - HTTP `Link` header with rel="next"
5. **JSON links** - Response contains `pagination.next` URL
6. **Single page** - No pagination needed

Per-endpoint override possible if API uses different strategies.

## Incremental Loading (Delta Sync)

```yaml
incremental:
  cursor_path: updated_at        # Which field tracks state
  start_param: since             # Query param name
  initial_value: "2023-01-01T00:00:00Z"
```

Framework tracks last state and only fetches new data.

## Authentication Types

```yaml
auth:
  type: apikey        # API Key
  type: bearer        # Bearer Token
  type: basic         # Basic Auth
  type: oauth2        # OAuth2
  type: apikey_with_location_in_query  # etc.
```

## Comparison: REST API vs. Verified Source

| Feature | REST API (github_api_init) | Verified Source (github_source_init) |
|---------|---------------------------|--------------------------------------|
| **Configuration** | YAML | Python code |
| **Learning curve** | Easy | Moderate |
| **Build time** | 1 hour | Days/weeks |
| **Customization** | Medium | High |
| **AI-friendly** | Excellent | Difficult |
| **Endpoints** | 32 generic REST | 2-3 specialized |
| **Use case** | Quick prototypes, any REST API | Complex, production sources |

## How It Represents dlt Best Practices

1. **Configuration-Driven Architecture**
   - Endpoints defined in machine/human-readable YAML
   - Easy to modify without touching Python code

2. **Security by Design**
   - Credentials never in code
   - Environment-based secrets management
   - Type-safe credential injection

3. **Framework Maturity**
   - Rest API framework handles pagination, errors, retries
   - Developer focuses on what data to extract, not how

4. **Scalability**
   - Supports multiple APIs (different endpoints, paginators)
   - Handles rate limiting and backoff
   - State management for incremental loads

5. **AI/Code Generation Potential**
   - YAML format enables automatic source generation from OpenAPI specs
   - Non-code approach reduces hallucination risk
   - Clear schema for MCP integration

6. **Documentation & Discovery**
   - All endpoints visible in single YAML file
   - No need to read Python to understand available data
   - github-docs.yaml is both config and documentation

## Production Readiness

**Out of the box:**
- Full pagination support
- Error handling and retries
- Rate limit handling
- Schema inference
- Incremental loading
- Data type detection

**What you need to add:**
- Configure actual API credentials
- Test with your specific API
- Monitor data quality
- Set up monitoring/alerting

## Extension Pattern

To add a new API:

1. **Copy template** - `cp -r github_api_init my_api_init`
2. **Extract endpoints** - Read API docs, identify REST endpoints
3. **Update github-docs.yaml**:
   - Change `source_name`
   - Update `client.base_url`, `auth` settings
   - List all endpoints in `resources`
   - Add `data_selector` for each endpoint
4. **Update github_pipeline.py** - Change source name/config
5. **Configure secrets** - Update `.dlt/secrets.toml`
6. **Run** - `python github_pipeline.py`

## Integration Points

**With dlt CLI:**
```bash
dlt init github duckdb           # Creates this structure
dlt pipeline github_data show    # Inspect loaded data
```

**With Destinations:**
Can load to DuckDB, Postgres, BigQuery, Snowflake, Delta Lake, etc.

**With Orchestration:**
Wrap in Dagster/Airflow assets or use dlt Cloud.

**With AI/MCP:**
YAML structure enables automatic integration with AI systems for source generation.

## Files Added for This Research

1. **RESEARCH_ANALYSIS.md** - Comprehensive technical breakdown
2. **COMPARISON_WITH_SOURCE_INIT.md** - Detailed REST API vs. Verified Source comparison
3. **QUICK_REFERENCE.md** - Copy-paste-ready examples and checklists
4. **This file** - Executive summary and key takeaways

## Key Takeaways

1. **Declarative approach** is the future of API data loading
2. **Configuration over code** reduces errors and increases auditability
3. **Framework handles complexity** (pagination, auth, retries, state)
4. **AI-friendly format** enables automatic source generation
5. **Production-ready** with zero custom code required for basic use
6. **Extensible** to any REST API without major changes

## Next Steps for Using This

1. **Study github-docs.yaml** - Understand endpoint structure
2. **Review github_pipeline.py** - See minimal code pattern
3. **Read QUICK_REFERENCE.md** - Copy examples
4. **Run with your API** - Replace endpoints and test
5. **Scale to production** - Add monitoring, error handling

## Related Files in This Directory

- **CLAUDE.md / AGENT.md** - Comprehensive AI coding rules for REST APIs (40KB each)
- **requirements.txt** - Just `dlt[duckdb]>=1.18.2`
- **dlt.yaml** - Empty project marker
- **.dlt/config.toml** - Runtime settings
- **.dlt/secrets.toml** - Credential template
- **.dlt/.sources** - Source versioning

## Absolute Paths

- Configuration: `/Users/cliste/dev/bonneagar/hackathon/data/examples/dlt/github_api_init/`
- Analysis docs: Same directory
- GitHub REST API: https://docs.github.com/en/rest
- dlt Documentation: https://dlthub.com/docs

---

**Status:** Research complete. Three analysis documents created. Ready for implementation/integration.


> Source: `docs/data_engineering/dlt/github_api_init/README_RESEARCH.md`

# github_api_init Research Documentation

This directory has been thoroughly analyzed and documented. This README guides you through the research materials.

## Start Here

### For Quick Understanding
1. **EXECUTIVE_SUMMARY.md** (5 min read)
   - What this directory contains
   - Key architectural decisions
   - 32 endpoints overview
   - Production readiness status

### For Hands-On Implementation  
2. **QUICK_REFERENCE.md** (10 min + copy-paste)
   - File manifest and purposes
   - Configuration structure with examples
   - Copy-paste code snippets
   - Common issues and solutions
   - Verification checklist

### For Deep Technical Understanding
3. **RESEARCH_ANALYSIS.md** (20 min read)
   - Complete directory structure breakdown
   - All files explained in detail
   - github-docs.yaml endpoints categorized
   - REST API framework features
   - Integration points with dlt stack

### For Comparison & Decision Making
4. **COMPARISON_WITH_SOURCE_INIT.md** (15 min read)
   - Side-by-side REST API vs. Verified Source
   - When to use each approach
   - Code generation potential
   - Architecture differences illustrated with examples

## File Organization

```
github_api_init/
│
├─ ORIGINAL FILES (from dlt init)
│  ├── github-docs.yaml           # 32 GitHub REST endpoints
│  ├── github_pipeline.py         # Minimal template
│  ├── requirements.txt           # dlt[duckdb]>=1.18.2
│  ├── dlt.yaml                  # Project config
│  ├── CLAUDE.md / AGENT.md      # AI coding rules (40KB)
│  └── .dlt/
│      ├── config.toml           # Runtime settings
│      ├── secrets.toml          # Credential templates
│      └── .sources              # Version tracking
│
└─ RESEARCH DOCUMENTATION (Added)
   ├── README_RESEARCH.md         # This file
   ├── EXECUTIVE_SUMMARY.md       # Executive overview
   ├── RESEARCH_ANALYSIS.md       # Technical deep dive
   ├── COMPARISON_WITH_SOURCE_INIT.md  # Architecture comparison
   └── QUICK_REFERENCE.md         # Implementation guide
```

## Key Findings

### 1. Architecture Pattern
- **Type:** Declarative configuration-driven API connector
- **Framework:** dlt REST API source with automatic pagination
- **Configuration:** YAML-based endpoint definitions
- **Security:** Secret injection via `.dlt/secrets.toml`

### 2. Pagination Support
Handles all 6 major pagination strategies:
- Page-based (GitHub uses this)
- Offset-based
- Cursor-based
- Link header-based
- JSON link-based
- Single page

### 3. Endpoints (32 total)
Organized in 9 categories:
- Organization/User (4)
- Repository Metadata (6)
- Issues (6)
- Pull Requests (6)
- Commits (3)
- Releases/Deployments (2)
- Events/Activity (2)
- Projects (3)
- CI/CD (2)

### 4. Best Practices Demonstrated
1. Configuration over code
2. Security by design
3. Automatic pagination handling
4. JSONPath-based data extraction
5. Incremental loading support
6. State management via framework
7. Error handling and retries built-in
8. Schema inference automatic

### 5. Comparison to Alternatives
- **vs. Verified Source:** Configuration-driven (easy) vs. code-driven (powerful)
- **vs. Manual pipelines:** Framework handles complexity vs. you code everything
- **vs. Low-code tools:** Production Python vs. UI-based configuration

## Document Navigation

### By Use Case

**"I want to use github_api_init for my project"**
→ Read: QUICK_REFERENCE.md

**"I'm deciding between REST API and Verified Source"**
→ Read: COMPARISON_WITH_SOURCE_INIT.md

**"I need to understand the full architecture"**
→ Read: RESEARCH_ANALYSIS.md

**"I want the executive summary for a meeting"**
→ Read: EXECUTIVE_SUMMARY.md

**"I want to understand dlt best practices"**
→ Read: RESEARCH_ANALYSIS.md + EXECUTIVE_SUMMARY.md

**"I'm implementing AI/LLM integration for source generation"**
→ Read: QUICK_REFERENCE.md + COMPARISON_WITH_SOURCE_INIT.md (section on AI-friendliness)

## Content Map

### EXECUTIVE_SUMMARY.md
- What you have
- Three core files
- 32 endpoints by category
- Key architectural decisions
- Pagination support overview
- Comparison table
- Production readiness
- Extension pattern
- Integration points

### RESEARCH_ANALYSIS.md
- Complete directory structure
- All files explained
- github-docs.yaml complete content breakdown
- github_pipeline.py pattern explanation
- .dlt/ configuration details
- Requirements and dependencies
- CLAUDE.md guidelines overview
- Architectural differences (API Init vs. Source Init)
- Best practices reflected
- REST API framework features
- How to use template
- Relationship to OpenAPI/Swagger
- Integration points

### COMPARISON_WITH_SOURCE_INIT.md
- Side-by-side comparison (10 dimensions)
- Approach differences
- Dependencies & setup
- Configuration files layout
- Endpoint discovery method
- Pagination handling
- Authentication patterns
- Incremental loading approach
- Write disposition & schema
- Data extraction
- Table generation
- When to use each
- Endpoints coverage
- Code generation potential
- Example code comparison
- Summary comparison table

### QUICK_REFERENCE.md
- File manifest (table)
- Configuration structure (YAML template)
- Pagination types (6 examples)
- Authentication types (4 examples)
- Data selector JSONPath examples
- Pipeline execution pattern (full code)
- Secrets configuration
- 32 endpoints by category
- Incremental loading setup (2 examples)
- Common issues & solutions table
- Best practices (10 items)
- Resource defaults example
- Integration examples (dlt CLI, destinations, orchestration)
- Files to modify for custom API
- Verification checklist
- Resources (links)

## Original Files (Not Modified)

All original files from `dlt init github duckdb` remain unchanged:

1. **github-docs.yaml** - 32 GitHub REST endpoints in declarative YAML
2. **github_pipeline.py** - Minimal template showing dlt pattern
3. **requirements.txt** - `dlt[duckdb]>=1.18.2`
4. **dlt.yaml** - Empty project marker
5. **CLAUDE.md** - 40KB AI coding guidelines
6. **AGENT.md** - Same as CLAUDE.md
7. **.dlt/config.toml** - Runtime configuration template
8. **.dlt/secrets.toml** - Credential templates
9. **.dlt/.sources** - Version tracking metadata
10. **.gitignore** - Standard dlt gitignore

## How to Use This Research

### Immediate Use
1. Copy QUICK_REFERENCE.md snippets into your project
2. Modify github-docs.yaml for your API
3. Update secrets.toml with real credentials
4. Run python github_pipeline.py

### Understanding
1. Read EXECUTIVE_SUMMARY.md (overview)
2. Skim RESEARCH_ANALYSIS.md (details)
3. Keep QUICK_REFERENCE.md handy (implementation)
4. Refer to COMPARISON_WITH_SOURCE_INIT.md when making architecture decisions

### Sharing
1. Send EXECUTIVE_SUMMARY.md to stakeholders (decision makers)
2. Share QUICK_REFERENCE.md with implementers (developers)
3. Reference RESEARCH_ANALYSIS.md for technical deep dives
4. Use COMPARISON_WITH_SOURCE_INIT.md for architecture discussions

## Research Methodology

- **Source:** Direct examination of /Users/cliste/dev/bonneagar/hackathon/data/examples/dlt/github_api_init/
- **Scope:** Complete directory analysis including all files and configurations
- **Depth:** From high-level architecture to implementation details
- **Comparison:** Contrasted with github_source_init (verified source approach)
- **Organization:** Four documents targeting different audiences/use cases

## Key Takeaways

1. **Declarative configuration** is modern data loading best practice
2. **REST API framework** eliminates boilerplate for common patterns
3. **YAML-based endpoints** are AI-friendly and maintainable
4. **Security by design** with secret injection patterns
5. **Production-ready** - handles pagination, errors, retries automatically
6. **Extensible** - easy to adapt to any REST API
7. **Well-documented** - both in code and in these research documents

## Document Statistics

- EXECUTIVE_SUMMARY.md: ~350 lines, 8.3 KB
- RESEARCH_ANALYSIS.md: ~600 lines, 12 KB
- COMPARISON_WITH_SOURCE_INIT.md: ~450 lines, 12 KB
- QUICK_REFERENCE.md: ~350 lines, 9.7 KB
- **Total research documentation: ~1,750 lines, 42 KB**

Plus original files:
- CLAUDE.md/AGENT.md: 40 KB each (comprehensive AI guidelines)
- github-docs.yaml: 5.7 KB (32 endpoints)
- All other files: < 2 KB

## Next Steps

1. **For implementation:** Start with QUICK_REFERENCE.md
2. **For learning:** Start with EXECUTIVE_SUMMARY.md
3. **For integration:** Check COMPARISON_WITH_SOURCE_INIT.md
4. **For details:** Reference RESEARCH_ANALYSIS.md

## Contact/Questions

Refer to the original dlt documentation at https://dlthub.com/docs for:
- REST API source detailed reference
- Configuration API
- Paginator types details
- Incremental loading advanced patterns

All four research documents are self-contained with examples and should answer most questions about this directory.

---

**Research completed:** November 27, 2025
**Status:** Complete analysis of github_api_init directory structure, endpoints, configuration, and best practices
**Deliverables:** 4 comprehensive research documents + original dlt files

Happy exploring! Use EXECUTIVE_SUMMARY.md to get started.


> Source: `docs/data_engineering/dlt/github_api_init/RESEARCH_ANALYSIS.md`

# dlt github_api_init Directory Analysis

## Overview
The `github_api_init` directory represents dlt's **REST API-first approach** to creating API sources. This is distinct from the `github_source_init` (verified source) approach and demonstrates dlt's best practices for building declarative, configuration-driven API connectors using the REST API framework.

## Directory Structure

```
github_api_init/
├── .dlt/                          # dlt configuration directory
│   ├── config.toml               # Runtime configuration
│   ├── secrets.toml              # API credentials (templated)
│   └── .sources                  # Source tracking metadata
├── github-docs.yaml              # REST API endpoint definitions (KEY)
├── github_pipeline.py            # Pipeline entry point (minimal template)
├── requirements.txt              # Python dependencies
├── dlt.yaml                      # Empty dlt project config
├── .gitignore                    # Standard dlt gitignore
├── CLAUDE.md                     # AI coding guidelines for REST APIs
└── AGENT.md                      # (same as CLAUDE.md)
```

## Key Files Explanation

### 1. github-docs.yaml - The Core API Specification

This file is the **central artifact** that declares all GitHub API endpoints in a declarative YAML format. It follows a structured pattern:

#### Structure:

```yaml
# Source Metadata
source_name: github
version: 1.8.30
authentication_required: true
api_types_available:
  - REST

# Client Configuration (Global)
client:
  base_url: https://api.github.com
  auth:
    type: apikey
    location: header
    header_name: Authorization
  headers:
    Accept: application/vnd.github.v3+json
  paginator:
    type: page
    page_size_param: per_page
    default_page_size: 30

# Resources (Endpoint Definitions)
resources:
  - name: assignees
    endpoint:
      path: /repos/{owner}/{repo}/assignees
      method: GET
      data_selector: 
      params: {}
  
  # ... 32 more endpoints ...

# Auth Details for Validation
auth_info:
  mentioned_objects:
    - PersonalAccessToken
    - OAuthApp

# Error Handling Reference
errors:
  - REQUEST_LIMIT_EXCEEDED: Throttle API calls or reduce frequency
  - 401 Unauthorized: Recheck OAuth scopes or token expiration
  - 404 Not Found: Validate repository or organization names
```

#### Endpoints Defined (32 total):

**Organization/User Level:**
- `organizations` - GET /user/orgs
- `users` - GET /users
- `teams` - GET /orgs/{org}/teams
- `repositories` - GET /users/{username}/repos

**Repository Metadata:**
- `assignees` - GET /repos/{owner}/{repo}/assignees
- `branches` - GET /repos/{owner}/{repo}/branches
- `collaborator` - GET /repos/{owner}/{repo}/collaborators
- `issue_labels` - GET /repos/{owner}/{repo}/labels
- `tags` - GET /repos/{owner}/{repo}/tags
- `workflows` - GET /repos/{owner}/{repo}/actions/workflows

**Issues & Tracking:**
- `issues` - GET /repos/{owner}/{repo}/issues
- `issue_events` - GET /repos/{owner}/{repo}/issues/events
- `issue_milestones` - GET /repos/{owner}/{repo}/milestones
- `comments` - GET /repos/{owner}/{repo}/issues/comments
- `issue_comment_reactions` - GET /repos/{owner}/{repo}/issues/comments/{comment_id}/reactions
- `issue_reactions` - GET /repos/{owner}/{repo}/issues/{issue_number}/reactions

**Pull Requests:**
- `pull_requests` - GET /repos/{owner}/{repo}/pulls
- `pull_request_commits` - GET /repos/{owner}/{repo}/pulls/{pull_number}/commits
- `pull_request_stats` - GET /repos/{owner}/{repo}/pulls/{pull_number}/stats
- `review_comments` - GET /repos/{owner}/{repo}/pulls/{pull_number}/comments
- `pull_request_comment_reactions` - GET /repos/{owner}/{repo}/pulls/{pull_number}/comments/{comment_id}/reactions
- `reviews` - GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews

**Commits & Code:**
- `commits` - GET /repos/{owner}/{repo}/commits
- `commit_comments` - GET /repos/{owner}/{repo}/commits/{commit_sha}/comments
- `commit_comment_reactions` - GET /repos/{owner}/{repo}/comments/{comment_id}/reactions

**Releases & Deployments:**
- `releases` - GET /repos/{owner}/{repo}/releases
- `deployments` - GET /repos/{owner}/{repo}/deployments

**Events & Activity:**
- `events` - GET /repos/{owner}/{repo}/events
- `stargazers` - GET /repos/{owner}/{repo}/stargazers

**Projects:**
- `projects` - GET /repos/{owner}/{repo}/projects
- `project_columns` - GET /projects/{project_id}/columns
- `project_cards` - GET /projects/{project_id}/cards

**CI/CD:**
- `workflow_runs` - GET /repos/{owner}/{repo}/actions/runs
- `workflow_jobs` - GET /repos/{owner}/{repo}/actions/runs/{run_id}/jobs

### 2. github_pipeline.py - Template Pipeline Implementation

This is a **minimal template** showing the dlt pattern:

```python
import dlt
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)

@dlt.source
def github_source(access_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://example.com/v1/",
            "auth": {
                "type": "bearer",
                "token": access_token,
            },
        },
        "resources": [
            # TODO: add resource definitions here
        ],
    }

    yield from rest_api_resources(config)

def get_data() -> None:
    pipeline = dlt.pipeline(
        pipeline_name='github_pipeline',
        destination='duckdb',
        dataset_name='github_data',
    )

    access_token = "my_access_token"
    load_info = pipeline.run(github_source(access_token))
    print(load_info)

if __name__ == "__main__":
    get_data()
```

**Key Patterns:**
- Uses `@dlt.source` decorator for dependency injection
- Uses `rest_api_resources()` to process config
- Passes secrets via function parameters
- Returns generator from decorator
- DuckDB as default destination

### 3. .dlt/ Configuration Files

#### .dlt/config.toml
```toml
[runtime]
log_level="WARNING"
dlthub_telemetry = true
```

**Purpose:** Runtime configuration for dlt behavior (logging, telemetry).

#### .dlt/secrets.toml
```toml
access_token = "access_token"        # Root level

[sources.github]
access_token = "<configure me>"      # Source-specific
```

**Purpose:** Credentials management with templated placeholders.

#### .dlt/.sources
YAML file tracking source metadata and integrity:
- Engine version
- Git commit SHAs
- File checksums
- dlt version constraints

**Purpose:** Source versioning and state management in dlt registry.

### 4. requirements.txt
```
dlt[duckdb]>=1.18.2
```

Minimal dependencies: dlt with DuckDB adapter.

### 5. CLAUDE.md - AI Coding Guidelines

Comprehensive guidance for AI assistants including:
- Prerequisites for writing REST API sources
- Authentication methods (API Key, Bearer, OAuth2, Basic)
- Pagination types (json_link, header_link, offset, page_number, cursor, single_page)
- Data selection with `data_selector` (JSONPath extraction)
- Incremental loading configuration
- Parameter extraction guide from API docs
- Verification checklist
- dlt REST API pagination configuration details

## Architectural Differences: API Init vs. Source Init

### github_api_init (REST API Approach)
- **Configuration-driven:** YAML file defines endpoints
- **Declarative:** Uses `RESTAPIConfig` dictionary
- **Minimal code:** Rest API framework handles all plumbing
- **Generated:** Created by `dlt init` command
- **Use case:** Any REST API without specialized logic
- **Flexibility:** Easy to add/remove endpoints by modifying YAML
- **Pagination:** Handled transparently via config
- **Best for:** Quick API source generation, MCP integration, OpenAPI-driven development

### github_source_init (Verified Source)
- **Code-driven:** Python functions with custom logic
- **Imperative:** Uses decorators and generators
- **Advanced features:** GraphQL support, complex incremental logic
- **Maintained:** Official dlt library sources
- **Use case:** Complex APIs needing custom handling
- **Flexibility:** Full Python power for edge cases
- **Pagination:** Manual with helper functions
- **Best for:** Production sources, complex APIs, official library contributions

## Best Practices Reflected

### 1. Configuration Over Code
```yaml
# Clean, readable endpoint definition
- name: issues
  endpoint:
    path: /repos/{owner}/{repo}/issues
    method: GET
    data_selector: 
    params: {}
```

### 2. Authentication Security
- Credentials never hardcoded
- Uses `dlt.secrets` pattern
- Separate secrets.toml template
- Secure credential injection via decorators

### 3. Pagination Standardization
```yaml
paginator:
  type: page
  page_size_param: per_page
  default_page_size: 30
```
Single paginator config handles all endpoints using same strategy.

### 4. Data Extraction
`data_selector` field uses JSONPath to unwrap nested responses - transparent to user.

### 5. State Management
`.dlt/.sources` tracks versions, checksums, git history for reproducibility.

### 6. Documentation
Every file has clear purpose:
- CLAUDE.md/AGENT.md: AI coding rules
- github-docs.yaml: API specification
- requirements.txt: Dependencies
- .dlt/config.toml: Runtime settings
- .dlt/secrets.toml: Credentials template

## Key REST API Framework Features

### Configuration Structure
```python
RESTAPIConfig = {
    "client": {           # Global HTTP client settings
        "base_url": "...",
        "auth": {...},
        "headers": {...},
        "paginator": {...}
    },
    "resource_defaults": {  # Apply to all resources
        "primary_key": "id",
        "write_disposition": "merge",
        "endpoint": {"params": {...}}
    },
    "resources": [        # Individual endpoint definitions
        {
            "name": "resource_name",
            "endpoint": {
                "path": "/endpoint",
                "method": "GET",
                "data_selector": "...",
                "params": {...},
                "paginator": {...},  # Override client paginator
                "incremental": {...}
            }
        }
    ]
}
```

### Pagination Types by Strategy

| Type | Use Case | Config Key |
|------|----------|-----------|
| `json_link` | Response contains next URL | `next_url_path` |
| `header_link` | Link header contains next URL | `links_next_key` |
| `offset` | Query params: offset + limit | `offset_param`, `limit_param` |
| `page_number` | Query params: page + limit | `page_param`, `limit_param` |
| `cursor` | Response contains cursor token | `cursor_path`, `cursor_param` |
| `single_page` | No pagination | (none) |

## How to Use This Template

1. **Start with github-docs.yaml** - Extract endpoints from API docs
2. **Configure client settings** - Base URL, auth type, headers, paginator
3. **Define resources** - One per endpoint with path, method, params, data_selector
4. **Add to github_pipeline.py** - Reference github-docs.yaml in config
5. **Set secrets** - Fill .dlt/secrets.toml with actual credentials
6. **Run** - Execute pipeline.run(github_source(token))

## Relationship to OpenAPI/Swagger

The github-docs.yaml structure mirrors OpenAPI concepts:
- `client.base_url` = OpenAPI server URL
- `client.auth` = OpenAPI securitySchemes
- `resources[].endpoint.path` = OpenAPI paths
- `resources[].endpoint.method` = OpenAPI operations
- `resources[].endpoint.params` = OpenAPI parameters
- Pagination = OpenAPI extension patterns

This enables **automatic source generation** from OpenAPI specs.

## Integration Points

### With dlt CLI
```bash
dlt init github duckdb  # Creates this structure
```

### With MCP (Model Context Protocol)
The github-docs.yaml format is suitable for MCP AI-to-AI communication.

### With Dagster
Outputs can be wrapped as Dagster assets for orchestration.

### With LLMs/AI
Configuration-driven approach enables AI to read/modify APIs without code generation.

## Summary

`github_api_init` represents dlt's **best practice for REST API sources**: 
- Declarative endpoint specification
- Security by design
- Minimal code boilerplate
- Framework handles pagination/errors
- Ready for production use
- AI-friendly configuration format


> Source: `docs/data_engineering/dlt/github_api_init/QUICK_REFERENCE.md`

# github_api_init: Quick Reference Guide

## File Manifest

| File | Purpose | Key Content |
|------|---------|------------|
| `github-docs.yaml` | API specification | 32 GitHub REST endpoints in declarative YAML format |
| `github_pipeline.py` | Entry point | Minimal template showing dlt pattern |
| `.dlt/config.toml` | Runtime config | Logging level, telemetry settings |
| `.dlt/secrets.toml` | Credentials | Template for GitHub API token |
| `.dlt/.sources` | Version tracking | Engine version, git SHAs, checksums |
| `requirements.txt` | Dependencies | `dlt[duckdb]>=1.18.2` |
| `dlt.yaml` | Project config | Empty project marker |
| `CLAUDE.md` / `AGENT.md` | AI guidelines | Comprehensive REST API coding rules |

## Configuration Structure (YAML)

```yaml
source_name: github
version: 1.8.30
authentication_required: true

# Global HTTP client settings
client:
  base_url: https://api.github.com
  auth:
    type: apikey
    location: header
    header_name: Authorization
  headers:
    Accept: application/vnd.github.v3+json
  paginator:
    type: page                  # page, offset, cursor, json_link, header_link, single_page
    page_size_param: per_page
    default_page_size: 30

# Individual endpoints
resources:
  - name: resource_name
    endpoint:
      path: /path/{param1}/{param2}
      method: GET
      data_selector: results   # JSONPath to extract data
      params:
        filter_param: value
      paginator:               # Override client paginator if needed
        type: cursor
        cursor_path: pagination.next
        cursor_param: after
      incremental:             # For incremental loading
        cursor_path: updated_at
        start_param: since
        initial_value: "2023-01-01T00:00:00Z"

# Reference sections
auth_info:
  mentioned_objects:
    - PersonalAccessToken
    - OAuthApp

errors:
  - 401 Unauthorized: Recheck auth
  - 404 Not Found: Validate parameters
```

## Pagination Types Quick Reference

```yaml
# Page-based (like GitHub uses)
paginator:
  type: page
  page_param: page
  limit_param: per_page
  total_path: total_pages

# Offset-based
paginator:
  type: offset
  offset_param: offset
  limit_param: limit
  total_path: total

# Cursor-based
paginator:
  type: cursor
  cursor_path: pagination.next_cursor
  cursor_param: after

# Link header-based (GitHub alternative)
paginator:
  type: header_link
  links_next_key: next

# Response contains next URL
paginator:
  type: json_link
  next_url_path: links.next

# No pagination
paginator:
  type: single_page
```

## Authentication Types

```yaml
# API Key in header
auth:
  type: apikey
  name: X-API-Key
  api_key: ...              # from dlt.secrets
  location: header

# API Key in query
auth:
  type: apikey
  name: api_token
  api_key: ...
  location: query

# Bearer token
auth:
  type: bearer
  token: ...                # from dlt.secrets

# Basic auth
auth:
  type: basic
  username: ...
  password: ...

# OAuth2
auth:
  type: oauth2
  token_url: https://auth.example.com/token
  client_id: ...
  client_secret: ...
  scopes:
    - read
    - write
```

## Data Selector (JSONPath) Examples

```yaml
# Flat response array
data_selector: .              # or leave empty

# Nested in data field
data_selector: data

# Nested deeper
data_selector: data.results

# Nested with wildcard
data_selector: data.*

# Multiple levels
data_selector: response.payload.items

# Selecting specific fields
data_selector: data.{id,name,created_at}
```

## Pipeline Execution Pattern

```python
import dlt
from dlt.sources.rest_api import rest_api_resources, RESTAPIConfig

@dlt.source
def my_api_source(api_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.example.com",
            "auth": {
                "type": "bearer",
                "token": api_token,
            }
        },
        "resources": [
            # Add resource definitions here
        ]
    }
    
    yield from rest_api_resources(config)

# Run the pipeline
pipeline = dlt.pipeline(
    pipeline_name='my_pipeline',
    destination='duckdb',
    dataset_name='my_data',
    progress="log"
)

# Load data
load_info = pipeline.run(my_api_source())
print(load_info)
```

## Secrets Configuration

`.dlt/secrets.toml`:
```toml
# Root level (used as default)
access_token = "your_actual_token_here"

# Source-specific
[sources.github]
access_token = "your_token"

# Per-resource credentials (advanced)
[sources.resource_name]
api_key = "key_value"
api_secret = "secret_value"
```

Reference in Python:
```python
@dlt.source
def source_func(token=dlt.secrets.value):
    # Token automatically injected from secrets.toml

@dlt.source
def source_func(token=dlt.secrets["my_api_token"]):
    # Specific named secret

@dlt.source
def source_func(token=dlt.secrets["sources.github"]["access_token"]):
    # Source-specific secret
```

## 32 GitHub API Endpoints Included

### Organization/User (4)
- organizations, users, teams, repositories

### Repository Metadata (6)
- assignees, branches, collaborator, issue_labels, tags, workflows

### Issues (6)
- issues, issue_events, issue_milestones, comments, issue_comment_reactions, issue_reactions

### Pull Requests (6)
- pull_requests, pull_request_commits, pull_request_stats, review_comments, pull_request_comment_reactions, reviews

### Commits (3)
- commits, commit_comments, commit_comment_reactions

### Releases & Deployments (2)
- releases, deployments

### Events & Activity (2)
- events, stargazers

### Projects (3)
- projects, project_columns, project_cards

### CI/CD (2)
- workflow_runs, workflow_jobs

## Incremental Loading Setup

For timestamp-based incremental:
```yaml
resources:
  - name: issues
    endpoint:
      path: /repos/{owner}/{repo}/issues
      params:
        since: "{incremental.start_value}"
      incremental:
        cursor_path: updated_at      # Field to track state
        start_param: since           # Query param name
        initial_value: "2023-01-01T00:00:00Z"
```

For ID-based incremental:
```yaml
resources:
  - name: items
    endpoint:
      path: /items
      params:
        min_id: "{incremental.start_value}"
      incremental:
        cursor_path: id              # Track item IDs
        start_param: min_id
        initial_value: 0
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| 401 Unauthorized | Check token in secrets.toml, verify scopes |
| 404 Not Found | Validate path parameters ({owner}, {repo}, etc.) |
| Empty data | Check data_selector JSONPath, verify API response |
| Pagination not working | Verify paginator type matches API behavior |
| Rate limit exceeded | Reduce page_size or add delays (dlt handles with retries) |
| Incremental not tracking | Ensure cursor_path matches response field names |

## Best Practices

1. **Start with github-docs.yaml** - Define all endpoints there
2. **Use data_selector** - Unwrap nested response data declaratively
3. **Respect rate limits** - Configure appropriate page_size
4. **Secure secrets** - Never hardcode tokens, always use .dlt/secrets.toml
5. **Test incrementally** - Start with small date ranges
6. **Document parameters** - Add comments to complex endpoint configs
7. **Validate JSONPath** - Test data_selector with sample responses
8. **Plan primary keys** - Know which fields uniquely identify records
9. **Consider write disposition** - Replace vs. Append vs. Merge
10. **Monitor schema changes** - API changes may require config updates

## Resource Defaults Example

```yaml
resource_defaults:
  primary_key: id                    # Default primary key
  write_disposition: merge           # Default write mode
  endpoint:
    params:
      limit: 100                    # Default page size
      
resources:
  - name: resource_using_defaults
    endpoint:
      path: /path
      # Inherits primary_key, write_disposition, params.limit from defaults
  
  - name: resource_override_primary_key
    endpoint:
      path: /path2
      # Can override: specify own primary_key in resource if needed
```

## Integration with Rest of Stack

### With dlt CLI
```bash
dlt init github duckdb           # Creates this structure
dlt run github_pipeline.py       # Executes the pipeline
dlt pipeline github show         # Inspect loaded data
```

### With Destinations
```python
pipeline = dlt.pipeline(
    pipeline_name='github',
    destination='duckdb',        # Can be postgres, bigquery, snowflake, etc.
    dataset_name='github_data'
)
```

### With Orchestration (Dagster example)
```python
from dagster import asset

@asset
def github_issues(context) -> None:
    pipeline = dlt.pipeline(...)
    pipeline.run(github_source(token))
```

## Files to Modify for Custom API

1. **github-docs.yaml** - Replace GitHub endpoints with your API's endpoints
2. **requirements.txt** - Keep as-is or add dlt extras for your destination
3. **dlt.yaml** - Rename pipeline/source names if desired
4. **.dlt/secrets.toml** - Replace with your API credentials
5. **github_pipeline.py** - Update source function name and config loading
6. **CLAUDE.md** - Reference as guide when building config

## Verification Checklist

Before running:
- [ ] Base URL is correct
- [ ] Authentication type and location verified
- [ ] All endpoint paths checked against API docs
- [ ] Data selector JSONPath tested with sample responses
- [ ] Pagination type matches API behavior
- [ ] Secrets configured in .dlt/secrets.toml
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] API token/credentials set and not expired
- [ ] Rate limits understood and page_size configured appropriately
- [ ] Output destination (duckdb) is available/writable

## Resources

- **dlt Documentation:** https://dlthub.com/docs
- **REST API Source Guide:** https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api
- **GitHub API Docs:** https://docs.github.com/en/rest
- **CLAUDE.md in this directory:** Comprehensive AI coding guidelines


> Source: `docs/data_engineering/dlt/github_api_init/AGENT.md`

# Rules

## Build the REST API config with cursor-based pagination

## Prerequisities to writing a source

1. VERY IMPORTANT. When writing a new source, you should have an example available in the rest_api_pipeline.py file. 
Use this example or the github rest api source example from dlt's documentation on rest api for the general structure of the code. If you do not see this file rest_api_pipeline.py, ask the user to add it
2. Recall OpenAPI spec. You will figure out the same information that the OpenAPI spec contains for each API.
3. In particular:
- API base url
- type of authentication
- list of endpoints with method GET (you can read data for those)
4. You will figure out additional information that is required for successful data extraction
- type of pagination
- if data from an endpoint can be loaded incrementally
- unwrapping end user data from a response
- write disposition of the endpoint: append, replace, merge
- in case of merge, you need to find primary key that can be compound
5. Some endpoints take data from other endpoints. For example, in the github rest api source example from dlt's documentation, the `comments` endpoint needs `post id` to get the list of comments per particular post. You'll need to figure out such connections
6. **ASK USER IF YOU MISS CRUCIAL INFORMATION** You will make sure the user has provided you with enough information to figure out the above. Below are the most common possibilities
- open api spec (file or link)
- any other api definition, for example Airbyte low code yaml
- a source code in Python, java or c# of such connector or API client
- a documentation of the api or endpoint
7. In case you find more than 10 endpoints and you do not get instructions which you should add to the source, ask user.
8. Make sure you use the right pagination and use exactly the arguments that are available in the pagination guide. do not try to guess anything. remember that we have many paginator types that are configured differently
9. When creating pipeline instance add progress="log" as parameter `pipeline = dlt.pipeline(..., progress="log")`
10. When fixing a bug report focus only on a single cause. ie. incremental, pagination or authentication or wrong dict fields
11. You should have references for paginator types, authenticator types and general reference for rest api in you context. **DO NOT GUESS. DO NOT INVENT CODE. YOU SHOULD HAVE DOCUMENTATION FOR EVERYTHING YOU NEED. IF NOT - ASK USER**


## Look for Required Client Settings
When scanning docs or legacy code, first extract the API-level configuration including:

Base URL:
• The API's base URL (e.g. "https://api.pipedrive.com/").

Authentication:
• The type of authentication used (commonly "api_key" or "bearer").
• The name/key (e.g. "api_token") and its placement (usually in the query).
• Use secrets (e.g. dlt.secrets["api_token"]) to keep credentials secure.

Headers (optional):
• Check if any custom headers are required.

## Authentication Methods
Configure the appropriate authentication method:

API Key Authentication:
```python
"auth": {
    "type": "api_key",
    "name": "api_key",
    "api_key": dlt.secrets["api_key"],
    "location": "query"  # or "header"
}
```

Bearer Token Authentication:
```python
"auth": {
    "type": "bearer",
    "token": dlt.secrets["bearer_token"]
}
```

Basic Authentication:
```python
"auth": {
    "type": "basic",
    "username": dlt.secrets["username"],
    "password": dlt.secrets["password"]
}
```

OAuth2 Authentication:
```python
"auth": {
    "type": "oauth2",
    "token_url": "https://auth.example.com/oauth/token",
    "client_id": dlt.secrets["client_id"],
    "client_secret": dlt.secrets["client_secret"],
    "scopes": ["read", "write"]
}
```

## Find right pagination type
These are the available paginator types to be used in `paginator` field of `endpoint`:

* `json_link`: The link to the next page is in the body (JSON) of the response
* `header_link`: The links to the next page are in the response headers
* `offset`: The pagination is based on an offset parameter, with the total items count either in the response body or explicitly provided
* `page_number`: The pagination is based on a page number parameter, with the total pages count either in the response body or explicitly provided
* `cursor`: The pagination is based on a cursor parameter, with the value of the cursor in the response body (JSON)
* `single_page`: The response will be interpreted as a single-page response, ignoring possible pagination metadata


## Different Paginations per Endpoint are possible
When analyzing the API documentation, carefully check for multiple pagination strategies:

• Different Endpoint Types:
  - Some endpoints might use cursor-based pagination
  - Others might use offset-based pagination
  - Some might use page-based pagination
  - Some might use link-based pagination

• Documentation Analysis:
  - Look for sections describing different pagination methods
  - Check if certain endpoints have special pagination requirements
  - Verify if pagination parameters differ between endpoints
  - Look for examples showing different pagination patterns

• Implementation Strategy:
  - Configure pagination at the endpoint level rather than globally
  - Use the appropriate paginator type for each endpoint
  - Document which endpoints use which pagination strategy
  - Test pagination separately for each endpoint type

## Select the right data from the response
In each endpoint the interesting data (typically an array of objects) may be wrapped
differently. You can unwrap this data by using `data_selector`

Data Selection Patterns:
```python
"endpoint": {
    "data_selector": "data.items.*",  # Basic array selection
    "data_selector": "data.*.items",  # Nested array selection
    "data_selector": "data.{id,name,created_at}",  # Field selection
}
```

## Resource Defaults & Endpoint Details
Ensure that the default settings applied across all resources are clearly delineated:

Defaults:
• Specify the default primary key (e.g., "id").
• Define the write disposition (e.g., "merge").
• Include common endpoint parameters (for example, a default limit value like 50).

Resource-Specific Configurations:
• For each resource, extract the endpoint path, method, and any additional query parameters.
• If incremental loading is supported, include the minimal incremental configuration (using fields like "start_param", "cursor_path", and "initial_value"), but try to keep it within the REST API config portion.

## Incremental Loading Configuration
Configure incremental loading for efficient data extraction. Your task is to get only new data from
the endpoint.

Typically you will identify query parameter that allows to get items that are newer than certain date:

```py
{
    "path": "posts",
    "data_selector": "results",
    "params": {
        "created_since": "{incremental.start_value}",  # Uses cursor value in query parameter
    },
    "incremental": {
        "cursor_path": "created_at",
        "initial_value": "2024-01-25T00:00:00Z",
    },
}
```


## End to end example
Below is an annotated template that illustrates how your output should look. Use it as a reference to guide your extraction:

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# Build the REST API config with cursor-based pagination
source = rest_api_source({
    "client": {
        "base_url": "https://api.pipedrive.com/",  # Extract this from the docs/legacy code
        "auth": {
            "type": "api_key",                    # Use the documented auth type
            "name": "api_token",
            "api_key": dlt.secrets["api_token"],    # Replace with secure token reference
            "location": "query"                     # Typically a query parameter for API keys
        }
    },
    "resource_defaults": {
        "primary_key": "id",                        # Default primary key for resources
        "write_disposition": "merge",               # Default write mode
        "endpoint": {
            "params": {
                "limit": 50                         # Default query parameter for pagination size
            }
        }
    },
    "resources": [
        {
            "name": "deals",                        # Example resource name extracted from code or docs
            "endpoint": {
                "path": "v1/recents",               # Endpoint path to be appended to base_url
                "method": "GET",                    # HTTP method (default is GET)
                "params": {
                    "items": "deal"
                    "since_timestamp": "{incremental.start_value}"
                },
                "data_selector": "data.*",          # JSONPath to extract the actual data
                "paginator": {                      # Endpoint-specific paginator
                    "type": "offset",
                    "offset": 0,
                    "limit": 100
                },
                "incremental": {                    # Optional incremental configuration
                    "cursor_path": "update_time",
                    "initial_value": "2023-01-01 00:00:00"
                }
            }
        }
    ]
})

if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="pipedrive_rest",
        destination="duckdb",
        dataset_name="pipedrive_data"
    )
    pipeline.run(source)
```

## How to Apply This Rule
Extraction:
• Search both the REST API docs and any legacy pipeline code for all mentions of "cursor" or "pagination".
• Identify the exact keys and JSONPath expressions needed for the cursor field.
• Look for authentication requirements and rate limiting information.
• Identify any dependent resources and their relationships.
• Check for multiple pagination strategies across different endpoints.

Configuration Building:
• Assemble the configuration in a dictionary that mirrors the structure in the example.
• Ensure that each section (client, resource defaults, resources) is as declarative as possible.
• Implement proper state management and incremental loading where applicable.
• Configure rate limiting based on API requirements.
• Configure pagination at the endpoint level when multiple strategies exist.

Verification:
• Double-check that the configuration uses the REST API config keys correctly.
• Verify that no extraneous Python code is introduced.
• Test the configuration with mock responses.
• Verify rate limiting and error handling.
• Test pagination separately for each endpoint type.

Customization:
• Allow for adjustments (like modifying the "initial_value") where incremental loading is desired.
• Customize rate limiting parameters based on API requirements.
• Adjust batch sizes and pagination parameters as needed.
• Implement custom error handling and retry logic where necessary.
• Handle different pagination strategies appropriately.

## Guidelines

# Guidelines
1. dlt means "data load tool". It is an open source Python library installable via `pip install dlt`.
2. To create a new pipeline, use `dlt init <source> <destination>`.
3. The dlt library comes with the `dlt` CLI. Add the `--help` flag to any command to verify its specs. 
4. The preferred way to configure dlt (sources, resources, destinations, etc.) is to use `.dlt/config.toml` and `.dlt/secrets.toml`
5. During development, always set `dev_mode=True` when creating a dlt Pipeline. `pipeline = dlt.pipeline(..., dev_mode=True)`. This allows to reset the pipeline's schema and state between iterations.
6. Use type annotations only if you're certain you're properly importing the types.
7. Use dlt's REST API source if loading data from the web.
8. Use dlt's SQL source when loading data from an SQL database or backend.
9. Use dlt's filesystem source if loading data from files (CSV, PDF, Parquet, JSON, and more). This works for local filesystems and cloud buckets (AWS, Azure, GCP, Minio, etc.).

## REST API Parameter Extraction Guide

# REST API Parameter Extraction Guide

This rule helps identify and extract ALL necessary parameters from API documentation to build a dlt REST API source. **Crucially, configuration parameters like pagination and incremental loading can vary significantly between different API endpoints. Do not assume a single global strategy applies to all resources.**

## 1. Base Configuration Parameters (Client Level)

These settings usually apply globally but *can* sometimes be overridden at the resource level.

### Client Settings
Look for these in the API documentation (often in "Overview", "Getting Started", "Authentication"):
- **Base URL**:
  - Aliases: "API endpoint", "root URL", "service URL"
  - Example Format: `https://api.example.com/v1/`
  - Find the main entry point for the API version you need.

- **Authentication**:
  - Keywords: "Authentication", "Authorization", "API Keys", "Security"
  - Common Types & dlt Mappings:
    - API Key: Look for "API Key", "Access Token", "Secret Token", "Subscription Key". Map API key value to `api_key`, name to `name`, location (`query` or `header`) to `location`.
    - Bearer Token: Look for "Bearer Token", "JWT". Map token value to `token`.
    - OAuth2: Look for "OAuth", "Client ID", "Client Secret", "Scopes", "Token URL". Map to `client_id`, `client_secret`, `scopes`, `token_url`.
    - Basic Auth: Look for "Basic Authentication". Map to `username` and `password`.
  - Note where credentials go (header, query parameter, request body).
  - **Secret Handling:**
    - **Pattern 1: Using `@dlt.source` or `@dlt.resource` Decorators (Recommended when applicable):**
      Define your source/resource function with arguments having defaults like `api_key: str = dlt.secrets.value` or `client_secret: str = dlt.secrets["specific_key"]`. `dlt` injects the resolved secret when calling the decorated function. You can then use the argument variable directly.
      ```python
      @dlt.source
      def my_api_source(api_key: str = dlt.secrets.value):
          config = {...
              "auth": {"type": "api_key", "api_key": api_key, ...}
              ...
          }
          yield rest_api_source(config)
      ```
    - **Pattern 2: Calling `rest_api_source` Directly (Requires Explicit Resolution):**
      If calling `rest_api_source` *without* a `@dlt.source/resource` decorator on the calling function, you **must resolve the secret explicitly *before* creating the configuration dictionary**. Using `dlt.secrets.value` directly in the dictionary or as a default function argument *will not work* in this context.
      ```python
      def my_api_source_direct():
          # Resolve secret explicitly first
          actual_key = dlt.secrets["my_api_key"]
          
          config = {
              "client": {
                  "auth": {
                      "type": "api_key",
                      "api_key": actual_key, # Use resolved value
                      ...
                  }
              }
          }
          return rest_api_source(config)
      
      # Pipeline call
      pipeline.run(my_api_source_direct())
      ```

- **Global Headers** (Optional):
  - Keywords: "Headers", "Request Headers", "Required Headers"
  - Common Headers: `Accept: application/json`, `Content-Type: application/json`, `User-Agent`.
  - Look for any custom headers required for *all* requests (e.g., `X-Api-Version`). Resource-specific headers go in the resource config.

## 2. Resource / Endpoint Parameters

**Crucially, examine the documentation for EACH resource/endpoint individually.**

### Endpoint Configuration
For each endpoint/resource (e.g., `/users`, `/orders/{order_id}`), find:
- **Path**:
  - Keywords: "Endpoints", "Resources", "API Methods", "Routes"
  - Format: `/resource`, `/v1/resource`. Note any path parameters like `{id}`.
  - This path is appended to the `base_url`.

- **Method**:
  - Usually explicit: `GET`, `POST`, `PUT`, `DELETE`.
  - Default is `GET` if not specified.

- **Resource-Specific Query Parameters**:
  - Keywords: "Parameters", "Query Parameters", "Optional Parameters", "Filtering", "Sorting"
  - Examples:
    - Filtering: `status=active`, `type=customer`, `created_after=...`
    - Sorting: `sort=created_at`, `order=desc`
    - Fields: `fields=id,name,email` (for selecting specific fields)
  - **Note:** Pagination and incremental parameters are covered separately below, but are often listed here too.

- **Request Body** (for `POST`, `PUT`, `PATCH`):
  - Keywords: "Request Body", "Payload", "Data"
  - Note the expected structure (usually JSON).

### Data Selection (Response Parsing)
- Keywords: "Response", "Response Body", "Example Response", "Schema"
- **Identify the JSON path** to the list/array of actual data items within the response.
- Common patterns & dlt `data_selector`:
  - `{"data": [...]}` -> `data`
  - `{"results": [...]}` -> `results`
  - `{"items": [...]}` -> `items`
  - `{"data": {"records": [...]}}` -> `data.records`
  - Sometimes the root is the list: `[{...}, {...}]` -> `.` or `[*] `(or no selector needed)

## 3. Pagination Parameters (Check Per Endpoint!)

**APIs often use different pagination methods for different endpoints. Check EACH endpoint's documentation for its specific pagination details.**

- **Identify the Strategy**: Look for sections titled "Pagination", "Paging", "Handling Large Responses", or examples showing how to get the next set of results.
- **Common Strategies & dlt Mapping**:
  - **Cursor-based**:
    - Keywords: `cursor`, `next_cursor`, `next_page_token`, `continuation_token`, `after`, `marker`
    - Identify: Where is the *next* cursor value found in the response? (e.g., `pagination.next_cursor`, `meta.next`, `links.next.href`). Map this to `cursor_path`.
    - Identify: What is the *query parameter name* to send the next cursor? (e.g., `cursor`, `page_token`, `after`). Map this to `cursor_param`.
    - Identify: What is the parameter for page size? Map to `limit_param` (set this in `endpoint.params`, not the paginator dict).
    - dlt `type`: `cursor`
  - **Offset-based**:
    - Keywords: `offset`, `skip`, `start`, `startIndex`
    - Identify: Parameter name for the starting index/offset. Map to `offset_param`.
    - Identify: Parameter for page size/limit. Map to `limit_param`.
    - Identify: Optional path to total items count in response (e.g., `summary.total`, `total_count`). Map to `total_path`.
    - dlt `type`: `offset`
  - **Page-based**:
    - Keywords: `page`, `page_number`, `pageNum`
    - Identify: Parameter name for the page number. Map to `page_param`.
    - Identify: Parameter for page size/limit. Map to `limit_param`.
    - Identify: Optional path to total pages or total items in response. Map to `total_path`.
    - dlt `type`: `page`
  - **Link Header-based**:
    - Check response headers for a `Link` header (e.g., `Link: <url>; rel="next"`).
    - dlt `type`: `link_header`, `next_url_path`: `next` (usually)
  - **No Pagination**: Some simple endpoints (e.g., fetching a single item by ID, small config lists) might not be paginated.

- **Configure at Resource Level**: If pagination differs between endpoints, define the `paginator` dictionary within the specific resource's `endpoint` configuration in `dlt`, overriding the client/default level.

## 4. Incremental Loading Parameters (Check Per Endpoint!)

Look for ways to fetch only new or updated data since the last run. This also often varies by endpoint. **The `incremental` configuration dictionary *always* requires the `cursor_path` field to be defined, even if `start_param` is also used.**

- **Identify Strategy & Parameters**:
  - **Timestamp-based**:
    - Keywords: `since`, `updated_since`, `modified_since`, `start_time`, `from_date`
    - Identify: The query parameter name used to filter by time (Optional). Map to `start_param`.
    - Identify: The field *in the response items* that contains the relevant timestamp (e.g., `updated_at`, `modified_ts`, `last_activity_date`). **Map this to `cursor_path` (Required)**. `dlt` uses this path to find the value for the next incremental run's state.
    - Note the required date format.
  - **ID-based / Event-based**:
    - Keywords: `since_id`, `min_id`, `last_event_id`, `sequence_number`, `offset` (if used like a cursor)
    - Identify: The query parameter name used to filter by ID/sequence (Optional). Map to `start_param`.
    - Identify: The field *in the response items* containing the ID/sequence. **Map this to `cursor_path` (Required)**.
  - **Cursor-based (using pagination cursor)**:
    - Sometimes the pagination cursor itself can be used for incremental loading if it's persistent and ordered (less common, often needs verification).
    - Map the response cursor path to `cursor_path` (**Required**) and the query parameter to `start_param` (Optional).

- **Initial Value**: Determine a safe starting point (e.g., a specific date `"2023-01-01T00:00:00Z"`, `0` for IDs). Map to `initial_value`.
- **Optional End Param**: If the API supports filtering up to a certain point (e.g., `end_date`, `max_id`), identify the parameter name (map to `end_param`) and potentially a value (map to `end_value`).
- **Optional Conversion**: If the `cursor_path` value needs transformation before being used in `start_param` or `end_param`, define a function and map it to `convert`.
- **Configure at Resource Level**: Define the `incremental` dictionary within the specific resource's `endpoint` configuration if the strategy or fields differ from others.

## 5. Common Documentation Patterns & Examples

(Keep existing examples, they are helpful)

### Authentication Section
```markdown
## Authentication
To authenticate, include your API key in the `Authorization: Bearer <your_token>` header.
```

### Endpoint Documentation Example (with variations)
```markdown
## List Orders
GET /v2/orders

Fetches a list of orders. This endpoint uses offset-based pagination.

Query Parameters:
- limit (integer, optional, default: 50): Max items per page.
- offset (integer, optional, default: 0): Number of items to skip.
- status (string, optional): Filter by status (e.g., 'completed', 'pending').
```

```markdown
## Get Activity Stream
GET /activities/stream

Fetches recent activities. Uses cursor-based pagination.

Query Parameters:
- page_size (integer, optional, default: 100): Number of activities.
- next_page_cursor (string, optional): Cursor from the previous response's `meta.next_page` field.

Response:
{
  "activities": [...],
  "meta": {
    "next_page": "aabbccddeeff"
  }
}
```

## 6. Enhanced Parameter Mapping (API Terminology -> dlt Config)

Map diverse API documentation terms to consistent `dlt` parameters. Identify the API's term first, then find the corresponding `dlt` key.

```yaml
client:
  base_url:
    common_api_terms: ["Base URL", "API Endpoint", "Root URL", "Service URL"]
    dlt_parameter: "client.base_url"
    notes: "Include version path (e.g., /v1/)"
  
  auth:
    api_key_value:
      common_api_terms: ["API Key", "Access Token", "Secret", "Token", "Key"]
      dlt_parameter: "client.auth.api_key"
      notes: "Handled via Secret Handling patterns"
    
    api_key_param_name:
      common_api_terms: ["api_key", "token", "key", "access_token"]
      dlt_parameter: "client.auth.name"
      notes: "Query param name or Header name"
    
    api_key_location:
      common_api_terms: ["Query parameter", "Header"]
      dlt_parameter: "client.auth.location"
      notes: "query or header"
    
    bearer_token:
      common_api_terms: ["Bearer Token", "JWT"]
      dlt_parameter: "client.auth.token"
      notes: "Handled via Secret Handling patterns"

pagination:
  note: "Define per-resource if strategies differ!"
  
  next_cursor_source:
    common_api_terms: ["next_cursor", "next_page", "nextToken", "marker"]
    dlt_parameter: "paginator.cursor_path"
    notes: "JSON path in response"
  
  next_cursor_param:
    common_api_terms: ["cursor", "page_token", "after", "next", "marker"]
    dlt_parameter: "paginator.cursor_param"
    notes: "Query param name to send cursor"
  
  offset_param:
    common_api_terms: ["offset", "skip", "start", "startIndex"]
    dlt_parameter: "paginator.offset_param"
    notes: "Query param name"
  
  page_number_param:
    common_api_terms: ["page", "page_number", "pageNum"]
    dlt_parameter: "paginator.page_param"
    notes: "Query param name"
  
  page_size_param:
    common_api_terms: ["limit", "per_page", "page_size", "count", "maxItems"]
    dlt_parameter: "paginator.limit_param"
    notes: "Query param name"
  
  total_items_source:
    common_api_terms: ["total", "total_count", "total_results", "count"]
    dlt_parameter: "paginator.total_path"
    notes: "Optional JSON path in response"
  
  link_header_relation:
    common_api_terms: ["next", "last"]
    dlt_parameter: "paginator.next_url_path"
    notes: "rel value in Link header"

incremental:
  note: "Define per-resource if strategies differ!"
  
  timestamp_param:
    common_api_terms: ["since", "updated_since", "modified_since", "from"]
    dlt_parameter: "incremental.start_param"
    notes: "Query param name"
  
  timestamp_source:
    common_api_terms: ["updated_at", "modified", "last_updated", "ts"]
    dlt_parameter: "incremental.cursor_path"
    notes: "JSON path in response item"
  
  id_sequence_param:
    common_api_terms: ["since_id", "min_id", "after_id", "sequence"]
    dlt_parameter: "incremental.start_param"
    notes: "Query param name"
  
  id_sequence_source:
    common_api_terms: ["id", "event_id", "sequence_id", "_id"]
    dlt_parameter: "incremental.cursor_path"
    notes: "JSON path in response item"
  
  initial_value:
    common_api_terms: ["N/A"]
    dlt_parameter: "incremental.initial_value"
    notes: "Start value for first run"

data:
  data_array_path:
    common_api_terms: ["data", "results", "items", "records", "entries"]
    dlt_parameter: "endpoint.data_selector"
    notes: "JSON path to the list of items"
```

## 7. Verification Checklist

Before finalizing the configuration:
1.  Verify Base URL format and version.
2.  Confirm Authentication method and *all* required parameters/headers.
3.  Verify Secret Handling pattern matches how the source is called.
4.  **For EACH resource:** Identify its specific pagination strategy (cursor, offset, page, link, none).
5.  **For EACH resource:** Extract the correct pagination parameters (`cursor_path`, `cursor_param`, `offset_param`, `page_param`, `limit_param` etc.) based on its strategy.
6.  **For EACH resource:** Determine if incremental loading is possible and identify its strategy (timestamp, ID, etc.).
7.  **For EACH resource:** Extract the correct incremental parameters (`cursor_path`, `initial_value`, `start_param`, etc.) based on its strategy.
8.  Validate the `data_selector` path for each resource by checking example responses.
9.  Check for any required Global Headers AND Resource-Specific Headers.

## dlt REST API Pagination Configuration Guide

# dlt REST API Pagination Configuration Guide
Use this rule when writing REST API Source to configure right pagination type for an Endpoint

This rule explains how to configure different pagination strategies for the `dlt` `rest_api` source. Understanding the API's specific pagination method is crucial for correct configuration.

If you are unsure what type of pagination to use due to lack of information from the api, consider curl-ing for responses (you can probably find credentials in secrets if needed)

We will use class based paginators and not declartive so if you search online in dlthub docs, make sure you do the right type

**Key Principle: Endpoint-Specific Pagination**

While you can set a default paginator at the `client` level, many APIs use *different* pagination methods for different endpoints. Always check the documentation for *each specific endpoint* you intend to load.

If an endpoint uses a different pagination method than the default, define its `paginator` configuration within that specific resource's `endpoint` section to override the client-level setting.

## DLT RESTClient Paginators Guide

To specify the pagination configuration, use the `paginator` field in the `client` or `endpoint` configurations. You should use a dictionary with a string alias in the `type` field along with the required parameters

#### Example

Suppose the API response for `https://api.example.com/posts` contains a `next` field with the URL to the next page:

```json
{
    "data": [
        {"id": 1, "title": "Post 1"},
        {"id": 2, "title": "Post 2"},
        {"id": 3, "title": "Post 3"}
    ],
    "pagination": {
        "next": "https://api.example.com/posts?page=2"
    }
}
```

You can configure the pagination for the `posts` resource like this:

```py
{
    "path": "posts",
    "paginator": {
        "type": "json_link",
        "next_url_path": "pagination.next",
    }
}
```

Currently, pagination is supported only for GET requests. To handle POST requests with pagination, you need to implement a custom paginator

These are the available paginator types to be used in `paginator` field:

* `json_link`: The link to the next page is in the body (JSON) of the response
* `header_link`: The links to the next page are in the response headers
* `offset`: The pagination is based on an offset parameter, with the total items count either in the response body or explicitly provided
* `page_number`: The pagination is based on a page number parameter, with the total pages count either in the response body or explicitly provided
* `cursor`: The pagination is based on a cursor parameter, with the value of the cursor in the response body (JSON)
* `single_page`: The response will be interpreted as a single-page response, ignoring possible pagination metadata


### Paginator arguments

#### json_link
Description: Paginator for APIs where the next page’s URL is included in the response JSON body (e.g. in a field like "next" or within a "pagination" object)​
dlthub.com

Parameters:
`next_url_path` (str, optional): JSONPath to the key in the response JSON that contains the next page URL​

When to Use
Use `json_link` when the API’s JSON response includes a direct link (URL) to the next page of results​

A common pattern is a field such as "next" or a nested key that holds the full URL for the next page. For example, an API might return a JSON structure like:
```json
{
  "data": [ ... ],
  "pagination": {
    "next": "https://api.example.com/posts?page=2"
  }
}
```

In the above, the "pagination.next" field provides the URL for the next page​

By specifying next_url_path="pagination.next", the `json_link` will extract that URL and request the next page automatically. This paginator is appropriate whenever the response body itself contains the next page URL, often indicated by keys like "next", "next_url", or a pagination object with a next link.

#### header_link

Description: Paginator for APIs where the next page’s URL is provided in an HTTP header (commonly the Link header with rel="next")​

Parameters
`links_next_key` (str, optional): The relation key in the Link response header that identifies the next page’s URL​. Default is "next". Example: If the header is Link: <https://api.example.com/items?page=2>; rel="next", the default links_next_key="next" will capture the URL for the next page.

When to Use
Use `header_link` when the API provides pagination links via HTTP headers rather than in the JSON body. This is common in APIs (like GitHub’s) that return a Link header containing URLs for next/prev pages. For example, an HTTP response might include:
```
Link: <https://api.example.com/items?page=2>; rel="next"
Link: <https://api.example.com/items?page=5>; rel="last"
```
In such cases, the `header_link` will parse the Link header, find the URL tagged with rel="next", and follow it​

You should use this paginator if the API documentation or responses indicate that pagination is controlled by header links. (Typically, look for a header named “Link” or similar, with URIs and relation types.) Note: By default, links_next_key="next" works for standard cases. If an API uses a different relation name in the Link header, you can specify that (e.g. HeaderLinkPaginator(links_next_key="pagination-next")).


#### offset
Description: Paginator for APIs that use numeric offset/limit parameters in query strings to paginate results​.
Each request fetches a set number of items (limit), and subsequent requests use an increasing offset.

Parameters
`limit` (int, required): The maximum number of items to retrieve per request (page size)​.
`offset` (int, optional): The starting offset for the first request​. Defaults to 0 (beginning of dataset).
`offset_param` (str, optional): Query parameter name for the offset value​. Default is "offset".
`limit_param` (str, optional): Query parameter name for the page size limit​. Default is "limit".
`total_path` (str or None, optional): JSONPath to the total number of items in the response. If provided, it helps determine when to stop pagination based on total count​. By default this is "total", assuming the response JSON has a field "total" for total item count. Use None if the API doesn’t return a total.
`maximum_offset` (int, optional): A cap on the maximum offset to reach​. If set, pagination stops when offset >= maximum_offset + limit.
`stop_after_empty_page` (bool, optional): Whether to stop when an empty page (no results) is encountered​. Defaults to True. If True, the paginator will halt as soon as a request returns zero items (useful for APIs that don’t provide a total count).
​
. To illustrate, if the first response looks like:
```json
{
  "items": [ ... ],
  "total": 1000
}
```
the paginator knows there are 1000 total items​
 and will continue until the offset reaches 1000 (or the final partial page). If the API does not provide a total count, OffsetPaginator will rely on getting an empty result page to stop by default​. You can also set maximum_offset to limit the number of items fetched (e.g., for testing, or if the API has an implicit max).

When to Use
Use `offset` for APIs that use offset-based pagination. Indicators include endpoint documentation or query parameters like offset (or skip/start) and limit(orpage_size`), and often a field in the response that gives the total count of items. For example, an API endpoint might be called as:
```
GET https://api.example.com/items?offset=0&limit=100
```
and return data with a structure like:
```json
{
  "items": [ ... ],
  "total": 1000
}
```
Here, the presence of offset/limit parameters and a "total" count in the JSON indicates offset-based pagination​. Choose `offset` when you see this pattern. This paginator will automatically increase the offset by the given limit each time, until it either reaches the total count (if known) or encounters an empty result set (if stop_after_empty_page=True). If the API lacks a total count and can continuously scroll, ensure you provide a stopping condition (like maximum_offset) or rely on an empty page to avoid infinite pagination.

#### page_number
Description: Paginator for APIs that use page number indexing in their queries (e.g. page=1, page=2, ... in the URL)​. It increments the page number on each request.

Parameters
`base_page` (int, optional): The starting page index as expected by the API​. This defines what number represents the first page (commonly 0 or 1). Default is 0.
`page` (int, optional): The page number for the first request. If not provided, it defaults to the value of base_page​. (Typically you either use base_page to set the start, or directly give an initial page number.)
`page_param` (str, optional): The query parameter name used for the page number​. Default is "page".
`total_path` (str or None, optional): JSONPath to the total number of pages (or total items) in the response​. If the API provides a total page count or total item count, you can specify its JSON field (e.g. "total_pages"). Defaults to "total" (common key for total count)​. If set to None or not present, the paginator will rely on other stopping criteria.
`maximum_page` (int, optional): The maximum page number to request​. If provided, pagination will stop once this page is reached (useful to limit page count during testing or to avoid excessive requests).
`stop_after_empty_page` (bool, optional): Whether to stop when an empty page is encountered (no results)​. Default is True. If False, you should ensure there is another stop condition (like total_path or maximum_page) to prevent infinite loops.

For example, if a response is:
```json
{
  "items": [ ... ],
  "total_pages": 10
}
```
the paginator knows there are 10 pages in total​ and will not go beyond that. If the API does not provide a total count of pages, PageNumberPaginator will paginate until an empty result page is returned by default​. You can also manually limit pages by maximum_page if needed (e.g., stop after page 5). Setting stop_after_empty_page=False can force it to continue even through empty pages, but then you must have a total_path or maximum_page to avoid infinite loops​


When to Use
Use `page_number` for APIs that indicate pagination through a page number parameter. Clues include endpoints documented like /resource?page=1, /resource?page=2, etc., or the presence of terms like "page" or "page_number" in the API docs. Often, the response will include something like a "total_pages" field or a "page" field in the payload to help manage pagination. For example:
```
GET https://api.example.com/items?page=1
```
Response:
```json
{
  "items": [ ... ],
  "total_pages": 10,
  "page": 1
}
```

In this scenario, the presence of "page" in the request and a total count of pages in the response suggests using a page-number-based paginator​. Choose `page_number` when the API paginates by page index. It will increment the page number on each call. Be mindful of whether the first page is indexed as 0 or 1 in that API (set base_page accordingly). If a total page count is given (e.g., "total_pages" or "last_page"), pass the appropriate JSON path via total_path so the paginator knows when to stop. If no total count is given, the paginator will stop when no more data is returned (or when you hit a maximum_page if you set one).

`cursor`
Description: Paginator for APIs that use a cursor or token in the JSON response to indicate the next page. The next cursor value is extracted from the response body and passed as a query parameter in the subsequent request​

Parameters
`cursor_path` (str, optional): JSONPath to the cursor/token in the response JSON​. Defaults to "cursors.next", which corresponds to a common pattern where the JSON has a "cursors" object with a "next" field.
`cursor_param` (str, optional): The name of the query parameter to send the cursor in for the next request​. Defaults to "after". This is the parameter that the API expects on the URL (or body) to fetch the next page (for example, many APIs use ?after=<token> or ?cursor=<token> in the query string).

When to Use
Use `cursor` when the API provides a continuation token or cursor in the JSON response rather than a direct URL. This is common in APIs where responses include a field like "next_cursor", "next_page_token", or a nested structure for cursors. For example, a response might look like:
```json
{
  "records": [ ... ],
  "cursors": {
    "next": "cursor_string_for_next_page"
  }
}
```

In this case, the value "cursor_string_for_next_page" is a token that the client must send in the next request to get the following page of results. The documentation might say something like “use the next cursor from the response for the next page, via a cursor query parameter.” Indicators for this paginator:
The presence of a field in the JSON that looks like a cryptic token (often base64 or long string) for pagination.
API docs using terminology like “cursor”, “continuation token”, “next token”, or showing request examples with parameters such as after, nextToken, cursor, etc.
Choose JSONResponseCursorPaginator if the API’s pagination is driven by such tokens in the response body. You will configure cursor_path to point at the JSON field containing the token (e.g. "cursors.next" as default, or "next_cursor", etc.), and cursor_param to the name of the query parameter the API expects (commonly "cursor" or "after"). The paginator will then automatically extract the token and append it as ?cursor=<token> (or your specified param name) on subsequent calls​



> Source: `docs/data_engineering/dlt/github_api_init/CLAUDE.md`

# Rules

## Build the REST API config with cursor-based pagination

## Prerequisities to writing a source

1. VERY IMPORTANT. When writing a new source, you should have an example available in the rest_api_pipeline.py file. 
Use this example or the github rest api source example from dlt's documentation on rest api for the general structure of the code. If you do not see this file rest_api_pipeline.py, ask the user to add it
2. Recall OpenAPI spec. You will figure out the same information that the OpenAPI spec contains for each API.
3. In particular:
- API base url
- type of authentication
- list of endpoints with method GET (you can read data for those)
4. You will figure out additional information that is required for successful data extraction
- type of pagination
- if data from an endpoint can be loaded incrementally
- unwrapping end user data from a response
- write disposition of the endpoint: append, replace, merge
- in case of merge, you need to find primary key that can be compound
5. Some endpoints take data from other endpoints. For example, in the github rest api source example from dlt's documentation, the `comments` endpoint needs `post id` to get the list of comments per particular post. You'll need to figure out such connections
6. **ASK USER IF YOU MISS CRUCIAL INFORMATION** You will make sure the user has provided you with enough information to figure out the above. Below are the most common possibilities
- open api spec (file or link)
- any other api definition, for example Airbyte low code yaml
- a source code in Python, java or c# of such connector or API client
- a documentation of the api or endpoint
7. In case you find more than 10 endpoints and you do not get instructions which you should add to the source, ask user.
8. Make sure you use the right pagination and use exactly the arguments that are available in the pagination guide. do not try to guess anything. remember that we have many paginator types that are configured differently
9. When creating pipeline instance add progress="log" as parameter `pipeline = dlt.pipeline(..., progress="log")`
10. When fixing a bug report focus only on a single cause. ie. incremental, pagination or authentication or wrong dict fields
11. You should have references for paginator types, authenticator types and general reference for rest api in you context. **DO NOT GUESS. DO NOT INVENT CODE. YOU SHOULD HAVE DOCUMENTATION FOR EVERYTHING YOU NEED. IF NOT - ASK USER**


## Look for Required Client Settings
When scanning docs or legacy code, first extract the API-level configuration including:

Base URL:
• The API's base URL (e.g. "https://api.pipedrive.com/").

Authentication:
• The type of authentication used (commonly "api_key" or "bearer").
• The name/key (e.g. "api_token") and its placement (usually in the query).
• Use secrets (e.g. dlt.secrets["api_token"]) to keep credentials secure.

Headers (optional):
• Check if any custom headers are required.

## Authentication Methods
Configure the appropriate authentication method:

API Key Authentication:
```python
"auth": {
    "type": "api_key",
    "name": "api_key",
    "api_key": dlt.secrets["api_key"],
    "location": "query"  # or "header"
}
```

Bearer Token Authentication:
```python
"auth": {
    "type": "bearer",
    "token": dlt.secrets["bearer_token"]
}
```

Basic Authentication:
```python
"auth": {
    "type": "basic",
    "username": dlt.secrets["username"],
    "password": dlt.secrets["password"]
}
```

OAuth2 Authentication:
```python
"auth": {
    "type": "oauth2",
    "token_url": "https://auth.example.com/oauth/token",
    "client_id": dlt.secrets["client_id"],
    "client_secret": dlt.secrets["client_secret"],
    "scopes": ["read", "write"]
}
```

## Find right pagination type
These are the available paginator types to be used in `paginator` field of `endpoint`:

* `json_link`: The link to the next page is in the body (JSON) of the response
* `header_link`: The links to the next page are in the response headers
* `offset`: The pagination is based on an offset parameter, with the total items count either in the response body or explicitly provided
* `page_number`: The pagination is based on a page number parameter, with the total pages count either in the response body or explicitly provided
* `cursor`: The pagination is based on a cursor parameter, with the value of the cursor in the response body (JSON)
* `single_page`: The response will be interpreted as a single-page response, ignoring possible pagination metadata


## Different Paginations per Endpoint are possible
When analyzing the API documentation, carefully check for multiple pagination strategies:

• Different Endpoint Types:
  - Some endpoints might use cursor-based pagination
  - Others might use offset-based pagination
  - Some might use page-based pagination
  - Some might use link-based pagination

• Documentation Analysis:
  - Look for sections describing different pagination methods
  - Check if certain endpoints have special pagination requirements
  - Verify if pagination parameters differ between endpoints
  - Look for examples showing different pagination patterns

• Implementation Strategy:
  - Configure pagination at the endpoint level rather than globally
  - Use the appropriate paginator type for each endpoint
  - Document which endpoints use which pagination strategy
  - Test pagination separately for each endpoint type

## Select the right data from the response
In each endpoint the interesting data (typically an array of objects) may be wrapped
differently. You can unwrap this data by using `data_selector`

Data Selection Patterns:
```python
"endpoint": {
    "data_selector": "data.items.*",  # Basic array selection
    "data_selector": "data.*.items",  # Nested array selection
    "data_selector": "data.{id,name,created_at}",  # Field selection
}
```

## Resource Defaults & Endpoint Details
Ensure that the default settings applied across all resources are clearly delineated:

Defaults:
• Specify the default primary key (e.g., "id").
• Define the write disposition (e.g., "merge").
• Include common endpoint parameters (for example, a default limit value like 50).

Resource-Specific Configurations:
• For each resource, extract the endpoint path, method, and any additional query parameters.
• If incremental loading is supported, include the minimal incremental configuration (using fields like "start_param", "cursor_path", and "initial_value"), but try to keep it within the REST API config portion.

## Incremental Loading Configuration
Configure incremental loading for efficient data extraction. Your task is to get only new data from
the endpoint.

Typically you will identify query parameter that allows to get items that are newer than certain date:

```py
{
    "path": "posts",
    "data_selector": "results",
    "params": {
        "created_since": "{incremental.start_value}",  # Uses cursor value in query parameter
    },
    "incremental": {
        "cursor_path": "created_at",
        "initial_value": "2024-01-25T00:00:00Z",
    },
}
```


## End to end example
Below is an annotated template that illustrates how your output should look. Use it as a reference to guide your extraction:

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# Build the REST API config with cursor-based pagination
source = rest_api_source({
    "client": {
        "base_url": "https://api.pipedrive.com/",  # Extract this from the docs/legacy code
        "auth": {
            "type": "api_key",                    # Use the documented auth type
            "name": "api_token",
            "api_key": dlt.secrets["api_token"],    # Replace with secure token reference
            "location": "query"                     # Typically a query parameter for API keys
        }
    },
    "resource_defaults": {
        "primary_key": "id",                        # Default primary key for resources
        "write_disposition": "merge",               # Default write mode
        "endpoint": {
            "params": {
                "limit": 50                         # Default query parameter for pagination size
            }
        }
    },
    "resources": [
        {
            "name": "deals",                        # Example resource name extracted from code or docs
            "endpoint": {
                "path": "v1/recents",               # Endpoint path to be appended to base_url
                "method": "GET",                    # HTTP method (default is GET)
                "params": {
                    "items": "deal"
                    "since_timestamp": "{incremental.start_value}"
                },
                "data_selector": "data.*",          # JSONPath to extract the actual data
                "paginator": {                      # Endpoint-specific paginator
                    "type": "offset",
                    "offset": 0,
                    "limit": 100
                },
                "incremental": {                    # Optional incremental configuration
                    "cursor_path": "update_time",
                    "initial_value": "2023-01-01 00:00:00"
                }
            }
        }
    ]
})

if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="pipedrive_rest",
        destination="duckdb",
        dataset_name="pipedrive_data"
    )
    pipeline.run(source)
```

## How to Apply This Rule
Extraction:
• Search both the REST API docs and any legacy pipeline code for all mentions of "cursor" or "pagination".
• Identify the exact keys and JSONPath expressions needed for the cursor field.
• Look for authentication requirements and rate limiting information.
• Identify any dependent resources and their relationships.
• Check for multiple pagination strategies across different endpoints.

Configuration Building:
• Assemble the configuration in a dictionary that mirrors the structure in the example.
• Ensure that each section (client, resource defaults, resources) is as declarative as possible.
• Implement proper state management and incremental loading where applicable.
• Configure rate limiting based on API requirements.
• Configure pagination at the endpoint level when multiple strategies exist.

Verification:
• Double-check that the configuration uses the REST API config keys correctly.
• Verify that no extraneous Python code is introduced.
• Test the configuration with mock responses.
• Verify rate limiting and error handling.
• Test pagination separately for each endpoint type.

Customization:
• Allow for adjustments (like modifying the "initial_value") where incremental loading is desired.
• Customize rate limiting parameters based on API requirements.
• Adjust batch sizes and pagination parameters as needed.
• Implement custom error handling and retry logic where necessary.
• Handle different pagination strategies appropriately.

## Guidelines

# Guidelines
1. dlt means "data load tool". It is an open source Python library installable via `pip install dlt`.
2. To create a new pipeline, use `dlt init <source> <destination>`.
3. The dlt library comes with the `dlt` CLI. Add the `--help` flag to any command to verify its specs. 
4. The preferred way to configure dlt (sources, resources, destinations, etc.) is to use `.dlt/config.toml` and `.dlt/secrets.toml`
5. During development, always set `dev_mode=True` when creating a dlt Pipeline. `pipeline = dlt.pipeline(..., dev_mode=True)`. This allows to reset the pipeline's schema and state between iterations.
6. Use type annotations only if you're certain you're properly importing the types.
7. Use dlt's REST API source if loading data from the web.
8. Use dlt's SQL source when loading data from an SQL database or backend.
9. Use dlt's filesystem source if loading data from files (CSV, PDF, Parquet, JSON, and more). This works for local filesystems and cloud buckets (AWS, Azure, GCP, Minio, etc.).

## REST API Parameter Extraction Guide

# REST API Parameter Extraction Guide

This rule helps identify and extract ALL necessary parameters from API documentation to build a dlt REST API source. **Crucially, configuration parameters like pagination and incremental loading can vary significantly between different API endpoints. Do not assume a single global strategy applies to all resources.**

## 1. Base Configuration Parameters (Client Level)

These settings usually apply globally but *can* sometimes be overridden at the resource level.

### Client Settings
Look for these in the API documentation (often in "Overview", "Getting Started", "Authentication"):
- **Base URL**:
  - Aliases: "API endpoint", "root URL", "service URL"
  - Example Format: `https://api.example.com/v1/`
  - Find the main entry point for the API version you need.

- **Authentication**:
  - Keywords: "Authentication", "Authorization", "API Keys", "Security"
  - Common Types & dlt Mappings:
    - API Key: Look for "API Key", "Access Token", "Secret Token", "Subscription Key". Map API key value to `api_key`, name to `name`, location (`query` or `header`) to `location`.
    - Bearer Token: Look for "Bearer Token", "JWT". Map token value to `token`.
    - OAuth2: Look for "OAuth", "Client ID", "Client Secret", "Scopes", "Token URL". Map to `client_id`, `client_secret`, `scopes`, `token_url`.
    - Basic Auth: Look for "Basic Authentication". Map to `username` and `password`.
  - Note where credentials go (header, query parameter, request body).
  - **Secret Handling:**
    - **Pattern 1: Using `@dlt.source` or `@dlt.resource` Decorators (Recommended when applicable):**
      Define your source/resource function with arguments having defaults like `api_key: str = dlt.secrets.value` or `client_secret: str = dlt.secrets["specific_key"]`. `dlt` injects the resolved secret when calling the decorated function. You can then use the argument variable directly.
      ```python
      @dlt.source
      def my_api_source(api_key: str = dlt.secrets.value):
          config = {...
              "auth": {"type": "api_key", "api_key": api_key, ...}
              ...
          }
          yield rest_api_source(config)
      ```
    - **Pattern 2: Calling `rest_api_source` Directly (Requires Explicit Resolution):**
      If calling `rest_api_source` *without* a `@dlt.source/resource` decorator on the calling function, you **must resolve the secret explicitly *before* creating the configuration dictionary**. Using `dlt.secrets.value` directly in the dictionary or as a default function argument *will not work* in this context.
      ```python
      def my_api_source_direct():
          # Resolve secret explicitly first
          actual_key = dlt.secrets["my_api_key"]
          
          config = {
              "client": {
                  "auth": {
                      "type": "api_key",
                      "api_key": actual_key, # Use resolved value
                      ...
                  }
              }
          }
          return rest_api_source(config)
      
      # Pipeline call
      pipeline.run(my_api_source_direct())
      ```

- **Global Headers** (Optional):
  - Keywords: "Headers", "Request Headers", "Required Headers"
  - Common Headers: `Accept: application/json`, `Content-Type: application/json`, `User-Agent`.
  - Look for any custom headers required for *all* requests (e.g., `X-Api-Version`). Resource-specific headers go in the resource config.

## 2. Resource / Endpoint Parameters

**Crucially, examine the documentation for EACH resource/endpoint individually.**

### Endpoint Configuration
For each endpoint/resource (e.g., `/users`, `/orders/{order_id}`), find:
- **Path**:
  - Keywords: "Endpoints", "Resources", "API Methods", "Routes"
  - Format: `/resource`, `/v1/resource`. Note any path parameters like `{id}`.
  - This path is appended to the `base_url`.

- **Method**:
  - Usually explicit: `GET`, `POST`, `PUT`, `DELETE`.
  - Default is `GET` if not specified.

- **Resource-Specific Query Parameters**:
  - Keywords: "Parameters", "Query Parameters", "Optional Parameters", "Filtering", "Sorting"
  - Examples:
    - Filtering: `status=active`, `type=customer`, `created_after=...`
    - Sorting: `sort=created_at`, `order=desc`
    - Fields: `fields=id,name,email` (for selecting specific fields)
  - **Note:** Pagination and incremental parameters are covered separately below, but are often listed here too.

- **Request Body** (for `POST`, `PUT`, `PATCH`):
  - Keywords: "Request Body", "Payload", "Data"
  - Note the expected structure (usually JSON).

### Data Selection (Response Parsing)
- Keywords: "Response", "Response Body", "Example Response", "Schema"
- **Identify the JSON path** to the list/array of actual data items within the response.
- Common patterns & dlt `data_selector`:
  - `{"data": [...]}` -> `data`
  - `{"results": [...]}` -> `results`
  - `{"items": [...]}` -> `items`
  - `{"data": {"records": [...]}}` -> `data.records`
  - Sometimes the root is the list: `[{...}, {...}]` -> `.` or `[*] `(or no selector needed)

## 3. Pagination Parameters (Check Per Endpoint!)

**APIs often use different pagination methods for different endpoints. Check EACH endpoint's documentation for its specific pagination details.**

- **Identify the Strategy**: Look for sections titled "Pagination", "Paging", "Handling Large Responses", or examples showing how to get the next set of results.
- **Common Strategies & dlt Mapping**:
  - **Cursor-based**:
    - Keywords: `cursor`, `next_cursor`, `next_page_token`, `continuation_token`, `after`, `marker`
    - Identify: Where is the *next* cursor value found in the response? (e.g., `pagination.next_cursor`, `meta.next`, `links.next.href`). Map this to `cursor_path`.
    - Identify: What is the *query parameter name* to send the next cursor? (e.g., `cursor`, `page_token`, `after`). Map this to `cursor_param`.
    - Identify: What is the parameter for page size? Map to `limit_param` (set this in `endpoint.params`, not the paginator dict).
    - dlt `type`: `cursor`
  - **Offset-based**:
    - Keywords: `offset`, `skip`, `start`, `startIndex`
    - Identify: Parameter name for the starting index/offset. Map to `offset_param`.
    - Identify: Parameter for page size/limit. Map to `limit_param`.
    - Identify: Optional path to total items count in response (e.g., `summary.total`, `total_count`). Map to `total_path`.
    - dlt `type`: `offset`
  - **Page-based**:
    - Keywords: `page`, `page_number`, `pageNum`
    - Identify: Parameter name for the page number. Map to `page_param`.
    - Identify: Parameter for page size/limit. Map to `limit_param`.
    - Identify: Optional path to total pages or total items in response. Map to `total_path`.
    - dlt `type`: `page`
  - **Link Header-based**:
    - Check response headers for a `Link` header (e.g., `Link: <url>; rel="next"`).
    - dlt `type`: `link_header`, `next_url_path`: `next` (usually)
  - **No Pagination**: Some simple endpoints (e.g., fetching a single item by ID, small config lists) might not be paginated.

- **Configure at Resource Level**: If pagination differs between endpoints, define the `paginator` dictionary within the specific resource's `endpoint` configuration in `dlt`, overriding the client/default level.

## 4. Incremental Loading Parameters (Check Per Endpoint!)

Look for ways to fetch only new or updated data since the last run. This also often varies by endpoint. **The `incremental` configuration dictionary *always* requires the `cursor_path` field to be defined, even if `start_param` is also used.**

- **Identify Strategy & Parameters**:
  - **Timestamp-based**:
    - Keywords: `since`, `updated_since`, `modified_since`, `start_time`, `from_date`
    - Identify: The query parameter name used to filter by time (Optional). Map to `start_param`.
    - Identify: The field *in the response items* that contains the relevant timestamp (e.g., `updated_at`, `modified_ts`, `last_activity_date`). **Map this to `cursor_path` (Required)**. `dlt` uses this path to find the value for the next incremental run's state.
    - Note the required date format.
  - **ID-based / Event-based**:
    - Keywords: `since_id`, `min_id`, `last_event_id`, `sequence_number`, `offset` (if used like a cursor)
    - Identify: The query parameter name used to filter by ID/sequence (Optional). Map to `start_param`.
    - Identify: The field *in the response items* containing the ID/sequence. **Map this to `cursor_path` (Required)**.
  - **Cursor-based (using pagination cursor)**:
    - Sometimes the pagination cursor itself can be used for incremental loading if it's persistent and ordered (less common, often needs verification).
    - Map the response cursor path to `cursor_path` (**Required**) and the query parameter to `start_param` (Optional).

- **Initial Value**: Determine a safe starting point (e.g., a specific date `"2023-01-01T00:00:00Z"`, `0` for IDs). Map to `initial_value`.
- **Optional End Param**: If the API supports filtering up to a certain point (e.g., `end_date`, `max_id`), identify the parameter name (map to `end_param`) and potentially a value (map to `end_value`).
- **Optional Conversion**: If the `cursor_path` value needs transformation before being used in `start_param` or `end_param`, define a function and map it to `convert`.
- **Configure at Resource Level**: Define the `incremental` dictionary within the specific resource's `endpoint` configuration if the strategy or fields differ from others.

## 5. Common Documentation Patterns & Examples

(Keep existing examples, they are helpful)

### Authentication Section
```markdown
## Authentication
To authenticate, include your API key in the `Authorization: Bearer <your_token>` header.
```

### Endpoint Documentation Example (with variations)
```markdown
## List Orders
GET /v2/orders

Fetches a list of orders. This endpoint uses offset-based pagination.

Query Parameters:
- limit (integer, optional, default: 50): Max items per page.
- offset (integer, optional, default: 0): Number of items to skip.
- status (string, optional): Filter by status (e.g., 'completed', 'pending').
```

```markdown
## Get Activity Stream
GET /activities/stream

Fetches recent activities. Uses cursor-based pagination.

Query Parameters:
- page_size (integer, optional, default: 100): Number of activities.
- next_page_cursor (string, optional): Cursor from the previous response's `meta.next_page` field.

Response:
{
  "activities": [...],
  "meta": {
    "next_page": "aabbccddeeff"
  }
}
```

## 6. Enhanced Parameter Mapping (API Terminology -> dlt Config)

Map diverse API documentation terms to consistent `dlt` parameters. Identify the API's term first, then find the corresponding `dlt` key.

```yaml
client:
  base_url:
    common_api_terms: ["Base URL", "API Endpoint", "Root URL", "Service URL"]
    dlt_parameter: "client.base_url"
    notes: "Include version path (e.g., /v1/)"
  
  auth:
    api_key_value:
      common_api_terms: ["API Key", "Access Token", "Secret", "Token", "Key"]
      dlt_parameter: "client.auth.api_key"
      notes: "Handled via Secret Handling patterns"
    
    api_key_param_name:
      common_api_terms: ["api_key", "token", "key", "access_token"]
      dlt_parameter: "client.auth.name"
      notes: "Query param name or Header name"
    
    api_key_location:
      common_api_terms: ["Query parameter", "Header"]
      dlt_parameter: "client.auth.location"
      notes: "query or header"
    
    bearer_token:
      common_api_terms: ["Bearer Token", "JWT"]
      dlt_parameter: "client.auth.token"
      notes: "Handled via Secret Handling patterns"

pagination:
  note: "Define per-resource if strategies differ!"
  
  next_cursor_source:
    common_api_terms: ["next_cursor", "next_page", "nextToken", "marker"]
    dlt_parameter: "paginator.cursor_path"
    notes: "JSON path in response"
  
  next_cursor_param:
    common_api_terms: ["cursor", "page_token", "after", "next", "marker"]
    dlt_parameter: "paginator.cursor_param"
    notes: "Query param name to send cursor"
  
  offset_param:
    common_api_terms: ["offset", "skip", "start", "startIndex"]
    dlt_parameter: "paginator.offset_param"
    notes: "Query param name"
  
  page_number_param:
    common_api_terms: ["page", "page_number", "pageNum"]
    dlt_parameter: "paginator.page_param"
    notes: "Query param name"
  
  page_size_param:
    common_api_terms: ["limit", "per_page", "page_size", "count", "maxItems"]
    dlt_parameter: "paginator.limit_param"
    notes: "Query param name"
  
  total_items_source:
    common_api_terms: ["total", "total_count", "total_results", "count"]
    dlt_parameter: "paginator.total_path"
    notes: "Optional JSON path in response"
  
  link_header_relation:
    common_api_terms: ["next", "last"]
    dlt_parameter: "paginator.next_url_path"
    notes: "rel value in Link header"

incremental:
  note: "Define per-resource if strategies differ!"
  
  timestamp_param:
    common_api_terms: ["since", "updated_since", "modified_since", "from"]
    dlt_parameter: "incremental.start_param"
    notes: "Query param name"
  
  timestamp_source:
    common_api_terms: ["updated_at", "modified", "last_updated", "ts"]
    dlt_parameter: "incremental.cursor_path"
    notes: "JSON path in response item"
  
  id_sequence_param:
    common_api_terms: ["since_id", "min_id", "after_id", "sequence"]
    dlt_parameter: "incremental.start_param"
    notes: "Query param name"
  
  id_sequence_source:
    common_api_terms: ["id", "event_id", "sequence_id", "_id"]
    dlt_parameter: "incremental.cursor_path"
    notes: "JSON path in response item"
  
  initial_value:
    common_api_terms: ["N/A"]
    dlt_parameter: "incremental.initial_value"
    notes: "Start value for first run"

data:
  data_array_path:
    common_api_terms: ["data", "results", "items", "records", "entries"]
    dlt_parameter: "endpoint.data_selector"
    notes: "JSON path to the list of items"
```

## 7. Verification Checklist

Before finalizing the configuration:
1.  Verify Base URL format and version.
2.  Confirm Authentication method and *all* required parameters/headers.
3.  Verify Secret Handling pattern matches how the source is called.
4.  **For EACH resource:** Identify its specific pagination strategy (cursor, offset, page, link, none).
5.  **For EACH resource:** Extract the correct pagination parameters (`cursor_path`, `cursor_param`, `offset_param`, `page_param`, `limit_param` etc.) based on its strategy.
6.  **For EACH resource:** Determine if incremental loading is possible and identify its strategy (timestamp, ID, etc.).
7.  **For EACH resource:** Extract the correct incremental parameters (`cursor_path`, `initial_value`, `start_param`, etc.) based on its strategy.
8.  Validate the `data_selector` path for each resource by checking example responses.
9.  Check for any required Global Headers AND Resource-Specific Headers.

## dlt REST API Pagination Configuration Guide

# dlt REST API Pagination Configuration Guide
Use this rule when writing REST API Source to configure right pagination type for an Endpoint

This rule explains how to configure different pagination strategies for the `dlt` `rest_api` source. Understanding the API's specific pagination method is crucial for correct configuration.

If you are unsure what type of pagination to use due to lack of information from the api, consider curl-ing for responses (you can probably find credentials in secrets if needed)

We will use class based paginators and not declartive so if you search online in dlthub docs, make sure you do the right type

**Key Principle: Endpoint-Specific Pagination**

While you can set a default paginator at the `client` level, many APIs use *different* pagination methods for different endpoints. Always check the documentation for *each specific endpoint* you intend to load.

If an endpoint uses a different pagination method than the default, define its `paginator` configuration within that specific resource's `endpoint` section to override the client-level setting.

## DLT RESTClient Paginators Guide

To specify the pagination configuration, use the `paginator` field in the `client` or `endpoint` configurations. You should use a dictionary with a string alias in the `type` field along with the required parameters

#### Example

Suppose the API response for `https://api.example.com/posts` contains a `next` field with the URL to the next page:

```json
{
    "data": [
        {"id": 1, "title": "Post 1"},
        {"id": 2, "title": "Post 2"},
        {"id": 3, "title": "Post 3"}
    ],
    "pagination": {
        "next": "https://api.example.com/posts?page=2"
    }
}
```

You can configure the pagination for the `posts` resource like this:

```py
{
    "path": "posts",
    "paginator": {
        "type": "json_link",
        "next_url_path": "pagination.next",
    }
}
```

Currently, pagination is supported only for GET requests. To handle POST requests with pagination, you need to implement a custom paginator

These are the available paginator types to be used in `paginator` field:

* `json_link`: The link to the next page is in the body (JSON) of the response
* `header_link`: The links to the next page are in the response headers
* `offset`: The pagination is based on an offset parameter, with the total items count either in the response body or explicitly provided
* `page_number`: The pagination is based on a page number parameter, with the total pages count either in the response body or explicitly provided
* `cursor`: The pagination is based on a cursor parameter, with the value of the cursor in the response body (JSON)
* `single_page`: The response will be interpreted as a single-page response, ignoring possible pagination metadata


### Paginator arguments

#### json_link
Description: Paginator for APIs where the next page’s URL is included in the response JSON body (e.g. in a field like "next" or within a "pagination" object)​
dlthub.com

Parameters:
`next_url_path` (str, optional): JSONPath to the key in the response JSON that contains the next page URL​

When to Use
Use `json_link` when the API’s JSON response includes a direct link (URL) to the next page of results​

A common pattern is a field such as "next" or a nested key that holds the full URL for the next page. For example, an API might return a JSON structure like:
```json
{
  "data": [ ... ],
  "pagination": {
    "next": "https://api.example.com/posts?page=2"
  }
}
```

In the above, the "pagination.next" field provides the URL for the next page​

By specifying next_url_path="pagination.next", the `json_link` will extract that URL and request the next page automatically. This paginator is appropriate whenever the response body itself contains the next page URL, often indicated by keys like "next", "next_url", or a pagination object with a next link.

#### header_link

Description: Paginator for APIs where the next page’s URL is provided in an HTTP header (commonly the Link header with rel="next")​

Parameters
`links_next_key` (str, optional): The relation key in the Link response header that identifies the next page’s URL​. Default is "next". Example: If the header is Link: <https://api.example.com/items?page=2>; rel="next", the default links_next_key="next" will capture the URL for the next page.

When to Use
Use `header_link` when the API provides pagination links via HTTP headers rather than in the JSON body. This is common in APIs (like GitHub’s) that return a Link header containing URLs for next/prev pages. For example, an HTTP response might include:
```
Link: <https://api.example.com/items?page=2>; rel="next"
Link: <https://api.example.com/items?page=5>; rel="last"
```
In such cases, the `header_link` will parse the Link header, find the URL tagged with rel="next", and follow it​

You should use this paginator if the API documentation or responses indicate that pagination is controlled by header links. (Typically, look for a header named “Link” or similar, with URIs and relation types.) Note: By default, links_next_key="next" works for standard cases. If an API uses a different relation name in the Link header, you can specify that (e.g. HeaderLinkPaginator(links_next_key="pagination-next")).


#### offset
Description: Paginator for APIs that use numeric offset/limit parameters in query strings to paginate results​.
Each request fetches a set number of items (limit), and subsequent requests use an increasing offset.

Parameters
`limit` (int, required): The maximum number of items to retrieve per request (page size)​.
`offset` (int, optional): The starting offset for the first request​. Defaults to 0 (beginning of dataset).
`offset_param` (str, optional): Query parameter name for the offset value​. Default is "offset".
`limit_param` (str, optional): Query parameter name for the page size limit​. Default is "limit".
`total_path` (str or None, optional): JSONPath to the total number of items in the response. If provided, it helps determine when to stop pagination based on total count​. By default this is "total", assuming the response JSON has a field "total" for total item count. Use None if the API doesn’t return a total.
`maximum_offset` (int, optional): A cap on the maximum offset to reach​. If set, pagination stops when offset >= maximum_offset + limit.
`stop_after_empty_page` (bool, optional): Whether to stop when an empty page (no results) is encountered​. Defaults to True. If True, the paginator will halt as soon as a request returns zero items (useful for APIs that don’t provide a total count).
​
. To illustrate, if the first response looks like:
```json
{
  "items": [ ... ],
  "total": 1000
}
```
the paginator knows there are 1000 total items​
 and will continue until the offset reaches 1000 (or the final partial page). If the API does not provide a total count, OffsetPaginator will rely on getting an empty result page to stop by default​. You can also set maximum_offset to limit the number of items fetched (e.g., for testing, or if the API has an implicit max).

When to Use
Use `offset` for APIs that use offset-based pagination. Indicators include endpoint documentation or query parameters like offset (or skip/start) and limit(orpage_size`), and often a field in the response that gives the total count of items. For example, an API endpoint might be called as:
```
GET https://api.example.com/items?offset=0&limit=100
```
and return data with a structure like:
```json
{
  "items": [ ... ],
  "total": 1000
}
```
Here, the presence of offset/limit parameters and a "total" count in the JSON indicates offset-based pagination​. Choose `offset` when you see this pattern. This paginator will automatically increase the offset by the given limit each time, until it either reaches the total count (if known) or encounters an empty result set (if stop_after_empty_page=True). If the API lacks a total count and can continuously scroll, ensure you provide a stopping condition (like maximum_offset) or rely on an empty page to avoid infinite pagination.

#### page_number
Description: Paginator for APIs that use page number indexing in their queries (e.g. page=1, page=2, ... in the URL)​. It increments the page number on each request.

Parameters
`base_page` (int, optional): The starting page index as expected by the API​. This defines what number represents the first page (commonly 0 or 1). Default is 0.
`page` (int, optional): The page number for the first request. If not provided, it defaults to the value of base_page​. (Typically you either use base_page to set the start, or directly give an initial page number.)
`page_param` (str, optional): The query parameter name used for the page number​. Default is "page".
`total_path` (str or None, optional): JSONPath to the total number of pages (or total items) in the response​. If the API provides a total page count or total item count, you can specify its JSON field (e.g. "total_pages"). Defaults to "total" (common key for total count)​. If set to None or not present, the paginator will rely on other stopping criteria.
`maximum_page` (int, optional): The maximum page number to request​. If provided, pagination will stop once this page is reached (useful to limit page count during testing or to avoid excessive requests).
`stop_after_empty_page` (bool, optional): Whether to stop when an empty page is encountered (no results)​. Default is True. If False, you should ensure there is another stop condition (like total_path or maximum_page) to prevent infinite loops.

For example, if a response is:
```json
{
  "items": [ ... ],
  "total_pages": 10
}
```
the paginator knows there are 10 pages in total​ and will not go beyond that. If the API does not provide a total count of pages, PageNumberPaginator will paginate until an empty result page is returned by default​. You can also manually limit pages by maximum_page if needed (e.g., stop after page 5). Setting stop_after_empty_page=False can force it to continue even through empty pages, but then you must have a total_path or maximum_page to avoid infinite loops​


When to Use
Use `page_number` for APIs that indicate pagination through a page number parameter. Clues include endpoints documented like /resource?page=1, /resource?page=2, etc., or the presence of terms like "page" or "page_number" in the API docs. Often, the response will include something like a "total_pages" field or a "page" field in the payload to help manage pagination. For example:
```
GET https://api.example.com/items?page=1
```
Response:
```json
{
  "items": [ ... ],
  "total_pages": 10,
  "page": 1
}
```

In this scenario, the presence of "page" in the request and a total count of pages in the response suggests using a page-number-based paginator​. Choose `page_number` when the API paginates by page index. It will increment the page number on each call. Be mindful of whether the first page is indexed as 0 or 1 in that API (set base_page accordingly). If a total page count is given (e.g., "total_pages" or "last_page"), pass the appropriate JSON path via total_path so the paginator knows when to stop. If no total count is given, the paginator will stop when no more data is returned (or when you hit a maximum_page if you set one).

`cursor`
Description: Paginator for APIs that use a cursor or token in the JSON response to indicate the next page. The next cursor value is extracted from the response body and passed as a query parameter in the subsequent request​

Parameters
`cursor_path` (str, optional): JSONPath to the cursor/token in the response JSON​. Defaults to "cursors.next", which corresponds to a common pattern where the JSON has a "cursors" object with a "next" field.
`cursor_param` (str, optional): The name of the query parameter to send the cursor in for the next request​. Defaults to "after". This is the parameter that the API expects on the URL (or body) to fetch the next page (for example, many APIs use ?after=<token> or ?cursor=<token> in the query string).

When to Use
Use `cursor` when the API provides a continuation token or cursor in the JSON response rather than a direct URL. This is common in APIs where responses include a field like "next_cursor", "next_page_token", or a nested structure for cursors. For example, a response might look like:
```json
{
  "records": [ ... ],
  "cursors": {
    "next": "cursor_string_for_next_page"
  }
}
```

In this case, the value "cursor_string_for_next_page" is a token that the client must send in the next request to get the following page of results. The documentation might say something like “use the next cursor from the response for the next page, via a cursor query parameter.” Indicators for this paginator:
The presence of a field in the JSON that looks like a cryptic token (often base64 or long string) for pagination.
API docs using terminology like “cursor”, “continuation token”, “next token”, or showing request examples with parameters such as after, nextToken, cursor, etc.
Choose JSONResponseCursorPaginator if the API’s pagination is driven by such tokens in the response body. You will configure cursor_path to point at the JSON field containing the token (e.g. "cursors.next" as default, or "next_cursor", etc.), and cursor_param to the name of the query parameter the API expects (commonly "cursor" or "after"). The paginator will then automatically extract the token and append it as ?cursor=<token> (or your specified param name) on subsequent calls​



## Deployment Guides


> Source: `docs/data_engineering/dlt/dlt_modal/README.md`

Sign Up or Login to modal.com

Download and configure the Python client
Run this in order to install the Python library locally:

```
pip install modal
python3 -m modal setup
```

The first command will install the Modal client library on your computer, along with its dependencies.

The second command creates an API token by authenticating through your web browser. It will open a new tab, but you can close it when you are done.

follow the instructions in quick Start

Add dlt and github source to requirements: https://modal.com/docs/examples/webscraper#add-dependencies

```py
dlt_image = modal.Image.debian_slim(python_version="3.12").run_commands(
    "apt-get update",
    'pip install "dlt[bigquery]"',
).add_local_python_source("github_pipeline")
```


### Credentials

Secrets are attached directly to functions:
```py
@app.function(
    image=dlt_image,
    secrets=[modal.Secret.from_name("github-api")]
)
def run_pipeline(resource):
    ...
```

### Run locally
```shell
modal run github_pipeline_modal.py
```

### Backfilling
```shell
modal run github_pipeline_modal_backfill.py --start-date '2025-08-01 05:47:07+00:00' --end-date '2025-09-01 05:47:07+00:00'
```

### Deploy 
```shell
modal deploy --name github_scheduled github_pipeline_modal.py
```

### Deploy in parallel

```shell
modal deploy --name github_scheduled_parallel github_pipeline_modal_parallel.py
```

> Source: `docs/data_engineering/dlt/Deploy with Google Cloud Functions _ dlt Docs.md`

---
title: "Deploy with Google Cloud Functions | dlt Docs"
source: "https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-google-cloud-functions"
author:
published:
created: 2025-12-29
description: "How to deploy a pipeline with Google Cloud Functions"
tags:
  - "clippings"
---
Version: 1.20.0 (latest)

This guide shows you how to deploy a pipeline using the gcloud shell and dlt CLI commands. To deploy a pipeline using this method, you must have a working knowledge of GCP and its associated services, such as Cloud Functions, IAM and permissions, and GCP service accounts.

To deploy a pipeline with GCP Cloud Functions, navigate to the directory on your local machine or cloud repository (e.g., GitHub, Bitbucket) from where the function code is to be deployed.

## 1\. Setup pipeline

1. In this guide, we'll be setting up the dlt [Notion verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/notion). However, you can use any verified source or create a custom one to suit your needs.
2. In the terminal:
	- Run the following command to initialize the verified source with Notion and create a pipeline example with BigQuery as the target.
		```sh
		dlt init notion bigquery
		```
	- After the command executes, new files and folders with the necessary configurations are created in the main directory where the command was executed.
	- Detailed information about initializing a verified source and a pipeline example can be found in the dlthub [documentation](https://dlthub.com/docs/dlt-ecosystem/verified-sources/notion).
3. Create a new Python file called "main.py" in the main directory. The file can be configured as follows:
	```sh
	from notion_pipeline import load_databasesdef pipeline_notion(request):  load_databases()  return "Pipeline run successfully!"
	```
	By default, Google Cloud Functions looks for the "main.py" file in the directory.
4. If you need any additional dependencies, add them to the "requirements.txt" that was created.

## 2\. Deploying GCP Cloud Function

In the terminal, navigate to the directory where the "main.py" file is located and run the following command in the terminal:

```sh
gcloud functions deploy pipeline_notion --runtime python310 \  --trigger-http --allow-unauthenticated --source . --timeout 300
```
- This command uses a function called `pipeline_notion` with Python 3.10 as the runtime environment, an HTTP trigger, and allows unauthenticated access. The source "." refers to all files in the directory. The timeout is set to 5 minutes (300 seconds). To learn more about deploying the cloud function, read the [documentation here.](https://cloud.google.com/functions/docs/deploy)
- If you are uploading a large number of files to the destination, you can increase this to 60 minutes for HTTP functions and 10 minutes for event-driven functions. To learn more about the function timeout, see the [documentation here](https://cloud.google.com/functions/docs/configuring/timeout).

> Your project has a default service account associated with the project ID. Please assign the `Cloud Functions Developer` role to the associated service account.

## 3\. Setting up environmental variables in the Cloud Function

Environmental variables can be declared in the Cloud Function in two ways:

#### 3a. Directly in the function:

- Go to the Google Cloud Function and select the deployed function. Click "EDIT".
- Navigate to the "BUILD" tab and click "ADD VARIABLE" under "BUILD ENVIRONMENTAL VARIABLE".
- Enter a name for the variable that corresponds to the argument required by the pipeline. Make sure to capitalize the variable name if it is specified in "secrets.toml". For example, if the variable name is `api_key`, set the variable name to `API_KEY`.
- Enter the value for the Notion API key.
- Click Next and deploy the function.

#### 3b. Use GCP Secret Manager:

- Go to the Google Cloud function and select the function you deployed. Click "EDIT".
- In the "Runtime, Build, Connections and Security Settings" section, select "Security and Images Repo".
- Click "Add a secret reference" and select the secret you created, for example, "notion\_secret".
- Set the "Reference method" to "Mounted as environment variable".
- In the "Environment Variable" field, enter the environment variable's name that corresponds to the argument required by the pipeline. Remember to capitalize the variable name if it is required by the pipeline and specified in secrets.toml. For example, if the variable name is `api_key`, you would declare the environment variable as `API_KEY`.
- Finally, click "DEPLOY" to deploy the function. The HTTP trigger will now successfully execute the pipeline each time the URL is triggered.
- Assign the `Secret Manager Secret Accessor` role to the service account used to deploy the cloud function. Typically, this is the default service account associated with the Google Project in which the function is being created.

## 4\. Monitor (and manually trigger) the cloud function

To manually trigger the created function, you can open the trigger URL created by the Cloud Function in the address bar. The message "Pipeline run successfully!" confirms that the pipeline was successfully run and the data was successfully loaded into the destination.

That's it! Have fun using dlt in Google Cloud Functions!

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.

> Source: `docs/data_engineering/dlt/Deploy GCP Cloud Function as a webhook _ dlt Docs.md`

---
title: "Deploy GCP Cloud Function as a webhook | dlt Docs"
source: "https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-gcp-cloud-function-as-webhook"
author:
published:
created: 2025-12-29
description: "A webhook is a way for one application to send automated messages or data to another application in real time. Unlike traditional APIs, which require constant polling for updates, webhooks allow applications to push information instantly as soon as an event occurs. This event-driven architecture enables faster and more responsive interactions between systems, saving valuable resources and improving overall system performance."
tags:
  - "clippings"
---
Version: 1.20.0 (latest)

A webhook is a way for one application to send automated messages or data to another application in real time. Unlike traditional APIs, which require constant polling for updates, webhooks allow applications to push information instantly as soon as an event occurs. This event-driven architecture enables faster and more responsive interactions between systems, saving valuable resources and improving overall system performance.

With this `dlt` Google Cloud event ingestion webhook, you can ingest the data and load it to the destination in real time as soon as a post request is triggered by the webhook. You can use this cloud function as an event ingestion webhook on various platforms such as Slack, Discord, Stripe, PayPal, and any other as per your requirement.

You can set up a GCP cloud function webhook using `dlt` as follows:

## 1\. Initialize deployment

1. Sign in to your GCP account and enable the Cloud Functions API.
2. Go to the Cloud Functions section and click Create Function. Set up the environment and select the region.
3. Configure the trigger type; you can use any trigger, but for this example, we will use HTTP and select "Allow unauthenticated invocations".
4. Click "Save" and then "Next".
5. Select "Python 3.10" as the environment.
6. Use the code provided to set up the cloud function for event ingestion:
	```markdown
	import dltimport timefrom google.cloud import bigqueryfrom dlt.common import jsondef your_webhook(request):    # Extract relevant data from the request payload    data = request.get_json()    Event = [data]    pipeline = dlt.pipeline(        pipeline_name='platform_to_bigquery',        destination='bigquery',        dataset_name='webhooks',    )    pipeline.run(Event, table_name='webhook') #table_name can be customized    return 'Event received and processed successfully.'
	```
7. Set the function name as "your\_webhook" in the Entry point field.
8. In the requirements.txt file, specify the necessary packages:
	```markdown
	# Function dependencies, for example:# package>=versiondltdlt[bigquery]
	```
9. Click on "Deploy" to complete the setup.

> You can now use this cloud function as a webhook for event ingestion on various platforms such as Slack, Discord, Stripe, PayPal, and any other as per your requirement. Just remember to use the “Trigger URL” created by the cloud function when setting up the webhook. The Trigger URL can be found in the Trigger tab.

## 2\. Monitor (and manually trigger) the webhook

To manually test the function you have created, you can send a manual POST request as a webhook using the following code:

```sh
import requestswebhook_url = 'please set me up!' # Your cloud function Trigger URLmessage = {    'text': 'Hello, Slack!',    'user': 'dlthub',    'channel': 'dlthub'}response = requests.post(webhook_url, json=message)if response.status_code == 200:  print('Message sent successfully.')else:  print('Failed to send message. Error:', response.text)
```

> Replace the webhook\_url with the Trigger URL for the cloud function created. Now, after setting up the webhook using cloud functions, every time an event occurs, the data will be ingested into your specified destination.

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.

> Source: `docs/data_engineering/dlt/Deploy with Google Cloud Run _ dlt Docs.md`

---
title: "Deploy with Google Cloud Run | dlt Docs"
source: "https://dlthub.com/docs/walkthroughs/deploy-a-pipeline/deploy-with-google-cloud-run"
author:
published:
created: 2025-12-29
description: "Step-by-step guide on deploying a pipeline with Google Cloud Run."
tags:
  - "clippings"
---
Version: 1.20.0 (latest)

This guide explains how to deploy a pipeline using the gcloud shell and dlt CLI commands. To deploy a pipeline using this method, you must have a working knowledge of GCP and its associated services, such as Cloud Run jobs, IAM and permissions, and GCP service accounts.

Deploy the pipeline using Google Cloud Run jobs. First, navigate to the directory on your local machine or cloud repository (e.g., GitHub, Bitbucket) where you want to create the function code for deployment.

## 1\. Setup pipeline

1. In this guide, we set up the dlt [Notion verified source](https://dlthub.com/docs/dlt-ecosystem/verified-sources/notion). However, you can use any verified source or create a custom one.
2. Run the following command to initialize the verified source with Notion and create a pipeline example with BigQuery as the target.
	```sh
	dlt init notion bigquery
	```
	- After the command executes, new files and folders with the necessary configurations are created in the main directory.
	- Detailed information about initializing a verified source and a pipeline example is available in the dlthub [documentation](https://dlthub.com/docs/dlt-ecosystem/verified-sources/notion).
3. Create a new file named "Procfile" in the main directory and configure it as follows:
	```sh
	web: python3 notion_pipeline.py
	```
	This instructs the Cloud Run job to run "notion\_pipeline.py", using python3.
4. If you need any additional dependencies, add them to the "requirements.txt" that was created.

## 2\. Deploying GCP Cloud Run Jobs

In the terminal, navigate to the directory where the "notion\_pipeline.py" file is located and run the following command in the terminal:

```sh
gcloud run jobs deploy notion-pipeline-job \    --source . \    --tasks 1 \    --max-retries 5 \    --cpu 4 \    --memory 4Gi \    --region us-central1 \    --project dlthub-sandbox
```
- This command creates a Cloud Run job. The source "." refers to all files in the directory. The number of vCPUs is set to 4 and memory 4GiB. You can tweak the parameters as per your requirement. To learn more about deploying the Cloud Run job, read the [documentation here.](https://cloud.google.com/run/docs/create-jobs#gcloud)
- By default, Cloud Run jobs have a 10-minute timeout, you can increase this up to 1440 minutes (24 hours). To learn more about the function timeout, see the [documentation here](https://cloud.google.com/run/docs/configuring/task-timeout).

> Your project has a default service account associated with the project ID. Please assign the `roles/run.invoker` role to the associated service account.

## 3\. Setting up environment variables in Cloud Run

Do not add secrets directly to the "secrets.toml" file, as it will be included in the deployed container for executing the job. Instead, use environment variables or Google Secrets Manager, as described below. Environment variables can be set in Cloud Run in two ways:

#### 3a. Directly in the function:

- Go to the Google Cloud Run job and select the deployed function. Click "VIEW AND EDIT JOB CONFIGURATION".
- In the "CONTAINERS" > "VARIABLE AND SECRETS" > "ADD VARIABLE".
- Enter a name for the variable according to the pipeline's requirements. Make sure to capitalize the variable name if it is specified in "secrets.toml". For example, if the variable name is `sources.notion.api_key`, set the variable name to `SOURCES__NOTION__API_KEY`.
- Enter the value for the Notion API key.
- Click "Done" and update the function.

#### 3b. Use GCP Secret Manager:

- Go to the Google Cloud Run job and select the deployed function. Click "VIEW AND EDIT JOB CONFIGURATION".
- In the "Containers" > "VARIABLE AND SECRETS" > "ADD VARIABLE".
- Click "Add a secret reference" and select the secret you created, for example, "notion\_secret".
- Set the "REFERENCE A SECRET" to mounted as an environment variable.
- In the "Environment Variable" field, enter the environment variable's name that corresponds to the argument required by the pipeline. Remember to capitalize the variable name if it is required by the pipeline and specified in secrets.toml. For example, if the variable name is `sources.notion.api_key`, you would declare the environment variable as `SOURCES__NOTION__API_KEY`.
- Select the secret to reference.
- Click "Done" and update the function.
- “Assign the Secret Manager Secret Accessor role to the Cloud Run service account. Typically, this is the default service account associated with the Google Project in which the function is being created.

## 4\. Monitor (and manually trigger) the Cloud Run

To manually trigger the job, click "EXECUTE". You can also set up a scheduled trigger to automate runs.

That's it! Have fun using dlt in Google Cloud Run!

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.

## Tool Integrations


> Source: `docs/data_engineering/dlt/Kafka _ dlt Docs.md`

---
title: "Kafka | dlt Docs"
source: "https://dlthub.com/docs/dlt-ecosystem/verified-sources/kafka"
author:
published:
created: 2025-12-20
description: "dlt verified source for Confluent Kafka"
tags:
  - "clippings"
---
Version: 1.20.0 (latest)

[Kafka](https://www.confluent.io/) is an open-source distributed event streaming platform, organized in the form of a log with message publishers and subscribers. The Kafka `dlt` verified source loads data using the Confluent Kafka API to the destination of your choice. See a [pipeline example](https://github.com/dlt-hub/verified-sources/blob/master/sources/kafka_pipeline.py).

The resource that can be loaded:

| Name | Description |
| --- | --- |
| kafka\_consumer | Extracts messages from Kafka topics |

## Setup guide

### Grab Kafka cluster credentials

1. Follow the [Kafka Setup](https://developer.confluent.io/get-started/python/#kafka-setup) to tweak a project.
2. Follow the [Configuration](https://developer.confluent.io/get-started/python/#configuration) to get the project credentials.

### Initialize the verified source

To get started with your data pipeline, follow these steps:

1. Enter the following command:
	```sh
	dlt init kafka duckdb
	```
	[This command](https://dlthub.com/docs/reference/command-line-interface) will initialize [the pipeline example](https://github.com/dlt-hub/verified-sources/blob/master/sources/kafka_pipeline.py) with Kafka as the [source](https://dlthub.com/docs/general-usage/source) and [duckdb](https://dlthub.com/docs/dlt-ecosystem/destinations/duckdb) as the [destination](https://dlthub.com/docs/dlt-ecosystem/destinations).
2. If you'd like to use a different destination, simply replace `duckdb` with the name of your preferred [destination](https://dlthub.com/docs/dlt-ecosystem/destinations).
3. After running this command, a new directory will be created with the necessary files and configuration settings to get started.

For more information, read the [Walkthrough: Add a verified source.](https://dlthub.com/docs/walkthroughs/add-a-verified-source)

### Add credentials

1. In the `.dlt` folder, there's a file called `secrets.toml`. It's where you store sensitive information securely, like access tokens. Keep this file safe.
	Use the following format for service account authentication:
```toml
[sources.kafka.credentials]
bootstrap_servers="web.address.gcp.confluent.cloud:9092"
group_id="test_group"
security_protocol="SASL_SSL"
sasl_mechanisms="PLAIN"
sasl_username="example_username"
sasl_password="example_secret"
```
1. Enter credentials for your chosen destination as per the [docs](https://dlthub.com/docs/dlt-ecosystem/destinations).

## Run the pipeline

1. Before running the pipeline, ensure that you have installed all the necessary dependencies by running the command:
	```sh
	pip install -r requirements.txt
	```
2. You're now ready to run the pipeline! To get started, run the following command:
	```sh
	python kafka_pipeline.py
	```
3. Once the pipeline has finished running, you can verify that everything loaded correctly by using the following command:
	```sh
	dlt pipeline <pipeline_name> show
	```

For more information, read the [Walkthrough: Run a pipeline](https://dlthub.com/docs/walkthroughs/run-a-pipeline).

## Sources and resources

`dlt` works on the principle of [sources](https://dlthub.com/docs/general-usage/source) and [resources](https://dlthub.com/docs/general-usage/resource).

### Source kafka\_consumer

This function retrieves messages from the given Kafka topics.

```markdown
@dlt.resource(name="kafka_messages", table_name=lambda msg: msg["_kafka"]["topic"])
def kafka_consumer(
    topics: Union[str, List[str]],
    credentials: Union[KafkaCredentials, Consumer] = dlt.secrets.value,
    msg_processor: Optional[Callable[[Message], Dict[str, Any]]] = default_msg_processor,
    batch_size: Optional[int] = 3000,
    batch_timeout: Optional[int] = 3,
    start_from: Optional[TAnyDateTime] = None,
) -> Iterable[TDataItem]:
   ...
```

`topics`: A list of Kafka topics to be extracted.

`credentials`: By default, it is initialized with the data from the `secrets.toml`. It may be used explicitly to pass an initialized Kafka Consumer object.

`msg_processor`: A function that will be used to process every message read from the given topics before saving them in the destination. It can be used explicitly to pass a custom processor. See the [default processor](https://github.com/dlt-hub/verified-sources/blob/fe8ed7abd965d9a0ca76d100551e7b64a0b95744/sources/kafka/helpers.py#L14-L50) as an example of how to implement processors.

`batch_size`: The number of messages to extract from the cluster at once. It can be set to tweak performance.

`batch_timeout`: The maximum timeout (in seconds) for a single batch reading operation. It can be set to tweak performance.

`start_from`: A timestamp, starting from which the messages must be read. When passed, `dlt` asks the Kafka cluster for an offset, which is actual for the given timestamp, and starts to read messages from this offset.

## Customization

### Create your own pipeline

1. Configure the pipeline by specifying the pipeline name, destination, and dataset as follows:
	```markdown
	pipeline = dlt.pipeline(
	     pipeline_name="kafka",     # Use a custom name if desired
	     destination="duckdb",      # Choose the appropriate destination (e.g., duckdb, redshift, post)
	     dataset_name="kafka_data"  # Use a custom name if desired
	)
	```
2. To extract several topics:
	```markdown
	topics = ["topic1", "topic2", "topic3"]
	resource = kafka_consumer(topics)
	pipeline.run(resource, write_disposition="replace")
	```
3. To extract messages and process them in a custom way:
	```markdown
	def custom_msg_processor(msg: confluent_kafka.Message) -> Dict[str, Any]:
	     return {
	         "_kafka": {
	             "topic": msg.topic(),  # required field
	             "key": msg.key().decode("utf-8"),
	             "partition": msg.partition(),
	         },
	         "data": msg.value().decode("utf-8"),
	     }
	 resource = kafka_consumer("topic", msg_processor=custom_msg_processor)
	 pipeline.run(resource)
	```
4. To extract messages, starting from a timestamp:
	```markdown
	resource = kafka_consumer("topic", start_from=pendulum.DateTime(2023, 12, 15))
	 pipeline.run(resource)
	```

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.

> Source: `docs/data_engineering/dlt/dlt - SQLMesh.md`

---
title: "dlt - SQLMesh"
source: "https://sqlmesh.readthedocs.io/en/stable/integrations/dlt/?h=dlt"
author:
published:
created: 2025-12-11
description:
tags:
  - "clippings"
---
[Skip to content](https://sqlmesh.readthedocs.io/en/stable/integrations/dlt/?h=dlt#dlt)

## dlt

SQLMesh enables efforless project generation using data ingested through [==dlt==](https://github.com/dlt-hub/dlt). This involves creating a baseline project scaffolding, generating incremental models to process the data from the pipeline's tables by inspecting its schema and configuring the gateway connection using the pipeline's credentials.

## Getting started

### Reading from a dlt pipeline

To load data from a ==dlt== pipeline into SQLMesh, ensure the ==dlt== pipeline has been run or restored locally. Then simply execute the sqlmesh `init` command *within the ==dlt== project root directory* using the `==dlt==` template option and specifying the pipeline's name with the `==dlt==-pipeline` option:

```js
$ sqlmesh init -t dlt --dlt-pipeline <pipeline-name> dialect
```

This will create the configuration file and directories, which are found in all SQLMesh projects:

- config.yaml
	- The file for project configuration. Refer to [configuration](https://sqlmesh.readthedocs.io/en/stable/reference/configuration/).
- ./models
	- SQL and Python models. Refer to [models](https://sqlmesh.readthedocs.io/en/stable/concepts/models/overview/).
- ./seeds
	- Seed files. Refer to [seeds](https://sqlmesh.readthedocs.io/en/stable/concepts/models/seed_models/).
- ./audits
	- Shared audit files. Refer to [auditing](https://sqlmesh.readthedocs.io/en/stable/concepts/audits/).
- ./tests
	- Unit test files. Refer to [testing](https://sqlmesh.readthedocs.io/en/stable/concepts/tests/).
- ./macros
	- Macro files. Refer to [macros](https://sqlmesh.readthedocs.io/en/stable/concepts/macros/overview/).

SQLMesh will also automatically generate models to ingest data from the pipeline incrementally. Incremental loading is ideal for large datasets where recomputing entire tables is resource-intensive. In this case utilizing the [`INCREMENTAL_BY_TIME_RANGE` model kind](https://sqlmesh.readthedocs.io/en/stable/concepts/models/model_kinds/#incremental_by_time_range). However, these model definitions can be customized to meet your specific project needs.

#### Specify the path to the pipelines directory

The default location for ==dlt== pipelines is `~/.==dlt==/pipelines/<pipeline_name>`. If your pipelines are in a [different directory](https://dlthub.com/docs/general-usage/pipeline#separate-working-environments-with-pipelines_dir), use the `--==dlt==-path` argument to specify the path explicitly:

```js
$ sqlmesh init -t dlt --dlt-pipeline <pipeline-name> --dlt-path <pipelines-directory> dialect
```

### Generating models on demand

To update the models in your SQLMesh project on demand, use the `==dlt==_refresh` command. This allows you to either specify individual tables to generate incremental models from or update all models at once.

- **Generate all missing tables**:
```js
$ sqlmesh dlt_refresh <pipeline-name>
```
- **Generate all missing tables and overwrite existing ones** (use with `--force` or `-f`):
```js
$ sqlmesh dlt_refresh <pipeline-name> --force
```
- **Generate specific ==dlt== tables** (using `--table` or `-t`):
```js
$ sqlmesh dlt_refresh <pipeline-name> --table <dlt-table>
```
- **Provide the explicit path to the pipelines directory** (using `--==dlt==-path`):
```js
$ sqlmesh dlt_refresh <pipeline-name> --dlt-path <pipelines-directory>
```

#### Configuration

SQLMesh will retrieve the data warehouse connection credentials from your ==dlt== project to configure the `config.yaml` file. This configuration can be modified or customized as needed. For more details, refer to the [configuration guide](https://sqlmesh.readthedocs.io/en/stable/guides/configuration/).

### Example

Generating a SQLMesh project ==dlt== is quite simple. In this example, we'll use the example `sushi_pipeline.py` from the [sushi- ==dlt== project](https://github.com/TobikoData/sqlmesh/tree/main/examples/sushi_dlt).

First, run the pipeline within the project directory:

```js
$ python sushi_pipeline.py
Pipeline sushi load step completed in 2.09 seconds
Load package 1728074157.660565 is LOADED and contains no failed jobs
```

After the pipeline has run, generate a SQLMesh project by executing:

```js
$ sqlmesh init -t dlt --dlt-pipeline sushi duckdb
```

Then the SQLMesh project is all set up. You can then proceed to run the SQLMesh `plan` command to ingest the ==dlt== pipeline data and populate the SQLMesh tables:

```js
$ sqlmesh plan
\`prod\` environment will be initialized

Models:
└── Added:
    ├── sushi_dataset_sqlmesh.incremental__dlt_loads
    ├── sushi_dataset_sqlmesh.incremental_sushi_types
    └── sushi_dataset_sqlmesh.incremental_waiters
Models needing backfill (missing dates):
├── sushi_dataset_sqlmesh.incremental__dlt_loads: 2024-10-03 - 2024-10-03
├── sushi_dataset_sqlmesh.incremental_sushi_types: 2024-10-03 - 2024-10-03
└── sushi_dataset_sqlmesh.incremental_waiters: 2024-10-03 - 2024-10-03
Apply - Backfill Tables [y/n]: y
[1/1] sushi_dataset_sqlmesh.incremental__dlt_loads evaluated in 0.01s
[1/1] sushi_dataset_sqlmesh.incremental_sushi_types evaluated in 0.00s
[1/1] sushi_dataset_sqlmesh.incremental_waiters evaluated in 0.01s
Evaluating models ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

All model batches have been executed successfully

Virtually Updating 'prod' ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 0:00:00

The target environment has been updated successfully
```

Once the models are planned and applied, you can continue as with any SQLMesh project, generating and applying [plans](https://sqlmesh.readthedocs.io/en/stable/concepts/overview/#make-a-plan), running [tests](https://sqlmesh.readthedocs.io/en/stable/concepts/overview/#tests) or [audits](https://sqlmesh.readthedocs.io/en/stable/concepts/overview/#audits), and executing models with a [scheduler](https://sqlmesh.readthedocs.io/en/stable/guides/scheduling/) if desired.

> Source: `docs/data_engineering/dlt/Explore data with marimo _ dlt Docs.md`

---
title: "Explore data with marimo | dlt Docs"
source: "https://dlthub.com/docs/general-usage/dataset-access/marimo"
author:
published:
created: 2025-12-09
description: "Explore your data with marimo"
tags:
  - "clippings"
---
Version: 1.19.1 (latest)

[marimo](https://github.com/marimo-team/marimo) is a reactive Python notebook. It completely revamps the Jupyter notebook experience. Whenever code is executed or you interact with a UI element, dependent cells are re-executed ensuring consistency between code and displayed outputs.

This page shows how dlt + marimo + [ibis](https://dlthub.com/docs/general-usage/dataset-access/ibis-backend) provide a rich environment to explore loaded data, write data transformations, and create data applications.

## Prerequisites

To install marimo and ibis with the duckdb extras, run the following command:

```sh
pip install marimo "ibis-framework[duckdb]"
```

## Launch marimo

Use this command to launch marimo (replace `my_notebook.py` with desired name). It will print a link to access the notebook web app.

```sh
marimo edit my_notebook.py

> Edit my_notebook.py in your browser 📝
>   ➜  URL: http://localhost:2718?access_token=Qfo_Hj2RbXqiqM4VT3XOwA
```

Here's a screenshot of the interface you should see:

![](https://dlthub.com/docs/assets/images/marimo_notebook-b12e23a23d11a80d938dfdf2814982ac.png)

## Features

### Use custom dlt widgets

Inside your marimo notebook, you can use widgets built and maintained by the dlt team.

Simply import them from `dlt.helpers.marimo` and pass them to the `render()` function. Note that `render()` is asynchronous and must be awaited with `await`.

```markdown
#%% cell 1
import marimo as mo
from dlt.helpers.marimo import render, load_package_viewer

#%% cell 2
await render(load_package_viewer)
```

![Example marimo widget](https://storage.googleapis.com/dlt-blog-images/marimo-widget-screenshot.png)

### View dataset tables and columns

After loading data with dlt, you can access it via the [dataset interface](https://dlthub.com/docs/general-usage/dataset-access/dataset), including a [native ibis connection](https://dlthub.com/docs/general-usage/dataset-access/ibis-backend).

In marimo, the **Datasources** panel provides a GUI to explore data tables and columns. When a cell contains a variable that's an ibis connection, it is automatically registered.

![](https://dlthub.com/docs/assets/images/marimo_dataset-147692752e667c08066a86e51fa005d4.png)

### Accessing data with SQL

Clicking on the **Add table to notebook** button will create a new SQL cell that you can use to query data. The output cell provides a rich and interactive results dataframe.

![](https://dlthub.com/docs/assets/images/marimo_sql-a28936601a41f5ff445fd4b75ddf6bc9.png)

### Accessing data with Python

You can also retrieve Ibis tables (lazy expressions) using Python. The **Datasources** panel will show under **Python** the output schema of your Ibis query, and the cell output will display detailed query planning.

Use `.execute()`, `.to_pandas()`, `.to_polars()`, or `.to_pyarrow()` to execute the Ibis expression and retrieve data that can displayed in a rich and interactive dataframe.

![](https://dlthub.com/docs/assets/images/marimo_python-74a6f55e32d9789f265444e191d1e161.png)

### Create a dashboard and data apps

marimo notebooks can be [deployed as web applications with interactive UI and charts](https://docs.marimo.io/guides/apps/) and the code hidden. Try adding [marimo UI input elements](https://docs.marimo.io/guides/interactivity/), rich markdown, and charts (matplotlib, plotly, altair, etc.). Combined, dlt + marimo + ibis make it easy to build a simple dashboard on top of fresh data.

- [Access loaded data in Python using dlt datasets](https://dlthub.com/docs/general-usage/dataset-access/dataset).
- [Learn about marimo dataframe and SQL features](https://docs.marimo.io/guides/working_with_data/)
- [Explore databases using the marimo GUI](https://docs.marimo.io/guides/coming_from/streamlit/)
- [Learn about marimo if you're coming from Streamlit](https://docs.marimo.io/guides/coming_from/streamlit/)

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.

> Source: `docs/data_engineering/dlt/Transformations _ dlt Docs.md`

---
title: "Transformations | dlt Docs"
source: "https://dlthub.com/docs/hub/features/transformations"
author:
published:
created: 2025-12-17
description: "Define Python-based or mixed SQL + Python transformations on data that is **already** in your destination."
tags:
  - "clippings"
---
Version: 1.20.0 (latest)

`dlt transformations` let you build new tables or full datasets from datasets that have *already* been ingested with `dlt`. `dlt transformations` are written and run in a very similar fashion to dlt source and resources. `dlt transformations` require you to have loaded data to a location, for example a local duckdb database, a bucket or a warehouse on which the transformations may be executed. `dlt transformations` are fully supported for all of our sql destinations including all filesystem and bucket formats.

You create them with the `@dlt.hub.transformation` decorator, which has the same signature as the `@dlt.resource` decorator but yields a SQL query, including the resulting column schema, rather than data items. dlt transformations support the same write\_dispositions per destination as dlt resources do.

## Motivations

A few real-world scenarios where dlt transformations can be useful:

- **Build one-stop reporting tables** – Flatten and enrich raw data into a wide table that analysts can pivot, slice, and dice without writing SQL each time.
- **Clean data** – Remove irrelevant columns or anonymize sensitive information before sending it to a layer with lower privacy protections.
- **Normalize JSON into 3-NF** – Break out repeating attributes from nested JSON so updates are consistent and storage isn't wasted.
- **Create dimensional (star-schema) models** – Produce fact and dimension tables so BI users can drag-and-drop metrics and break them down by any dimension.
- **Generate task-specific feature sets** – Deliver slim tables tailored for personalization, forecasting, or other ML workflows.
- **Apply shared business definitions** – Encode rules such as "a *sale* is a transaction whose status became *paid* this month," ensuring every metric is counted the same way.
- **Merge heterogeneous sources** – Combine Shopify, Amazon, WooCommerce (etc.) into one canonical *orders* feed for unified inventory and revenue reporting.
- **Run transformations during ingestion pre-warehouse** – Pre-aggregate or pre-filter data before it hits the warehouse to cut compute and storage costs.
- **…and more** – Any scenario where reshaping, enriching, or aggregating existing data unlocks faster insight or cleaner downstream pipelines.

## Quick-start in three simple steps

For the example below, you can copy–paste everything into one script and run it.

### 1\. Load some example data

The snippets below assume that we have a simple fruitshop dataset as produced by the dlt fruitshop template:

```markdown
import dlt
from dlt.destinations import duckdb
from dlt._workspace._templates._single_file_templates.fruitshop_pipeline import (
    fruitshop as fruitshop_source,
)

fruitshop_pipeline = dlt.pipeline(
    "fruitshop", destination=duckdb("./test_duck.duckdb"), dev_mode=True
)
fruitshop_pipeline.run(fruitshop_source())
```

### 2\. Inspect the dataset

```markdown
# Show row counts for every table
print(fruitshop_pipeline.dataset().row_counts().df())
```

### 3\. Write and run a transformation

```markdown
from typing import Any

@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    customers_table = dataset["customers"]
    yield customers_table.order_by("name").limit(5)

# Same pipeline & same dataset
fruitshop_pipeline.run(copied_customers(fruitshop_pipeline.dataset()))

# show rowcounts again, we now have a new table in the schema and the destination
print(fruitshop_pipeline.dataset().row_counts().df())
```

### 3.1 Alternatively use pure SQL for the transformation

```markdown
# Convert the transformation above that selected the first 5 customers to a sql query
@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    customers_table = dataset(
        """
        SELECT *
        FROM customers
        ORDER BY name
        LIMIT 5
    """
    )
    yield customers_table
```

That's it — `copied_customers` is now a new table in **the same** DuckDB schema with the first 5 customers when ordered by name. `dlt` has detected that we are loading into the same dataset and executed this transformation in SQL - no data was transferred to and from the machine executing this pipeline. Additionally, the new destination table `copied_customers` was automatically evolved to the correct new schema, and you could also set a different write disposition and even merge data from a transformation.

## Defining a transformation

```markdown
@dlt.hub.transformation(name="orders_per_user", write_disposition="merge")
def orders_per_user(dataset: dlt.Dataset) -> Any:
    purchases = dataset.table("purchases").to_ibis()
    yield purchases.group_by(purchases.customer_id).aggregate(
        order_count=purchases.id.count()
    )
```
- **Decorator arguments** mirror those accepted by `@dlt.resource`.
- The transformation function signature must contain at least one `dlt.Dataset` which is used inside the function to create the transformation SQL statements and calculate the resulting schema update.
- A transformation yields a `Relation` created with ibis expressions or a select query which will be materialized into the destination table. If the first item yielded is a valid sql query or relation object, data will be interpreted as a transformation. In all other cases, the transformation decorator will work like any other resource.

Below we load to the same DuckDB instance with a new pipeline that points to another `dataset`. dlt will be able to detect that both datasets live on the same destination and will run the transformation as pure SQL.

```markdown
import dlt
from dlt.destinations import duckdb

@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    customers_table = dataset["customers"]
    yield customers_table.order_by("name").limit(5)

# Same duckdb instance, different dataset
dest_p = dlt.pipeline(
    "fruitshop_dataset",
    destination=duckdb("./test_duck.duckdb"),
    dataset_name="copied_dataset",
    dev_mode=True,
)
dest_p.run(copied_customers(fruitshop_pipeline.dataset()))
```

Below we load the data from our local DuckDB instance to a Postgres instance. dlt will use the query to extract the data as Parquet files and will do a regular dlt load, pushing the data to Postgres. Note that you can use the exact same transformation functions for both scenarios. This can be extremely useful when you want to avoid compute costs in warehouses by running transformations directly from a local duckdb instance or raw data in a bucket into the warehouse, as the compute will happen on the machine executing the pipeline that runs the transformations.

```markdown
# Different engine (Postgres → DuckDB)
duck_p = dlt.pipeline("fruitshop_warehouse", destination="postgres")
duck_p.run(copied_customers(fruitshop_pipeline.dataset()))
```

## Using transformations

### Grouping multiple transformations in a source

`dlt transformations` can be grouped like all other resources into sources and will be executed together. You can even mix regular resources and transformations in one pipeline load.

```markdown
import dlt

@dlt.source
def my_transformations(dataset: dlt.Dataset) -> Any:
    @dlt.hub.transformation(write_disposition="append")
    def enriched_purchases(dataset: dlt.Dataset) -> Any:
        purchases = dataset.table("purchases").to_ibis()
        customers = dataset.table("customers").to_ibis()
        yield purchases.join(customers, purchases.customer_id == customers.id)

    @dlt.hub.transformation(write_disposition="replace")
    def total_items_sold(dataset: dlt.Dataset) -> Any:
        purchases = dataset.table("purchases").to_ibis()
        yield purchases.aggregate(total_qty=purchases.quantity.sum())

    return enriched_purchases(dataset), total_items_sold(dataset)

fruitshop_pipeline.run(my_transformations(fruitshop_pipeline.dataset()))
```

### Yielding multiple transformations from one transformation resource

`dlt transformations` may also yield more than one transformation instruction. If no further table name hints are supplied, the result will be a union of the yielded transformation instructions. `dlt` will take care of the necessary schema migrations, you will just need to ensure that no columns are marked as non-nullable that are missing from one of the transformation instructions:

```markdown
import dlt

# this (probably nonsensical) transformation will create a union of the customers and purchases tables
@dlt.hub.transformation(write_disposition="append")
def union_of_tables(dataset: dlt.Dataset) -> Any:
    yield dataset.table("purchases")
    yield dataset.table("customers")
```

### Supplying additional hints

You may supply column and table hints the same way you do for regular resources. `dlt` will derive schema hints from your query, but in some cases you may need to modify or extend them — for example, making columns nullable as in the example above, or adjusting the precision or type of a column to ensure compatibility with a specific target destination (if it differs from the source).

```markdown
import dlt

# change precision and scale of the price column
@dlt.hub.transformation(
    write_disposition="append", columns={"price": {"precision": 10, "scale": 2}}
)
def precision_change(dataset: dlt.Dataset) -> Any:
    yield dataset.inventory
```

### Writing your queries in SQL

If you prefer to write your queries in SQL, you can omit ibis expressions by simply creating a `Relation` from a query on your dataset:

```markdown
# Convert the transformation above that selected the first 5 customers to a sql query
@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    customers_table = dataset(
        """
        SELECT *
        FROM customers
        ORDER BY name
        LIMIT 5
    """
    )
    yield customers_table

# Joins and other more complex queries are also possible
@dlt.hub.transformation
def enriched_purchases(dataset: dlt.Dataset) -> Any:
    enriched_purchases = dataset(
        """
        SELECT customers.name, purchases.quantity
        FROM purchases
        JOIN customers
            ON purchases.customer_id = customers.id
        """
    )
    yield enriched_purchases

# You can even use a different dialect than the one used by the destination by supplying the dialect parameter
# dlt will compile the query to the right destination dialect
@dlt.hub.transformation
def enriched_purchases_postgres(dataset: dlt.Dataset) -> Any:
    enriched_purchases = dataset(
        """
        SELECT customers.name, purchases.quantity
        FROM purchases
        JOIN customers
            ON purchases.customer_id = customers.id
        """,
        query_dialect="duckdb",
    )
    yield enriched_purchases
```

The identifiers (table and column names) used in these raw SQL expressions must correspond to the identifiers as they are present in your dlt schema, NOT in your destination database schema.

## Using pandas dataframes or arrow tables

You can also write transformations directly using pandas or arrow. Note that in this case your transformation resource behaves like a regular resource: column-level hints will not be propagated, and `dlt` will simply treat the yielded dataframes or arrow tables like data from any other resource. This behavior may change in the future.

```markdown
@dlt.hub.transformation
def copied_customers(dataset: dlt.Dataset) -> Any:
    # get full customers table as arrow table
    customers = dataset.table("customers").arrow()

    # Sort the table by 'name'
    sorted_customers = customers.sort_by([("name", "ascending")])

    # Take first 5 rows
    yield sorted_customers.slice(0, 5)

# Example tables (replace with your actual data)
@dlt.hub.transformation
def enriched_purchases(dataset: dlt.Dataset) -> Any:
    # get both fully tables as dataframes
    purchases = dataset.table("purchases").df()
    customers = dataset.table("customers").df()

    # Merge (JOIN) the DataFrames
    result = purchases.merge(customers, left_on="customer_id", right_on="id")

    # Select only the desired columns
    yield result[["name", "quantity"]]
```

## Schema evolution and hints lineage

When executing transformations, `dlt` computes the resulting schema before the transformation is executed. This allows `dlt` to:

1. Migrate the destination schema accordingly, creating new columns or tables as needed
2. Fail early if there are schema mismatches that cannot be resolved
3. Preserve column-level hints from source to destination

### Schema evolution

For example, if your transformation joins two tables and creates new columns, `dlt` will automatically update the destination schema to accommodate these changes. If your transformation would result in incompatible schema changes (like changing a column's data type in a way that could lose data), `dlt` will fail before executing the transformation, protecting your data and saving execution and debug time.

You can inspect the computed result schema during development by looking at the result of `compute_columns_schema` on your `Relation`:

```markdown
# Show the computed schema before the transformation is executed
dataset = fruitshop_pipeline.dataset()
purchases = dataset.table("purchases").to_ibis()
customers = dataset.table("customers").to_ibis()
enriched_purchases = purchases.join(
    customers, purchases.customer_id == customers.id
)
print(dataset(enriched_purchases).columns)
```

### Column level hint forwarding

When creating or updating tables with transformation resources, `dlt` will also forward certain column hints to the new tables. In our fruitshop source, we have applied a custom hint named `x-annotation-pii` set to True for the `name` column, which indicates that this column contains PII (personally identifiable information). Downstream of the transformation layer, we may want to know which columns originate from columns that contain private data:

```markdown
@dlt.hub.transformation
def enriched_purchases(dataset: dlt.Dataset) -> Any:
    enriched_purchases = dataset(
        """
        SELECT customers.name, purchases.quantity
        FROM purchases
        JOIN customers
            ON purchases.customer_id = customers.id
        """
    )
    yield enriched_purchases

# Let's run the transformation and see that the name column in the NEW table is also marked as PII
fruitshop_pipeline.run(enriched_purchases(fruitshop_pipeline.dataset()))
assert (
    fruitshop_pipeline.dataset().schema.tables["enriched_purchases"]["columns"][
        "name"
    ][
        "x-annotation-pii"  # type: ignore
    ]
    is True
)
```

#### Features and limitations:

- `dlt` will only forward certain types of hints to the resulting tables: custom hints starting with `x-annotation...` and type hints such as `nullable`, `data_type`, `precision`, `scale`, and `timezone`. Other hints, such as `primary_key` or `merge_keys`, will need to be set via the `columns` argument on the transformation decorator, since `dlt` does not know how the transformed tables will be used.
- `dlt` cannot forward hints for columns that result from combining multiple origin columns, such as when they are concatenated or produced through other SQL operations.

## Lifecycle of a SQL transformation

In this section, we focus on the lifecycle of transformations that yield a `Relation` object, which we call SQL transformations here. This is in contrast to Python-based transformations that yield dataframes or arrow tables, which go through the regular extract, normalize, and load lifecycle of a `dlt` resource.

### Extract

In the extract stage, a `Relation` yielded by a transformation is converted into a SQL string and saved as a `.model` file along with its source SQL dialect. At this stage, the SQL string is just the user's original query — either the string that was explicitly provided or the one generated by `Relation.to_sql()`. No `dlt` -specific columns like `_dlt_id` or `_dlt_load_id` are added yet.

### Normalize

In the normalize stage, `.model` files are read and processed. The normalization process modifies your SQL queries to ensure they execute correctly and integrate with `dlt` 's features.

#### Adding dlt columns

During normalization, `dlt` adds internal `dlt` columns to your SQL queries depending on the configuration:

- `_dlt_load_id`, which tracks which load operation created or modified each row, is **added by default**. Even if present in your query, the `_dlt_load_id` column will be **replaced with a constant value** corresponding to the current load ID. To disable this behavior, set:
	```toml
	[normalize.model_normalizer]
	add_dlt_load_id = false
	```
	In this case, the column will not be added or replaced.
- `_dlt_id`, a unique identifier for each row, is **not added by default**. If your query already includes a `_dlt_id` column, it will be left unchanged. To enable automatic generation of this column when it’s missing, set:
	```toml
	[normalize.model_normalizer]
	add_dlt_id = true
	```
	When enabled and the column is not in the query, dlt will generate a `_dlt_id`. Note that if the column is already present, it will **not** be replaced.
	The `_dlt_id` column is generated using the destination's UUID function, such as `generateUUIDv4()` in ClickHouse. For dialects without native UUID support:
	- In **Redshift**, `_dlt_id` is generated using an `MD5` hash of the load ID and row number.
	- In **SQLite**, `_dlt_id` is simulated using `lower(hex(randomblob(16)))`.

#### Query transformations

The normalization process also applies the following transformations to ensure your queries work correctly:

1. Fully qualifies all identifiers with database and dataset prefixes
2. Quotes and adjusts identifier casing to match destination requirements
3. Normalizes column names according to the selected naming convention
4. Aliases columns and tables to handle naming convention differences
5. Reorders columns to match the destination table schema
6. Fills in `NULL` values for columns that exist in the destination but aren't in your query

### Load

In the load stage, the normalized queries from `.model` files are wrapped in INSERT statements and executed on the destination. For example, given this query from the extract stage:

```sql
SELECT
    "my_table"."id" AS "id",
    "my_table"."value" AS "value"
FROM "my_pipeline_dataset"."my_table" AS "my_table"
```

After the normalize stage processes it (adding dlt columns, wrapping in subquery, etc.) and results in:

```sql
SELECT
    _dlt_subquery."id" AS "id",
    _dlt_subquery."value" AS "value",
    '1749134128.17655' AS "_dlt_load_id",
    UUID() AS "_dlt_id"
FROM (
    SELECT
        "my_table"."id" AS "id",
        "my_table"."value" AS "value"
    FROM "my_pipeline_dataset"."my_table" AS "my_table"
    )
AS _dlt_subquery
```

The load stage executes:

```sql
INSERT INTO
    "my_pipeline_dataset"."my_transformation" ("id", "value", "_dlt_load_id", "_dlt_id")
SELECT
    _dlt_subquery."id" AS "id",
    _dlt_subquery."value" AS "value",
    '1749134128.17655' AS "_dlt_load_id",
    UUID() AS "_dlt_id"
FROM (
    SELECT
        "my_table"."id" AS "id",
        "my_table"."value" AS "value"
    FROM "my_pipeline_dataset"."my_table" AS "my_table"
    )
AS _dlt_subquery
```

The query is executed via the destination's SQL client, materializing the transformation result directly in the database.

## Examples

### Local in-transit transformations example

If you require aggregated or otherwise transformed data in your warehouse, but would like to avoid or reduce the costs of running queries across many rows in your warehouse tables, you can run some or all of your transformations "in transit" while loading data from your source. The code below demonstrates how you can extract data with our `rest_api` source to a local DuckDB instance and then forward aggregated data to a warehouse destination.

```markdown
from dlt.sources.rest_api import (
    rest_api_source,
)

# loads some data from our example api at https://jaffle-shop.scalevector.ai/docs
source = rest_api_source(
    {
        "client": {
            "base_url": "https://jaffle-shop.scalevector.ai/api/v1",
        },
        "resources": [
            "stores",
            {
                "name": "orders",
                "endpoint": {
                    "path": "orders",
                    "params": {
                        "start_date": "2017-01-01",
                        "end_date": "2017-01-31",
                    },
                },
            },
        ],
    }
)

# load to a local DuckDB instance
transit_pipeline = dlt.pipeline(
    "jaffle_shop", destination="duckdb", dataset_name="in_transit"
)
transit_pipeline.run(source)

# load aggregated data to a warehouse destination
@dlt.hub.transformation
def orders_per_store(dataset: dlt.Dataset) -> Any:
    orders = dataset.table("orders").to_ibis()
    stores = dataset.table("stores").to_ibis()
    yield (
        orders.join(stores, orders.store_id == stores.id)
        .group_by(stores.name)
        .aggregate(order_count=orders.id.count())
    )

# load aggregated data to a warehouse destination
warehouse_pipeline = dlt.pipeline(
    "jaffle_warehouse",
    destination="postgres",
    dataset_name="warehouse",
    dev_mode=True,
)
warehouse_pipeline.run(orders_per_store(transit_pipeline.dataset()))
```

This script demonstrates:

- Fetching data from a REST API using dlt's rest\_api\_source
- Loading raw data into a local DuckDB instance as an intermediate step
- Transforming the data by joining orders with stores and aggregating order counts directly on the local DuckDB instance, not in the destination warehouse
- Loading only the aggregated results to a production warehouse (Postgres)
- Reducing warehouse compute costs by performing transformations locally in DuckDB
- Using multiple pipelines in a single workflow for different stages of processing

### Incremental transformations example

```markdown
from dlt.pipeline.exceptions import PipelineNeverRan

@dlt.hub.transformation(
    write_disposition="append",
    primary_key="id",
)
def cleaned_customers(dataset: dlt.Dataset) -> Any:
    # get newest primary key from the output dataset
    max_pimary_key = -1
    try:
        output_dataset = dlt.current.pipeline().dataset()
        if output_dataset.schema.tables.get("cleaned_customers"):
            max_pimary_key_expr = (
                output_dataset.table("cleaned_customers").to_ibis().id.max()
            )
            max_pimary_key = output_dataset(max_pimary_key_expr).fetchscalar()
    except PipelineNeverRan:
        # we get this exception if the destination dataset has not been run yet
        # so we can assume that all customers are new
        pass

    # return filtered transformation
    customers_table = dataset.table("customers").to_ibis()

    # filter only new customers and exclude the name column in the result
    yield customers_table.filter(customers_table.id > max_pimary_key).drop(
        customers_table.name
    )

# create a warehouse dataset, would ordinarily be snowflake or some other warehousing destination
warehouse_pipeline = dlt.pipeline(
    "warehouse", destination="duckdb", dataset_name="cleaned_customers"
)
warehouse_pipeline.run(cleaned_customers(fruitshop_pipeline.dataset()))

# new items get added to the input dataset
# ...

# run the transformation again, only new customers are processed and appended to the destination table
warehouse_pipeline.run(cleaned_customers(fruitshop_pipeline.dataset()))
```

This example demonstrates how you can incrementally transform incoming new data for the customers table into a cleaned\_customers table where the name column has been removed. It:

- Uses primary key-based incremental loading to process only new data
- Tracks the highest ID processed so far to filter out already processed records
- Handles first-time runs with the PipelineNeverRan exception
- Removes sensitive data (name column) during the transformation
- Uses write\_disposition="append" to add only new records to the destination table
- Can be run repeatedly as new data arrives, processing only the delta

This demo works on codespaces. Codespaces is a development environment available for free to anyone with a Github account. You'll be asked to fork the demo repository and from there the README guides you with further steps.

The demo uses the Continue VSCode extension.

  
[Off to codespaces!](https://github.com/codespaces/new/dlt-hub/dlt-llm-code-playground?ref=create-pipeline)

## DHelp

## Ask a question

Welcome to "Codex Central", your next-gen help center, driven by OpenAI's GPT-4 model. It's more than just a forum or a FAQ hub – it's a dynamic knowledge base where coders can find AI-assisted solutions to their pressing problems. With GPT-4's powerful comprehension and predictive abilities, Codex Central provides instantaneous issue resolution, insightful debugging, and personalized guidance. Get your code running smoothly with the unparalleled support at Codex Central - coding help reimagined with AI prowess.

> Source: `docs/data_engineering/dlt/Load Datadog data in Python using dltHub.md`

---
title: "Load Datadog data in Python using dltHub"
source: "https://dlthub.com/workspace/source/datadog"
author:
published: 2025-07-15
created: 2025-12-29
description: "Build a Datadog-to-database or-dataframe pipeline in Python using dlt with automatic Cursor support."
tags:
  - "clippings"
---
![Datadog connector icon](https://dlthub.com/workspace/_next/image?url=https%3A%2F%2Fimg.logo.dev%2Fdatadoghq.com%3Ftoken%3Dpk_YkEESHvtSxKYU1570SChwA&w=256&q=75)

Build a Datadog-to-database or-dataframe pipeline in Python using dlt with automatic Cursor support.

In this guide, we'll set up a complete Datadog data pipeline from API credentials to your first data load in just 10 minutes. You'll end up with a fully declarative Python pipeline based on dlt's REST API connector, like in the partial example code below:

```
Example code@dlt.source
def datadog_source(access_token=dlt.secrets.value):
    config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.datadoghq.com/api/v1/",
            "auth": {
                "type": "bearer",
                "token": access_token,
            },
        },
        "resources": [
            "audit_logs",
            "dashboards",
            "incidents"
            ],
    }
    [...]
    yield from rest_api_resources(config)

def get_data() -> None:
    # Connect to destination
    pipeline = dlt.pipeline(
        pipeline_name='datadog_pipeline',
        destination='duckdb',
        dataset_name='datadog_data', 
    )
    # Load the data
    load_info = pipeline.run(datadog_source())
    print(load_info)
```

### Why use dltHub Workspace with LLM Context to generate Python pipelines?

- Accelerate pipeline development with AI-native context
- Debug pipelines, validate schemas and data with the integrated **Pipeline Dashboard**
- Build Python notebooks for end users of your data
- **Low maintenance** thanks to Schema evolution with type inference, resilience and self documenting REST API connectors. A shallow learning curve makes the pipeline easy to extend by any team member
- dlt is the tool of choice for Pythonic Iceberg Lakehouses, bringing mature data loading loading to pythonic Iceberg with or without catalogs

## What you’ll do

We’ll show you how to generate a readable and easily maintainable Python script that fetches data from datadog’s API and loads it into Iceberg, DataFrames, files, or a database of your choice. Here are some of the endpoints you can load:

- Audit Logs: Fetch logs for auditing purposes.
- Dashboards: Access and manage dashboards.
- Downtimes: Retrieve information on scheduled downtimes.
- Incident Teams: Manage teams involved in incident response.
- Incidents: Access incident information and details.
- Logs: Retrieve logs for monitoring and analysis.
- Metrics: Query and retrieve metrics data.
- Monitors: Access and manage monitors for various metrics.
- Service Level Objectives: Retrieve information on service level objectives.
- Synthetic Tests: Manage and retrieve synthetic test results.
- Users: Access user information and management.
- Series: Retrieve time series data.

You will then debug the Datadog pipeline using our Pipeline Dashboard tool to ensure it is copying the data correctly, before building a Notebook to explore your data and build reports.

## Setup & steps to follow

```
💡Before getting started, let's make sure Cursor is set up correctly:

We suggest using a model like Claude 3.7 Sonnet or better
Index the REST API Source tutorial: https://dlthub.com/docs/dlt-ecosystem/verified-sources/rest_api/ and add it to context as @dlt rest api

Read our full steps on setting up Cursor
```

Now you're ready to get started!

1. ⚙️ **Set up `dlt` Workspace**
	Install dlt with duckdb support:
	```
	pip install "dlt[workspace]"
	```
	Initialize a dlt pipeline with Datadog support.
	```
	dlt init dlthub:datadog duckdb
	```
	The `init` command will setup the necessary files and folders for the next step.
2. 🤠 **Start LLM-assisted coding**
	Here’s a prompt to get you started:
3. 🔒 **Set up credentials**
	Authentication requires both an API key and an application key to access the endpoints. The API key is provided in the header named 'DD-API-KEY'.
	To get the appropriate API keys, please visit the original source at [https://www.datadoghq.com/](https://www.datadoghq.com/). If you want to protect your environment secrets in a production environment, look into [setting up credentials with dlt](https://dlthub.com/docs/walkthroughs/add_credentials).
4. 🏃♀️ **Run the pipeline in the Python terminal in Cursor**
	```
	python datadog_pipeline.py
	```
	If your pipeline runs correctly, you’ll see something like the following:
	```
	Pipeline datadog load step completed in 0.26 seconds
	1 load package(s) were loaded to destination duckdb and into dataset datadog_data
	The duckdb destination used duckdb:/datadog.duckdb location to store data
	Load package 1749667187.541553 is LOADED and contains no failed jobs
	```
5. 📈 **Debug your pipeline and data with the Pipeline Dashboard**
	Now that you have a running pipeline, you need to make sure it’s correct, so you do not introduce silent failures like misconfigured pagination or incremental loading errors. By launching the dlt Workspace Pipeline Dashboard, you can see various information about the pipeline to enable you to test it. Here you can see:
	- Pipeline overview: State, load metrics
	- Data’s schema: tables, columns, types, hints
	- You can query the data itself
	```
	dlt pipeline datadog_pipeline show
	```
6. 🐍 **Build a Notebook with data explorations and reports**
	With the pipeline and data partially validated, you can continue with custom data explorations and reports. To get started, paste the snippet below into a new marimo Notebook and ask your LLM to go from there. Jupyter Notebooks and regular Python scripts are supported as well.
	```
	import dlt
	data = dlt.pipeline("datadog_pipeline").dataset()
	# get "audit_logs" table as Pandas frame
	data.audit_logs.df().head()
	```

## Running into errors?

While accessing the API, it's important to note that both API key and application key are required. Additionally, some endpoints may have rate limits that could affect the frequency of requests. Unauthorized access may occur if credentials are invalid, and permissions should be checked if access is forbidden.

### Extra resources:

- [Learn more with our 1h LLM-assisted coding course!](https://www.youtube.com/watch?v=GGid70rnJuM)

## Next steps

- [How to deploy a pipeline](https://dlthub.com/docs/walkthroughs/deploy-a-pipeline)
- [How to explore your data in marimo Notebooks](https://dlthub.com/docs/general-usage/dataset-access/marimo)
- [How to query your data in Python with dataset](https://dlthub.com/docs/general-usage/dataset-access/dataset)
- [How to create REST API Sources with Cursor](https://dlthub.com/docs/dlt-ecosystem/llm-tooling/cursor-restapi)

## Original Sources

- `docs/data_engineering/dlt/Deploy GCP Cloud Function as a webhook _ dlt Docs.md`
- `docs/data_engineering/dlt/Deploy with Google Cloud Functions _ dlt Docs.md`
- `docs/data_engineering/dlt/Deploy with Google Cloud Run _ dlt Docs.md`
- `docs/data_engineering/dlt/dlt - SQLMesh.md`
- `docs/data_engineering/dlt/dlt_modal/README.md`
- `docs/data_engineering/dlt/dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md`
- `docs/data_engineering/dlt/dlthub-codebase-analysis.md`
- `docs/data_engineering/dlt/dlthub.md`
- `docs/data_engineering/dlt/Explore data with marimo _ dlt Docs.md`
- `docs/data_engineering/dlt/github_api_init/AGENT.md`
- `docs/data_engineering/dlt/github_api_init/CLAUDE.md`
- `docs/data_engineering/dlt/github_api_init/COMPARISON_WITH_SOURCE_INIT.md`
- `docs/data_engineering/dlt/github_api_init/EXECUTIVE_SUMMARY.md`
- `docs/data_engineering/dlt/github_api_init/QUICK_REFERENCE.md`
- `docs/data_engineering/dlt/github_api_init/README_RESEARCH.md`
- `docs/data_engineering/dlt/github_api_init/RESEARCH_ANALYSIS.md`
- `docs/data_engineering/dlt/Kafka _ dlt Docs.md`
- `docs/data_engineering/dlt/KCG_SUMMARY.md`
- `docs/data_engineering/dlt/Load Datadog data in Python using dltHub.md`
- `docs/data_engineering/dlt/small-data-sf-2025/1_basics/README.md`
- `docs/data_engineering/dlt/small-data-sf-2025/elvis/presentation.md`
- `docs/data_engineering/dlt/small-data-sf-2025/README.md`
- `docs/data_engineering/dlt/Transformations _ dlt Docs.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
