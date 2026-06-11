---
title: 'Dagster - Modern Data Orchestration'
domain: 'data_platform'
status: 'stable'
description: 'Expert assistance for data orchestration with Dagster. Use when users need workflow pipelines, asset-based data engineering, ETL/ELT orchestration, partitioned processing, or integration with modern data stack tools.'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/dagster.md
ccc_query_hints:
  - dagster - modern data orchestration
name: 'dagster'
---

# Dagster - Modern Data Orchestration

**Version:** 1.12.x | **Last Updated:** 2025-01

## Overview

Dagster is an orchestrator for the modern data stack, providing:

- **Asset-First Design**: Define data assets, not just tasks
- **Observability**: Rich metadata, lineage, and data quality tracking
- **Type Safety**: ConfigurableResource with Pydantic validation
- **Partitioning**: Efficient incremental processing at scale
- **Testing**: First-class support for mocked resources and unit tests

**Documentation**: https://docs.dagster.io

## When to Use This Skill

Activate when users need:

- "Create a data pipeline for ETL/ELT"
- "Orchestrate data transformations"
- "Build partitioned/incremental data processing"
- "Integrate dbt, Spark, or cloud services"
- "Set up schedules and sensors for pipelines"
- "Test data pipelines"

## Core Concepts

### 1. Assets - The Primary Abstraction

```python
from dagster import asset, AssetExecutionContext
import pandas as pd

@asset
def raw_customers() -> pd.DataFrame:
    """Extract raw customer data from source."""
    return pd.read_csv("customers.csv")

@asset
def cleaned_customers(raw_customers: pd.DataFrame) -> pd.DataFrame:
    """Clean and validate customer data."""
    df = raw_customers.dropna(subset=["email"])
    df["email"] = df["email"].str.lower()
    return df

@asset
def customer_analytics(cleaned_customers: pd.DataFrame) -> pd.DataFrame:
    """Compute customer analytics."""
    return cleaned_customers.groupby("segment").agg({
        "revenue": "sum",
        "orders": "count"
    }).reset_index()
```

### 2. Resources - Dependency Injection

```python
from dagster import asset, ConfigurableResource, EnvVar, Definitions
import duckdb

class DuckDBResource(ConfigurableResource):
    """Configured connection to DuckDB."""
    database: str = "data/analytics.duckdb"

    def query(self, sql: str):
        with duckdb.connect(self.database) as conn:
            return conn.execute(sql).fetchdf()

    def execute(self, sql: str):
        with duckdb.connect(self.database) as conn:
            conn.execute(sql)

@asset
def load_customers(duckdb: DuckDBResource, cleaned_customers: pd.DataFrame):
    """Load customers into DuckDB."""
    duckdb.execute("CREATE TABLE IF NOT EXISTS customers AS SELECT * FROM cleaned_customers")

defs = Definitions(
    assets=[raw_customers, cleaned_customers, customer_analytics, load_customers],
    resources={
        "duckdb": DuckDBResource(database="data/analytics.duckdb")
    }
)
```

### 3. Partitions - Incremental Processing

```python
from dagster import asset, DailyPartitionsDefinition, AssetExecutionContext
from datetime import datetime

daily = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily)
def daily_events(context: AssetExecutionContext) -> pd.DataFrame:
    """Load events for a specific day."""
    date = context.partition_key
    return load_events_for_date(date)

@asset(partitions_def=daily)
def daily_aggregates(context: AssetExecutionContext, daily_events: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily events."""
    return daily_events.groupby("event_type").size().reset_index(name="count")
```

**Partition Types:**
- `DailyPartitionsDefinition` - Daily partitions
- `HourlyPartitionsDefinition` - Hourly partitions
- `WeeklyPartitionsDefinition` - Weekly partitions
- `MonthlyPartitionsDefinition` - Monthly partitions
- `StaticPartitionsDefinition` - Fixed set of partitions
- `DynamicPartitionsDefinition` - Runtime-defined partitions
- `MultiPartitionsDefinition` - Multiple partition dimensions

### 4. Schedules and Sensors

```python
from dagster import (
    asset, schedule, sensor, RunRequest, SensorEvaluationContext,
    ScheduleEvaluationContext, AssetSelection, define_asset_job
)

# Define job from assets
analytics_job = define_asset_job("analytics_job", selection=AssetSelection.all())

# Schedule - time-based trigger
@schedule(cron_schedule="0 6 * * *", job=analytics_job)
def daily_analytics_schedule(context: ScheduleEvaluationContext):
    """Run analytics every day at 6 AM."""
    return RunRequest()

# Sensor - event-based trigger
@sensor(job=analytics_job)
def new_file_sensor(context: SensorEvaluationContext):
    """Trigger when new files appear."""
    new_files = check_for_new_files()
    if new_files:
        yield RunRequest(
            run_key=f"files-{datetime.now().isoformat()}",
            run_config={"files": new_files}
        )
```

### 5. Asset Checks - Data Quality

