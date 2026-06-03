# Data Pipeline Capability

## Overview

Modern data orchestration and ETL/ELT pipelines with asset-based design, incremental loading, schema inference, and integration with the modern data stack.

## Requirements

### Requirement: Asset-Based Pipelines
The system SHALL define data assets, not just tasks.

#### Scenario: Bronze/Silver/Gold Architecture
- **GIVEN** a data pipeline with bronze, silver, and gold layers
- **WHEN** assets are materialized
- **THEN** data flows through layers with appropriate transformations

#### Scenario: Asset Dependencies
- **GIVEN** assets with clear dependencies
- **WHEN** a downstream asset is materialized
- **THEN** upstream assets are automatically materialized first

### Requirement: Incremental Loading
The system SHALL support cursor-based incremental extraction.

#### Scenario: Time-Based Incremental
- **GIVEN** a resource with an updated_at timestamp
- **WHEN** the pipeline runs
- **THEN** only records since the last run are fetched

#### Scenario: Cursor-Based Extraction
- **GIVEN** a paginated API with cursor
- **WHEN** fetching data
- **THEN** pagination continues from the last cursor position

### Requirement: Schema Inference
The system SHALL automatically detect and evolve schemas.

#### Scenario: Nested JSON Normalization
- **GIVEN** nested JSON data
- **WHEN** loaded into the pipeline
- **THEN** nested structures are flattened into related tables

#### Scenario: Schema Evolution
- **GIVEN** data with new columns
- **WHEN** the pipeline runs
- **THEN** schema evolves to include new columns

### Requirement: Partitioning
The system SHALL support efficient partitioned processing.

#### Scenario: Daily Partitions
- **GIVEN** an asset with daily partitioning
- **WHEN** processing data
- **THEN** each day is processed independently

#### Scenario: Multi-Dimensional Partitions
- **GIVEN** an asset with multiple partition dimensions
- **WHEN** querying data
- **THEN** partitions can be filtered by any dimension

## Supported Frameworks

### Dagster (>=1.9.0)

**Key Features:**
- Asset-first design with automatic dependency tracking
- Observability with rich metadata, lineage, and data quality tracking
- Type safety with ConfigurableResource and Pydantic validation
- Partitioning for efficient incremental processing at scale
- First-class testing with mocked resources and unit tests
- Retry policies with exponential backoff
- Asset checks for data quality validation

**Documentation:** https://docs.dagster.io

**Skill:** [`.skills/dagster/SKILL.md`](.skills/dagster/SKILL.md)

### DLT (>=1.4.0)

**Key Features:**
- Declarative loading with decorators for resources and sources
- Automatic schema detection and evolution
- Cursor-based incremental extraction
- Multiple destinations (DuckDB, BigQuery, Snowflake, Postgres, S3)
- Automatic flattening of nested JSON structures
- Pythonic pipeline definitions
- Streaming support for real-time data
- REST API source with pagination support

**Documentation:** https://dlthub.com/docs

**Skill:** [`.skills/dlt/SKILL.md`](.skills/dlt/SKILL.md)

### SQLMesh (>=0.228.1)

**Key Features:**
- DuckDB integration for local development
- Virtual data environments for isolated testing
- CI/CD for SQL transformations
- Model versioning and deployment
- Data quality checks

**Documentation:** https://sqlmesh.com

**Skill:** [`.skills/sqlmesh/SKILL.md`](.skills/sqlmesh/SKILL.md)

## Pipeline Patterns

### Bronze/Silver/Gold Architecture

```python
from dagster import asset

@asset(group_name="bronze")
def bronze_orders() -> pd.DataFrame:
    """Raw extraction from source."""
    return extract_from_source("orders")

@asset(group_name="silver")
def silver_orders(bronze_orders: pd.DataFrame) -> pd.DataFrame:
    """Cleaned and validated."""
    df = bronze_orders.dropna()
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

@asset(group_name="gold")
def gold_order_summary(silver_orders: pd.DataFrame) -> pd.DataFrame:
    """Business-ready aggregations."""
    return silver_orders.groupby("customer_id").agg({
        "amount": "sum",
        "order_id": "count"
    })
```

### Incremental Loading with DLT

```python
import dlt

@dlt.resource(
    write_disposition="merge",
    primary_key="id"
)
def orders(
    updated_at=dlt.sources.incremental("updated_at")
):
    """Fetch orders incrementally by updated_at."""
    params = {"since": updated_at.last_value.isoformat()}
    
    for order in fetch_api("/orders", params=params):
        yield {
            "id": order["id"],
            "updated_at": order["updated_at"],
            "amount": order["amount"]
        }
```

### Dagster Integration with DLT

