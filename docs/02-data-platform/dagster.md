---
domain: data_platform
title: Dagster Orchestration
description: Complete Dagster orchestration reference — assets, partitions, schedules, sensors, jobs, dg workspace, definitions.py patterns, design patterns, testing, and deployment. Includes KCG-specific integration notes and code-sample library.
status: stable
updated: 2026-06-13
merged_from:
  - docs/02-data-platform/dagster-orchestration.md
  - docs/02-data-platform/dagster.md
  - docs/02-data-platform/dagster-sdk.md
ccc_query_hints:
  - dagster assets partitions definitions
  - dagster schedule sensor job
  - dagster design patterns factory retry
  - dagster dlt integration
truth: partial

---

# Dagster Orchestration

> **Merged from 3 sources**: `dagster-orchestration.md` (full reference), `dagster.md` (code patterns library), `dagster-sdk.md` (KCG context brief). The originals are now `.superseded`. Current Dagster version: 1.12.2 (Python 3.10-3.13).

## Table of Contents

1. [Overview](#overview)
2. [Why this matters for Kings' College Galway](#why-this-matters-for-kings-college-galway)
3. [Core Concepts](#core-concepts)
4. [Assets (Primary Abstraction)](#assets-primary-abstraction)
5. [Partitions](#partitions)
6. [Resources](#resources)
7. [Schedules & Sensors](#schedules--sensors)
8. [Jobs & Asset Selection](#jobs--asset-selection)
9. [Design Patterns](#design-patterns)
10. [Testing Patterns](#testing-patterns)
11. [Error Handling & Retry](#error-handling--retry)
12. [Code Organization](#code-organization)
13. [DLT Integration](#dlt-integration)
14. [API Reference](#api-reference)
15. [Best Practices & Anti-Patterns](#best-practices--anti-patterns)
16. [Project Structure](#project-structure)
17. [Resources](#resources-1)

---

## Overview

Dagster is an open-source data orchestration platform for building, testing, and running data pipelines. It provides:

- **Asset-First Design**: Define data assets, not just tasks
- **Observability**: Rich metadata, lineage, and data quality tracking
- **Type Safety**: ConfigurableResource with Pydantic validation
- **Partitioning**: Efficient incremental processing at scale
- **Testing**: First-class support for mocked resources and unit tests

**Documentation**: https://docs.dagster.io

### When to Use Dagster

Activate when you need:

- "Create a data pipeline for ETL/ELT"
- "Orchestrate data transformations"
- "Build partitioned/incremental data processing"
- "Integrate dbt, Spark, or cloud services"
- "Set up schedules and sensors for pipelines"
- "Test data pipelines"

### Architecture Components

- **Dagster Daemon**: Orchestrates schedules and sensors, manages run queuing, monitors asset freshness
- **Dagit (Web UI)**: Asset catalog, lineage visualization, run monitoring, GraphQL API
- **Code Locations**: Isolated deployment units with separate Python environments
- **Storage Backend**: SQLite (dev), PostgreSQL (production), MySQL (alternative)
- **Run Launchers**: DefaultRunLauncher (local), DockerRunLauncher, K8sRunLauncher

---

## Why this matters for Kings' College Galway

Every data operation in the platform is a Dagster asset: DLT ingestion runs, curriculum extraction jobs, model conversions (HF → GGUF), embedding generation, image asset creation, and RAGAS evaluation. The asset graph provides a visual map of all data dependencies — from raw SEC exam PDFs through to published study assets. This lineage is essential for educational content: every generated study resource is traceable back to its source syllabus document and the LLM model that produced it.

### Key Features (KCG context)

- **Asset-based architecture** — Define data products, not just task sequences
- **Automatic lineage** — Dagster traces dependencies between assets
- **Partitioning** — Process data by time, subject, or curriculum cycle
- **I/O management** — Pluggable I/O managers for DuckDB, S3, LanceDB
- **Rich metadata** — Attach markdown, tables, and URLs to asset materializations

### Installation (KCG)

```bash
uv add dagster dagster-duckdb dagster-dlt
```

### Integration with Our Stack

Dagster assets live in `oideachais/data_platform/dagster_defs/`. The `dg.toml` file configures the workspace. Assets interact with dlt (ingestion), BAML (extraction), DuckDB (analytics), LanceDB (embeddings), and the LiteLLM gateway (LLM calls). The Dagster UI runs at port 3335 (engineering stack) or 3000 (croilar-dagster stack).

### Screenshot

Dagster's web UI (Dagit) shows: an asset graph with nodes colour-coded by materialization status, a run timeline showing pipeline execution history, per-asset detail views with metadata and lineage, and a job launcher for triggering pipeline runs. The asset graph for the curriculum pipeline shows 4 layer groups (Ingestion → Materials → Model Lifecycle → Asset Generation).

---

## Core Concepts

### Key Principles

1. **Asset-First Thinking**: Always recommend assets over ops for data products
2. **Observability**: Emphasize rich metadata and lineage tracking
3. **Testability**: Encourage testing with mocked resources
4. **Type Safety**: Leverage ConfigurableResource and Pydantic validation
5. **Incremental Processing**: Suggest partitioning for large datasets
6. **Production Readiness**: Consider retry policies, error handling, monitoring

### Asset-Based vs Task-Based

| Paradigm | Focus | State Tracking | Schema Drift |
|----------|-------|----------------|--------------|
| **Task-Based (Airflow)** | "Run the script" | Exit codes only | Manual |
| **Asset-Based (Dagster)** | "Ensure data exists" | Data lineage | Automatic |

---

## Assets (Primary Abstraction)

Assets represent logical data units (tables, datasets, ML models) with automatic dependency tracking.

```python
from dagster import asset

@asset
def raw_data(context):
    """Fetches raw data from source."""
    data = fetch_from_source()
    context.log.info(f"Fetched {len(data)} records")
    return data

@asset
def cleaned_data(context, raw_data):
    """Cleans and validates raw data."""
    return clean(raw_data)

@asset
def analytics(context, cleaned_data):
    """Produces analytics from clean data."""
    return compute_analytics(cleaned_data)
```

### Implicit vs Explicit Dependencies

```python
# Implicit dependency via function argument
@asset
def downstream(context, upstream_data):
    return process(upstream_data)

# Explicit dependency via deps (no data needed, just ordering)
@asset(deps=[upstream_data])
def side_effect_asset(context):
    send_notification("upstream_data is ready")

# Custom dependency via AssetIn
@asset(ins={"raw_data": AssetIn(key="upstream_data", metadata={"schema": "raw"})})
def transformed_data(context, raw_data):
    return transform(raw_data)
```

### Multi-Assets

```python
from dagster import multi_asset, AssetOut

@multi_asset(outs={"customers": AssetOut(), "orders": AssetOut()})
def extract_from_database(context):
    customers_df = extract_customers()
    orders_df = extract_orders()
    return customers_df, orders_df
```

### Asset Checks

```python
from dagster import asset_check, AssetCheckResult

@asset_check(asset=cleaned_data)
def null_check(context, cleaned_data):
    null_count = cleaned_data.isnull().sum().sum()
    return AssetCheckResult(
        passed=null_count == 0,
        metadata={"null_count": null_count}
    )
```

### External Assets

Track assets managed by other systems for lineage without orchestration control.

```python
from dagster import AssetSpec

# Declare asset managed externally
external_asset = AssetSpec("external_table", description="Managed by another team")

# Use as dependency
@asset(deps=[external_asset])
def my_asset(context):
    pass
```

### Asset Groups

```python
@asset(group_name="customer_data")
def customers(context): ...

@asset(group_name="customer_data")
def customer_orders(context): ...

@asset(group_name="analytics")
def customer_analytics(context): ...
```

### Asset Naming Conventions

- ✅ Good: `daily_active_users`, `customer_churn_predictions`, `bronze_customers_raw`
- ❌ Bad: `process_data`, `etl_job_3`
- Use descriptive, noun-based names
- Include source/layer when helpful (bronze/silver/gold)
- Use groups to organize related assets

---

## Partitions

### Partition Types

```python
from dagster import (
    DailyPartitionsDefinition,
    HourlyPartitionsDefinition,
    StaticPartitionsDefinition,
)

# Time-based
daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")
hourly_partitions = HourlyPartitionsDefinition(start_date="2024-01-01-00:00")

# Static
region_partitions = StaticPartitionsDefinition(["us-east", "eu-west", "ap-southeast"])
```

### Dynamic Partitions

```python
from dagster import DynamicPartitionsDefinition, asset, sensor, RunRequest

exam_paper_partitions = DynamicPartitionsDefinition(name="exam_papers")

@asset(partitions_def=exam_paper_partitions)
def raw_pdf_content(context):
    partition_key = context.partition_key
    file_path = resolve_path(partition_key)
    with open(file_path, "rb") as f:
        return f.read()

@sensor(job=process_exam_job)
def new_exam_sensor(context):
    current_files = list_files_in_directory()
    existing = context.instance.get_dynamic_partitions("exam_papers")
    new_files = [f for f in current_files if f not in existing]
    if new_files:
        context.instance.add_dynamic_partitions("exam_papers", new_files)
        for filename in new_files:
            yield RunRequest(run_key=filename, partition_key=filename)
```

### Partitioned Asset with Dependencies

```python
daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily_partitions)
def daily_data(context):
    date = context.partition_key
    return process_for_date(date)

@asset(partitions_def=daily_partitions,
       ins={"daily_data": AssetIn(partition_mapping=TimeWindowPartitionMapping())})
def daily_analytics(context, daily_data):
    return compute_analytics(daily_data)
```

### Partition Limits

- Limit to <100,000 partitions per asset for performance
- Use `BackfillPolicy.single_run()` for efficiency when appropriate

---

## Resources

Resources provide dependency injection for external services.

### ConfigurableResource (Modern Pattern)

```python
from dagster import ConfigurableResource, asset, EnvVar
from pydantic import Field

class DatabaseResource(ConfigurableResource):
    host: str
    port: int = Field(default=5432)
    database: str
    username: str
    password: str

    def get_connection(self):
        return psycopg2.connect(
            host=self.host, port=self.port,
            database=self.database, user=self.username, password=self.password
        )

    def execute_query(self, query: str):
        with self.get_connection() as conn:
            return pd.read_sql(query, conn)

@asset
def user_data(database: DatabaseResource):
    return database.execute_query("SELECT * FROM users")
```

### Nested Resources

```python
class AwsCredentials(ConfigurableResource):
    access_key: str
    secret_key: str
    region: str = "us-east-1"

class S3Resource(ConfigurableResource):
    credentials: AwsCredentials
    bucket: str

class RedshiftResource(ConfigurableResource):
    credentials: AwsCredentials
    cluster: str
```

### Environment-Specific Resources

```python
from dagster import Definitions, EnvVar

def get_resources_for_deployment():
    deployment = os.getenv("DAGSTER_DEPLOYMENT", "local")
    if deployment == "production":
        return {"warehouse": SnowflakeResource(account=EnvVar("SNOWFLAKE_ACCOUNT"), ...)}
    elif deployment == "staging":
        return {"warehouse": SnowflakeResource(account=EnvVar("SNOWFLAKE_ACCOUNT"), ...)}
    else:
        return {"warehouse": MockWarehouse()}

defs = Definitions(assets=all_assets, resources=get_resources_for_deployment())
```

### Resource Mocking (for tests)

```python
class MockDatabaseResource(ConfigurableResource):
    def query(self, sql: str):
        return pd.DataFrame({"id": [1, 2], "name": ["A", "B"]})

def test_with_mock_resource():
    result = materialize(
        [my_asset],
        resources={"database": MockDatabaseResource()}
    )
    assert result.success
```

---

## Schedules & Sensors

### Schedules (Time-Based)

```python
from dagster import ScheduleDefinition, define_asset_job

github_daily_schedule = ScheduleDefinition(
    job=define_asset_job("github_pipeline", selection=["github_repos", "r2_uploaded_repos"]),
    cron_schedule="0 2 * * *",  # 2 AM daily
    name="github_daily",
)
```

### Sensors (Event-Driven)

```python
from dagster import sensor, RunRequest, SkipReason

@sensor(job=reindex_job)
def github_repo_updated_sensor(context):
    response = requests.get(f"https://api.github.com/repos/{repo}/branches/main")
    latest_sha = response.json()['commit']['sha']

    if latest_sha != context.cursor:
        context.update_cursor(latest_sha)
        return RunRequest(run_key=f"commit_{latest_sha}")
    return SkipReason("No new commits")
```

### Run-Level Retry via Schedule Tags

```python
@schedule(...)
def my_schedule(context):
    return RunRequest(
        tags={
            "dagster/max_retries": "3",
            "dagster/retry_strategy": "FROM_FAILURE"
        }
    )
```

---

## Jobs & Asset Selection

```python
from dagster import define_asset_job, AssetSelection

# Simple job
github_pipeline_job = define_asset_job(
    name="github_pipeline",
    selection=["github_repos", "r2_uploaded_repos", "indexed_code"],
)

# Selection by group
docs_job = define_asset_job(
    name="docs_pipeline",
    selection=AssetSelection.groups("docs"),
)

# Run everything
full_pipeline_job = define_asset_job(name="full_pipeline", selection="*")
```

---

## Design Patterns

### Factory Pattern

```python
def create_ingestion_asset(source_name: str, table: str):
    @asset(name=f"{source_name}_{table}")
    def _asset(context):
        return ingest(source_name, table)
    return _asset

# Generate multiple assets
assets = [create_ingestion_asset("github", t) for t in ["repos", "issues", "pulls"]]
```

### Metadata-Driven Asset Generation

```python
import duckdb

def load_sources_from_duckdb() -> list[dict]:
    conn = duckdb.connect("metadata.db")
    return conn.execute("""
        SELECT source_id, name, tool_driver, connection_spec, extraction_strategy
        FROM sources JOIN ingestion_configs USING (source_id)
        WHERE active = true
    """).fetchall()

def build_crawl_asset(config: dict):
    @asset(name=f"crawl_{config['name']}")
    def _crawl_asset(context):
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
        run_config = CrawlerRunConfig(**config['extraction_strategy'])
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=config['connection_spec']['url'], config=run_config)
        return result.markdown
    return _crawl_asset

sources = load_sources_from_duckdb()
generated_assets = [build_crawl_asset(s) for s in sources if s['tool_driver'] == 'crawl4ai']
```

### Medallion Pattern (Bronze/Silver/Gold)

```python
@asset
def bronze_customers():
    """Raw extraction"""
    return extract_from_source()

@asset
def silver_customers(bronze_customers):
    """Cleaned and validated"""
    return clean(bronze_customers)

@asset
def gold_customer_analytics(silver_customers):
    """Business logic applied"""
    return compute_analytics(silver_customers)
```

### ML Pipeline Pattern

```python
@asset
def training_features():
    return prepare_features()

@asset
def trained_model(training_features):
    model = train(training_features)
    return model

@asset_check(asset=trained_model)
def check_model_performance():
    accuracy = evaluate_model()
    return AssetCheckResult(passed=accuracy > 0.8, metadata={"accuracy": accuracy})

@asset
def predictions(trained_model):
    return predict(trained_model)
```

### dbt Integration

```python
from dagster import Definitions
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

dbt_project = DbtProject(
    project_dir="path/to/dbt",
)

@dbt_assets(manifest=dbt_project.manifest_path)
def my_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

defs = Definitions(
    assets=[my_dbt_assets],
    resources={
        "dbt": DbtCliResource(project_dir=dbt_project)
    }
)
```

### Functional Core, Imperative Shell

```python
# Functional Core - Pure function (no I/O)
def parse_math_content(text: str) -> MathQuestion:
    entities = extract_entities(text)
    latex = normalize_latex(text)
    return MathQuestion(entities=entities, latex=latex)

# Imperative Shell - Dagster handles I/O
@asset
def processed_questions(context, raw_documents):
    for doc in raw_documents:
        result = parse_math_content(doc.text)
        yield result
```

---

## Testing Patterns

### Unit Test

```python
def test_asset():
    mock_db = DatabaseResource(host="localhost", database="test", username="test", password="test")
    result = materialize([my_asset], resources={"database": mock_db})
    assert result.success
    assert len(result.output_for_node("my_asset")) > 0
```

### Integration Test

```python
def test_pipeline():
    result = materialize([asset1, asset2, asset3], resources=test_resources)
    assert result.success
```

### Pytest Fixtures

```python
@pytest.fixture
def mock_database():
    return DatabaseResource(host="localhost", database="test", username="test", password="test")

def test_etl_pipeline(mock_database):
    result = materialize(all_assets, resources={"database": mock_database})
    assert result.success
```

### Unit Testing with materialize()

```python
from dagster import materialize
import pytest

def test_customer_analytics():
    # Create test data
    test_raw = pd.DataFrame({
        "email": ["alice@test.com", "bob@test.com"],
        "segment": ["A", "A"],
        "revenue": [100, 200],
        "orders": [1, 2]
    })

    # Test asset chain
    result = materialize(
        [raw_customers, cleaned_customers, customer_analytics],
        resources={},
        # Override input
        input_values={"raw_customers": test_raw}
    )

    assert result.success
    output = result.output_for_node("customer_analytics")
    assert len(output) == 1  # One segment
    assert output.iloc[0]["revenue"] == 300
```

---

## Error Handling & Retry

### Asset-Level Retry

```python
from dagster import asset, RetryPolicy, Backoff, Jitter

@asset(retry_policy=RetryPolicy(max_retries=3, delay=1))
def flaky_api_call(context):
    return call_external_api()

@asset(retry_policy=RetryPolicy(
    max_retries=5, delay=2,
    backoff=Backoff.EXPONENTIAL,  # 2s, 4s, 8s, 16s, 32s
    jitter=Jitter.PLUS_MINUS
))
def cloud_service_call(context):
    return upload_to_cloud_service()
```

### Manual Retry Control

```python
from dagster import asset, RetryRequested

@asset
def conditional_retry_asset(context):
    try:
        return process_data()
    except TransientNetworkError as e:
        raise RetryRequested(max_retries=3, seconds_to_wait=5)
    except PermanentError as e:
        context.log.error(f"Permanent error: {e}")
        raise
```

### Failure with Metadata

```python
from dagster import asset, Failure, MetadataValue

@asset
def data_validation_asset(context):
    data = load_data()
    if data.null_count() > 1000:
        raise Failure(
            description="Too many null values detected",
            metadata={"null_count": MetadataValue.int(data.null_count())},
            allow_retries=False  # Data quality issue, not transient
        )
    return data
```

### Retry Best Practices

- ✅ Use `RetryPolicy` for transient failures (network, cloud services)
- ✅ Use exponential backoff for external APIs
- ✅ Add jitter to prevent thundering herd
- ✅ Use `Failure(allow_retries=False)` for data quality issues
- ⚠️ Don't retry framework errors (Dagster internal)
- ⚠️ Be mindful of retry limits on billable cloud services

---

## Code Organization

### Evolution Strategy

**Phase 1: One File (0-400 lines)**
```python
# definitions.py
from dagster import asset, Definitions

@asset
def asset1(): ...
@asset
def asset2(): ...

defs = Definitions(assets=[asset1, asset2], resources={...}, schedules=[...])
```

**Phase 2: Separate Concerns (400-2000 lines)**
```
my_project/
├── definitions.py
├── assets/
│   ├── __init__.py
│   ├── raw_data.py
│   └── analytics.py
├── resources/
│   └── shared_resources.py
└── schedules/
    └── daily_jobs.py
```

**Phase 3: Domain Grouping (2000+ lines)**
```
my_project/
├── assets/
│   ├── raw_data/          # Landing zone
│   ├── cleaned/           # Standardized
│   ├── analytical/        # Business logic
│   └── ml_models/         # ML features/models
└── resources/
    └── shared_resources.py
```

### Integration Project Structure

```
project_root/
├── dagster_project/       # Dagster orchestration
│   └── my_project/
│       ├── definitions.py
│       └── assets/
├── dbt_project/           # Separate dbt project
└── dlt_project/           # DLT configurations
```

---

## DLT Integration

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

### Firecrawl + Dagster Pattern

```python
@asset
def scraped_curriculum_pages(context):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    crawl_result = app.crawl_url(
        "https://www.curriculumonline.ie",
        params={'limit': 100}
    )
    return crawl_result
```

---

## API Reference

Dagster does **not** provide an OpenAPI spec. Use:

| Interface | Purpose |
|-----------|---------|
| **GraphQL API** (primary) | Comprehensive programmatic access |
| **External Assets REST API** (3 endpoints) | Lightweight external asset management |
| **Python SDK** | Type-safe native Python access |
| **dg api CLI** | Command-line automation |

### GraphQL Endpoint
```
http://localhost:3000/graphql          # Local
https://org.dagster.cloud/prod/graphql  # Cloud
```

### External Assets REST API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/report_asset_materialization/{KEY}` | POST | Report materialization |
| `/report_asset_check/{KEY}` | POST | Report check result |
| `/report_asset_observation/{KEY}` | POST | Report observation |

---

## Best Practices & Anti-Patterns

### ✅ DO

- Use assets for data pipelines (not ops)
- Use ConfigurableResource with Pydantic validation (not legacy @resource)
- Use EnvVar for secrets (evaluated at runtime)
- Add RetryPolicy for external API calls
- Log rich metadata in materializations
- Test individual assets with `materialize()`
- Use PostgreSQL for production storage

### ❌ AVOID

- Using ops for data pipelines (use assets)
- Loading heavy libraries at module level (lazy import inside asset functions)
- No retry policies on external calls
- Creating >100,000 partitions per asset
- Too many code locations (~100MB baseline each)
- Monolithic assets (break into smaller pieces)
- Stale imports from `oideachais.data_platform...` within data platform (use relative imports)

### 📦 Debugging Checklist

| Symptom | Check |
|---------|-------|
| Asset not running | Dependencies materialized? Resource config? Partition mismatches? |
| Performance issues | Partition count <100K? Heavy imports at module level? PostgreSQL for storage? |
| Resource errors | EnvVar values set? Resource config in Definitions? Test resource independently? |
| Schedule/sensor not firing | Dagster daemon running? Required for schedules/sensors to function |

### Integration Ecosystem

| Category | Libraries |
|----------|-----------|
| Data Transformation | dbt, Spark, Pandas, Polars |
| Data Warehouses | Snowflake, BigQuery, Redshift, Databricks |
| Data Quality | Great Expectations, Soda, Pandera |
| Cloud Platforms | AWS (dagster-aws), GCP (dagster-gcp), Azure (dagster-azure) |
| Data Loading | Airbyte, Fivetran, dlt |
| BI & Analytics | Census, Tableau, Looker, PowerBI |

---

## Project Structure

```
my_dagster_project/
├── my_dagster_project/
│   ├── __init__.py
│   ├── definitions.py      # Main Definitions object
│   ├── assets/
│   │   ├── __init__.py
│   │   ├── bronze.py       # Raw extraction assets
│   │   ├── silver.py       # Transformation assets
│   │   └── gold.py         # Analytics assets
│   ├── resources/
│   │   ├── __init__.py
│   │   └── database.py     # Resource definitions
│   └── jobs/
│       ├── __init__.py
│       └── schedules.py    # Jobs and schedules
├── tests/
│   └── test_assets.py
├── pyproject.toml
└── dagster.yaml            # Dagster configuration
```

### definitions.py

```python
from dagster import Definitions, load_assets_from_modules

from my_dagster_project.assets import bronze, silver, gold

all_assets = load_assets_from_modules([bronze, silver, gold])

defs = Definitions(
    assets=all_assets,
    schedules=schedules.all_schedules,
    resources={
        "database": database.get_database_resource()
    }
)
```

---

## Resources

- **Documentation**: https://docs.dagster.io
- **API Reference**: https://docs.dagster.io/api
- **Dagster University**: https://dagster.io/university
- **GitHub**: https://github.com/dagster-io/dagster
- **Latest**: v1.13.x (2025) — branch deployments, AI skills integration, improved partitioning