```python
from dagster import asset, asset_check, AssetCheckResult, AssetCheckSeverity

@asset
def customers() -> pd.DataFrame:
    return load_customers()

@asset_check(asset=customers)
def check_no_null_emails(customers: pd.DataFrame) -> AssetCheckResult:
    """Ensure no null emails in customer data."""
    null_count = customers["email"].isna().sum()
    return AssetCheckResult(
        passed=null_count == 0,
        severity=AssetCheckSeverity.ERROR,
        metadata={"null_count": null_count}
    )

@asset_check(asset=customers)
def check_valid_revenue(customers: pd.DataFrame) -> AssetCheckResult:
    """Ensure all revenue values are non-negative."""
    invalid = (customers["revenue"] < 0).sum()
    return AssetCheckResult(
        passed=invalid == 0,
        severity=AssetCheckSeverity.WARN,
        metadata={"invalid_count": invalid}
    )
```

### 6. Retry Policies

```python
from dagster import asset, RetryPolicy, Backoff, Jitter

@asset(
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=2,
        backoff=Backoff.EXPONENTIAL,
        jitter=Jitter.PLUS_MINUS
    )
)
def api_data():
    """Fetch data from external API with retries."""
    return call_external_api()
```

## Common Patterns

### Bronze/Silver/Gold Architecture

```python
from dagster import asset, AssetKey
import pandas as pd

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
    }).rename(columns={"order_id": "order_count"})
```

### Factory Pattern

```python
from dagster import asset, AssetSpec
from typing import Callable

def create_table_asset(source: str, table: str) -> Callable:
    @asset(name=f"{source}_{table}", group_name=source)
    def _asset():
        return extract_table(source, table)
    return _asset

# Create multiple assets
sources = ["postgres", "mysql"]
tables = ["users", "orders", "products"]

assets = [
    create_table_asset(source, table)
    for source in sources
    for table in tables
]
```

### Multi-Environment Configuration

```python
import os
from dagster import Definitions, ConfigurableResource

class DatabaseResource(ConfigurableResource):
    host: str
    database: str
    username: str
    password: str

def get_resources():
    env = os.getenv("DAGSTER_DEPLOYMENT", "local")

    if env == "production":
        return {
            "database": DatabaseResource(
                host="prod-db.example.com",
                database="analytics",
                username=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
        }
    else:
        return {
            "database": DatabaseResource(
                host="localhost",
                database="dev_analytics",
                username="dev",
                password="dev"
            )
        }

defs = Definitions(
    assets=all_assets,
    resources=get_resources()
)
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

### ML Pipeline

```python
from dagster import asset, asset_check, AssetCheckResult
import mlflow

@asset
def training_data() -> pd.DataFrame:
    """Prepare training dataset."""
    return prepare_features()

@asset
def trained_model(training_data: pd.DataFrame):
    """Train and log model."""
    X, y = split_features_target(training_data)
    model = train_model(X, y)

    with mlflow.start_run():
        mlflow.sklearn.log_model(model, "model")

    return model

@asset_check(asset=trained_model)
def check_model_accuracy(trained_model):
    """Validate model performance."""
    accuracy = evaluate_model(trained_model)
    return AssetCheckResult(
        passed=accuracy > 0.8,
        metadata={"accuracy": accuracy}
    )

@asset
def predictions(trained_model, inference_data: pd.DataFrame) -> pd.DataFrame:
    """Generate predictions."""
    return pd.DataFrame({
        "prediction": trained_model.predict(inference_data)
    })
```

## Testing

### Unit Testing

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

### Resource Mocking

```python
from dagster import materialize

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
from my_dagster_project.resources import database
from my_dagster_project.jobs import schedules

all_assets = load_assets_from_modules([bronze, silver, gold])

defs = Definitions(
    assets=all_assets,
    schedules=schedules.all_schedules,
    resources={
        "database": database.get_database_resource()
    }
)
```

## Best Practices

### Asset Naming
- Use descriptive, noun-based names
- Good: `daily_active_users`, `customer_churn_predictions`
- Bad: `process_data`, `etl_job_3`

### Performance
- Don't import heavy libraries at module level
- Use lazy imports inside asset functions
- PostgreSQL for production (not SQLite)
- Limit partitions to <100,000 per asset

### Observability
- Add rich metadata to materializations
- Use asset checks for data quality
- Log important info via `context.log`

### Error Handling
- Use RetryPolicy for transient failures
- Use exponential backoff for external APIs
- Use `Failure` with `allow_retries=False` for data quality issues

## Debugging Checklist

1. **Asset Not Running**
   - Check dependencies are materialized
   - Verify resource configuration
   - Check for partition mismatches

2. **Performance Issues**
   - Check partition count (<100K?)
   - Heavy imports at module level?
   - Appropriate storage backend?

3. **Resource Errors**
   - Verify EnvVar values set
   - Check resource in Definitions
   - Test resource independently

## Resources

- **Documentation**: https://docs.dagster.io
- **API Reference**: https://docs.dagster.io/api
- **Dagster University**: https://dagster.io/university
- **GitHub**: https://github.com/dagster-io/dagster