```python
from dagster import asset
import dlt

@asset(compute_kind="dlt")
def dlt_github_repos(context):
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

## Write Dispositions

| Disposition | Use Case | Primary Key Required |
|-------------|----------|-------------------|
| `merge` | Upsert based on primary key | Yes |
| `append` | Add new records only | No |
| `replace` | Full refresh | No |

## Destinations

### DuckLake (Recommended - Production)
DuckLake destination writes Parquet files to Garage S3 with Postgres catalog for ACID transactions, time-travel queries, and multi-reader safety.

```python
pipeline = dlt.pipeline(
    pipeline_name="curriculum_unified",
    destination="dlt.destinations.ducklake",
    dataset_name="curriculum"
)
# DuckLake connects via Postgres catalog + S3 endpoint
# ATTACH 'postgresql://lakekeeper:password@host:5433/ducklake_oideachais'
#     AS ducklake (TYPE POSTGRES);
# Then SET s3_endpoint, s3_access_key_id, s3_secret_access_key
```

### DuckDB (Local Development)
```python
pipeline = dlt.pipeline(
    pipeline_name="local_analysis",
    destination="duckdb",
    dataset_name="analytics"
)
# Falls back to local .duckdb file when USE_DUCKLAKE=false
```

### BigQuery
```python
pipeline = dlt.pipeline(
    pipeline_name="bq_pipeline",
    destination="bigquery",
    dataset_name="raw_data"
)
```

### PostgreSQL
```python
pipeline = dlt.pipeline(
    pipeline_name="postgres_pipeline",
    destination="postgres",
    dataset_name="warehouse"
)
```

### Filesystem (S3/R2/GCS)
```python
pipeline = dlt.pipeline(
    pipeline_name="file_pipeline",
    destination="filesystem",
    staging="filesystem"
)
```

## Partition Types

| Type | Use Case | Example |
|------|----------|---------|
| `DailyPartitionsDefinition` | Daily partitions | Event logs, transactions |
| `HourlyPartitionsDefinition` | Hourly partitions | Real-time metrics |
| `WeeklyPartitionsDefinition` | Weekly partitions | Weekly reports |
| `MonthlyPartitionsDefinition` | Monthly partitions | Monthly aggregations |
| `StaticPartitionsDefinition` | Fixed partitions | Geographic regions |
| `DynamicPartitionsDefinition` | Runtime-defined partitions | Dynamic customer segments |
| `MultiPartitionsDefinition` | Multiple dimensions | Country + Date |

## Best Practices

### Asset Design
1. **Descriptive Names**: Use noun-based names (e.g., `daily_active_users`)
2. **Clear Dependencies**: Let Dagster infer dependencies from function signatures
3. **Group Organization**: Use groups to organize related assets

### Performance
1. **Lazy Imports**: Don't import heavy libraries at module level
2. **Batch Operations**: Process multiple items together when possible
3. **Partition Limits**: Keep partitions under 100,000 per asset
4. **Parquet Format**: Use Parquet for better compression and performance

### Data Quality
1. **Asset Checks**: Implement checks for critical data quality rules
2. **Retry Policies**: Use exponential backoff for transient failures
3. **Schema Validation**: Use Pydantic for type safety

### Incremental Loading
1. **Cursor Fields**: Always include cursor field in yielded data
2. **Initial Values**: Set appropriate initial values for incremental extraction
3. **Primary Keys**: Define primary keys for merge operations

## Configuration

### Dagster Configuration

```python
from dagster import Definitions, ConfigurableResource

class DatabaseResource(ConfigurableResource):
    host: str
    database: str
    username: str
    password: str

defs = Definitions(
    assets=all_assets,
    resources={
        "database": DatabaseResource(
            host="localhost",
            database="analytics",
            username="user",
            password="pass"
        )
    }
)
```

### DLT Configuration

```toml
# .dlt/config.toml
[runtime]
log_level = "INFO"
dlthub_telemetry = false

[normalize]
max_nesting = 2

# .dlt/secrets.toml
[destination.bigquery]
project_id = "my-project"
credentials = '{"type": "service_account", ...}'
```

## Testing

### Unit Testing Dagster Assets

```python
from dagster import materialize
import pytest

def test_customer_analytics():
    test_raw = pd.DataFrame({
        "email": ["alice@test.com", "bob@test.com"],
        "segment": ["A", "A"],
        "revenue": [100, 200]
    })
    
    result = materialize(
        [raw_customers, cleaned_customers, customer_analytics],
        input_values={"raw_customers": test_raw}
    )
    
    assert result.success
    output = result.output_for_node("customer_analytics")
    assert len(output) == 1
```

### Resource Mocking

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

## Integration with Other Systems

### Knowledge Graph Integration
- **Cognee**: Load data into knowledge graphs for semantic search
- **Graphiti Core**: Transform data into temporal knowledge graphs

### Agent Integration
- **Agno**: Provide data to agents for knowledge base queries
- **Google ADK**: Enable agents to access data through tools

### Observability Integration
- **Langfuse**: Track pipeline performance and costs
- **RAGAS**: Evaluate data quality with trace-based metrics
