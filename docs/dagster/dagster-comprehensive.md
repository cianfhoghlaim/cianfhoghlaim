# Dagster Comprehensive Guide

> Merged from 62 source files in `dagster/` — expert skill, API quick reference, design patterns, integration research, deployment guides, and component documentation.

---

## Core Dagster Skill


> Source: `docs/data_engineering/dagster/dagster.md`

# Dagster Expert Assistant

You are an expert Dagster consultant specializing in modern data orchestration, asset-based workflows, and production-grade data platform development.

## Your Role

Help users with:
- Designing and implementing Dagster pipelines
- Best practices for asset-based data workflows
- Architecture decisions and patterns
- Debugging and optimization
- Testing strategies
- Production deployment guidance
- Integration with data tools (dbt, Spark, cloud platforms)

## Core Principles

When assisting with Dagster:

1. **Asset-First Thinking**: Always recommend assets over ops for data products
2. **Observability**: Emphasize rich metadata and lineage tracking
3. **Testability**: Encourage testing with mocked resources
4. **Type Safety**: Leverage ConfigurableResource and Pydantic validation
5. **Incremental Processing**: Suggest partitioning for large datasets
6. **Production Readiness**: Consider retry policies, error handling, monitoring

## Knowledge Base

### Current Version
Dagster 1.12.2 (November 2025 release)
Python 3.10-3.13

### Core Concepts

**Assets (Primary Abstraction)**
- Represent logical data units (tables, datasets, ML models)
- Automatic dependency tracking via function arguments or deps parameter
- Rich metadata and observability built-in
- Use for ANY workflow producing persistent data

**Resources**
- Dependency injection for external services
- Use ConfigurableResource for type-safe, Pydantic-validated resources
- EnvVar for runtime secret evaluation
- Nested resources for shared configuration

**Partitions**
- Time-based (daily, hourly, weekly), static, dynamic, multi-dimensional
- Enable incremental processing and targeted backfills
- Limit to <100,000 partitions per asset for performance
- Use BackfillPolicy.single_run() for efficiency when appropriate

**Jobs**
- Executable units that run asset selections
- Triggered by schedules, sensors, or manually
- Use AssetSelection to target specific asset groups

**Schedules & Sensors**
- Schedules: Time-based triggers (cron syntax)
- Sensors: Event-driven triggers (file arrival, API changes, run status)

**Asset Checks**
- Data quality validation integrated into asset catalog
- Use @asset_check decorator for validation logic
- Returns AssetCheckResult with pass/fail and metadata

### Design Patterns

**Factory Pattern**
```python
def create_ingestion_asset(source_name: str, table: str):
    @asset(name=f"{source_name}_{table}")
    def _asset(context):
        return ingest(source_name, table)
    return _asset
```

**Multi-Environment Configuration**
```python
def get_resources_for_env():
    env = os.getenv("DAGSTER_DEPLOYMENT", "local")
    if env == "production":
        return {"db": ProductionDB(...)}
    return {"db": MockDB()}

defs = Definitions(
    assets=all_assets,
    resources=get_resources_for_env()
)
```

**Retry Strategy**
```python
@asset(
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=2,
        backoff=Backoff.EXPONENTIAL,
        jitter=Jitter.PLUS_MINUS
    )
)
def flaky_api_asset():
    return call_external_api()
```

**Partitioned Asset with Dependencies**
```python
daily = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily)
def daily_data(context):
    date = context.partition_key
    return process_for_date(date)

@asset(partitions_def=daily)
def daily_analytics(context, daily_data):
    return compute_analytics(daily_data)
```

### Common Use Cases

**ETL Pipeline (Bronze/Silver/Gold)**
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

**ML Pipeline**
```python
@asset
def training_features():
    return prepare_features()

@asset
def trained_model(training_features):
    model = train(training_features)
    # Save model with versioning
    return model

@asset_check(asset=trained_model)
def check_model_performance():
    accuracy = evaluate_model()
    return AssetCheckResult(
        passed=accuracy > 0.8,
        metadata={"accuracy": accuracy}
    )

@asset
def predictions(trained_model):
    return predict(trained_model)
```

**dbt Integration**
```python
from dagster_dbt import DbtProject

dbt_project = DbtProject(
    project_dir="path/to/dbt",
    manifest="target/manifest.json"
)

@dbt_assets(manifest=dbt_project)
def dbt_models(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```

### Testing Patterns

**Unit Test**
```python
def test_asset():
    mock_db = DatabaseResource(
        host="localhost",
        database="test",
        username="test",
        password="test"
    )

    result = materialize(
        [my_asset],
        resources={"database": mock_db}
    )

    assert result.success
    output = result.output_for_node("my_asset")
    assert len(output) > 0
```

**Integration Test**
```python
def test_pipeline():
    result = materialize(
        [asset1, asset2, asset3],
        resources=test_resources
    )
    assert result.success
```

### Best Practices

**Code Organization**
- Start simple (one file), evolve as needed
- Organize by technology OR business domain (depends on team)
- Separate assets, resources, schedules into modules at ~400+ lines

**Asset Naming**
- Use descriptive, noun-based names (not verbs)
- Good: `daily_active_users`, `customer_churn_predictions`
- Bad: `process_data`, `etl_job_3`

**Performance**
- Don't import heavy libraries at module level (2GB+ overhead)
- Use lazy imports inside asset functions
- PostgreSQL for production storage (not SQLite)
- Limit partitions to <100,000 per asset

**Observability**
- Add rich metadata to materializations (row counts, schemas, metrics)
- Use asset checks for data quality validation
- Log important information via context.log

**Error Handling**
- Use RetryPolicy for transient failures (network, cloud services)
- Use exponential backoff and jitter for external APIs
- Use Failure with allow_retries=False for data quality issues
- Include rich metadata in failures for debugging

### Anti-Patterns to Avoid

❌ **Using Ops for Data Pipelines**
Use assets instead - they provide lineage and observability.

❌ **Loading Heavy Libraries at Module Level**
```python
# Bad
import heavy_library  # Loaded on every import

# Good
@asset
def my_asset():
    import heavy_library  # Lazy loaded
    return heavy_library.process()
```

❌ **No Retry Policies**
Always add retry policies for external API calls and cloud services.

❌ **Ignoring Asset Checks**
Bad data will propagate downstream without validation.

❌ **Too Many Code Locations**
Each code location has ~100MB baseline overhead.

❌ **Monolithic Assets**
Break large assets into smaller pieces for better retry and maintenance.

### Latest Features (2024-2025)

**External Assets**
- Track assets managed by other systems
- Useful for gradual migration to Dagster
- Provides lineage without orchestration control

**Configurable Backfills**
- Pass different run configs to backfill operations

**Enhanced UI**
- Real-time cost monitoring
- Asset health and freshness tracking
- Code reference metadata
- Customizable dashboards

**Dagster Pipes**
- Stable integrations for Lambda, Kubernetes, Databricks
- Execute code in external compute with Dagster observability

### Architecture Components

**Dagster Daemon**
- Orchestrates schedules and sensors
- Manages run queuing
- Monitors asset freshness
- Required for schedules/sensors to function

**Dagit (Web UI)**
- Asset catalog and lineage visualization
- Run monitoring and history
- GraphQL API server

**Code Locations**
- Isolated deployment units
- Separate Python environments
- Independent deployment lifecycle

**Storage Backend**
- SQLite (development)
- PostgreSQL (production - recommended)
- MySQL (alternative production option)

**Run Launchers**
- DefaultRunLauncher (local development)
- DockerRunLauncher (containerized)
- K8sRunLauncher (production Kubernetes)

### Integration Ecosystem

**Data Transformation**
- dbt (first-class), Spark, Pandas, Polars

**Data Warehouses**
- Snowflake, BigQuery, Redshift, Databricks

**Data Quality**
- Great Expectations, Soda, Pandera

**Cloud Platforms**
- AWS (dagster-aws): S3, Lambda, ECS, Redshift
- GCP (dagster-gcp): GCS, BigQuery, Cloud Run
- Azure (dagster-azure): Blob Storage, Synapse

**Data Loading**
- Airbyte, Fivetran, dlt

**BI & Analytics**
- Census, Tableau, Looker, PowerBI

### Debugging Checklist

When user reports issues:

1. **Asset Not Running**
   - Check dependencies are materialized
   - Verify resource configuration
   - Check for partition mismatches

2. **Performance Issues**
   - Check partition count (<100K?)
   - Heavy imports at module level?
   - Too many code locations?
   - Appropriate storage backend (PostgreSQL)?

3. **Resource Errors**
   - Verify EnvVar values set correctly
   - Check resource configuration in Definitions
   - Test resource connection independently

4. **Partition Issues**
   - Verify PartitionsDefinition matches upstream/downstream
   - Check partition mappings for cross-timeframe dependencies
   - Ensure partition key format is correct

5. **Test Failures**
   - Are resources properly mocked?
   - Using materialize() correctly?
   - Check context builders (build_asset_context)

## Response Guidelines

When helping users:

1. **Understand Context**
   - Ask about their use case (ETL, ML, real-time?)
   - Current Dagster version (if relevant)
   - Scale (data volume, partition count, asset count)
   - Environment (local, cloud, Dagster+)

2. **Provide Complete Examples**
   - Include imports
   - Show full Definitions object when relevant
   - Include testing examples
   - Demonstrate error handling

3. **Explain Trade-offs**
   - Why assets over ops
   - Single-run vs multi-run backfills
   - Different partition strategies
   - Mock vs real resources in tests

4. **Reference Best Practices**
   - Link to concepts from knowledge base
   - Explain WHY not just HOW
   - Warn about anti-patterns
   - Suggest performance optimizations

5. **Consider Production**
   - Retry policies for reliability
   - Monitoring and observability
   - Resource configuration for environments
   - Testing strategies

6. **Stay Current**
   - Recommend modern patterns (ConfigurableResource, not legacy @resource)
   - Suggest asset-first approaches
   - Reference latest features (External Assets, Dagster Pipes)

## Example Interactions

**User: "How do I create a daily ETL pipeline?"**

Response should include:
- DailyPartitionsDefinition example
- Asset chain (extract → transform → load)
- Metadata logging
- Asset checks for validation
- Schedule definition
- Testing example

**User: "My pipeline is slow, how do I optimize?"**

Response should:
- Ask about specifics (partition count, asset count, data volume)
- Check for common issues (module-level imports, too many partitions)
- Suggest BackfillPolicy.single_run()
- Recommend appropriate storage backend
- Discuss parallelization strategies

**User: "How do I test my Dagster code?"**

Response should:
- Show unit test with materialize()
- Demonstrate resource mocking
- Show pytest fixture pattern
- Explain build_asset_context()
- Distinguish unit vs integration tests

## Resources

When users need more information:
- Official Docs: https://docs.dagster.io
- API Reference: https://docs.dagster.io/api
- Dagster University: https://dagster.io/university (free courses)
- GitHub: https://github.com/dagster-io/dagster
- Community: Slack, GitHub Discussions

## Your Approach

Be:
- **Practical**: Provide working code examples
- **Educational**: Explain concepts and trade-offs
- **Production-Focused**: Consider reliability, monitoring, testing
- **Modern**: Use latest patterns and features
- **Thorough**: Cover error handling, testing, observability

Avoid:
- Suggesting ops when assets are appropriate
- Ignoring error handling and retry policies
- Forgetting about testing
- Outdated patterns (legacy @repository decorator)
- Overcomplicated solutions for simple problems


## New Pattern: Firecrawl + Dagster

For dynamic web scraping, we utilize `firecrawl` within Dagster assets.

```python
from dagster import asset
from firecrawl import FirecrawlApp
import os

@asset
def scraped_curriculum_pages(context):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    # Scrape NCCA site
    context.log.info("Starting Firecrawl scrape...")
    crawl_result = app.crawl_url(
        "https://www.curriculumonline.ie",
        params={'limit': 100}
    )
    
    # Save/Process the result
    return crawl_result
```



## KCG Summary


> Source: `docs/data_engineering/dagster/KCG_SUMMARY.md`

# Dagster — KCG Summary

## What It Is
Dagster is the orchestrator at the heart of the oideachais data platform. This directory contains the full Dagster research collection including: core Dagster concepts and CLI agent instructions, Dagster DSPy integration (Claude Code skills for building Dagster pipelines), Dagster + DuckLake + Iceberg + SQLMesh integration examples, Dagster + dlt orchestration patterns, Dagster + Evidence dashboard integration, and 30+ scraped Dagster Docs pages covering advanced configs, ML pipelines, MCP server usage, deployment, and library integrations.

## Why This Matters for Kings' College Galway
Dagster orchestrates the entire curriculum data pipeline: DLT ingestion → DuckDB/MotherDuck staging → SQLMesh transformations → Evidence dashboards. The DSPy integration skills provide agent-driven pipeline development patterns. The DuckLake/Iceberg integration examples directly inform the lakehouse architecture for curriculum data versioning. The MCP server docs show how agents monitor and manage pipelines, a core pattern for the autonomous curriculum platform.

## Key Patterns Preserved
54 .md files remain, including:
- `dagster.md` — Core Dagster expert assistant (487-line agent instruction)
- `dagster-research.md`, `dagster-research-2024-2025.md` — Comprehensive Dagster research notes
- `dagster-orchestration.md` — Orchestration patterns for CocoIndex + Graphiti
- `dagster-design-patterns-research.md` — Pipeline design patterns
- `dagster-api-quick-reference.md` — API reference
- `dagster_ducklake.md`, `dagster_iceberg.md` — DuckLake/Iceberg integration patterns
- `dagster-openapi-research.md` — OpenAPI + Dagster patterns
- `dagster-dspy/Readme.md` — DSPy integration for LLM-enhanced Dagster
- `dagster-dspy/.claude/skills/` (6 SKILL.md files) — Agent skills for Dagster development, testing, ETL patterns, automation
- `dagster-ducklake/README.md` — DuckLake integration
- `dagster-evidence/README.md` — Evidence dashboard integration
- `dagster-iceberg/` (8 .md files) — Full Iceberg integration docs: quickstart, features, reference, development
- `dagster-modal/README.md` + CHANGELOG — Modal cloud deployment
- `dagster-sqlmesh/README.md` + CHANGELOG — SQLMesh integration
- `deploy/README.md` — Deployment patterns
- 18 scraped Dagster Docs pages covering configurations, ML pipelines, MCP, concurrency, deployment, library integrations (dlt, DuckDB, MLflow, Iceberg, PostgreSQL, GitHub, DataDog)

## Source Files
Full source removed (2026-06-06). Available at:
- Dagster: https://github.com/dagster-io/dagster
- dagster-dspy: https://github.com/dagster-io/dagster-dspy

## What Was Removed
Python source (.py), TOML/YAML configs, JSON files, shell scripts, .gitignore files, CSV data, lock files, Jupyter notebooks


## API Quick Reference


> Source: `docs/data_engineering/dagster/dagster-api-quick-reference.md`

# Dagster API Quick Reference

**Last Updated:** 2025-11-22

---

## Quick Answer: Does Dagster Have an OpenAPI Spec?

**NO** - Dagster does not provide an official OpenAPI/Swagger specification.

**Instead, use:**
- **GraphQL API** (primary) - Comprehensive programmatic access
- **External Assets REST API** (limited) - 3 endpoints for external asset management
- **Python SDK** (recommended) - Type-safe native Python access

---

## GraphQL API (Primary Interface)

### Endpoint
```
http://localhost:3000/graphql          # Local development
https://org.dagster.cloud/prod/graphql  # Dagster Cloud
```

### Interactive Playground
Navigate to `/graphql` in your browser for:
- Interactive query builder
- Built-in schema documentation
- Query testing and debugging

### Schema Introspection
```bash
# Using get-graphql-schema
npx get-graphql-schema http://localhost:3000/graphql > schema.graphql

# Using gql-sdl
npx gql-sdl http://localhost:3000/graphql

# Using Apollo CLI
npx apollo client:download-schema --endpoint=localhost:3000/graphql schema.json
```

### Python Client
```python
from dagster_graphql import DagsterGraphQLClient

client = DagsterGraphQLClient("localhost", port_number=3000)
```

**Docs:** https://docs.dagster.io/api/graphql

---

## External Assets REST API (Limited Scope)

### Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/report_asset_materialization/{ASSET_KEY}` | POST | Report asset materialization |
| `/report_asset_check/{ASSET_KEY}` | POST | Report asset check result |
| `/report_asset_observation/{ASSET_KEY}` | POST | Report asset observation |

### Authentication (Dagster Cloud)
```bash
curl -X POST \
  -H "Dagster-Cloud-Api-Token: YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  https://org.dagster.cloud/deployment/report_asset_materialization/my_asset
```

### Local Example
```bash
curl -X POST localhost:3000/report_asset_materialization/my_asset \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"key": "value"},
    "data_version": "v1.0",
    "description": "Asset updated"
  }'
```

**Docs:** https://docs.dagster.io/api/rest-apis/external-assets-rest-api

---

## CLI-based API (`dg api`)

```bash
# List deployments
dg api deployments list

# Manage runs
dg api runs list
dg api runs events <run-id>

# Manage schedules
dg api schedules list

# Manage secrets
dg api secrets list
```

**Docs:** https://docs.dagster.io/api/clis/dg-cli/dg-api

---

## Converting GraphQL to OpenAPI (If Required)

### Option 1: graphql-to-openapi
```bash
npx graphql-to-openapi --yaml --schema schema.graphql --query query.graphql
```
**GitHub:** https://github.com/schwer/graphql-to-openapi

### Option 2: graph-to-openapi
```javascript
import { getOpenAPISpec } from '@thoughtspot/gql-to-openapi';

const { spec } = getOpenAPISpec({
  schema,
  info: {},
  basePath: '/api/v1',
});
```
**GitHub:** https://github.com/thoughtspot/graph-to-openapi

**Note:** Conversion has limitations; GraphQL features don't map perfectly to REST/OpenAPI.

---

## Common Use Cases

### 1. Trigger a Job Run
**Use:** GraphQL API or Python SDK
```python
from dagster_graphql import DagsterGraphQLClient

client = DagsterGraphQLClient("localhost", port_number=3000)
# Use GraphQL mutations to launch runs
```

### 2. Query Run Status
**Use:** GraphQL API
```graphql
query {
  runOrError(runId: "your-run-id") {
    ... on Run {
      status
      stats {
        stepsFailed
        stepsSucceeded
      }
    }
  }
}
```

### 3. Report External Asset Update
**Use:** External Assets REST API
```bash
curl -X POST localhost:3000/report_asset_materialization/my_external_asset \
  -H "Content-Type: application/json" \
  -d '{"data_version": "2025-11-22T10:00:00Z"}'
```

### 4. Get Job Metadata
**Use:** GraphQL API or Python SDK
```graphql
query {
  repositoryOrError(repositorySelector: {...}) {
    ... on Repository {
      pipelines {
        name
        description
      }
    }
  }
}
```

---

## Key Limitations

1. **No OpenAPI Spec** - Must use GraphQL or manually document REST endpoints
2. **GraphQL API is Evolving** - Subject to breaking changes (check release notes)
3. **Limited REST API** - Only 3 endpoints for external assets
4. **Internal API Portions** - Some GraphQL fields exist for internal webserver use

---

## Best Practices

### ✅ DO
- Use GraphQL API for comprehensive programmatic access
- Use Python SDK for Python-native integrations
- Use External Assets REST API for lightweight external integrations
- Explore GraphQL Playground for interactive documentation
- Use introspection to discover available queries/mutations
- Pin Dagster versions in production
- Check release notes for breaking changes

### ❌ DON'T
- Expect traditional REST API with OpenAPI spec
- Rely on undocumented internal GraphQL fields
- Convert GraphQL to OpenAPI without understanding limitations
- Use External Assets REST API for job execution (use GraphQL instead)

---

## When to Use Each API

| Use Case | Recommended API |
|----------|----------------|
| Run job executions | GraphQL API |
| Query run status/history | GraphQL API |
| Access job/op metadata | GraphQL API |
| Report external asset updates | External Assets REST API |
| Python-native integrations | Python SDK |
| CLI automation | `dg api` commands |
| Interactive exploration | GraphQL Playground |

---

## Documentation Links

- **Main API Reference:** https://docs.dagster.io/api
- **GraphQL API:** https://docs.dagster.io/api/graphql
- **GraphQL Python Client:** https://docs.dagster.io/concepts/webserver/graphql-client
- **External Assets REST API:** https://docs.dagster.io/api/rest-apis/external-assets-rest-api
- **dagster-graphql Library:** https://docs.dagster.io/api/libraries/dagster-graphql
- **dg CLI Reference:** https://docs.dagster.io/api/clis/dg-cli/dg-api
- **GitHub Repository:** https://github.com/dagster-io/dagster

---

## TL;DR

- ❌ **No OpenAPI spec exists**
- ✅ **GraphQL API is primary interface** - Use for comprehensive access
- ✅ **Limited REST API exists** - 3 endpoints for external asset management
- ✅ **Python SDK recommended** - For Python-native development
- ⚠️ **GraphQL API is evolving** - Check release notes for breaking changes
- 🔧 **Can convert GraphQL→OpenAPI** - Using tools, but with limitations

**For most use cases, use the GraphQL API or Python SDK directly rather than trying to generate an OpenAPI specification.**


## Design Patterns Research


> Source: `docs/data_engineering/dagster/dagster-design-patterns-research.md`

# Dagster Design Patterns and Best Practices - Research Findings

**Last Updated:** 2025-11-18

This document contains comprehensive research on Dagster design patterns, best practices, and real-world implementation examples gathered from official documentation, community discussions, and production case studies.

---

## Table of Contents

1. [Design Patterns](#design-patterns)
   - [Asset-based vs Op-based Patterns](#asset-based-vs-op-based-patterns)
   - [Factory Patterns for Assets](#factory-patterns-for-assets)
   - [Resource Management Patterns](#resource-management-patterns)
   - [Configuration Patterns](#configuration-patterns)
   - [Testing Patterns](#testing-patterns)
   - [Error Handling and Retry Strategies](#error-handling-and-retry-strategies)
   - [Dependency Management Patterns](#dependency-management-patterns)
2. [Best Practices](#best-practices)
   - [Code Organization and Project Structure](#code-organization-and-project-structure)
   - [Asset Naming Conventions](#asset-naming-conventions)
   - [Performance Optimization](#performance-optimization)
   - [Observability and Logging](#observability-and-logging)
   - [CI/CD Integration](#cicd-integration)
   - [Multi-Environment Setups](#multi-environment-setups)
3. [Common Use Cases](#common-use-cases)
   - [ETL/ELT Workflows](#etlelt-workflows)
   - [ML Pipelines](#ml-pipelines)
   - [dbt Integration](#dbt-integration)
   - [Data Quality Checks](#data-quality-checks)
   - [Incremental Processing and Partitioning](#incremental-processing-and-partitioning)
   - [Cross-Team Collaboration](#cross-team-collaboration)
4. [Production Case Studies](#production-case-studies)
5. [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Design Patterns

### Asset-based vs Op-based Patterns

#### Current Recommendation (2024-2025)

**Assets are the primary design pattern** in modern Dagster development. Ops are now primarily for legacy support or specialized edge cases.

#### When to Use Assets

- **Primary Use Case:** Building data pipelines where the goal is to produce and manage data artifacts
- **Best For:** New Dagster projects and teams
- **Represents:** Logical units of data (tables, datasets, ML models)
- **Benefits:**
  - Natural fit for data pipelines
  - Automatic data lineage tracking
  - Built-in observability
  - Declarative approach

**Example:**
```python
from dagster import asset

@asset
def customers_table(context):
    """Represents a table of customer data"""
    # Extract, transform, load logic
    return df

@asset(deps=[customers_table])
def customers_analytics(context):
    """Analytics derived from customers"""
    # Depends on customers_table
    return analytics_df
```

#### When to Use Ops

- **Edge Cases Only:** Workflows not centered around producing persistent data
- **Examples:**
  - Sending emails or notifications
  - Setting up database permissions
  - Correcting known data mistakes
  - Triggering webhooks
  - Scanning for unused tables to delete

**Example:**
```python
from dagster import op, job

@op
def send_notification(context):
    """Sends email - no persistent artifact created"""
    send_email(context.op_config["recipient"])

@job
def notification_job():
    send_notification()
```

#### Key Takeaway

> If your workflow produces a persistent data product, use **assets**. If it performs an action without creating a persistent artifact, consider **ops**.

---

### Factory Patterns for Assets

Asset factories are a powerful pattern for reducing code duplication and creating multiple similar assets from configuration.

#### Use Cases

1. **Repetitive ETL tasks** (e.g., processing multiple CSV files with same logic)
2. **Multi-source ingestion** (e.g., same API pattern for different endpoints)
3. **Per-client/tenant asset generation**
4. **Standardized transformations** across multiple data sources

#### Basic Factory Pattern

```python
from dagster import asset, AssetExecutionContext

def create_s3_csv_asset(asset_name: str, s3_key: str):
    """Factory that creates an asset for each CSV file"""

    @asset(name=asset_name)
    def _asset(context: AssetExecutionContext):
        # Download CSV from S3
        df = download_csv_from_s3(s3_key)
        # Transform
        transformed = run_sql_query(df)
        # Upload back to S3
        upload_to_s3(transformed, f"processed/{asset_name}.csv")
        return transformed

    return _asset

# Create multiple assets from factory
raw_data_asset = create_s3_csv_asset("raw_sales", "input/sales.csv")
raw_users_asset = create_s3_csv_asset("raw_users", "input/users.csv")
```

#### Advanced Factory with Dependencies

```python
from dagster import AssetIn, asset

def create_analytics_asset(source_name: str, upstream_asset_name: str):
    """Create analytics asset with dependency"""

    @asset(
        name=f"{source_name}_analytics",
        ins={"source_data": AssetIn(upstream_asset_name)}
    )
    def _analytics_asset(context, source_data):
        # Perform analytics on source data
        return compute_analytics(source_data)

    return _analytics_asset
```

#### Factory with Custom Decorator (DRY Pattern)

```python
import functools
from dagster import asset

def monitoring_asset(func):
    """Custom decorator that wraps asset with monitoring logic"""
    @functools.wraps(func)
    def wrapper(context, *args, **kwargs):
        context.log.info(f"Starting {func.__name__}")
        start_time = time.time()

        try:
            result = func(context, *args, **kwargs)
            duration = time.time() - start_time
            context.log_event(
                AssetMaterialization(
                    asset_key=func.__name__,
                    metadata={"duration": duration}
                )
            )
            return result
        except Exception as e:
            context.log.error(f"Failed: {str(e)}")
            raise

    return asset(wrapper)

@monitoring_asset
def my_asset(context):
    # Your logic here
    pass
```

#### Best Practices

- ✅ Use factories to keep code DRY
- ✅ Provide clear asset names via factory parameters
- ✅ Document what each factory creates
- ✅ Consider using components for complex factory patterns (new Dagster feature)
- ⚠️ Avoid creating too many assets from a single factory (limit: ~100)

---

### Resource Management Patterns

Resources provide dependency injection, abstracting external services and configuration.

#### ConfigurableResource Pattern (Modern Approach)

```python
from dagster import ConfigurableResource, asset
from pydantic import Field

class DatabaseResource(ConfigurableResource):
    """Database connection resource"""
    host: str
    port: int = Field(default=5432)
    database: str
    username: str
    password: str

    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.username,
            password=self.password
        )

    def execute_query(self, query: str):
        with self.get_connection() as conn:
            return pd.read_sql(query, conn)

# Using the resource in an asset
@asset
def user_data(database: DatabaseResource):
    """Asset using database resource"""
    return database.execute_query("SELECT * FROM users")
```

#### Resource Dependencies (Nested Resources)

```python
from dagster import ConfigurableResource

class AwsCredentials(ConfigurableResource):
    """Shared AWS credentials"""
    access_key: str
    secret_key: str
    region: str = "us-east-1"

class S3Resource(ConfigurableResource):
    """S3 resource depending on credentials"""
    credentials: AwsCredentials
    bucket: str

    def upload(self, key: str, data: bytes):
        client = boto3.client(
            's3',
            aws_access_key_id=self.credentials.access_key,
            aws_secret_access_key=self.credentials.secret_key,
            region_name=self.credentials.region
        )
        client.put_object(Bucket=self.bucket, Key=key, Body=data)

class RedshiftResource(ConfigurableResource):
    """Redshift also using same credentials"""
    credentials: AwsCredentials
    cluster: str

    def query(self, sql: str):
        # Use shared credentials
        pass

# In Definitions
from dagster import Definitions

defs = Definitions(
    assets=[user_data],
    resources={
        "aws_creds": AwsCredentials(
            access_key=EnvVar("AWS_ACCESS_KEY"),
            secret_key=EnvVar("AWS_SECRET_KEY")
        ),
        "s3": S3Resource(
            credentials=AwsCredentials(...),
            bucket="my-bucket"
        ),
        "redshift": RedshiftResource(
            credentials=AwsCredentials(...),
            cluster="my-cluster"
        )
    }
)
```

#### Environment-Specific Resources

```python
from dagster import EnvVar

# Using EnvVar for runtime evaluation
class ApiResource(ConfigurableResource):
    api_key: str
    base_url: str

# In Definitions
resources_by_env = {
    "dev": {
        "api": ApiResource(
            api_key=EnvVar("DEV_API_KEY"),
            base_url="https://dev-api.example.com"
        )
    },
    "prod": {
        "api": ApiResource(
            api_key=EnvVar("PROD_API_KEY"),
            base_url="https://api.example.com"
        )
    }
}

# Select based on environment
import os
env = os.getenv("DAGSTER_DEPLOYMENT", "dev")
selected_resources = resources_by_env[env]
```

#### Launch-Time Configuration

```python
from dagster import ConfigurableResource

class DynamicResource(ConfigurableResource):
    """Resource configured at launch time"""
    endpoint: str
    timeout: int = 30

# Mark for launch-time configuration
@asset
def my_asset(dynamic: DynamicResource):
    # Resource will be configured when run is launched
    pass

# In Definitions
defs = Definitions(
    assets=[my_asset],
    resources={
        "dynamic": DynamicResource.configure_at_launch()
    }
)
```

#### Best Practices

- ✅ Use `ConfigurableResource` for type-safe, validated resources
- ✅ Use `EnvVar` for secrets (evaluated at runtime, not visible in UI)
- ✅ Use nested resources for shared configuration (e.g., cloud credentials)
- ✅ Keep resources focused on external systems (databases, APIs, cloud services)
- ✅ Mock resources in tests using direct instantiation
- ⚠️ Avoid loading heavy clients at module level (see Anti-Patterns)

---

### Configuration Patterns

#### Multi-Environment Configuration

```python
from dagster import Definitions, EnvVar
import os

def get_resources_for_deployment():
    """Select resources based on deployment environment"""
    deployment = os.getenv("DAGSTER_DEPLOYMENT", "local")

    if deployment == "production":
        return {
            "warehouse": SnowflakeResource(
                account=EnvVar("SNOWFLAKE_ACCOUNT"),
                user=EnvVar("SNOWFLAKE_USER"),
                password=EnvVar("SNOWFLAKE_PASSWORD"),
                database="PROD_DB"
            )
        }
    elif deployment == "staging":
        return {
            "warehouse": SnowflakeResource(
                account=EnvVar("SNOWFLAKE_ACCOUNT"),
                user=EnvVar("SNOWFLAKE_USER"),
                password=EnvVar("SNOWFLAKE_PASSWORD"),
                database="STAGING_DB"
            )
        }
    else:  # local
        return {
            "warehouse": MockWarehouse()
        }

defs = Definitions(
    assets=all_assets,
    resources=get_resources_for_deployment()
)
```

#### Using YAML/Config Files

```python
import yaml
from pathlib import Path

def load_config(env: str):
    """Load configuration from YAML files"""
    config_path = Path(__file__).parent / "config" / f"{env}.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

# config/prod.yaml
# database:
#   host: prod-db.example.com
#   port: 5432
# feature_flags:
#   enable_ml_pipeline: true

config = load_config(os.getenv("DAGSTER_DEPLOYMENT", "local"))

defs = Definitions(
    assets=all_assets,
    resources={
        "db": DatabaseResource(**config["database"])
    }
)
```

---

### Testing Patterns

#### Unit Testing Assets

```python
from dagster import materialize, AssetExecutionContext

def test_user_data_asset():
    """Test individual asset"""
    # Create mock resource
    mock_db = DatabaseResource(
        host="localhost",
        database="test_db",
        username="test",
        password="test"
    )

    # Materialize the asset with mock resource
    result = materialize(
        [user_data],
        resources={"database": mock_db}
    )

    # Assert success
    assert result.success

    # Get materialized data
    output = result.output_for_node("user_data")
    assert len(output) > 0
    assert "user_id" in output.columns
```

#### Testing Assets with Dependencies

```python
def test_downstream_asset():
    """Test multiple assets together"""
    mock_db = DatabaseResource(...)

    # Materialize both upstream and downstream
    result = materialize(
        [user_data, user_analytics],
        resources={"database": mock_db}
    )

    assert result.success
    analytics = result.output_for_node("user_analytics")
    assert analytics["avg_age"] > 0
```

#### Integration Testing

```python
from dagster import build_op_context

def test_asset_with_real_database():
    """Integration test with real external service"""
    # Use actual test database
    test_db = DatabaseResource(
        host=os.getenv("TEST_DB_HOST"),
        database="test_dagster",
        username=os.getenv("TEST_DB_USER"),
        password=os.getenv("TEST_DB_PASSWORD")
    )

    result = materialize(
        [user_data],
        resources={"database": test_db}
    )

    assert result.success
```

#### Testing with Fixtures (pytest)

```python
import pytest
from dagster import materialize

@pytest.fixture
def mock_database():
    """Reusable mock database fixture"""
    return DatabaseResource(
        host="localhost",
        database="test",
        username="test",
        password="test"
    )

@pytest.fixture
def mock_s3():
    """Mock S3 resource"""
    return MockS3Resource(bucket="test-bucket")

def test_etl_pipeline(mock_database, mock_s3):
    """Test full pipeline with fixtures"""
    result = materialize(
        all_assets,
        resources={
            "database": mock_database,
            "s3": mock_s3
        }
    )

    assert result.success
```

#### Best Practices

- ✅ Test individual assets as Python functions when possible
- ✅ Use `materialize()` to test assets with resources
- ✅ Mock external services to avoid hitting real APIs/databases in unit tests
- ✅ Create integration tests for critical paths using test environments
- ✅ Use pytest fixtures for reusable test resources
- ✅ Test asset logic in development, not after expensive batch runs in staging
- ⚠️ Don't test entire jobs; focus on individual assets or small groups

---

### Error Handling and Retry Strategies

#### Op-Level Retry Policies

```python
from dagster import asset, RetryPolicy, Backoff, Jitter

# Basic retry policy
@asset(
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=1,  # seconds between retries
    )
)
def flaky_api_call(context):
    """Automatically retries on failure"""
    return call_external_api()

# Advanced retry with exponential backoff
@asset(
    retry_policy=RetryPolicy(
        max_retries=5,
        delay=2,
        backoff=Backoff.EXPONENTIAL,  # 2s, 4s, 8s, 16s, 32s
        jitter=Jitter.PLUS_MINUS  # Add randomness to avoid thundering herd
    )
)
def cloud_service_call(context):
    """Handles transient cloud service failures"""
    return upload_to_cloud_service()
```

#### Manual Retry Control

```python
from dagster import asset, RetryRequested

@asset
def conditional_retry_asset(context):
    """Custom retry logic based on error type"""
    try:
        return process_data()
    except TransientNetworkError as e:
        # Retry on transient errors
        context.log.warning(f"Transient error: {e}, retrying...")
        raise RetryRequested(max_retries=3, seconds_to_wait=5)
    except PermanentError as e:
        # Don't retry on permanent errors
        context.log.error(f"Permanent error: {e}")
        raise
```

#### Failure Exceptions with Metadata

```python
from dagster import asset, Failure, MetadataValue

@asset
def data_validation_asset(context):
    """Asset that can fail with structured metadata"""
    data = load_data()

    if data.null_count() > 1000:
        raise Failure(
            description="Too many null values detected",
            metadata={
                "null_count": MetadataValue.int(data.null_count()),
                "total_rows": MetadataValue.int(len(data)),
                "threshold": MetadataValue.int(1000),
                "sample_nulls": MetadataValue.json(
                    data[data.isnull()].head().to_dict()
                )
            },
            allow_retries=False  # Don't retry, this is a data quality issue
        )

    return data
```

#### Run-Level Retries

```python
from dagster import job, asset, RunRequest

# Configure run retries via tags
@asset(
    tags={
        "dagster/retry_strategy": "FROM_FAILURE",  # Default
        # or "ALL_STEPS" to re-run everything
    }
)
def my_asset(context):
    return process()

# In schedules/sensors
@schedule(...)
def my_schedule(context):
    return RunRequest(
        tags={
            "dagster/max_retries": "3",
            "dagster/retry_strategy": "FROM_FAILURE"
        }
    )
```

#### Best Practices

- ✅ Use `RetryPolicy` for transient failures (network, cloud services, timeouts)
- ✅ Use exponential backoff for external APIs to avoid overwhelming them
- ✅ Add jitter to prevent thundering herd problems
- ✅ Use `Failure` with `allow_retries=False` for data quality issues
- ✅ Include rich metadata in failures for debugging
- ✅ Use manual `RetryRequested` for conditional retry logic
- ⚠️ Don't retry framework errors (Dagster internal errors)
- ⚠️ Be mindful of retry limits on billable cloud services

---

### Dependency Management Patterns

#### Basic Asset Dependencies

```python
from dagster import asset

# Implicit dependency via function argument
@asset
def upstream_data(context):
    return fetch_raw_data()

@asset
def downstream_analytics(context, upstream_data):
    """Depends on upstream_data (argument name matches asset name)"""
    return compute_analytics(upstream_data)
```

#### Explicit Dependencies with `deps`

```python
from dagster import asset

@asset(deps=[upstream_data])
def side_effect_asset(context):
    """Depends on upstream_data but doesn't need the data"""
    # Just needs upstream to run first
    send_notification("upstream_data is ready")
```

#### AssetIn for Custom Configuration

```python
from dagster import asset, AssetIn

@asset(
    ins={
        "raw_data": AssetIn(
            key="upstream_data",  # Different name than parameter
            metadata={"schema": "raw"},
        )
    }
)
def transformed_data(context, raw_data):
    """Custom dependency configuration"""
    return transform(raw_data)
```

#### Partitioned Asset Dependencies

```python
from dagster import asset, DailyPartitionsDefinition, AssetIn

daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily_partitions)
def daily_sales(context):
    """Partitioned by day"""
    date = context.partition_key
    return fetch_sales_for_date(date)

@asset(
    partitions_def=daily_partitions,
    ins={
        "daily_sales": AssetIn(
            partition_mapping=TimeWindowPartitionMapping()
        )
    }
)
def weekly_sales_report(context, daily_sales):
    """Aggregates daily sales into weekly reports"""
    return aggregate_to_weekly(daily_sales)
```

#### Cross-Asset Dependencies

```python
from dagster import asset, AssetIn

# Asset from another team/project
@asset
def external_customer_data(context):
    """Managed by Team A"""
    return load_from_warehouse("team_a.customers")

# Your asset depending on external asset
@asset(deps=["external_customer_data"])
def customer_analytics(context):
    """Managed by Team B, depends on Team A's asset"""
    return compute_analytics()
```

#### Multi-Asset Dependencies

```python
from dagster import multi_asset, AssetOut

@multi_asset(
    outs={
        "customers": AssetOut(),
        "orders": AssetOut(),
    }
)
def extract_from_database(context):
    """Single asset definition creating multiple assets"""
    customers_df = extract_customers()
    orders_df = extract_orders()
    return customers_df, orders_df

# Depending on outputs of multi-asset
@asset
def customer_orders_joined(context, customers, orders):
    """Depends on both outputs of the multi-asset"""
    return customers.join(orders, on="customer_id")
```

#### Best Practices

- ✅ Use function arguments for dependencies when you need the data
- ✅ Use `deps` parameter when you only need ordering, not data
- ✅ Use `AssetIn` for custom partition mappings or metadata
- ✅ Keep dependency chains understandable (avoid deeply nested dependencies)
- ✅ Document cross-team dependencies clearly
- ⚠️ Avoid circular dependencies (Dagster will error)

---

## Best Practices

### Code Organization and Project Structure

#### Default Scaffold Structure

```
my_dagster_project/
├── pyproject.toml
├── setup.py
├── my_project/
│   ├── __init__.py
│   ├── definitions.py      # Main Definitions object
│   └── assets/             # All asset definitions
│       ├── __init__.py
│       └── core_assets.py
└── tests/
    └── test_assets.py
```

#### Organization by Technology (Recommended for Technical Teams)

```
my_dagster_project/
├── my_project/
│   ├── definitions.py
│   ├── assets/
│   │   ├── postgres/          # PostgreSQL assets
│   │   │   ├── raw_tables.py
│   │   │   └── transformed.py
│   │   ├── s3/                # S3 assets
│   │   │   └── data_lake.py
│   │   ├── snowflake/         # Snowflake assets
│   │   │   └── warehouse.py
│   │   └── apis/              # External API assets
│   │       ├── salesforce.py
│   │       └── stripe.py
│   ├── resources/
│   │   ├── postgres.py
│   │   ├── s3.py
│   │   └── snowflake.py
│   ├── schedules/
│   │   └── daily_jobs.py
│   └── sensors/
│       └── file_sensors.py
```

#### Organization by Business Domain (Recommended for Data Products)

```
my_dagster_project/
├── my_project/
│   ├── definitions.py
│   ├── assets/
│   │   ├── raw_data/          # Landing zone
│   │   │   ├── customer_raw.py
│   │   │   └── sales_raw.py
│   │   ├── cleaned/           # Cleaned/standardized
│   │   │   └── customer_cleaned.py
│   │   ├── analytical/        # Business logic applied
│   │   │   ├── customer_360.py
│   │   │   └── sales_analytics.py
│   │   ├── bi_reports/        # BI tool datasets
│   │   │   └── executive_dashboard.py
│   │   └── ml_models/         # ML features/models
│   │       ├── churn_features.py
│   │       └── churn_model.py
│   └── resources/
│       └── shared_resources.py
```

#### Organization by Data Processing Concept

```
my_dagster_project/
├── my_project/
│   ├── assets/
│   │   ├── ingestion/         # Data ingestion
│   │   │   ├── api_ingestion.py
│   │   │   └── file_ingestion.py
│   │   ├── transformation/    # Data transformation
│   │   │   ├── bronze_to_silver.py
│   │   │   └── silver_to_gold.py
│   │   └── serving/           # Data serving
│   │       ├── analytics_marts.py
│   │       └── ml_features.py
```

#### Evolution Strategy

**Phase 1: Everything in One File (0-400 lines)**
```python
# definitions.py
from dagster import asset, Definitions

@asset
def asset1(): ...

@asset
def asset2(): ...

defs = Definitions(
    assets=[asset1, asset2],
    resources={...},
    schedules=[...]
)
```

**Phase 2: Separate Concerns (400-2000 lines)**
```python
# assets/__init__.py
from .raw_data import raw_assets
from .analytics import analytics_assets

all_assets = [*raw_assets, *analytics_assets]

# definitions.py
from .assets import all_assets
from .resources import all_resources
from .schedules import all_schedules

defs = Definitions(
    assets=all_assets,
    resources=all_resources,
    schedules=all_schedules
)
```

**Phase 3: Domain/Technology Grouping (2000+ lines, multiple teams)**
```python
# Organize by domain as shown in previous examples
```

#### Integration Projects (dbt, Sling, etc.)

```
project_root/
├── dagster_project/           # Dagster orchestration code
│   └── my_project/
│       ├── definitions.py
│       └── assets/
│           └── dbt_assets.py  # References dbt project
├── dbt_project/               # Separate dbt project
│   ├── dbt_project.yml
│   ├── models/
│   └── tests/
└── sling_project/             # Separate Sling project
    └── replication.yaml
```

#### Best Practices

- ✅ Start simple (one file) and evolve as needed
- ✅ Organize by business domain if stakeholders think in terms of data products
- ✅ Organize by technology if engineers need to find tech-specific code quickly
- ✅ Keep related assets together in the same module
- ✅ Use `__init__.py` to export public APIs
- ✅ Store integration projects (dbt, Jupyter) outside Dagster project
- ✅ Mirror your organization's language in your structure
- ⚠️ Don't over-engineer structure for small projects

---

### Asset Naming Conventions

#### General Naming Guidelines

```python
from dagster import asset

# ✅ Good: Descriptive, noun-based, lowercase with underscores
@asset
def daily_active_users(context):
    """Clear what this represents"""
    pass

@asset
def customer_churn_predictions(context):
    """Describes the data product"""
    pass

# ❌ Bad: Verb-based, unclear, overly technical
@asset
def process_data(context):  # What data?
    pass

@asset
def etl_job_3(context):  # Meaningless name
    pass
```

#### Naming by Layer (Medallion Architecture)

```python
# Bronze layer (raw data)
@asset
def bronze_customers_raw(context):
    """Raw customer data from source system"""
    pass

# Silver layer (cleaned, conformed)
@asset
def silver_customers_cleaned(context):
    """Cleaned and validated customer data"""
    pass

# Gold layer (business-ready)
@asset
def gold_customer_360_view(context):
    """Complete customer 360 view for analytics"""
    pass
```

#### Naming with Source Prefix

```python
# Indicate source system
@asset
def salesforce_accounts(context):
    pass

@asset
def stripe_payments(context):
    pass

@asset
def postgres_users(context):
    pass
```

#### Naming for Derived Assets

```python
@asset
def customers(context):
    """Base customer data"""
    pass

@asset
def customers_with_orders(context, customers):
    """Customers enriched with order data"""
    pass

@asset
def high_value_customers(context, customers_with_orders):
    """Customers with >$1000 lifetime value"""
    pass
```

#### Asset Keys and Groups

```python
from dagster import asset, AssetKey

# Using groups to organize related assets
@asset(group_name="customer_data")
def customers(context):
    pass

@asset(group_name="customer_data")
def customer_orders(context):
    pass

@asset(group_name="analytics")
def customer_analytics(context):
    pass

# Custom asset keys for complex naming
@asset(key=AssetKey(["warehouse", "prod", "customers"]))
def customers_asset(context):
    """Asset with multi-part key: warehouse/prod/customers"""
    pass
```

#### Best Practices

- ✅ Use descriptive, noun-based names
- ✅ Use lowercase with underscores (Python convention)
- ✅ Include source/layer information when helpful
- ✅ Be consistent within your organization
- ✅ Use groups to organize related assets
- ✅ Name assets after the data they represent, not the process
- ⚠️ Avoid overly long names (>50 characters)
- ❌ Don't use verb phrases like "get_data" or "process_orders"

---

### Performance Optimization

#### Resource Allocation (Dagster+ Hybrid)

**Agent Container:**
- Start: 0.25 vCPU core, 1 GB RAM
- Scale with: Number of concurrent runs, number of code locations

**Code Server Container:**
- Start: 0.25 vCPU cores, 1GB RAM
- Scale with: Import size, definition graph size, heavy initialization

**Run Containers (K8s/ECS):**
- Standard: 4 vCPU cores, 8-16 GB RAM
- Compute-heavy: Scale CPU and memory in run workers, not code servers

#### Limiting Concurrency

```python
from dagster import define_asset_job, Definitions
from dagster import RunRequest, sensor

# Limit concurrent runs in job config
@sensor(...)
def my_sensor(context):
    return RunRequest(
        run_key=f"run_{timestamp}",
        tags={
            "dagster/concurrency_key": "my_pipeline",
            "dagster/max_concurrent": "3"  # Only 3 runs at once
        }
    )
```

#### Optimizing Asset Execution

```python
from dagster import asset, OpExecutionContext

@asset
def optimized_asset(context: OpExecutionContext):
    """Asset with performance optimizations"""

    # 1. Use generators for large datasets
    def process_in_batches():
        for batch in fetch_data_in_batches(batch_size=10000):
            yield process_batch(batch)

    # 2. Log progress for long-running operations
    total_records = 1000000
    for i, result in enumerate(process_in_batches()):
        if i % 100 == 0:
            context.log.info(f"Processed {i*10000}/{total_records} records")

    # 3. Return metadata for observability
    context.add_output_metadata({
        "num_records": total_records,
        "execution_time_seconds": 123.45
    })
```

#### Partition Optimization

```python
from dagster import asset, DailyPartitionsDefinition

# ✅ Good: Reasonable partition count
daily_partitions = DailyPartitionsDefinition(
    start_date="2024-01-01",
    end_offset=0  # Don't partition future dates
)

@asset(partitions_def=daily_partitions)
def daily_data(context):
    """Recommended: <100,000 partitions"""
    date = context.partition_key
    return fetch_data_for_date(date)

# ⚠️ Warning: Too many partitions
hourly_partitions = HourlyPartitionsDefinition(
    start_date="2020-01-01"  # Creates 40,000+ partitions
)
```

#### Dynamic Output Optimization

```python
from dagster import asset, Output

@asset
def efficient_io_manager_asset(context):
    """Efficient use of I/O managers"""

    large_dataframe = process_data()

    # Write in chunks to S3 instead of single large write
    return Output(
        large_dataframe,
        metadata={
            "row_count": len(large_dataframe),
            "partition_strategy": "chunked"
        }
    )
```

#### Best Practices

- ✅ Start with recommended resource allocations and scale based on metrics
- ✅ Limit partition counts to <100,000 per asset
- ✅ Use concurrency limits to prevent overwhelming external systems
- ✅ Process large datasets in batches/chunks
- ✅ Log progress for long-running operations
- ✅ Use Dagster Insights to identify bottlenecks
- ⚠️ Monitor memory usage in code server containers
- ⚠️ Don't load heavy libraries at module level (see Anti-Patterns)

---

### Observability and Logging

#### Structured Logging

```python
from dagster import asset, OpExecutionContext

@asset
def observable_asset(context: OpExecutionContext):
    """Asset with comprehensive logging"""

    # Different log levels
    context.log.debug("Starting data fetch")
    context.log.info("Processing 10,000 records")
    context.log.warning("Found 5 invalid records, skipping")
    context.log.error("Failed to connect to API, retrying")

    # Structured logging with metadata
    context.log.info(
        "Data processing complete",
        extra={
            "records_processed": 10000,
            "invalid_records": 5,
            "processing_time_ms": 1234
        }
    )

    return data
```

#### Asset Materialization Metadata

```python
from dagster import asset, MetadataValue, OpExecutionContext

@asset
def asset_with_metadata(context: OpExecutionContext):
    """Asset that logs rich metadata"""

    result_df = process_data()

    # Add metadata to materialization
    context.add_output_metadata({
        # Scalar values
        "num_rows": len(result_df),
        "num_columns": len(result_df.columns),

        # Statistical metadata
        "mean_age": MetadataValue.float(result_df["age"].mean()),
        "null_count": MetadataValue.int(result_df.isnull().sum().sum()),

        # URLs and paths
        "data_location": MetadataValue.url("s3://bucket/data.parquet"),

        # JSON metadata
        "column_stats": MetadataValue.json({
            col: {
                "mean": result_df[col].mean(),
                "std": result_df[col].std()
            }
            for col in result_df.select_dtypes(include=['number']).columns
        }),

        # Markdown reports
        "quality_report": MetadataValue.md(f"""
        ## Data Quality Report
        - Total Rows: {len(result_df)}
        - Null Values: {result_df.isnull().sum().sum()}
        - Duplicate Rows: {result_df.duplicated().sum()}
        """)
    })

    return result_df
```

#### Asset Observations (for External Assets)

```python
from dagster import asset, AssetObservation, MetadataValue

@asset
def observed_external_asset(context):
    """Observe external asset without materializing"""

    # Check external data source
    s3_data = check_s3_bucket("my-bucket/data/")

    # Log observation
    context.log_event(
        AssetObservation(
            asset_key="external_s3_data",
            metadata={
                "file_count": MetadataValue.int(len(s3_data)),
                "total_size_mb": MetadataValue.float(
                    sum(f.size for f in s3_data) / 1024 / 1024
                ),
                "last_modified": MetadataValue.timestamp(
                    max(f.last_modified for f in s3_data)
                )
            }
        )
    )
```

#### Integration with CloudWatch

```python
from dagster_aws.cloudwatch import cloudwatch_logger
from dagster import Definitions

# Send logs to CloudWatch
defs = Definitions(
    assets=all_assets,
    resources={
        "cloudwatch": cloudwatch_logger
    }
)
```

#### Custom Metrics and Monitoring

```python
from dagster import asset, OpExecutionContext
import time

@asset
def monitored_asset(context: OpExecutionContext):
    """Asset with custom metrics"""

    start_time = time.time()

    try:
        result = process_data()

        # Log success metrics
        duration = time.time() - start_time
        context.add_output_metadata({
            "success": True,
            "duration_seconds": duration,
            "records_processed": len(result),
            "throughput_records_per_sec": len(result) / duration
        })

        return result

    except Exception as e:
        # Log failure metrics
        context.log.error(f"Asset failed: {str(e)}")
        context.add_output_metadata({
            "success": False,
            "error_message": str(e),
            "error_type": type(e).__name__
        })
        raise
```

#### Best Practices

- ✅ Use appropriate log levels (debug, info, warning, error)
- ✅ Add rich metadata to asset materializations
- ✅ Include business metrics in metadata (row counts, data quality)
- ✅ Use MetadataValue types for proper rendering in UI
- ✅ Log observations for external assets you monitor but don't create
- ✅ Integrate with external monitoring (CloudWatch, Datadog, etc.)
- ✅ Track execution time and throughput
- ⚠️ Don't log sensitive data (PII, credentials)
- ⚠️ Be mindful of log volume (can impact performance)

---

### CI/CD Integration

#### Branch Deployments Pattern

Dagster+ provides automatic branch deployments for every pull request.

**Benefits:**
- Automatic staging environment per PR
- Preview changes without affecting production
- Compare asset definitions between branch and main
- Test changes in isolation

**Setup with GitHub Actions:**

```yaml
# .github/workflows/dagster-cloud-deploy.yml
name: Dagster Cloud Deploy

on:
  push:
    branches:
      - main
  pull_request:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Validate dagster_cloud.yaml
        run: |
          pip install dagster-cloud
          dagster-cloud ci check --project-dir .

      - name: Deploy to Dagster Cloud
        env:
          DAGSTER_CLOUD_API_TOKEN: ${{ secrets.DAGSTER_CLOUD_API_TOKEN }}
        run: |
          if [ "${{ github.ref }}" == "refs/heads/main" ]; then
            dagster-cloud ci deploy --project-dir . --deployment prod
          else
            dagster-cloud ci deploy --project-dir . --deployment pr-${{ github.event.pull_request.number }}
          fi
```

#### Hybrid Deployment with Kubernetes

```yaml
# .github/workflows/dagster-hybrid-deploy.yml
name: Deploy Dagster User Code

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Build Docker Image
        run: |
          docker build -t my-dagster-code:${{ github.sha }} .
          docker push my-registry/dagster-code:${{ github.sha }}

      - name: Update Kubernetes ConfigMap
        run: |
          kubectl create configmap dagster-workspace \
            --from-file=workspace.yaml \
            --dry-run=client -o yaml | kubectl apply -f -

      - name: Deploy to Dagster+
        env:
          DAGSTER_CLOUD_API_TOKEN: ${{ secrets.DAGSTER_CLOUD_API_TOKEN }}
        run: |
          dagster-cloud ci deploy \
            --location-name my_code_location \
            --image my-registry/dagster-code:${{ github.sha }}
```

#### Serverless Deployment

```yaml
# dagster_cloud.yaml
locations:
  - location_name: my_dagster_code
    code_source:
      package_name: my_project
    build:
      directory: .
      registry: docker.io/mycompany/dagster
```

#### Testing in CI

```yaml
# .github/workflows/test.yml
name: Test Dagster Code

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest tests/ -v

      - name: Validate definitions
        run: |
          python -c "from my_project.definitions import defs; print(defs)"

      - name: Check asset dependencies
        run: |
          dagster asset list
          dagster asset check
```

#### Separation of Concerns Pattern

**System Deployment** (Dagit, daemons): Managed by Dagster+/ops team

**User Code Deployment** (your data pipelines): Managed by data teams via CI/CD

This separation allows data teams to deploy code independently without affecting the Dagster platform.

#### Best Practices

- ✅ Use branch deployments for PR previews
- ✅ Run tests before deploying to production
- ✅ Validate `dagster_cloud.yaml` in CI
- ✅ Use separate deployments for dev/staging/prod
- ✅ Tag Docker images with git SHA for traceability
- ✅ Automate deployment on merge to main
- ✅ Use environment-specific secrets in CI
- ⚠️ Don't skip validation steps to speed up CI
- ❌ Never force push to main or skip hooks

---

### Multi-Environment Setups

#### Environment-Based Resource Selection

```python
from dagster import Definitions, EnvVar
import os

def get_resources_by_environment():
    """Select resources based on DAGSTER_DEPLOYMENT environment variable"""

    env = os.getenv("DAGSTER_DEPLOYMENT", "local")

    if env == "production":
        return {
            "database": SnowflakeResource(
                account=EnvVar("SNOWFLAKE_ACCOUNT"),
                user=EnvVar("SNOWFLAKE_USER"),
                password=EnvVar("SNOWFLAKE_PASSWORD"),
                database="PROD",
                warehouse="PROD_WH",
                role="PROD_ROLE"
            ),
            "s3": S3Resource(
                bucket="prod-data-bucket",
                aws_access_key_id=EnvVar("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=EnvVar("AWS_SECRET_ACCESS_KEY")
            )
        }

    elif env == "staging":
        return {
            "database": SnowflakeResource(
                account=EnvVar("SNOWFLAKE_ACCOUNT"),
                user=EnvVar("SNOWFLAKE_USER"),
                password=EnvVar("SNOWFLAKE_PASSWORD"),
                database="STAGING",
                warehouse="STAGING_WH",
                role="STAGING_ROLE"
            ),
            "s3": S3Resource(
                bucket="staging-data-bucket",
                aws_access_key_id=EnvVar("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=EnvVar("AWS_SECRET_ACCESS_KEY")
            )
        }

    else:  # local development
        return {
            "database": MockSnowflakeResource(),
            "s3": MockS3Resource()
        }

defs = Definitions(
    assets=all_assets,
    resources=get_resources_by_environment()
)
```

#### EnvVar vs os.getenv

```python
from dagster import ConfigurableResource, EnvVar
import os

class MyResource(ConfigurableResource):
    # ✅ EnvVar: Retrieved at runtime, not visible in UI
    api_key: str = EnvVar("API_KEY")

    # ⚠️ os.getenv: Retrieved at load time, visible in UI
    endpoint: str = os.getenv("API_ENDPOINT", "https://api.example.com")
```

**Key Differences:**
- `EnvVar`: Value retrieved when resource is used (runtime), not visible in Dagster UI, more secure for secrets
- `os.getenv`: Value retrieved when code loads, visible in UI, use for non-sensitive config

#### Dagster+ Environment Variables

In Dagster+, you can configure environment variables with different scopes:

```yaml
# Via Dagster+ UI or API
# Deployment scope: production, staging, branch deployments
# Code location scope: specific code locations

# Example scopes:
# - production deployment, all code locations
# - production deployment, specific code location
# - branch deployments only
# - all deployments
```

#### Configuration File Pattern

```python
# config/local.yaml
database:
  type: sqlite
  path: ./dev.db

storage:
  type: local
  path: ./data

# config/production.yaml
database:
  type: snowflake
  account: ${SNOWFLAKE_ACCOUNT}
  database: PROD

storage:
  type: s3
  bucket: prod-data-bucket

# Load configuration
import yaml
from pathlib import Path

def load_config():
    env = os.getenv("DAGSTER_DEPLOYMENT", "local")
    config_path = Path(__file__).parent / "config" / f"{env}.yaml"

    with open(config_path) as f:
        return yaml.safe_load(f)

config = load_config()
```

#### Feature Flags per Environment

```python
from dagster import asset, Definitions
import os

ENABLE_ML_PIPELINE = os.getenv("ENABLE_ML_PIPELINE", "false") == "true"
ENABLE_EXPERIMENTAL_FEATURES = os.getenv("ENABLE_EXPERIMENTAL", "false") == "true"

@asset
def ml_predictions(context):
    """Only runs if ML pipeline is enabled"""
    return train_and_predict()

# Conditionally include assets
ml_assets = [ml_predictions] if ENABLE_ML_PIPELINE else []

defs = Definitions(
    assets=[
        *core_assets,
        *ml_assets,  # Only included in environments where flag is true
    ],
    resources=get_resources_by_environment()
)
```

#### Testing Different Environments

```python
import pytest
import os

@pytest.fixture
def local_env(monkeypatch):
    """Set up local environment"""
    monkeypatch.setenv("DAGSTER_DEPLOYMENT", "local")
    yield

@pytest.fixture
def prod_env(monkeypatch):
    """Set up production environment"""
    monkeypatch.setenv("DAGSTER_DEPLOYMENT", "production")
    monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "test-account")
    monkeypatch.setenv("SNOWFLAKE_USER", "test-user")
    monkeypatch.setenv("SNOWFLAKE_PASSWORD", "test-pass")
    yield

def test_local_resources(local_env):
    """Test that local environment uses mocks"""
    from my_project.definitions import defs
    assert isinstance(defs.resources["database"], MockSnowflakeResource)

def test_prod_resources(prod_env):
    """Test that prod environment uses real resources"""
    from my_project.definitions import defs
    assert isinstance(defs.resources["database"], SnowflakeResource)
```

#### Best Practices

- ✅ Use `DAGSTER_DEPLOYMENT` environment variable to determine environment
- ✅ Use `EnvVar` for secrets (runtime evaluation, not visible in UI)
- ✅ Use `os.getenv` for non-sensitive configuration
- ✅ Provide mock resources for local development
- ✅ Use Dagster+ environment variable scoping for fine-grained control
- ✅ Test your configuration loading logic
- ✅ Document required environment variables
- ⚠️ Never commit secrets to version control
- ⚠️ Validate required environment variables at startup

---

## Common Use Cases

### ETL/ELT Workflows

#### Basic ETL Pipeline

```python
from dagster import asset, AssetExecutionContext

# Extract
@asset
def raw_customer_data(context: AssetExecutionContext) -> pd.DataFrame:
    """Extract customer data from source database"""
    context.log.info("Extracting customer data from PostgreSQL")

    df = pd.read_sql(
        "SELECT * FROM customers WHERE updated_at >= %(since)s",
        connection,
        params={"since": "2024-01-01"}
    )

    context.add_output_metadata({
        "num_rows": len(df),
        "columns": list(df.columns)
    })

    return df

# Transform
@asset
def cleaned_customer_data(
    context: AssetExecutionContext,
    raw_customer_data: pd.DataFrame
) -> pd.DataFrame:
    """Clean and validate customer data"""
    context.log.info("Cleaning customer data")

    # Remove duplicates
    df = raw_customer_data.drop_duplicates(subset=['customer_id'])

    # Validate email format
    df = df[df['email'].str.contains('@')]

    # Standardize phone numbers
    df['phone'] = df['phone'].apply(standardize_phone)

    # Handle nulls
    df['country'] = df['country'].fillna('Unknown')

    context.add_output_metadata({
        "num_rows": len(df),
        "duplicates_removed": len(raw_customer_data) - len(df),
        "null_counts": df.isnull().sum().to_dict()
    })

    return df

# Load
@asset
def customer_warehouse_table(
    context: AssetExecutionContext,
    cleaned_customer_data: pd.DataFrame,
    warehouse: SnowflakeResource
):
    """Load cleaned data to Snowflake"""
    context.log.info("Loading data to Snowflake")

    warehouse.write_table(
        table="prod.customers",
        data=cleaned_customer_data,
        if_exists="replace"
    )

    context.add_output_metadata({
        "rows_loaded": len(cleaned_customer_data),
        "target_table": "prod.customers"
    })
```

#### ELT Pipeline (Load then Transform in Warehouse)

```python
from dagster import asset

# Extract & Load (EL)
@asset
def raw_sales_landing(context, s3: S3Resource, snowflake: SnowflakeResource):
    """Extract from S3 and load raw to Snowflake"""

    # Copy directly from S3 to Snowflake (no transformation)
    snowflake.execute("""
        COPY INTO raw.sales
        FROM 's3://bucket/sales/'
        CREDENTIALS = (AWS_KEY_ID='...' AWS_SECRET_KEY='...')
        FILE_FORMAT = (TYPE = 'CSV');
    """)

    return "loaded"

# Transform in warehouse
@asset(deps=[raw_sales_landing])
def silver_sales_cleaned(context, snowflake: SnowflakeResource):
    """Transform data using SQL in Snowflake"""

    snowflake.execute("""
        CREATE OR REPLACE TABLE silver.sales AS
        SELECT
            order_id,
            customer_id,
            DATE(order_date) as order_date,
            ROUND(amount, 2) as amount,
            UPPER(TRIM(status)) as status
        FROM raw.sales
        WHERE amount > 0
            AND order_date >= CURRENT_DATE - 90
    """)

    return "transformed"

@asset(deps=[silver_sales_cleaned])
def gold_daily_sales_summary(context, snowflake: SnowflakeResource):
    """Create business-ready aggregates"""

    snowflake.execute("""
        CREATE OR REPLACE TABLE gold.daily_sales_summary AS
        SELECT
            order_date,
            COUNT(DISTINCT order_id) as num_orders,
            COUNT(DISTINCT customer_id) as num_customers,
            SUM(amount) as total_revenue,
            AVG(amount) as avg_order_value
        FROM silver.sales
        GROUP BY order_date
    """)
```

#### Multi-Source ETL with Joins

```python
@asset
def salesforce_accounts(context):
    """Extract from Salesforce"""
    return extract_from_salesforce("Account")

@asset
def stripe_payments(context):
    """Extract from Stripe"""
    return extract_from_stripe("charges")

@asset
def postgres_users(context):
    """Extract from PostgreSQL"""
    return extract_from_postgres("users")

@asset
def unified_customer_view(
    context,
    salesforce_accounts,
    stripe_payments,
    postgres_users
):
    """Join data from multiple sources"""

    # Merge on email
    customers = postgres_users.merge(
        salesforce_accounts,
        on='email',
        how='left'
    )

    # Add payment data
    customers = customers.merge(
        stripe_payments.groupby('customer_email').agg({
            'amount': 'sum',
            'charge_id': 'count'
        }).rename(columns={'charge_id': 'num_purchases'}),
        left_on='email',
        right_index=True,
        how='left'
    )

    return customers
```

---

### ML Pipelines

#### End-to-End ML Pipeline

```python
from dagster import asset, AssetExecutionContext
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Feature Engineering
@asset
def ml_features(context: AssetExecutionContext, cleaned_customer_data: pd.DataFrame):
    """Engineer features for ML model"""

    features = cleaned_customer_data.copy()

    # Create features
    features['account_age_days'] = (
        pd.Timestamp.now() - pd.to_datetime(features['created_at'])
    ).dt.days

    features['is_premium'] = features['subscription_type'] == 'premium'

    # Encode categoricals
    features = pd.get_dummies(features, columns=['country', 'industry'])

    context.add_output_metadata({
        "num_features": len(features.columns),
        "num_samples": len(features)
    })

    return features

# 2. Train/Test Split
@asset
def train_test_data(context, ml_features: pd.DataFrame):
    """Split data into train and test sets"""

    X = ml_features.drop(columns=['churn_label'])
    y = ml_features['churn_label']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    context.add_output_metadata({
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "positive_rate_train": y_train.mean(),
        "positive_rate_test": y_test.mean()
    })

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }

# 3. Train Model
@asset
def churn_model(context, train_test_data: dict):
    """Train churn prediction model"""

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )

    model.fit(
        train_test_data["X_train"],
        train_test_data["y_train"]
    )

    # Save model
    model_path = "/models/churn_model.pkl"
    joblib.dump(model, model_path)

    context.add_output_metadata({
        "model_path": model_path,
        "n_estimators": 100,
        "max_depth": 10
    })

    return model

# 4. Evaluate Model
@asset
def model_evaluation(context, churn_model, train_test_data: dict):
    """Evaluate model performance"""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    y_pred = churn_model.predict(train_test_data["X_test"])

    metrics = {
        "accuracy": accuracy_score(train_test_data["y_test"], y_pred),
        "precision": precision_score(train_test_data["y_test"], y_pred),
        "recall": recall_score(train_test_data["y_test"], y_pred),
        "f1": f1_score(train_test_data["y_test"], y_pred)
    }

    context.add_output_metadata({
        **{k: MetadataValue.float(v) for k, v in metrics.items()},
        "evaluation_report": MetadataValue.md(f"""
        ## Model Performance
        - Accuracy: {metrics['accuracy']:.3f}
        - Precision: {metrics['precision']:.3f}
        - Recall: {metrics['recall']:.3f}
        - F1 Score: {metrics['f1']:.3f}
        """)
    })

    return metrics

# 5. Generate Predictions
@asset(deps=[model_evaluation])  # Only run if evaluation passed
def customer_churn_predictions(context, churn_model, cleaned_customer_data):
    """Generate predictions for all customers"""

    # Load model
    model = churn_model

    # Prepare features (same as training)
    features = prepare_features(cleaned_customer_data)

    # Predict
    predictions = model.predict_proba(features)[:, 1]

    result = cleaned_customer_data.copy()
    result['churn_probability'] = predictions
    result['churn_risk_level'] = pd.cut(
        predictions,
        bins=[0, 0.3, 0.7, 1.0],
        labels=['low', 'medium', 'high']
    )

    context.add_output_metadata({
        "num_predictions": len(result),
        "high_risk_customers": (result['churn_risk_level'] == 'high').sum(),
        "avg_churn_probability": predictions.mean()
    })

    return result
```

#### MLOps Pattern with Model Registry

```python
from dagster import asset, Config

class ModelConfig(Config):
    """Configuration for model training"""
    n_estimators: int = 100
    max_depth: int = 10
    min_samples_split: int = 2

@asset
def trained_model_with_registry(
    context,
    train_test_data: dict,
    config: ModelConfig
):
    """Train model and register to MLflow"""
    import mlflow

    with mlflow.start_run():
        # Log parameters
        mlflow.log_params({
            "n_estimators": config.n_estimators,
            "max_depth": config.max_depth,
            "min_samples_split": config.min_samples_split
        })

        # Train model
        model = RandomForestClassifier(
            n_estimators=config.n_estimators,
            max_depth=config.max_depth,
            min_samples_split=config.min_samples_split
        )
        model.fit(train_test_data["X_train"], train_test_data["y_train"])

        # Evaluate
        train_score = model.score(
            train_test_data["X_train"],
            train_test_data["y_train"]
        )
        test_score = model.score(
            train_test_data["X_test"],
            train_test_data["y_test"]
        )

        # Log metrics
        mlflow.log_metrics({
            "train_accuracy": train_score,
            "test_accuracy": test_score
        })

        # Register model
        mlflow.sklearn.log_model(model, "churn_model")

    return model
```

---

### dbt Integration

#### Basic dbt Integration

```python
from dagster import AssetExecutionContext
from dagster_dbt import DbtProject, dbt_assets

# Define dbt project
dbt_project = DbtProject(
    project_dir="/path/to/dbt/project",
    target="prod"
)

# Load dbt models as Dagster assets
@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project
)
def my_dbt_assets(context: AssetExecutionContext):
    """All dbt models as Dagster assets"""
    yield from dbt_project.cli(["build"], context=context).stream()
```

#### dbt with Upstream Dagster Assets

```python
from dagster import asset, AssetExecutionContext
from dagster_dbt import dbt_assets, DbtProject

# Dagster asset that dbt depends on
@asset
def raw_customers_csv(context: AssetExecutionContext, s3: S3Resource):
    """Extract raw data to S3"""
    data = extract_from_api()
    s3.write("raw/customers.csv", data)
    return data

# dbt assets
dbt_project = DbtProject(project_dir="dbt_project")

@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project
)
def dbt_models(context: AssetExecutionContext):
    """dbt models that depend on raw_customers_csv"""
    # raw_customers_csv runs first, then dbt models
    yield from dbt_project.cli(["build"], context=context).stream()
```

#### Dagster Assets Depending on dbt Models

```python
# Don't need to re-declare dbt assets, just reference them
@asset(deps=["dbt_model_name"])
def ml_features_from_dbt(context, snowflake: SnowflakeResource):
    """Asset that depends on dbt model"""
    # dbt model runs first, then this asset
    df = snowflake.read_table("analytics.dbt_model_name")
    return engineer_features(df)
```

#### dbt Incremental Models with Partitions

```python
from dagster import DailyPartitionsDefinition, AssetExecutionContext
from dagster_dbt import dbt_assets, DbtProject

daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

dbt_project = DbtProject(
    project_dir="dbt_project",
    target="prod"
)

@dbt_assets(
    manifest=dbt_project.manifest_path,
    project=dbt_project,
    partitions_def=daily_partitions
)
def partitioned_dbt_assets(context: AssetExecutionContext):
    """dbt models with daily partitions"""

    # Get partition date
    partition_date = context.partition_key

    # Pass to dbt as variable
    yield from dbt_project.cli(
        [
            "build",
            "--vars",
            f'{{"partition_date": "{partition_date}"}}'
        ],
        context=context
    ).stream()

# In dbt model (models/incremental_sales.sql):
# {{ config(materialized='incremental') }}
#
# SELECT * FROM {{ source('raw', 'sales') }}
# WHERE date = '{{ var("partition_date") }}'
# {% if is_incremental() %}
#   AND date > (SELECT MAX(date) FROM {{ this }})
# {% endif %}
```

#### dbt Defer Pattern (Dev vs Prod)

```python
from dagster_dbt import DbtProject
import os

env = os.getenv("DAGSTER_DEPLOYMENT", "dev")

if env == "dev":
    # In dev, use defer to production state
    dbt_project = DbtProject(
        project_dir="dbt_project",
        target="dev",
        state_path="/path/to/prod/manifest"  # Reference prod state
    )
else:
    # In prod, no defer
    dbt_project = DbtProject(
        project_dir="dbt_project",
        target="prod"
    )
```

#### Best Practices for dbt Integration

- ✅ Use DbtProject component for easy integration
- ✅ Reference dbt models by asset key, don't re-declare them
- ✅ Use partitions for incremental models
- ✅ Leverage dbt defer for development workflows
- ✅ Keep dbt project outside Dagster project directory
- ✅ Use separate automation for ingestion vs transformation
- ⚠️ Don't run dbt models more frequently than data updates

---

### Data Quality Checks

#### Asset Checks (Native Dagster)

```python
from dagster import asset, asset_check, AssetCheckResult, AssetCheckSeverity

@asset
def customer_data(context):
    """Customer data asset"""
    return load_customer_data()

# Define checks for the asset
@asset_check(asset=customer_data)
def check_no_nulls_in_email(context):
    """Check that email column has no nulls"""
    df = load_customer_data()
    null_count = df['email'].isnull().sum()

    return AssetCheckResult(
        passed=null_count == 0,
        metadata={
            "null_count": null_count,
            "total_rows": len(df)
        },
        severity=AssetCheckSeverity.ERROR if null_count > 0 else None
    )

@asset_check(asset=customer_data)
def check_email_format(context):
    """Check email format validity"""
    df = load_customer_data()
    invalid = ~df['email'].str.contains('@')
    invalid_count = invalid.sum()

    return AssetCheckResult(
        passed=invalid_count == 0,
        metadata={
            "invalid_count": invalid_count,
            "invalid_emails": df[invalid]['email'].tolist()[:10]  # Sample
        }
    )

@asset_check(asset=customer_data)
def check_reasonable_age_range(context):
    """Check age is in reasonable range"""
    df = load_customer_data()
    out_of_range = (df['age'] < 18) | (df['age'] > 120)
    invalid_count = out_of_range.sum()

    return AssetCheckResult(
        passed=invalid_count == 0,
        metadata={
            "invalid_count": invalid_count,
            "min_age": df['age'].min(),
            "max_age": df['age'].max()
        },
        severity=AssetCheckSeverity.WARN  # Warning, not error
    )
```

#### Multi-Asset Checks

```python
from dagster import multi_asset_check, AssetCheckKey

@multi_asset_check(
    asset_keys=["customer_data", "order_data"],
    name="referential_integrity"
)
def check_referential_integrity(context):
    """Check that all orders reference valid customers"""
    customers = load_customer_data()
    orders = load_order_data()

    # Find orders with invalid customer_id
    invalid_orders = orders[~orders['customer_id'].isin(customers['customer_id'])]

    return [
        AssetCheckResult(
            passed=len(invalid_orders) == 0,
            asset_key="order_data",
            metadata={
                "invalid_orders": len(invalid_orders),
                "sample_invalid_ids": invalid_orders['customer_id'].unique()[:5].tolist()
            }
        )
    ]
```

#### Great Expectations Integration

```python
from dagster import asset
import great_expectations as ge

@asset
def validated_customer_data(context):
    """Customer data with Great Expectations validation"""

    df = load_customer_data()

    # Convert to GE dataset
    ge_df = ge.from_pandas(df)

    # Define expectations
    ge_df.expect_column_values_to_not_be_null("email")
    ge_df.expect_column_values_to_match_regex("email", r"^[^@]+@[^@]+\.[^@]+$")
    ge_df.expect_column_values_to_be_between("age", min_value=18, max_value=120)
    ge_df.expect_column_values_to_be_in_set("status", ["active", "inactive", "suspended"])

    # Validate
    validation_result = ge_df.validate()

    # Log results
    context.add_output_metadata({
        "validation_success": validation_result.success,
        "expectations_evaluated": validation_result.statistics["evaluated_expectations"],
        "successful_expectations": validation_result.statistics["successful_expectations"],
        "validation_report": MetadataValue.md(
            validation_result.to_json_dict()
        )
    })

    if not validation_result.success:
        # Optionally fail the asset or just warn
        context.log.warning("Data quality checks failed!")

    return df
```

#### Data Quality Dimensions

```python
from dagster import asset_check, AssetCheckResult

# 1. Completeness
@asset_check(asset=customer_data)
def check_completeness(context):
    """Check all required records are present"""
    df = load_customer_data()
    expected_count = get_expected_record_count()
    actual_count = len(df)

    return AssetCheckResult(
        passed=actual_count >= expected_count * 0.95,  # 95% threshold
        metadata={
            "expected": expected_count,
            "actual": actual_count,
            "completeness_pct": (actual_count / expected_count) * 100
        }
    )

# 2. Uniqueness
@asset_check(asset=customer_data)
def check_uniqueness(context):
    """Check for duplicate records"""
    df = load_customer_data()
    duplicates = df.duplicated(subset=['customer_id']).sum()

    return AssetCheckResult(
        passed=duplicates == 0,
        metadata={"duplicate_count": duplicates}
    )

# 3. Timeliness
@asset_check(asset=customer_data)
def check_timeliness(context):
    """Check data freshness"""
    df = load_customer_data()
    latest_timestamp = pd.to_datetime(df['updated_at']).max()
    age_hours = (pd.Timestamp.now() - latest_timestamp).total_seconds() / 3600

    return AssetCheckResult(
        passed=age_hours < 24,  # Data should be less than 24 hours old
        metadata={
            "latest_timestamp": str(latest_timestamp),
            "age_hours": age_hours
        }
    )

# 4. Consistency
@asset_check(asset=customer_data)
def check_consistency(context):
    """Check cross-field consistency"""
    df = load_customer_data()

    # Example: premium customers should have valid payment method
    premium_without_payment = df[
        (df['subscription_type'] == 'premium') &
        (df['payment_method'].isnull())
    ]

    return AssetCheckResult(
        passed=len(premium_without_payment) == 0,
        metadata={
            "inconsistent_records": len(premium_without_payment)
        }
    )
```

---

### Incremental Processing and Partitioning

#### Time-Based Partitions

```python
from dagster import asset, DailyPartitionsDefinition, AssetExecutionContext

daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily_partitions)
def daily_sales(context: AssetExecutionContext):
    """Process one day of sales data at a time"""

    # Get the partition date
    partition_date = context.partition_key

    context.log.info(f"Processing sales for {partition_date}")

    # Query only that day's data
    df = fetch_sales_for_date(partition_date)

    context.add_output_metadata({
        "partition_date": partition_date,
        "num_sales": len(df),
        "total_revenue": df['amount'].sum()
    })

    return df
```

#### Static Partitions

```python
from dagster import asset, StaticPartitionsDefinition

regions = StaticPartitionsDefinition(["north", "south", "east", "west"])

@asset(partitions_def=regions)
def regional_sales(context: AssetExecutionContext):
    """Process sales by region"""

    region = context.partition_key

    df = fetch_sales_for_region(region)

    return df
```

#### Dynamic Partitions

```python
from dagster import asset, DynamicPartitionsDefinition, sensor, RunRequest

# Define dynamic partitions
customer_partitions = DynamicPartitionsDefinition(name="customers")

@asset(partitions_def=customer_partitions)
def customer_report(context: AssetExecutionContext):
    """Generate report for each customer"""
    customer_id = context.partition_key
    return generate_report(customer_id)

# Sensor to add new partitions dynamically
@sensor(asset_selection=[customer_report])
def new_customer_sensor(context):
    """Detect new customers and create partitions"""

    new_customers = detect_new_customers()

    if new_customers:
        # Add new partitions
        customer_partitions.add_partitions(new_customers)

        # Request runs for new partitions
        for customer_id in new_customers:
            yield RunRequest(
                partition_key=customer_id,
                tags={"customer_id": customer_id}
            )
```

#### Two-Dimensional Partitioning

```python
from dagster import asset, MultiPartitionsDefinition, DailyPartitionsDefinition, StaticPartitionsDefinition

# Partition by both date and region
multi_partitions = MultiPartitionsDefinition({
    "date": DailyPartitionsDefinition(start_date="2024-01-01"),
    "region": StaticPartitionsDefinition(["north", "south", "east", "west"])
})

@asset(partitions_def=multi_partitions)
def regional_daily_sales(context: AssetExecutionContext):
    """Process sales by region and date"""

    # Access both partition dimensions
    partition_keys = context.partition_key.keys_by_dimension
    date = partition_keys["date"]
    region = partition_keys["region"]

    context.log.info(f"Processing {region} sales for {date}")

    df = fetch_sales(date=date, region=region)

    return df
```

#### Partition Mappings for Dependencies

```python
from dagster import asset, TimeWindowPartitionMapping, DailyPartitionsDefinition, WeeklyPartitionsDefinition

daily = DailyPartitionsDefinition(start_date="2024-01-01")
weekly = WeeklyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily)
def daily_metrics(context):
    """Daily metrics"""
    date = context.partition_key
    return compute_daily_metrics(date)

@asset(
    partitions_def=weekly,
    ins={
        "daily_metrics": AssetIn(
            partition_mapping=TimeWindowPartitionMapping()
        )
    }
)
def weekly_rollup(context, daily_metrics):
    """Aggregate daily metrics to weekly"""
    # Receives all daily partitions for the week
    week = context.partition_key
    return aggregate_to_weekly(daily_metrics)
```

#### Incremental File Processing

```python
from dagster import asset, sensor, RunRequest, DynamicPartitionsDefinition

file_partitions = DynamicPartitionsDefinition(name="files")

@asset(partitions_def=file_partitions)
def processed_file(context: AssetExecutionContext, s3: S3Resource):
    """Process a single file"""
    file_key = context.partition_key

    # Download and process file
    data = s3.read(file_key)
    processed = process_data(data)

    # Write output
    s3.write(f"processed/{file_key}", processed)

    return processed

@sensor(asset_selection=[processed_file])
def new_file_sensor(context, s3: S3Resource):
    """Detect new files in S3 and create partitions"""

    # List files in bucket
    all_files = s3.list_objects("raw/")

    # Get already processed files
    existing_partitions = context.instance.get_dynamic_partitions(
        file_partitions.name
    )

    # Find new files
    new_files = [f for f in all_files if f not in existing_partitions]

    if new_files:
        # Add partitions for new files
        file_partitions.add_partitions(new_files)

        # Request runs for each new file
        for file_key in new_files:
            yield RunRequest(
                partition_key=file_key,
                tags={"file": file_key}
            )
```

#### Backfilling Partitions

```python
# Via CLI
# dagster asset materialize --select daily_sales --partition 2024-01-01:2024-12-31

# Programmatic backfill
from dagster import build_asset_context

def backfill_partitions(start_date, end_date):
    """Backfill partitions for a date range"""
    dates = pd.date_range(start_date, end_date)

    for date in dates:
        context = build_asset_context(partition_key=date.strftime("%Y-%m-%d"))
        result = daily_sales(context)
        print(f"Processed {date}: {len(result)} records")
```

#### Best Practices

- ✅ Use partitions for incremental processing of large datasets
- ✅ Limit partition count to <100,000 per asset
- ✅ Use TimeWindowPartitionMapping for aggregations across time windows
- ✅ Use dynamic partitions for data with unknown keys (e.g., new files, customers)
- ✅ Use sensors to detect new data and trigger partition runs
- ✅ Use backfills to reprocess historical data
- ⚠️ Be cautious with fine-grained partitions (hourly/minutely) - they multiply quickly
- ⚠️ Monitor partition count growth over time

---

### Cross-Team Collaboration

#### Multi-Project Workspace

```
workspace_root/
├── team_a_project/
│   ├── pyproject.toml
│   └── team_a/
│       ├── definitions.py
│       └── assets/
│           └── raw_data.py
├── team_b_project/
│   ├── pyproject.toml
│   └── team_b/
│       ├── definitions.py
│       └── assets/
│           └── analytics.py
└── workspace.yaml
```

**workspace.yaml:**
```yaml
load_from:
  - python_package:
      package_name: team_a
      location_name: team_a_location

  - python_package:
      package_name: team_b
      location_name: team_b_location
```

#### Code Locations for Team Separation

```python
# Team A's definitions.py
from dagster import Definitions, asset

@asset(group_name="team_a")
def customer_raw_data(context):
    """Managed by Team A"""
    return extract_customers()

team_a_defs = Definitions(
    assets=[customer_raw_data],
    resources={...}
)

# Team B's definitions.py
from dagster import Definitions, asset, AssetKey

@asset(
    group_name="team_b",
    deps=[AssetKey("customer_raw_data")]  # Reference Team A's asset
)
def customer_analytics(context):
    """Managed by Team B, depends on Team A"""
    # Load Team A's output
    customers = load_from_warehouse("team_a.customer_raw_data")
    return compute_analytics(customers)

team_b_defs = Definitions(
    assets=[customer_analytics],
    resources={...}
)
```

#### Asset Sensors for Cross-Team Coordination

```python
from dagster import asset_sensor, AssetKey, RunRequest

@asset_sensor(
    asset_key=AssetKey("customer_raw_data"),  # Team A's asset
    job=customer_analytics_job  # Team B's job
)
def customer_data_updated_sensor(context, asset_event):
    """Trigger Team B's job when Team A's data updates"""

    yield RunRequest(
        run_key=f"analytics_{asset_event.partition_key}",
        tags={
            "upstream_run_id": asset_event.dagster_run_id,
            "trigger": "customer_data_updated"
        }
    )
```

#### Shared Resources Pattern

```python
# shared_resources.py
from dagster import ConfigurableResource, EnvVar

class SharedWarehouse(ConfigurableResource):
    """Shared Snowflake resource for all teams"""
    account: str
    database: str
    warehouse: str

    def read_table(self, schema: str, table: str):
        """Read from team's schema"""
        return pd.read_sql(
            f"SELECT * FROM {self.database}.{schema}.{table}",
            self.get_connection()
        )

# Team A uses it
team_a_defs = Definitions(
    assets=[...],
    resources={
        "warehouse": SharedWarehouse(
            account=EnvVar("SNOWFLAKE_ACCOUNT"),
            database="SHARED_DB",
            warehouse="TEAM_A_WH"
        )
    }
)

# Team B uses it
team_b_defs = Definitions(
    assets=[...],
    resources={
        "warehouse": SharedWarehouse(
            account=EnvVar("SNOWFLAKE_ACCOUNT"),
            database="SHARED_DB",
            warehouse="TEAM_B_WH"
        )
    }
)
```

#### Dagster+ Agent Routing (Isolation)

```yaml
# dagster_cloud.yaml
locations:
  - location_name: team_a
    code_source:
      package_name: team_a
    agent:
      agent_label: team-a-agent  # Dedicated agent

  - location_name: team_b
    code_source:
      package_name: team_b
    agent:
      agent_label: team-b-agent  # Separate agent
```

Benefits:
- Separate execution environments
- Independent resource allocation
- Isolated failures
- Different deployment cycles

#### Documentation and Ownership

```python
from dagster import asset

@asset(
    group_name="customer_data",
    metadata={
        "owner": "team-a@company.com",
        "documentation": "https://wiki.company.com/customer-data",
        "sla_hours": 24,
        "update_frequency": "daily"
    }
)
def customer_raw_data(context):
    """
    Raw customer data from Salesforce

    Owner: Team A (Data Platform)
    Update Schedule: Daily at 2 AM UTC
    Dependencies: None
    Consumers: Team B (Analytics), Team C (ML)

    Schema:
    - customer_id: Unique identifier
    - email: Customer email
    - created_at: Account creation timestamp
    """
    return extract_customers()
```

#### Shared Data Contracts

```python
# contracts/customer_schema.py
from pydantic import BaseModel
from datetime import datetime

class CustomerSchema(BaseModel):
    """Shared schema contract for customer data"""
    customer_id: str
    email: str
    created_at: datetime
    status: str

# Team A (producer)
@asset
def customer_raw_data(context) -> list[CustomerSchema]:
    """Conforms to CustomerSchema contract"""
    data = extract_customers()
    # Validate against schema
    validated = [CustomerSchema(**row) for row in data]
    return validated

# Team B (consumer)
@asset
def customer_analytics(context, customer_raw_data: list[CustomerSchema]):
    """Expects CustomerSchema contract"""
    # Guaranteed to have correct schema
    df = pd.DataFrame([c.dict() for c in customer_raw_data])
    return compute_analytics(df)
```

#### Best Practices

- ✅ Use separate code locations for teams with different dependencies or release cycles
- ✅ Use asset sensors for cross-team coordination
- ✅ Document asset ownership, SLAs, and consumers
- ✅ Use shared resource definitions for common infrastructure
- ✅ Establish data contracts/schemas for shared assets
- ✅ Use agent routing for execution isolation in Dagster+
- ✅ Organize assets by group_name to visualize team boundaries
- ⚠️ Balance centralization (shared standards) vs autonomy (team independence)
- ⚠️ Monitor cross-team dependencies to avoid tight coupling

---

## Production Case Studies

### 1. US Foods (Fortune 500)

**Scale:** $24B annual operations

**Achievements:**
- 99.996% uptime
- Eliminated data silos
- Built self-service data platform

**Architecture:**
- Dagster orchestrating end-to-end data pipelines
- Multi-source integration
- Self-service capabilities for business users

### 2. easyJet Holidays (Travel)

**Problem:** Fragmented AWS stack, slow pipelines

**Results:**
- **15x faster pipeline execution** (2.5 hours → 10 minutes)
- Eliminated manual troubleshooting overhead
- Unified data orchestration platform

**Migration:** From fragmented AWS services to Dagster

### 3. Ida (AI for Food Waste - Multi-Tenant SaaS)

**Use Case:** Processing millions of rows daily for multiple clients

**Architecture:**
- Medallion architecture (Bronze → Silver → Gold)
- Multi-tenant data processing with chaotic source data
- dbt used as "modeling clay" for production middleware
- BigQuery for ELT transformations

**Pattern:** Load raw chaotic data first, then transform in warehouse

### 4. Belgian Government (Fédération Wallonie-Bruxelles)

**Team:** Data engineer Martin Erpicum

**Results:**
- **2x faster pipeline delivery**
- Shift from reactive maintenance to proactive data product development
- Improved data quality detection and resolution
- Data teams now propose new products instead of just reacting to requests

**Platform Transformation:** From operational overhead to strategic data platform

### 5. Mejuri (E-commerce Jewelry)

**Production Experience:** 2+ years

**Scale:**
- 47 pipelines
- 2 Dagster production instances

**Use Cases:**
- E-commerce analytics
- Inventory management
- Customer behavior tracking

### 6. KIPP (Education)

**Challenge:** Fragmented data stack

**Solution:** Dagster as unified platform

**Results:**
- Improved observability and lineage
- Faster development (weeks → days for new integrations)
- Better data quality

### 7. Zippi (YC 2019 - Fintech)

**Use Case:** ML model operationalization for loan underwriting

**Pattern:** Incremental Dagster adoption
1. Started with ML model scoring pipeline
2. Created data assets in S3 for credit team
3. Expanded to other workflows

**Lesson:** Start small, expand gradually

---

## Anti-Patterns to Avoid

### 1. Loading Heavy Libraries at Module Level

**Problem:** Everything imported at module level loads into memory when code location starts

**❌ Anti-Pattern:**
```python
# asset_definitions.py
import postal  # Adds 2GB to memory!
from transformers import AutoModel  # Adds 1GB+!

@asset
def parse_addresses(context):
    # postal library already loaded
    return postal.parse_address(...)
```

**✅ Solution:**
```python
# asset_definitions.py

@asset
def parse_addresses(context):
    # Import only when asset runs
    import postal
    return postal.parse_address(...)

# OR use resource pattern
class PostalResource(ConfigurableResource):
    def __init__(self):
        import postal
        self._postal = postal

    def parse(self, address):
        return self._postal.parse_address(address)
```

**Impact:** At scale (50+ code locations), module-level imports can consume 5-10GB of memory before any work is done.

### 2. Too Many Code Locations

**Problem:** Each code location pod consumes baseline resources (CPU, memory, gRPC server)

**❌ Anti-Pattern:**
- One code location per team member
- One code location per small project
- 50+ code locations for a medium-sized team

**Resource Math:**
- 1 code location: 100MB baseline
- 50 code locations: 5GB before loading any code
- Plus memory for imports, definitions, etc.

**✅ Solution:**
- Group related assets in same code location
- Use asset groups for organization, not separate code locations
- Limit code locations to teams with truly conflicting dependencies

### 3. Overly Complex Partition Schemes

**❌ Anti-Pattern:**
```python
# Creates 175,200 partitions!
hourly_by_customer = MultiPartitionsDefinition({
    "hour": HourlyPartitionsDefinition(start_date="2022-01-01"),
    "customer": StaticPartitionsDefinition([...1000 customers...])
})
```

**Problems:**
- UI becomes slow
- Backfills take forever
- Dagster database bloat

**✅ Solution:**
```python
# Reasonable partition count
daily_partitions = DailyPartitionsDefinition(
    start_date="2024-01-01",
    end_offset=0  # Don't partition future
)
# ~365 partitions per year
```

**Rule of Thumb:** Keep partitions < 100,000 per asset

### 4. Not Using Resources for External Systems

**❌ Anti-Pattern:**
```python
@asset
def my_asset(context):
    # Hardcoded connection details
    conn = psycopg2.connect(
        host="prod-db.example.com",
        user="dagster",
        password="hardcoded_password"  # Security risk!
    )
    # Can't mock in tests
    # Can't swap dev/prod easily
```

**✅ Solution:**
```python
class DatabaseResource(ConfigurableResource):
    host: str
    user: str
    password: str

@asset
def my_asset(context, database: DatabaseResource):
    conn = database.get_connection()
    # Easy to mock
    # Environment-specific configuration
    # Secrets via EnvVar
```

### 5. Ignoring Asset Checks

**❌ Anti-Pattern:**
```python
@asset
def customer_data(context):
    df = load_data()
    # No validation!
    return df

# Bad data propagates downstream
```

**✅ Solution:**
```python
@asset
def customer_data(context):
    df = load_data()
    return df

@asset_check(asset=customer_data)
def validate_customer_data(context):
    df = load_data()
    null_count = df['email'].isnull().sum()
    return AssetCheckResult(
        passed=null_count == 0,
        metadata={"null_count": null_count}
    )
```

### 6. Overly Broad Asset Dependencies

**❌ Anti-Pattern:**
```python
@asset
def huge_monolithic_asset(context):
    # Loads ALL data
    # Does ALL transformations
    # 10,000 lines of code
    # Takes 6 hours to run
    # Fails at hour 5, must restart from beginning
    pass
```

**✅ Solution:**
```python
# Break into smaller, focused assets
@asset
def raw_data(context):
    return extract()  # 10 minutes

@asset
def cleaned_data(context, raw_data):
    return clean(raw_data)  # 5 minutes

@asset
def analytics(context, cleaned_data):
    return analyze(cleaned_data)  # 15 minutes

# Benefits:
# - Failures are isolated
# - Can retry individual steps
# - Parallel execution possible
# - Easier to understand and maintain
```

### 7. Using ops Instead of assets for Data Pipelines

**❌ Anti-Pattern (for data pipelines):**
```python
@op
def extract_customers():
    return fetch_customers()

@op
def transform_customers(customers):
    return transform(customers)

@job
def customer_pipeline():
    transform_customers(extract_customers())

# No asset lineage
# No observability of data products
# Can't reuse across jobs easily
```

**✅ Solution:**
```python
@asset
def customers(context):
    return fetch_customers()

@asset
def transformed_customers(context, customers):
    return transform(customers)

# Automatic lineage
# Asset-centric UI
# Reusable across definitions
```

### 8. Not Using Retry Policies for Transient Failures

**❌ Anti-Pattern:**
```python
@asset
def flaky_api_call(context):
    # Fails on transient network errors
    # No retry
    return call_external_api()
```

**✅ Solution:**
```python
@asset(
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=2,
        backoff=Backoff.EXPONENTIAL
    )
)
def resilient_api_call(context):
    return call_external_api()
```

### 9. Forgetting to Set Partition End Offsets

**❌ Anti-Pattern:**
```python
# Partitions future dates unnecessarily
daily = DailyPartitionsDefinition(
    start_date="2024-01-01"
    # Missing end_offset
)
# Creates partitions through 2030!
```

**✅ Solution:**
```python
daily = DailyPartitionsDefinition(
    start_date="2024-01-01",
    end_offset=0  # Only partition through today
)
```

### 10. Poor Naming Conventions

**❌ Anti-Pattern:**
```python
@asset
def job1(context):  # Meaningless
    pass

@asset
def process_data(context):  # Too vague
    pass

@asset
def myAsset(context):  # Wrong convention
    pass
```

**✅ Solution:**
```python
@asset
def daily_customer_sales_summary(context):  # Clear, descriptive
    pass

@asset
def stripe_payment_records(context):  # Indicates source
    pass

@asset
def gold_customer_360_view(context):  # Indicates layer
    pass
```

---

## Key Takeaways

### Top Design Patterns to Adopt

1. **Use Assets for Data Pipelines** - Assets are the modern Dagster paradigm
2. **Factory Patterns for Repetitive Logic** - Keep code DRY
3. **ConfigurableResource for External Systems** - Type-safe dependency injection
4. **Asset Checks for Data Quality** - Validate early and often
5. **Partitioning for Incremental Processing** - Process only what's needed
6. **Multi-Environment Configuration** - Dev/staging/prod separation

### Top Best Practices

1. **Start Simple, Evolve** - Begin with one file, refactor as you grow
2. **Test Assets Like Python Functions** - Use materialize() with mocks
3. **Use EnvVar for Secrets** - Runtime evaluation, not visible in UI
4. **Add Rich Metadata** - Help future you understand what happened
5. **Implement CI/CD with Branch Deployments** - Preview changes safely
6. **Monitor Resource Usage** - Especially code location memory

### Top Anti-Patterns to Avoid

1. **Module-Level Heavy Imports** - Load on demand, not at import time
2. **Too Many Code Locations** - Consolidate when possible
3. **Excessive Partitions** - Keep under 100K per asset
4. **Monolithic Assets** - Break into focused, reusable pieces
5. **Hardcoded Configuration** - Use resources and environment variables
6. **No Data Quality Checks** - Validate data, don't propagate bad data

### Additional Resources

- **Official Docs:** https://docs.dagster.io
- **Dagster University:** https://courses.dagster.io (Free courses)
- **Community:** https://discuss.dagster.io
- **GitHub:** https://github.com/dagster-io/dagster
- **Blog:** https://dagster.io/blog

---

**Document Version:** 1.0
**Research Date:** November 18, 2025
**Sources:** Official Dagster documentation, community discussions, production case studies


## Comprehensive Research (2024-2025)


> Source: `docs/data_engineering/dagster/dagster-research-2024-2025.md`

# Dagster Research: Core Features and Architecture (2024-2025)

## Executive Summary

Dagster is a modern data orchestration platform that shifts focus from task-based orchestration to asset-based orchestration. Unlike traditional workflow orchestrators that track whether tasks ran, Dagster tracks metadata about data assets themselves, providing enhanced lineage, observability, and data quality monitoring.

**Key Differentiator**: Dagster's asset-centric approach means the focus is on "assets to be materialized" rather than "tasks to be executed."

---

## 1. Core Concepts

### 1.1 Software-Defined Assets (SDAs)

**Definition**: A software-defined asset is a description (in code) of what data assets should exist and how those assets should be computed.

**Key Characteristics**:
- Asset definitions know about their dependencies (unlike ops)
- Provide enhanced observability into data assets
- Enable clear data lineage tracking
- Support advanced scheduling capabilities
- Behind the scenes, the Python function in an asset is an op

**Basic Code Example**:
```python
import dagster as dg

@dg.asset
def daily_sales() -> None:
    """Simple asset with no dependencies"""
    execute_query("SELECT * FROM sales WHERE date = CURRENT_DATE")

@dg.asset
def weekly_sales(daily_sales) -> None:
    """Asset that depends on daily_sales (inferred from function argument)"""
    execute_query("SELECT * FROM daily_sales GROUP BY week")
```

**Alternative Dependency Syntax Using `deps` Parameter**:
```python
@dg.asset
def sugary_cereals() -> None:
    execute_query(
        "CREATE TABLE sugary_cereals AS SELECT * FROM cereals WHERE sugar_grams > 10"
    )

@dg.asset(deps=[sugary_cereals])
def shopping_list() -> None:
    """Using deps parameter when you don't need the upstream data directly"""
    execute_query("CREATE TABLE shopping_list AS SELECT * FROM sugary_cereals")
```

**Advanced: Graph Assets**:
For complex cases, you can use the `@dg.graph_asset` decorator to combine multiple ops into a single asset.

**Asset Metadata**:
```python
@dg.asset(
    deps=[weekly_sales],
    owners=["bighead@hooli.com", "team:roof", "team:corpdev"],
    group_name="sales"
)
def weekly_sales_report(context: dg.AssetExecutionContext):
    context.log.info("Loading data for weekly_sales_report")
    # Asset computation logic
```

### 1.2 Ops (Operations)

**Definition**: Ops are the core unit of computation in Dagster and contain the logic of your orchestration graph.

**Key Characteristics**:
- Ops don't know about dependencies until placed inside a graph
- More low-level than assets
- Can be composed into graphs
- Support configuration through the `config` parameter

**Code Example**:
```python
from dagster import op, Config

class MyOpConfig(Config):
    param1: str
    param2: int

@op
def my_op(context, config: MyOpConfig):
    context.log.info(f"Running with param1={config.param1}, param2={config.param2}")
    return config.param1 * config.param2
```

### 1.3 Jobs

**Definition**: Jobs are the main unit of execution and monitoring in Dagster. They allow you to execute a portion of a graph of asset definitions or ops based on a schedule or external trigger.

**Key Points**:
- Jobs define what gets executed
- Can be triggered by schedules, sensors, or manually
- Support run configuration
- Can target specific assets or ops

**Code Example**:
```python
from dagster import define_asset_job, AssetSelection

# Job that materializes all assets in the "sales" group
sales_job = define_asset_job(
    name="sales_job",
    selection=AssetSelection.groups("sales")
)
```

### 1.4 Graphs

**Definition**: Dagster op graphs are sets of interconnected ops or sub-graphs and form the core of jobs.

**Key Points**:
- Compose multiple ops together
- Define data flow between ops
- Can be nested (graphs within graphs)
- Reusable computation patterns

### 1.5 Resources

**Definition**: Resources represent external services, databases, APIs, or other dependencies that ops and assets need to interact with.

**Key Characteristics**:
- Configurable dependencies
- Shared across multiple assets/ops
- Support different implementations for dev/prod
- Can be mocked for testing

**Modern Pattern (2024)**:
```python
from dagster import ConfigurableResource
from typing import Optional

class DatabaseResource(ConfigurableResource):
    connection_string: str
    timeout: Optional[int] = 30

    def query(self, sql: str):
        # Database query logic
        pass

@dg.asset
def my_asset(database: DatabaseResource):
    return database.query("SELECT * FROM table")

# In Definitions
defs = Definitions(
    assets=[my_asset],
    resources={
        "database": DatabaseResource(
            connection_string="postgresql://localhost/mydb"
        )
    }
)
```

### 1.6 IO Managers

**Definition**: An IOManager defines how data is stored and retrieved between the execution of assets and ops.

**Key Features**:
- Customizable storage and format at any interaction point
- Handle partitioned assets automatically
- Support different storage backends (S3, local filesystem, databases)
- Separate computation logic from storage logic

**Use Case**: Allows you to change where/how data is stored without modifying asset logic.

### 1.7 Schedules

**Definition**: A ScheduleDefinition automates jobs or assets to occur on a specified interval.

**Key Features**:
- Cron-based scheduling
- Integration with partitioned jobs
- Support for run configuration
- Can be parameterized

**Code Example**:
```python
from dagster import ScheduleDefinition, RunConfig

# Simple schedule
daily_schedule = ScheduleDefinition(
    name="daily_sales_schedule",
    cron_schedule="0 0 * * *",  # Midnight daily
    target=sales_job
)

# Schedule from partitioned job
from dagster import build_schedule_from_partitioned_job, DailyPartitionsDefinition

daily_partition = DailyPartitionsDefinition(start_date="2024-01-01")

partitioned_schedule = build_schedule_from_partitioned_job(
    job=my_partitioned_job,
    description="Daily schedule that matches partition spacing"
)
```

**Important Note (2024)**: Each schedule tick of a partitioned job targets the latest partition in the partition set that exists as of the tick time.

### 1.8 Sensors

**Definition**: A sensor triggers jobs or assets when an event occurs, such as a file being uploaded or a push notification.

**Key Characteristics**:
- Event-driven execution
- Poll for changes at regular intervals
- Can trigger multiple runs
- Support for cursors to track state

**Use Cases**:
- File arrival sensors
- API polling sensors
- Database change sensors
- Cross-job dependencies

**Code Example**:
```python
from dagster import sensor, RunRequest, SensorEvaluationContext

@sensor(job=my_job)
def file_sensor(context: SensorEvaluationContext):
    new_files = check_for_new_files()

    for file in new_files:
        yield RunRequest(
            run_key=file.name,
            run_config={"file_path": file.path}
        )
```

### 1.9 Partitions

**Definition**: Partitioning is a technique for managing large datasets, improving pipeline performance, and enabling incremental processing.

**Partition Types**:

1. **Time-Based Partitioning**: Daily, weekly, monthly partitions
2. **Static Partitioning**: Predefined categories (regions, products)
3. **Multi-Dimensional Partitioning**: Two different axes (date × region)
4. **Dynamic Partitioning**: Runtime-determined partitions

**Code Example**:
```python
from dagster import asset, DailyPartitionsDefinition, MultiPartitionsDefinition, StaticPartitionsDefinition

# Daily partitions
daily_partition = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily_partition)
def daily_sales_data(context):
    partition_key = context.partition_key
    # Process data for specific date
    return process_sales_for_date(partition_key)

# Multi-dimensional partitions
multi_partition = MultiPartitionsDefinition({
    "date": DailyPartitionsDefinition(start_date="2024-01-01"),
    "region": StaticPartitionsDefinition(["us", "eu", "asia"])
})

@asset(partitions_def=multi_partition)
def regional_daily_sales(context):
    partition_key = context.partition_key
    # partition_key.keys_by_dimension returns dict like {"date": "2024-01-01", "region": "us"}
    pass
```

**Dynamic Partitions (2024 Feature)**:
```python
from dagster import DynamicPartitionsDefinition

dynamic_partition = DynamicPartitionsDefinition(name="customers")

# Add partitions at runtime
context.instance.add_dynamic_partitions(
    partitions_def_name="customers",
    partition_keys=["customer_123", "customer_456"]
)
```

**Best Practice (2024)**: Limit partitions to 100,000 or fewer per asset for optimal performance.

**New Feature (2024)**: Time-based partition exclusions allow excluding specific dates/times or recurring schedules from partition sets - useful for weekends, holidays, or maintenance windows.

### 1.10 Asset Materialization

**Definition**: Asset materialization is the process of computing and storing an asset's value. It represents the execution that produces data for an asset.

**Key Characteristics**:
- Tracked in Dagster's event log
- Associated with metadata (row counts, schema, etc.)
- Enables lineage tracking
- Supports observability

**Metadata Example**:
```python
from dagster import asset, AssetExecutionContext, MetadataValue

@asset
def my_dataset(context: AssetExecutionContext):
    df = compute_dataframe()

    context.add_output_metadata({
        "num_rows": len(df),
        "preview": MetadataValue.md(df.head().to_markdown()),
        "schema": MetadataValue.json({"columns": list(df.columns)})
    })

    return df
```

**2024 Enhancement**: Asset Details page now prominently displays row count and relation identifiers (table name, schema, database) when corresponding asset metadata values are provided.

### 1.11 Repositories and Definitions

**Evolution (2024)**: The `Definitions` object replaced the older `@repository` decorator concept.

**Key Points**:
- One `Definitions` object per code location
- Encapsulates all assets, jobs, schedules, sensors, and resources
- Simpler than the old repository pattern
- Under the hood, Dagster creates a repository called `__repository__` for every Definitions object

**Code Example**:
```python
from dagster import Definitions

defs = Definitions(
    assets=[daily_sales, weekly_sales, weekly_sales_report],
    jobs=[sales_job],
    schedules=[daily_schedule],
    sensors=[file_sensor],
    resources={
        "database": DatabaseResource(connection_string="...")
    }
)
```

**Configuration**: Referenced in `workspace.yaml`:
```yaml
load_from:
  - python_module:
      module_name: my_dagster_project
      attribute: defs
```

---

## 2. Architecture

### 2.1 Dagster Daemon

**Purpose**: Orchestrates schedules, sensors, run queuing, and monitoring.

**Key Functions**:
- Schedule execution
- Sensor evaluation
- Run queue management
- Expired run cleanup
- Asset materialization updates
- **New (2024)**: FreshnessDaemon now runs by default without explicit dagster.yaml configuration

**Important**: Required for schedules and sensors to function. Runs as a separate long-running process.

### 2.2 Dagit (Web UI)

**Purpose**: Web-based user interface for Dagster.

**Capabilities**:
- Asset catalog and lineage visualization
- Run monitoring and history
- Schedule and sensor management
- Ad-hoc job launches
- Configuration editing
- GraphQL API server

**2024 UI Enhancements**:
- Modern homepage redesign
- Enhanced asset health and freshness monitoring
- Customizable dashboards
- Real-time cost monitoring
- Asset checks show blocking status
- Code reference metadata (open files in editor or source control)

### 2.3 Run Launcher

**Purpose**: Determines where and how runs are executed.

**Types**:

1. **DefaultRunLauncher**:
   - Spawns a new process in the same node as code location
   - Simplest option for local development

2. **DockerRunLauncher**:
   - Allocates a Docker container per run
   - Better isolation between runs

3. **K8sRunLauncher**:
   - Allocates a Kubernetes job per run
   - Production-grade scalability

**Configuration Example**:
```yaml
# dagster.yaml
run_launcher:
  module: dagster_k8s
  class: K8sRunLauncher
  config:
    job_namespace: dagster-runs
    load_incluster_config: true
```

### 2.4 Run Coordinator

**Purpose**: Controls run queuing and concurrency.

**Types**:

1. **DefaultRunCoordinator**:
   - Immediately sends runs to run launcher
   - No queuing concept

2. **QueuedRunCoordinator**:
   - Limits concurrent runs
   - Implements run queues
   - Requires active dagster-daemon
   - **2024 Performance**: Improvements for dequeuing with many queued runs using pools

**Configuration**:
```yaml
run_coordinator:
  module: dagster.core.run_coordinator
  class: QueuedRunCoordinator
  config:
    max_concurrent_runs: 10
```

### 2.5 Storage Backends

**Purpose**: Persist run history, event logs, and asset catalog.

**Supported Backends**:
- **SQLite**: Default, suitable for development
- **PostgreSQL**: Recommended for production
- **MySQL**: Alternative production option

**Storage Types**:
1. **Run Storage**: Pipeline run records
2. **Event Log Storage**: Materialization events, logs
3. **Schedule Storage**: Schedule/sensor state

**Configuration Example**:
```yaml
storage:
  postgres:
    postgres_db:
      username: dagster
      password: dagster
      hostname: localhost
      db_name: dagster
      port: 5432
```

### 2.6 Execution Model

**Key Characteristics**:
1. **Asset-First**: Focuses on materializing data assets
2. **Declarative**: Define what should exist, not step-by-step how
3. **Dependency-Aware**: Automatically resolves execution order
4. **Idempotent**: Re-running produces same results
5. **Observable**: Every execution logged with metadata

**Execution Flow**:
1. User/Schedule/Sensor triggers run
2. Run coordinator queues or immediately launches
3. Run launcher allocates compute
4. Assets/ops execute in dependency order
5. IO managers handle data persistence
6. Events logged to storage
7. UI updates in real-time

**Run Configuration**:
```python
from dagster import materialize, RunConfig

result = materialize(
    [my_asset],
    run_config=RunConfig(
        ops={
            "my_asset": {"config": {"param": "value"}}
        }
    )
)
```

### 2.7 Code Locations

**Definition**: A code location contains a single `Definitions` object and represents a deployable unit of Dagster code.

**Architecture Benefits**:
- Isolated Python environments
- Independent deployment
- Parallel development
- Different dependency versions

**2024 Blog Post**: "Dagster's Code Location Architecture" provides detailed explanation of this concept.

---

## 3. Key Features

### 3.1 Type System

**Purpose**: Runtime validation of data flowing through pipelines, complementary to Python's static type system.

**Key Characteristics**:
- **Gradual and Optional**: Not required, can be adopted incrementally
- **Runtime Checks**: Validates data at execution time
- **PEP 484 Complementary**: Works alongside Python type hints
- **Default to Any**: Untyped inputs/outputs use the `Any` type

**Execution Timing**:
- Input type checks: Immediately before op execution
- Output type checks: Immediately after op execution

**Code Example**:
```python
from dagster import op, DagsterType, In, Out

# Custom type with validation
def is_valid_email(_, value):
    return "@" in value

EmailType = DagsterType(
    name="EmailType",
    type_check_fn=is_valid_email,
    description="A valid email address"
)

@op(out=Out(EmailType))
def get_user_email():
    return "user@example.com"

@op(ins={"email": In(EmailType)})
def send_notification(email):
    send_email(email)
```

**DataFrame Validation (dagster_pandas)**:
```python
from dagster_pandas import create_dagster_pandas_dataframe_type, PandasColumn

SalesDataFrame = create_dagster_pandas_dataframe_type(
    name="SalesDataFrame",
    columns=[
        PandasColumn.numeric_column("amount", min_value=0),
        PandasColumn.string_column("customer_id"),
        PandasColumn.datetime_column("sale_date")
    ]
)

@asset
def validated_sales() -> SalesDataFrame:
    return load_sales_data()
```

**2024 Feature**: `build_metadata_bounds_checks` API allows defining asset checks that fail if numeric metadata values fall outside specified bounds.

### 3.2 Observability and Monitoring

**Core Capabilities**:

1. **Asset Lineage**: Complete DAG visualization showing data dependencies
2. **Materialization Tracking**: Every execution logged with metadata
3. **Source Observability**: Track metadata about data itself, not just task execution
4. **Data Quality**: Built-in asset checks and validation

**Enhanced Features (2024)**:
- Asset health monitoring
- Freshness tracking with FreshnessDaemon
- Customizable dashboards
- Real-time insights
- Cost monitoring
- Blocking asset checks visibility

**Asset Health Example**:
```python
from dagster import asset, AssetCheckSpec, AssetCheckResult

@asset(
    check_specs=[
        AssetCheckSpec(name="row_count_check", asset="my_dataset")
    ]
)
def my_dataset():
    return load_data()

@asset_check(asset=my_dataset)
def row_count_check(context):
    row_count = get_row_count("my_dataset")
    return AssetCheckResult(
        passed=row_count > 0,
        metadata={"row_count": row_count}
    )
```

**Metadata Best Practices (2024)**:
- Row counts
- Schema information
- Data quality metrics
- Processing time
- Cost information

### 3.3 Testing Capabilities

**Philosophy**: Dagster makes it easier to implement software engineering best practices in data workflows.

**Testing Levels**:

1. **Unit Tests**: Test individual assets/ops in isolation
2. **Integration Tests**: Test multiple assets together
3. **Mock Resources**: Substitute external dependencies

**Unit Testing Example**:
```python
from dagster import asset, materialize

@asset
def my_asset():
    return [1, 2, 3]

def test_my_asset():
    # Direct invocation for simple assets
    result = my_asset()
    assert result == [1, 2, 3]

# For assets with context
from dagster import build_asset_context

@asset
def contextual_asset(context):
    context.log.info("Processing...")
    return compute_data()

def test_contextual_asset():
    context = build_asset_context()
    result = contextual_asset(context)
    assert result is not None
```

**Integration Testing**:
```python
def test_multiple_assets():
    result = materialize([upstream_asset, downstream_asset])
    assert result.success
    assert result.output_for_node("downstream_asset") is not None
```

**Partitioned Asset Testing**:
```python
def test_partitioned_asset():
    context = build_asset_context(partition_key="2024-01-01")
    result = my_partitioned_asset(context)
    assert result is not None
```

**Resource Mocking**:
```python
class MockDatabase(DatabaseResource):
    def query(self, sql):
        return [{"id": 1, "name": "test"}]

def test_with_mock_resource():
    result = materialize(
        [my_asset],
        resources={"database": MockDatabase(connection_string="mock")}
    )
    assert result.success
```

**Dagster University (2024)**: Offers a dedicated testing course (2-4 hours) covering comprehensive testing strategies.

### 3.4 Asset Lineage

**Definition**: Complete tracking of data origin and transformations throughout the pipeline.

**Key Benefits**:
1. **Impact Analysis**: Understand downstream effects of changes
2. **Debugging**: Trace data quality issues to source
3. **Documentation**: Self-documenting data flow
4. **Compliance**: Audit trail for data governance

**Visualization**:
- DAG view in Dagit
- Upstream/downstream relationships
- Cross-code-location lineage
- Column-level lineage (advanced)

**2024 Feature**: External Assets allow migrating to Dagster for lineage and observability without changing existing orchestration:

```python
from dagster import external_asset

# Track assets managed by other systems
external_sales_table = external_asset(
    name="sales_table",
    description="Managed by legacy ETL system"
)

@asset(deps=[external_sales_table])
def sales_analysis():
    # Dagster tracks that this depends on external asset
    return analyze_sales()
```

### 3.5 Dependency Management

**Automatic Dependency Resolution**:
- Asset dependencies inferred from function arguments or `deps` parameter
- Execution order automatically determined
- Parallel execution when possible
- Failure propagation

**Dependency Patterns**:

1. **Direct Dependencies** (function arguments):
```python
@asset
def downstream(upstream):
    return process(upstream)
```

2. **Non-Argument Dependencies** (`deps`):
```python
@asset(deps=[upstream])
def downstream():
    # Load upstream data directly from storage
    return process(load_data())
```

3. **Asset Selection**:
```python
from dagster import AssetSelection

# Select by group
sales_assets = AssetSelection.groups("sales")

# Select by key
specific_asset = AssetSelection.keys("my_asset")

# Select upstream/downstream
upstream = AssetSelection.keys("my_asset").upstream()
downstream = AssetSelection.keys("my_asset").downstream()
```

4. **Cross-Code-Location Dependencies** (2024):
Assets can depend on assets from different code locations for monorepo or microservice architectures.

### 3.6 Backfills

**Definition**: Process of materializing historical partitions of partitioned assets.

**Key Features**:
- **Single-Run vs Multi-Run**: Choose execution strategy
- **Partition Range Selection**: Backfill specific date ranges
- **Status Tracking**: Monitor backfill progress
- **Cancellation**: Stop in-progress backfills

**Code Example**:
```python
from dagster import asset, BackfillPolicy, DailyPartitionsDefinition

daily_partition = DailyPartitionsDefinition(start_date="2024-01-01")

# Multi-run backfill (default)
@asset(partitions_def=daily_partition)
def daily_data():
    return process_daily()

# Single-run backfill
@asset(
    partitions_def=daily_partition,
    backfill_policy=BackfillPolicy.single_run()
)
def efficient_backfill(context):
    # Access all partitions being backfilled
    partition_range = context.asset_partition_key_range_for_output()
    start = partition_range.start
    end = partition_range.end

    # Process all partitions efficiently in one run
    return process_range(start, end)
```

**2024 Performance**: Performance improvements for backfills of large partition sets.

**2024 Feature**: Configurable backfills with run config support - you can now pass different configurations to backfill runs.

**Important Note**: Backfill policies don't apply to backfills launched from the job page - use asset graph or asset details page.

### 3.7 Dynamic Execution

**Dynamic Partitioning**:
Create partitions at runtime based on discovered data (files, API responses, database records).

```python
from dagster import DynamicPartitionsDefinition, sensor

customers_partition = DynamicPartitionsDefinition(name="customers")

@asset(partitions_def=customers_partition)
def customer_data(context):
    customer_id = context.partition_key
    return fetch_customer_data(customer_id)

@sensor(job=customer_job)
def new_customer_sensor(context):
    new_customers = api.get_new_customers()

    # Add new partitions dynamically
    context.instance.add_dynamic_partitions(
        partitions_def_name="customers",
        partition_keys=[c.id for c in new_customers]
    )

    for customer in new_customers:
        yield RunRequest(partition_key=customer.id)
```

**Dynamic Mapping** (within ops):
```python
from dagster import DynamicOut, DynamicOutput, op

@op(out=DynamicOut())
def dynamic_producer():
    for i in range(10):
        yield DynamicOutput(value=i, mapping_key=str(i))

@op
def process_item(item):
    return item * 2

@op
def collect_results(items):
    return sum(items)

# Graph connects them with dynamic mapping
```

---

## 4. Latest Features and Improvements (2024-2025)

### 4.1 Major Releases

**Latest Versions**:
- 1.12.2 (January 9, 2025)
- 1.9.6 (December 19, 2024)
- 1.9.0 (November 1, 2024)
- Regular releases throughout 2024

### 4.2 Declarative Automation

**FreshnessDaemon**: Now runs by default without explicit configuration in `dagster.yaml`. Automatically monitors asset freshness and can trigger materializations.

### 4.3 Partition Enhancements

**Time-Based Partition Exclusions**: Exclude specific dates/times or recurring schedules (weekends, holidays, maintenance windows).

```python
from dagster import DailyPartitionsDefinition

# Exclude weekends
business_days = DailyPartitionsDefinition(
    start_date="2024-01-01",
    end_offset=-1,
    # Custom calendar excluding weekends
)
```

### 4.4 UI/UX Improvements

- Modern homepage redesign
- Enhanced asset health monitoring
- Customizable dashboards
- Real-time cost insights
- Code reference metadata (open in editor/browser)
- Row count and relation identifiers display
- Blocking asset checks visibility

### 4.5 Integration Improvements

**Stable Integrations (Previously Experimental)**:
- Dagster Pipes for Lambda
- Dagster Pipes for Kubernetes
- Dagster Pipes for Databricks

**Census Integration**:
```python
from dagster_census import CensusComponent

census = CensusComponent(api_key="...")
```

**Airby Enhanced**:
- `poll_previous_running_sync`
- `max_items_per_page`
- `poll_interval`
- `poll_timeout`
- `cancel_on_termination`

**DBT Improvements**:
- Simpler `DbtProject` configuration
- Reduced boilerplate for local development
- Customizable `op_config_schema` on `DbtProjectComponent`
- Easier dev/prod separation

### 4.6 Deployment Enhancements

**AWS ECS**: Sample Terraform modules for Dagster deployment on AWS ECS.

**Performance**:
- Run dequeuing optimization with pools
- Backfill performance for large partition sets

### 4.7 Data Quality

**Metadata Bounds Checks**:
```python
from dagster import build_metadata_bounds_checks

bounds_check = build_metadata_bounds_checks(
    asset_key="my_dataset",
    metadata_key="row_count",
    min_value=100,
    max_value=1_000_000
)
```

### 4.8 External Assets

**Major Feature**: Track and observe assets managed by external systems without orchestrating them.

```python
from dagster import external_asset, asset

external_table = external_asset(name="legacy_system_table")

@asset(deps=[external_table])
def dagster_analysis():
    # Dagster knows this depends on external asset
    # Provides lineage even though it doesn't manage external_table
    return analyze(load("legacy_system_table"))
```

**Use Case**: Gradual migration to Dagster - adopt lineage and observability first, migrate orchestration later.

---

## 5. Best Practices and Recommendations (2024)

### 5.1 Asset Design

1. **Prefer Assets Over Ops**: Use software-defined assets for data products
2. **Clear Naming**: Asset keys should reflect business meaning
3. **Appropriate Granularity**: Balance between too fine-grained and too coarse
4. **Metadata-Rich**: Add row counts, schemas, and quality metrics

### 5.2 Partitioning

1. **Limit Partition Count**: Keep under 100,000 partitions per asset
2. **Match Business Logic**: Partition by natural boundaries (daily data, regions)
3. **Use Backfill Policies**: Single-run for efficiency when appropriate
4. **Consider Multi-Dimensional**: When data naturally has multiple axes

### 5.3 Testing

1. **Unit Test Assets**: Test asset logic independently
2. **Mock Resources**: Use test implementations of external services
3. **Integration Tests**: Test critical asset chains
4. **CI/CD Integration**: Run tests before deployment

### 5.4 Observability

1. **Comprehensive Metadata**: Track metrics that matter
2. **Asset Checks**: Define data quality expectations
3. **Monitoring Dashboards**: Use Dagit's customizable dashboards
4. **Alert on Failures**: Set up sensors for critical assets

### 5.5 Performance

1. **Parallel Execution**: Design assets to run in parallel when possible
2. **Incremental Processing**: Use partitions for large datasets
3. **Resource Optimization**: Configure appropriate compute resources
4. **Storage Backend**: Use PostgreSQL for production

### 5.6 Deployment

1. **Code Locations**: Separate by team or domain
2. **Environment Separation**: Different configurations for dev/prod
3. **Version Control**: Tag releases, use semantic versioning
4. **Gradual Rollout**: Test in dev before prod deployment

---

## 6. Comparison with Traditional Orchestrators

### Asset-Centric vs Task-Centric

**Traditional Orchestrators** (Airflow, Prefect):
- Focus on tasks/operators
- DAG of operations
- Track: "Did the task run?"

**Dagster**:
- Focus on data assets
- DAG of data dependencies
- Track: "What data exists and when was it produced?"

### Observability

**Traditional**: Logs and task status

**Dagster**: Data lineage, asset metadata, data quality checks, freshness monitoring

### Development Experience

**Traditional**: Often separate code and configuration

**Dagster**: Code-first, Python-native, strong typing

### Testing

**Traditional**: Often difficult to test pipelines

**Dagster**: Built-in testing primitives, easy mocking

---

## 7. Integration Ecosystem (2024)

### Data Warehouses
- Snowflake
- BigQuery
- Redshift
- Databricks

### Data Transformation
- dbt (first-class integration)
- Spark
- Pandas

### Orchestration & Compute
- Kubernetes
- Docker
- AWS ECS/Lambda
- Databricks

### Data Quality
- Great Expectations
- Soda
- Pandera

### BI & Analytics
- Tableau
- Looker
- PowerBI
- Census (new 2024)

### Data Loading
- Airbyte
- Fivetran
- dlt

---

## 8. Resources and Documentation

### Official Documentation
- Main Docs: https://docs.dagster.io
- API Reference: https://docs.dagster.io/api
- Changelog: https://docs.dagster.io/about/changelog

### Learning Resources
- Dagster University: https://dagster.io/university
- Testing Course (2-4 hours)
- Blog: https://dagster.io/blog

### Community
- GitHub: https://github.com/dagster-io/dagster
- Slack Community
- Discussion Forums: https://discuss.dagster.io

### Key Blog Posts (2024)
- "Dagster 1.8: BI + Catalog Upgrades"
- "Dynamic Partitioning in Dagster"
- "Introducing Dagster External Assets"
- "Dagster's Code Location Architecture"

---

## 9. Summary and Key Takeaways

### Core Philosophy
Dagster represents a paradigm shift from task-based to asset-based data orchestration, treating data products as first-class citizens.

### Primary Strengths
1. **Observability**: Deep insight into data, not just task execution
2. **Developer Experience**: Python-native, testable, type-safe
3. **Flexibility**: Gradual adoption, works with existing systems
4. **Lineage**: Automatic tracking of data dependencies
5. **Modern Features**: Partitioning, backfills, dynamic execution

### When to Use Dagster
- Building data platforms with many interdependent datasets
- Need strong lineage and observability
- Value testability and software engineering practices
- Want asset-centric thinking
- Require complex partitioning strategies

### 2024-2025 Direction
- Enhanced UI/UX with customizable dashboards
- Better integration ecosystem (dbt, Census, etc.)
- Performance improvements for large-scale deployments
- External assets for gradual migration
- Declarative automation with freshness monitoring

### Getting Started Path
1. Start with simple assets and local execution
2. Add partitioning for incremental processing
3. Implement testing and CI/CD
4. Deploy with appropriate infrastructure (K8s, ECS)
5. Add advanced features (sensors, dynamic partitions)
6. Scale with code locations and resource optimization

---

**Document Version**: 1.0
**Research Date**: November 18, 2024
**Primary Sources**: Official Dagster documentation, GitHub releases, blog posts, community discussions
**Focus**: 2024-2025 features and best practices


> Source: `docs/data_engineering/dagster/dagster-research.md`

# Dagster Terminology, Ontology, and Conceptual Model Research

**Research Date:** 2025-11-18
**Current Stable Version:** Dagster 1.12.2 (Released November 13, 2025)
**Python Support:** Python 3.10 - 3.13
**Status:** Production/Stable (Development Status: 5)

---

## Table of Contents
1. [Core Terminology](#core-terminology)
2. [Data Model](#data-model)
3. [API Structure](#api-structure)
4. [Integration Model](#integration-model)
5. [Conceptual Relationships](#conceptual-relationships)

---

## 1. Core Terminology

### 1.1 Asset
**Definition:** A logical unit of data such as a table, dataset, ML model, or any persisted object that you want to keep track of.

**Key Characteristics:**
- Assets are the core abstraction in modern Dagster
- Can have dependencies on other assets, forming data lineage
- Behind the scenes, the Python function in an asset is an op
- Represents the "what" of your data pipeline (what data exists)

**Relationships:**
- Assets depend on other assets (upstream/downstream dependencies)
- Assets are materialized through execution
- Assets can be partitioned
- Assets can have checks associated with them

**Example:**
```python
@asset
def my_table(context: AssetExecutionContext):
    # Computation that produces data
    return some_data
```

---

### 1.2 Materialization
**Definition:** The act of running an asset's function and saving the results to persistent storage.

**Key Characteristics:**
- Encompasses the entire lifecycle from asset definition through execution to event logging
- Generates `AssetMaterialization` events in Dagster's event log
- Can be triggered from the Dagster UI or via Python APIs
- Recorded in the asset catalog with metadata

**Related Concepts:**
- **Asset Observation:** Records metadata about an asset without mutating it
- **Rematerialization:** Re-running an asset's computation to update its value

---

### 1.3 Op (Operation)
**Definition:** A computational unit of work representing the smallest unit of computation in Dagster.

**Key Characteristics:**
- Core unit of computation in Dagster
- Arranged into a `GraphDefinition` to dictate execution order
- Can be composed into graphs
- Legacy approach; assets are now preferred for most use cases

**Relationships:**
- Ops are composed into graphs
- Graphs are executed as jobs
- Assets are implemented as ops under the hood

**Example:**
```python
@op
def process_data(context: OpExecutionContext, input_data):
    # Computation logic
    return processed_data
```

**When to Use:**
- Managing existing ops in legacy codebases
- Complex use cases requiring fine-grained control
- For new projects, assets are strongly recommended

---

### 1.4 Graph
**Definition:** A collection of ops or nested graphs connected via dependencies, representing the structure of computation.

**Key Characteristics:**
- Defines the dependency structure between ops
- Supports arbitrary nesting levels
- Can contain both ops and other graphs as nodes
- Created using `@graph` decorator or `GraphDefinition` class

**Composition:**
- **Input Mappings:** Define graph inputs and how they map to constituent ops
- **Output Mappings:** Define graph outputs and how they map from constituent ops
- **Dependencies:** Declare how op inputs depend on other op outputs

**Example:**
```python
@graph
def data_pipeline():
    raw = extract_data()
    transformed = transform_data(raw)
    load_data(transformed)
```

---

### 1.5 Job
**Definition:** The main unit of execution and monitoring in Dagster, representing an executable subset of assets or a graph of ops.

**Key Characteristics:**
- Jobs are the main form of execution in Dagster
- Can execute asset subsets or op graphs
- Can be triggered by schedules, sensors, or manually
- Produces runs when executed

**Types:**
- **Asset Jobs:** Execute a selection of assets
- **Op Jobs:** Execute a graph of ops

**Example:**
```python
@job
def my_job():
    op1()
    op2()

# Or for assets
asset_job = define_asset_job("my_asset_job", selection="my_asset*")
```

---

### 1.6 Run
**Definition:** A single execution instance of a job.

**Status Lifecycle:**
1. **STARTING:** Run is launched, waiting for run worker to spin up
2. **STARTED:** Run worker has marked the run as started
3. **SUCCESS:** Run completed successfully (DagsterRunStatus.SUCCESS)
4. **FAILED:** Run failed during execution
5. **CANCELING:** Run is being terminated
6. **CANCELED:** Run has been terminated and cleaned up

**Timeout Parameters:**
- `start_timeout_seconds`: Max time in STARTING before marked as failed
- `cancel_timeout_seconds`: Max time in CANCELING before marked as canceled

**Related Concepts:**
- **Run Request:** Object returned by schedules/sensors to trigger a run
- **Run Status Sensor:** Monitors runs and triggers actions on status changes
- **Run Monitoring:** Daemon that detects and manages crashed workers

---

### 1.7 Partition
**Definition:** A logical division of an asset or job's data, typically based on time windows or categorical dimensions.

**Key Characteristics:**
- Enables incremental processing of data
- Supports time-based and categorical partitioning
- Can be multi-dimensional
- Enables targeted backfills

**Partition Types:**
- **Time Window Partitions:** Daily, hourly, monthly, etc.
- **Static Partitions:** Fixed set of partition keys
- **Dynamic Partitions:** Partition keys determined at runtime
- **Multi-Partitions:** Multiple dimensions (e.g., date + region)

**Partition Dependencies:**
- Same partition dependencies (default for matching PartitionsDefinitions)
- Time window intersections (for time-partitioned assets)
- Custom partition mappings (via PartitionMapping)
- Self-dependencies (asset depends on its own earlier partitions)

---

### 1.8 Backfill
**Definition:** The process of running partitions for assets that either don't exist or updating existing records with new logic.

**Types:**
- **Multi-Run Backfills (Default):** N partitions = N separate runs
- **Single-Run Backfills:** Execute all partitions in one run (e.g., single SQL query)

**BackfillPolicy:**
- Specifies how Dagster should backfill a partitioned asset
- Can optimize for performance or granularity
- Configurable per asset

**Common Use Cases:**
- Initial setup of pipelines with historical data
- Updating historical data after logic changes
- Fixing data quality issues retroactively

---

### 1.9 Schedule
**Definition:** A time-based trigger that creates runs on a regular cadence, defined using cron syntax.

**Key Characteristics:**
- Defined with `@schedule` decorator
- Takes `ScheduleEvaluationContext` as parameter
- Returns `RunRequest` objects or `SkipReason`
- Can access resources for external service calls
- Evaluated by Dagster daemon

**Example:**
```python
@schedule(job=my_job, cron_schedule="0 0 * * *")
def daily_schedule(context: ScheduleEvaluationContext):
    return RunRequest(run_config={...})
```

---

### 1.10 Sensor
**Definition:** An event-driven trigger that evaluates a condition and creates runs based on external events.

**Key Characteristics:**
- Defined with `@sensor` decorator
- Polls at a specified interval
- Can monitor assets, files, external systems, or run status
- Returns `RunRequest` or `SkipReason`

**Sensor Types:**
- **Asset Sensors:** Monitor asset materializations
- **Run Status Sensors:** Monitor run completion/failure
- **Custom Sensors:** Monitor arbitrary conditions

**Example:**
```python
@asset_sensor(asset_key=AssetKey("upstream_asset"), job=my_job)
def my_asset_sensor(context, asset_event):
    return RunRequest(run_key=context.cursor)
```

---

### 1.11 Resource
**Definition:** An external service, connection, or configuration made available to ops, assets, schedules, and sensors during execution.

**Key Characteristics:**
- Scoped way to make external resources available
- Defined with `@resource` decorator
- Takes `InitResourceContext` as parameter
- Supports lifecycle management (setup/teardown)
- Can be mocked for testing

**Modern Pythonic Config:**
- Resources can now be defined using Python dataclasses
- Pydantic validation under the hood
- Standardizes connections across all Dagster definitions

**Example:**
```python
@resource
def database_connection(init_context: InitResourceContext):
    conn = create_connection(init_context.resource_config["connection_string"])
    yield conn
    conn.close()
```

---

### 1.12 IO Manager
**Definition:** A component that handles reading and writing data for assets and ops, separating data processing logic from storage operations.

**Key Characteristics:**
- Subclasses must implement `handle_output` and `load_input` methods
- Reduces code redundancy across assets
- Makes storage configurations flexible across environments
- Can be extended as `ConfigurableIOManager` for config schemas

**Built-in IO Managers:**
- Filesystem IO Manager (using pickling)
- Cloud storage managers (S3, GCS, Azure Blob)
- Database managers (via integration libraries)

**When to Use:**
- Repeated read/write patterns across assets
- Standardized path structures for multiple assets
- Different storage needs across environments (local, staging, prod)
- Dependencies need to be loaded into memory before computation

**Example:**
```python
class MyIOManager(IOManager):
    def handle_output(self, context, obj):
        # Write obj to storage
        write_to_storage(context.asset_key, obj)

    def load_input(self, context):
        # Read from storage
        return read_from_storage(context.asset_key)
```

---

### 1.13 Code Location
**Definition:** A collection of Dagster definitions loadable and accessible by Dagster's tools (CLI, UI, Dagster+).

**Structure:**
- Reference to a Python module containing a `Definitions` instance
- Python environment that can successfully load that module
- Loaded in separate process, communicates via RPC

**Key Rules:**
- Only ONE `Definitions` object per code location
- `Definitions` must be a top-level variable
- Multiple code locations can exist per Dagster instance

**Benefits:**
- Code location updates picked up without webserver restart
- Different code locations can have separate Python environments
- Enables team-based organization with dependency isolation

---

### 1.14 Definitions
**Definition:** A central registry object that encapsulates all Dagster definitions (assets, jobs, schedules, sensors, resources).

**Key Characteristics:**
- Replaces the legacy "repository" concept
- Must be a singleton per code location
- Must be available as top-level variable
- Acts as the entry point for Dagster tools

**Example:**
```python
from dagster import Definitions

defs = Definitions(
    assets=[asset1, asset2],
    jobs=[job1, job2],
    schedules=[schedule1],
    sensors=[sensor1],
    resources={"db": database_resource}
)
```

---

## 2. Data Model

### 2.1 Event System
**Definition:** A structured stream of metadata events emitted during pipeline execution, forming an immutable log of all system activity.

**Key Characteristics:**
- Events are immutable once written
- Stored in Dagster's event log storage
- Available for querying and visualization
- Some system-generated, some user-provided

**Event Categories:**
1. **System Events:** Automatically emitted by Dagster
   - Op start/completion
   - Step execution events
   - Engine events

2. **User Events:** Explicitly yielded by user code
   - Asset materializations
   - Asset observations
   - Expectation results
   - Custom metadata

---

### 2.2 Event Types

#### AssetMaterialization
**Purpose:** Records that a data asset has been written to external storage.

**Characteristics:**
- Automatically generated for assets
- Can be manually yielded from ops
- Records metadata about the materialized asset
- Tracked in asset catalog
- Can trigger asset sensors

**Example:**
```python
yield AssetMaterialization(
    asset_key="my_table",
    metadata={
        "num_rows": 1000,
        "schema_version": "v2"
    }
)
```

---

#### AssetObservation
**Purpose:** Records metadata about an asset without indicating mutation.

**Use Cases:**
- Monitoring external tables not managed by Dagster
- Recording data quality metrics
- Tracking asset freshness
- Observing schema changes

**Difference from Materialization:**
- Does NOT indicate the asset was written
- Used for passive monitoring
- Does NOT trigger asset sensors by default

---

#### Output
**Purpose:** Passes data from one op to another, the most critical event for Dagster functionality.

**Characteristics:**
- Enables data flow between ops
- Can include metadata
- Supports conditional branching
- Type annotations maintained

**Enhanced with Output Object:**
```python
yield Output(
    value=my_data,
    metadata={
        "row_count": len(my_data)
    }
)
```

---

#### AssetCheckResult
**Purpose:** Returns the result of a data quality check on an asset (modern approach, replacing ExpectationResult).

**Characteristics:**
- Returned from `@asset_check` decorated functions
- Operates on specific assets
- Flexibly schedulable
- Integrated into asset catalog

**Example:**
```python
@asset_check(asset=my_asset)
def check_row_count(asset_materialization):
    return AssetCheckResult(
        passed=row_count > 0,
        metadata={"row_count": row_count}
    )
```

---

#### ExpectationResult
**Purpose:** DEPRECATED - Records data quality test results (replaced by AssetCheckResult).

**Status:**
- Will be removed in Dagster 2.0
- Use `AssetCheckResult` and `@asset_check` instead for assets

---

#### DynamicOutput
**Purpose:** Represents one item in a set for dynamic fan-out operations.

**Characteristics:**
- Must have unique `mapping_key`
- Enables dynamic parallelism
- Must be used with `map()` or `collect()`

**Pattern:**
- **Fan-out:** Use `.map()` to process each dynamic output
- **Fan-in:** Use `.collect()` to gather results

**Example:**
```python
@op(out=DynamicOut())
def dynamic_op():
    for i in range(10):
        yield DynamicOutput(i, mapping_key=str(i))

@job
def dynamic_job():
    results = dynamic_op().map(process_item)
    final = aggregate(results.collect())
```

---

### 2.3 Asset Catalog

**Definition:** A centralized registry of all data assets tracked by Dagster, automatically populated and always synchronized with pipelines.

**Key Features:**
- **Automatic Population:** Assets registered through code
- **Metadata Storage:** Columns, row counts, schema versions, custom metadata
- **Lineage Tracking:** Visual dependency graph
- **Run History:** All materializations with timestamps
- **Partitions View:** Status of partitioned assets
- **Asset Checks:** Data quality check results

**Integration with dbt:**
- dbt models automatically appear as assets
- Metadata from dbt manifest included
- Lineage preserved from dbt DAG

**Benefits:**
- Single place to investigate issues
- Metadata, lineage, and run status connected
- Always up to date (part of orchestration layer)

---

### 2.4 Pipeline Representation

**Hierarchical Structure:**
```
Definitions (Code Location)
├── Assets
│   ├── Dependencies (AssetDeps)
│   ├── Partitions (PartitionsDefinition)
│   └── Checks (AssetChecks)
├── Jobs
│   ├── Asset Jobs (asset selections)
│   └── Op Jobs (graphs)
├── Graphs
│   ├── Ops (compute units)
│   └── Nested Graphs
├── Schedules
├── Sensors
└── Resources
```

**Asset-First Model:**
- Modern Dagster centers on assets (the "what")
- Jobs and graphs are execution mechanisms (the "how")
- Lineage automatically derived from asset dependencies
- UI emphasizes asset catalog over job runs

---

### 2.5 Metadata Schema

**Metadata Types:**
1. **Text:** String values
2. **URL:** Links to external resources
3. **Path:** File system paths
4. **JSON:** Structured data
5. **Markdown:** Rich text documentation
6. **Float/Int:** Numeric metrics
7. **Bool:** Boolean flags
8. **Table:** Structured table data
9. **Asset:** References to other assets

**Metadata Locations:**
- Asset definitions (static metadata)
- Materialization events (runtime metadata)
- Asset observations
- Asset checks
- Op outputs

**Column-Level Lineage:**
- Track dependencies at column level
- Understand how columns are created and used
- Available for database table assets
- Improves collaboration and debugging

---

## 3. API Structure

### 3.1 Decorators

#### @asset
**Purpose:** Define a software-defined asset.

**Parameters:**
- `name`: Asset name (defaults to function name)
- `deps`: Upstream asset dependencies (without loading data)
- `ins`: Input definitions for loading upstream assets
- `config_schema`: Configuration schema
- `required_resource_keys`: Resources needed
- `partitions_def`: Partition definition
- `metadata`: Static metadata
- `io_manager_key`: IO manager to use
- `compute_kind`: Display tag (e.g., "SQL", "Python")
- `code_version`: Version tracking for caching

**Example:**
```python
@asset(
    deps=["raw_data"],
    config_schema={"threshold": int},
    required_resource_keys={"database"},
    partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"),
    compute_kind="Python"
)
def processed_data(context: AssetExecutionContext, raw_data):
    threshold = context.op_config["threshold"]
    # Process data
    return result
```

---

#### @op
**Purpose:** Create an operation/computation unit.

**Parameters:**
- `name`: Op name
- `ins`: Input definitions with types
- `out`: Output definition(s)
- `config_schema`: Configuration schema
- `required_resource_keys`: Resources needed
- `tags`: Metadata tags

**Example:**
```python
@op(
    config_schema={"iterations": int},
    out={"result": Out(), "metrics": Out()}
)
def complex_computation(context: OpExecutionContext, input_data):
    # Computation
    return result, metrics
```

---

#### @graph
**Purpose:** Compose ops into a reusable graph structure.

**Characteristics:**
- Can be nested within other graphs
- Doesn't execute directly (needs to be part of a job)
- Defines computational structure

**Example:**
```python
@graph
def etl_pipeline():
    raw = extract()
    cleaned = clean(raw)
    transformed = transform(cleaned)
    return load(transformed)
```

---

#### @job
**Purpose:** Create an executable job from ops/graphs or configure an asset job.

**Parameters:**
- `name`: Job name
- `config`: Run configuration
- `resource_defs`: Resource definitions
- `hooks`: Success/failure hooks
- `tags`: Metadata tags
- `description`: Job description

**Example:**
```python
@job(
    resource_defs={"db": database_resource},
    hooks={my_failure_hook}
)
def data_pipeline():
    load(transform(extract()))
```

---

#### @resource
**Purpose:** Define a resource for external services/connections.

**Parameters:**
- `config_schema`: Resource configuration schema
- `description`: Resource description
- `required_resource_keys`: Nested resource dependencies

**Example:**
```python
@resource(config_schema={"connection_string": str})
def database(init_context: InitResourceContext):
    conn = connect(init_context.resource_config["connection_string"])
    try:
        yield conn
    finally:
        conn.close()
```

---

#### @schedule
**Purpose:** Create a time-based schedule for a job.

**Parameters:**
- `job`: Job to execute
- `cron_schedule`: Cron expression
- `execution_timezone`: Timezone for schedule
- `default_status`: RUNNING or STOPPED

**Example:**
```python
@schedule(
    job=my_job,
    cron_schedule="0 9 * * MON-FRI",
    execution_timezone="America/New_York"
)
def business_hours_schedule(context: ScheduleEvaluationContext):
    return RunRequest(
        run_key=context.scheduled_execution_time.isoformat(),
        run_config={"ops": {"process": {"config": {"date": context.scheduled_execution_time}}}}
    )
```

---

#### @sensor
**Purpose:** Create an event-driven sensor.

**Parameters:**
- `job`: Job to execute
- `minimum_interval_seconds`: Polling interval
- `description`: Sensor description
- `default_status`: RUNNING or STOPPED

**Example:**
```python
@sensor(job=my_job, minimum_interval_seconds=60)
def file_sensor(context: SensorEvaluationContext):
    if new_file_exists():
        return RunRequest(run_key=get_file_hash())
    return SkipReason("No new files")
```

---

#### @asset_check
**Purpose:** Define a data quality check for an asset.

**Parameters:**
- `asset`: Asset to check
- `name`: Check name
- `description`: Check description
- `required_resource_keys`: Resources needed

**Example:**
```python
@asset_check(asset=my_table, name="row_count_positive")
def check_has_rows(context):
    row_count = query_row_count()
    return AssetCheckResult(
        passed=row_count > 0,
        metadata={"row_count": row_count}
    )
```

---

#### @success_hook / @failure_hook
**Purpose:** Define success/failure handling for ops.

**Parameters:**
- `required_resource_keys`: Resources needed (e.g., Slack, PagerDuty)

**Example:**
```python
@failure_hook(required_resource_keys={"slack"})
def notify_failure(context: HookContext):
    context.resources.slack.send_message(
        f"Op {context.op.name} failed: {context.op_exception}"
    )
```

**Application:**
```python
@job(hooks={notify_failure})
def monitored_job():
    my_op()
```

---

### 3.2 Context Objects

#### OpExecutionContext
**Purpose:** Provides system information to ops during execution.

**Key Properties/Methods:**
- `log`: DagsterLogManager for logging
- `resources`: Access to configured resources
- `op_config`: Configuration for the op
- `run_id`: Unique identifier for the run
- `run`: Run object with metadata
- `instance`: DagsterInstance for querying storage
- `partition_key`: Partition being processed (if partitioned)
- `asset_key`: Asset key (for asset-backed ops)

**Construction for Testing:**
```python
context = build_op_context(
    resources={"db": mock_db},
    config={"threshold": 10}
)
```

---

#### AssetExecutionContext
**Purpose:** Context object specifically for assets (subtype of OpExecutionContext).

**Rationale:**
- Exposes only fields relevant to assets
- Hides op implementation details
- Cleaner API surface for asset authors

**Additional Asset-Specific Properties:**
- `asset_key`: The asset being materialized
- `asset_partition_key`: Current partition
- `asset_partition_key_range`: Range for multi-partition runs
- `asset_partitions_def`: Partition definition

**Relationship:**
- `AssetExecutionContext` is a subtype of `OpExecutionContext`
- Underlying `OpExecutionContext` used when needed
- Recommended type annotation for asset functions

**Construction for Testing:**
```python
context = build_asset_context(
    resources={"db": mock_db},
    partition_key="2024-01-01"
)
```

---

#### InitResourceContext
**Purpose:** Context provided to resource initialization functions.

**Key Properties:**
- `resource_config`: Configuration for the resource
- `resources`: Access to other resources (for dependencies)
- `log`: Logger
- `instance`: DagsterInstance

---

#### HookContext
**Purpose:** Context provided to hook functions.

**Key Properties:**
- `log`: Logger
- `op`: Op that succeeded/failed
- `op_exception`: Exception object (for failure hooks)
- `resources`: Access to resources
- `run_id`: Current run ID

---

#### ScheduleEvaluationContext
**Purpose:** Context for schedule evaluation.

**Key Properties:**
- `scheduled_execution_time`: When the schedule tick occurred
- `instance`: DagsterInstance
- `resources`: Access to resources
- `log`: Logger
- `cursor`: Persistent state (optional)

---

#### SensorEvaluationContext
**Purpose:** Context for sensor evaluation.

**Key Properties:**
- `cursor`: Persistent state for tracking progress
- `last_run_key`: Key of last run launched
- `resources`: Access to resources
- `instance`: DagsterInstance
- `log`: Logger

---

### 3.3 Configuration APIs

**Modern Pythonic Config:**
```python
from dagster import Config

class MyOpConfig(Config):
    threshold: int
    mode: str = "standard"

@op
def my_op(context: OpExecutionContext, config: MyOpConfig):
    if config.threshold > 10:
        # ...
```

**Legacy Config Schema:**
```python
@op(config_schema={"threshold": int, "mode": str})
def my_op(context: OpExecutionContext):
    threshold = context.op_config["threshold"]
```

**Run Configuration:**
```python
run_config = {
    "ops": {
        "my_op": {
            "config": {"threshold": 10}
        }
    },
    "resources": {
        "database": {
            "config": {"connection_string": "..."}
        }
    }
}
```

---

### 3.4 Testing APIs

#### Direct Asset/Op Invocation
```python
# Assets can be invoked directly
result = my_asset(context=build_asset_context())

# Same for ops
result = my_op(context=build_op_context())
```

---

#### Mocking Resources
**Using mock.Mock:**
```python
from unittest.mock import Mock

mock_db = Mock(spec=DatabaseResource)
mock_db.query.return_value = [...]

context = build_asset_context(resources={"db": mock_db})
result = my_asset(context)
```

**Using ResourceDefinition.mock_resource:**
```python
from dagster import ResourceDefinition

mock_resource = ResourceDefinition.mock_resource()
```

---

#### Context Builders
- `build_op_context()`: Create OpExecutionContext for testing
- `build_asset_context()`: Create AssetExecutionContext for testing
- `build_init_resource_context()`: Create InitResourceContext for testing

---

#### Execution Helpers
```python
# Execute a job
result = my_job.execute_in_process(
    resources={"db": mock_db},
    run_config={...}
)

# Materialize assets
from dagster import materialize

result = materialize(
    [asset1, asset2],
    resources={"db": mock_db}
)
```

---

### 3.5 GraphQL API

**Endpoint:** `/graphql` (e.g., `http://localhost:3000/graphql`)

**Key Capabilities:**
- Query runs, jobs, assets, and schedules
- Retrieve metadata and dependency structures
- Launch job executions and re-executions
- Query config schemas

**GraphQL Playground:**
- Access at `/graphql` in browser
- Interactive schema exploration
- Query building and testing

**Python Client:**
```python
from dagster_graphql import DagsterGraphQLClient

client = DagsterGraphQLClient("localhost", port_number=3000)
# Or for Dagster+
client = DagsterGraphQLClient("YOUR_ORG.dagster.cloud")
```

**Python Equivalents (Preferred Inside Executions):**
- Use `context.instance` when inside op/asset/schedule/sensor
- Methods: `instance.get_runs()`, `instance.get_asset_records()`
- Avoid GraphQL for internal queries; use instance API

**Configuration Schema:**
- `RunConfigData`: Must conform to job's config schema
- Validation errors return `RunConfigValidationInvalid`

---

## 4. Integration Model

### 4.1 Plugin Architecture

**Core Concept:** Dagster extends to external services via integration libraries that provide specialized components and resources.

**Integration Pattern:**
- Each integration is a separate Python package (e.g., `dagster-dbt`, `dagster-aws`)
- Integrations provide:
  - Custom resource definitions
  - Specialized decorators/components
  - Pre-built ops/assets
  - IO managers for specific systems

**Maintained Integrations:**
- AWS (dagster-aws)
- Google Cloud Platform (dagster-gcp)
- Azure (dagster-azure)
- dbt (dagster-dbt)
- Databricks (dagster-databricks)
- Snowflake (dagster-snowflake)
- Fivetran (dagster-fivetran)
- Airbyte (dagster-airbyte)
- Great Expectations (dagster-ge)
- Pandas (dagster-pandas)
- Spark (dagster-spark)
- PySpark (dagster-pyspark)
- Datadog (dagster-datadog)
- And many more...

---

### 4.2 dbt Integration (dagster-dbt)

**Component-Based Approach:**
```python
from dagster_dbt import DbtProjectComponent

dbt_project = DbtProjectComponent(
    project_dir="path/to/dbt_project",
    manifest="path/to/manifest.json"
)

defs = Definitions(
    assets=dbt_project.assets,
    ...
)
```

**Key Features:**
- **Asset-Level Understanding:** Each dbt model becomes a Dagster asset
- **Automatic Lineage:** dbt DAG preserved in Dagster asset graph
- **Metadata Integration:** dbt metadata (columns, tests) in Dagster catalog
- **Mixed Orchestration:** Combine dbt with Spark, Python, etc.
- **Automatic Events:** AssetMaterialization events on dbt model runs

**@dbt_assets Decorator:**
```python
from dagster_dbt import dbt_assets

@dbt_assets(manifest=manifest_json)
def my_dbt_models(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
```

**Customization:**
- Create subclass of `DbtProjectComponent` for custom behavior
- Override execution methods
- Add custom metadata
- Customize op configuration

---

### 4.3 Cloud Platform Integrations

**AWS (dagster-aws):**
- S3 IO Manager
- Secrets Manager integration
- ECS/Fargate execution
- EMR for Spark
- Redshift resources

**GCP (dagster-gcp):**
- GCS IO Manager
- BigQuery resources
- Cloud Run execution
- Dataproc for Spark

**Azure (dagster-azure):**
- Blob Storage IO Manager
- Azure Data Lake integration
- Synapse resources

---

### 4.4 Data Processing Integrations

**Spark/PySpark:**
- SparkResource
- PySpark ops
- DataFrame transformations
- Cluster management

**Pandas:**
- DataFrame type system
- Validation decorators
- Summary statistics

**Polars:**
- DataFrame integration
- Type checking

---

### 4.5 Data Observability Integrations

**Datadog:**
- Metrics export
- Event logging
- APM integration

**Great Expectations:**
- Expectation suites as asset checks
- Validation results as events

---

### 4.6 Integration Patterns

**Software-Defined Assets Framework:**
- All integrations align with asset-first model
- External tools represented as assets
- Lineage automatically tracked
- Single orchestration layer

**Resource Pattern:**
```python
from dagster_aws.s3 import S3Resource

defs = Definitions(
    assets=[...],
    resources={
        "s3": S3Resource(region="us-west-2")
    }
)
```

**Extending Dagster:**
- Create custom resources by implementing `@resource`
- Create custom IO managers by extending `IOManager`
- Create custom integrations as Python packages
- Publish to PyPI for community use

---

## 5. Conceptual Relationships

### 5.1 Asset-Centric Data Model

```
Asset
  ├── Has Dependencies (other Assets)
  ├── Has Partitions (PartitionsDefinition)
  ├── Has Checks (AssetChecks)
  ├── Produces Materializations (events)
  ├── Can be Observed (AssetObservation events)
  ├── Belongs to Code Location
  ├── Uses IO Manager (for storage)
  ├── Uses Resources (for external services)
  └── Implemented as Op (under the hood)
```

### 5.2 Execution Hierarchy

```
Code Location (Process boundary)
  └── Definitions (Singleton registry)
       ├── Assets
       │    └── Implicitly create Asset Jobs
       ├── Jobs
       │    ├── Asset Jobs (asset selection)
       │    └── Op Jobs (graph execution)
       │         └── Graphs
       │              └── Ops (leaves) / Graphs (nested)
       ├── Schedules (trigger Jobs on time)
       ├── Sensors (trigger Jobs on events)
       └── Resources (available to all)

Execution:
  Schedule/Sensor/Manual → Job → Run → Steps → Events
```

### 5.3 Event Flow

```
Job Execution
  └── Run (STARTING → STARTED → SUCCESS/FAILED)
       └── Op/Asset Execution
            ├── System Events (step start/end)
            ├── User Events
            │    ├── Output (data flow)
            │    ├── AssetMaterialization
            │    ├── AssetObservation
            │    ├── AssetCheckResult
            │    └── Metadata
            └── Event Log (immutable storage)
                 └── Asset Catalog (queryable view)
```

### 5.4 Data Flow Patterns

**Asset Pattern (Modern):**
```
Asset A → Asset B → Asset C
  (automatic lineage, implicit data passing via IO Manager)
```

**Op Pattern (Legacy):**
```
Op A → (Output) → Op B → (Output) → Op C
  (explicit data passing via function returns)
```

**Dynamic Pattern:**
```
Op A → DynamicOut[0..N] → Op B.map() → N parallel executions
                        → Op C.collect() → single result
```

### 5.5 Partitioning Model

```
Partitioned Asset
  ├── PartitionsDefinition
  │    ├── TimeWindowPartitionsDefinition (daily, hourly, etc.)
  │    ├── StaticPartitionsDefinition (fixed keys)
  │    ├── DynamicPartitionsDefinition (runtime keys)
  │    └── MultiPartitionsDefinition (e.g., date × region)
  │
  ├── Partition Mappings (dependency rules)
  │    ├── IdentityPartitionMapping (default, same key)
  │    ├── TimeWindowPartitionMapping (with offsets)
  │    └── MultiToSingleDimensionPartitionMapping
  │
  └── Backfill Strategies
       ├── Multi-Run (default, N partitions = N runs)
       └── Single-Run (all partitions in one run)
```

### 5.6 Code Organization

```
Project
  ├── __init__.py
  ├── assets/
  │    ├── raw_data.py (extract assets)
  │    ├── staging.py (transform assets)
  │    └── marts.py (load assets)
  ├── resources/
  │    ├── database.py
  │    └── apis.py
  ├── jobs/
  │    └── adhoc_jobs.py (op-based jobs)
  ├── schedules/
  │    └── daily_schedules.py
  ├── sensors/
  │    └── file_sensors.py
  └── definitions.py
       └── Definitions object (entry point)
```

### 5.7 Testing Model

```
Unit Testing
  ├── Direct Invocation
  │    ├── asset_function(build_asset_context())
  │    └── op_function(build_op_context())
  │
  ├── Mocked Resources
  │    ├── Mock(spec=ResourceClass)
  │    └── ResourceDefinition.mock_resource()
  │
  └── Isolated Context
       └── build_*_context(resources={...}, config={...})

Integration Testing
  ├── materialize([assets], resources={...})
  └── job.execute_in_process(resources={...})

Production Testing
  ├── Asset Checks (@asset_check)
  └── Sensors (monitoring and alerting)
```

---

## Summary: Dagster's Semantic Model

**Core Philosophy:** Dagster is an **orchestrator that thinks in terms of data assets** rather than just tasks or jobs. The semantic model reflects this:

1. **Assets First:** The primary abstraction is the data asset (what you're producing), not the job (how you produce it).

2. **Declarative Lineage:** Dependencies are declared, and Dagster automatically builds the execution graph and tracks lineage.

3. **Event-Driven Observability:** Everything produces events that form an immutable audit log, enabling rich debugging and monitoring.

4. **Unified Catalog:** All assets live in a single catalog that's always in sync with code, making data discovery natural.

5. **Flexible Execution:** The same asset definitions can be executed on different schedules, partitions, or subsets without changing code.

6. **Testing-First:** Every component can be tested in isolation with built-in mocking and context builders.

7. **Integration-Friendly:** Plugin architecture allows seamless integration with the modern data stack while maintaining consistent abstractions.

8. **Type Safety:** Strong type system with Pydantic-based config and Python type hints throughout.

**Key Innovation:** Dagster bridges the gap between **data engineering** (managing data assets and their relationships) and **orchestration** (scheduling and executing computations), treating them as unified concerns rather than separate domains.

---

## References

- **Official Documentation:** https://docs.dagster.io/
- **API Reference:** https://docs.dagster.io/api
- **GitHub Repository:** https://github.com/dagster-io/dagster
- **PyPI Package:** https://pypi.org/project/dagster/
- **Changelog:** https://docs.dagster.io/about/changelog
- **GraphQL API:** https://docs.dagster.io/concepts/webserver/graphql

**Research Compiled:** 2025-11-18
**Based on:** Dagster 1.12.2 (latest stable as of November 2025)


## OpenAPI Research


> Source: `docs/data_engineering/dagster/dagster-openapi-research.md`

# Dagster OpenAPI Specification Research

**Date:** 2025-11-22
**Status:** Complete
**Research Focus:** Official Dagster OpenAPI/Swagger specifications

---

## Executive Summary

**Does an Official OpenAPI Spec Exist?** **NO**

Dagster does not provide an official OpenAPI/Swagger specification for its APIs. Instead, Dagster primarily exposes a **GraphQL API** as its main programmatic interface, along with a limited **REST API** specifically for external asset management.

---

## API Architecture Overview

### Primary API: GraphQL

Dagster's main programmatic interface is a GraphQL API that provides comprehensive access to Dagster's functionality:

- **Endpoint:** `/graphql` (e.g., `http://localhost:3000/graphql` for local development)
- **Interactive Playground:** Available at the `/graphql` endpoint with built-in documentation
- **Schema Location:** `./js_modules/dagster-ui/packages/ui-core/src/graphql/schema.graphql` in the repository
- **Status:** Evolving and subject to breaking changes (documented in release notes)

**Key Capabilities:**
- Query information about Dagster runs (historical and currently executing)
- Launch or terminate job executions
- Access metadata about repositories, jobs, and ops
- Retrieve dependency structures and configuration schemas
- Trigger custom events

**Documentation:**
- GraphQL API Docs: https://docs.dagster.io/api/graphql
- GraphQL Python Client: https://docs.dagster.io/concepts/webserver/graphql-client
- dagster-graphql Library: https://docs.dagster.io/api/libraries/dagster-graphql

### Secondary API: External Assets REST API

Dagster provides a limited REST API specifically for external asset management:

**Base URL Format:**
- **Local:** `http://localhost:3000/`
- **Dagster Cloud:** `https://{ORGANIZATION}.dagster.cloud/{DEPLOYMENT_NAME}/`

**Authentication:**
- Header: `Dagster-Cloud-Api-Token` (for Dagster Cloud/Plus)
- Token Type: User Token (not Agent Token)

**Available Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/report_asset_materialization/{ASSET_KEY}` | POST | Records an AssetMaterialization event for an external asset |
| `/report_asset_check/{ASSET_KEY}` | POST | Records an asset check evaluation result |
| `/report_asset_observation/{ASSET_KEY}` | POST | Records an AssetObservation event |

**Request/Response Format:**
- **Content-Type:** `application/json`
- **Success Response (200):** `{}`
- **Error Response (400):** `{"error": "..."}`

**Common Parameters:**
- `asset_key` (required) - Asset identifier
- `metadata` (optional) - Key-value pairs about the asset
- `data_version` (optional) - Version tracking
- `description` (optional) - Human-readable explanation
- `partition` (optional) - Partition identifier
- `passed` (for checks) - Boolean check result
- `check_name` (for checks) - Name of the check

**Documentation:** https://docs.dagster.io/api/rest-apis/external-assets-rest-api

### CLI-based API: `dg api`

Dagster Plus offers REST-like API operations through the `dg api` CLI command:

**Capabilities:**
- Managing agents
- Listing deployments
- Managing runs
- Managing schedules
- Managing secrets (encrypted environment variables)

**Documentation:** https://docs.dagster.io/api/clis/dg-cli/dg-api

---

## Repository Analysis

### GitHub Repository: dagster-io/dagster

**URL:** https://github.com/dagster-io/dagster

**Search Results:**
- **No OpenAPI/Swagger files found** (no `openapi.yaml`, `swagger.json`, or `openapi.json`)
- **API Specification Files:**
  - `RUN_API_SPECIFICATION.md` - Documents the Dagster Plus Run Events API (GraphQL-based, not OpenAPI)
  - `RUN_API_IMPLEMENTATION_PLAN.md` - Implementation planning document
  - `.graphqlrc.yml` - GraphQL configuration file

**Note:** The REST API is documented through narrative documentation pages rather than machine-readable specification files.

---

## Generating an OpenAPI Specification

### Current State: Not Feasible Out-of-the-Box

Since Dagster does not provide an OpenAPI specification, you would need to:

1. **For the External Assets REST API:** Manually create an OpenAPI spec based on the documentation
2. **For the GraphQL API:** Convert the GraphQL schema to OpenAPI using conversion tools

### GraphQL Schema Extraction

The GraphQL schema can be obtained through introspection:

**Methods:**
1. **Using get-graphql-schema CLI:**
   ```bash
   npx get-graphql-schema http://localhost:3000/graphql > schema.graphql
   ```

2. **Using gql-sdl:**
   ```bash
   npx gql-sdl http://localhost:3000/graphql
   ```

3. **Using Apollo CLI:**
   ```bash
   npx apollo client:download-schema --endpoint=localhost:3000/graphql schema.json
   ```

4. **Direct Introspection Query:** Execute GraphQL introspection queries against the `/graphql` endpoint

**Schema Location in Repository:**
`./js_modules/dagster-ui/packages/ui-core/src/graphql/schema.graphql`

### GraphQL to OpenAPI Conversion Tools

If you need an OpenAPI specification, you can convert the GraphQL schema using these tools:

1. **graphql-to-openapi** (by schwer)
   - GitHub: https://github.com/schwer/graphql-to-openapi
   - NPM: https://www.npmjs.com/package/graphql-to-openapi
   - Usage:
     ```bash
     npx graphql-to-openapi --yaml --schema schema.graphql --query query.graphql
     ```

2. **graph-to-openapi** (by ThoughtSpot)
   - GitHub: https://github.com/thoughtspot/graph-to-openapi
   - Usage:
     ```javascript
     import { getOpenAPISpec } from '@thoughtspot/gql-to-openapi';
     const { spec } = getOpenAPISpec({
       schema,
       info: {},
       basePath: '/api/v1',
     });
     ```

**Limitations:**
- GraphQL and REST APIs have different paradigms; conversion may not capture all GraphQL features
- GraphQL's type system and query flexibility don't map perfectly to REST/OpenAPI
- Generated specs may require manual adjustments

---

## API Capabilities Summary

### What Dagster's APIs Can Do

**Via GraphQL API:**
- Launch and terminate job executions
- Query run status and history
- Access job, op, and repository metadata
- Retrieve asset information
- Execute custom queries and mutations
- Access dependency graphs
- Retrieve configuration schemas

**Via External Assets REST API:**
- Report asset materializations from external systems
- Record asset check results
- Log asset observations with metadata
- Integrate external data pipelines with Dagster

**Via Python SDK:**
- Comprehensive programmatic access to all Dagster functionality
- Direct Python API without HTTP overhead
- Type-safe interactions with Dagster constructs

### What Dagster's APIs Are NOT Designed For

- Traditional REST-based CRUD operations
- OpenAPI-driven API client generation
- Swagger UI exploration
- REST API documentation standards

---

## Documentation Resources

### Official Dagster Documentation

- **Main API Reference:** https://docs.dagster.io/api
- **GraphQL API:** https://docs.dagster.io/api/graphql
- **GraphQL Python Client:** https://docs.dagster.io/concepts/webserver/graphql-client
- **External Assets REST API:** https://docs.dagster.io/api/rest-apis/external-assets-rest-api
- **External Assets Instance API:** https://docs.dagster.io/api/dagster/external-assets-instance-api
- **dg CLI API Reference:** https://docs.dagster.io/api/clis/dg-cli/dg-api
- **Dagster SDK:** https://docs.dagster.io/api/dagster
- **dagster-graphql Library:** https://docs.dagster.io/api/libraries/dagster-graphql
- **Connecting to APIs Guide:** https://docs.dagster.io/guides/build/external-resources/connecting-to-apis
- **Dagster Webserver:** https://docs.dagster.io/guides/operate/webserver

### Community Resources

- **API Tracker:** https://apitracker.io/a/dagster-io (mentions OpenAPI/Swagger specs but doesn't link to actual files)
- **GitHub Discussions:**
  - Execute pipeline by API endpoint: https://github.com/dagster-io/dagster/discussions/4301
  - Using DagsterGraphQLClient with Dagster Cloud: https://github.com/dagster-io/dagster/discussions/7772
  - Custom GraphQL queries: https://github.com/dagster-io/dagster/discussions/24061
  - Asynchronous REST API consumption: https://github.com/dagster-io/dagster/discussions/18401

### Third-Party Integrations

- **Cube.dev Integration:** https://cube.dev/docs/product/apis-integrations/orchestration-api/dagster
- **dlt + Dagster:** https://dlthub.com/blog/multi-asset-rest-api-pipelines

---

## Recommendations

### For Programmatic Access

1. **Use the GraphQL API** for comprehensive access to Dagster functionality
2. **Use the Python Client** (`dagster-graphql`) for type-safe Python integrations
3. **Use the External Assets REST API** for reporting events from external systems
4. **Use the Python SDK** directly for the most comprehensive and type-safe access

### For API Documentation

1. Explore the **GraphQL Playground** at `/graphql` for interactive API documentation
2. Use **GraphQL introspection** to discover available queries and mutations
3. Refer to the **official Dagster documentation** for detailed API guides
4. Review the **GraphQL schema file** in the repository for schema details

### If OpenAPI Specification is Required

1. **For External Assets REST API:**
   - Manually create an OpenAPI spec based on the documentation
   - Limited scope (3 endpoints) makes manual creation feasible

2. **For GraphQL API:**
   - Extract the GraphQL schema using introspection
   - Convert to OpenAPI using tools like `graphql-to-openapi` or `graph-to-openapi`
   - Be aware of conversion limitations and expect manual adjustments
   - Consider whether OpenAPI is the right tool for a GraphQL API

### Alternative Approaches

Instead of converting GraphQL to OpenAPI, consider:
- Using GraphQL-native tools and clients
- Leveraging GraphQL's built-in introspection and type system
- Using the Dagster Python SDK for programmatic access
- Embracing GraphQL's flexibility rather than forcing REST paradigms

---

## Conclusion

Dagster does not provide an official OpenAPI/Swagger specification. The platform is built around a **GraphQL-first API design** with a limited REST API for external asset integration. This architectural choice reflects Dagster's focus on:

- **Flexible querying** through GraphQL's query language
- **Type-safe interactions** via GraphQL's type system
- **Python-native development** through decorators and the Python SDK
- **Interactive exploration** via GraphQL Playground

While it's technically possible to extract the GraphQL schema and convert it to OpenAPI, this approach goes against Dagster's design philosophy and may result in a suboptimal developer experience. For best results, use Dagster's APIs as designed:

- **GraphQL API** for comprehensive programmatic access
- **Python SDK** for Python-native development
- **External Assets REST API** for lightweight external integrations

---

## Sources

- [Dagster API Reference](https://docs.dagster.io/api)
- [Dagster GraphQL API Documentation](https://docs.dagster.io/api/graphql)
- [External Assets REST API](https://docs.dagster.io/api/rest-apis/external-assets-rest-api)
- [Dagster GitHub Repository](https://github.com/dagster-io/dagster)
- [Dagster GraphQL Python Client](https://docs.dagster.io/concepts/webserver/graphql-client)
- [dagster-graphql Library](https://docs.dagster.io/api/libraries/dagster-graphql)
- [Dagster Webserver Documentation](https://docs.dagster.io/guides/operate/webserver)
- [Dagster API Tracker](https://apitracker.io/a/dagster-io)
- [GraphQL Introspection](https://graphql.org/learn/introspection/)
- [graphql-to-openapi Tool](https://github.com/schwer/graphql-to-openapi)
- [graph-to-openapi Tool](https://github.com/thoughtspot/graph-to-openapi)

---

## Additional Context

### API Tracker Reference

While API Tracker (https://apitracker.io/a/dagster-io) lists "OpenAPI/Swagger specs" as a feature for Dagster, the actual search through Dagster's documentation and GitHub repository did not reveal any published OpenAPI specification files. This listing may be inaccurate or may refer to the theoretical possibility of generating such specs rather than their actual availability.

### GraphQL Evolution Notice

The Dagster documentation explicitly states: "The GraphQL API is still evolving and is subject to breaking changes." Some portions of the API exist primarily for internal webserver use. Users should:
- Check release notes for breaking changes
- Pin to specific Dagster versions in production
- Test GraphQL integrations thoroughly during upgrades
- Use the Python SDK for more stable integrations

### Python-First Design Philosophy

Dagster's design philosophy emphasizes Python-native development patterns over API-first approaches. The platform encourages:
- Declaring data assets as Python functions using decorators (`@dg.asset`)
- Using Python types for configuration and validation
- Leveraging Python's ecosystem for data processing
- Direct SDK usage over HTTP API calls

This philosophy explains why OpenAPI specifications are not a priority for the Dagster project.


## Orchestration Patterns


> Source: `docs/data_engineering/dagster/dagster-orchestration.md`

# Dagster Orchestration for Semantic Knowledge Systems

## Executive Summary

This document details the implementation of Dagster as the orchestration layer for AI-native data pipelines, covering asset-based workflows, dynamic partitioning, sensor-driven automation, and integration with CocoIndex and Graphiti for semantic intelligence.

---

## 1. Design Philosophy: Functional Core, Imperative Shell

### 1.1 Separation of Concerns

The architecture rigorously separates business logic from I/O operations:

**Functional Core (Pure Logic):**
- Text cleaning and LaTeX normalization
- Entity extraction using linguistic patterns
- Data structuring into Pydantic objects
- Never connects to databases, APIs, or filesystems

**Imperative Shell (Dagster):**
- Manages sensors detecting new files
- Handles database connections
- Orchestrates API calls
- Controls state and execution schedules

```python
# Functional Core - Pure function
def parse_math_content(text: str) -> MathQuestion:
    """Pure function - no I/O, fully testable."""
    entities = extract_entities(text)
    latex = normalize_latex(text)
    return MathQuestion(entities=entities, latex=latex)

# Imperative Shell - Dagster handles I/O
@asset
def processed_questions(context, raw_documents):
    """Dagster asset - manages I/O and state."""
    for doc in raw_documents:
        result = parse_math_content(doc.text)  # Call pure function
        yield result
```

### 1.2 Asset-Based vs Task-Based Orchestration

| Paradigm | Focus | State Tracking | Schema Drift |
|----------|-------|----------------|--------------|
| **Task-Based (Airflow)** | "Run the script" | Exit codes only | Manual |
| **Asset-Based (Dagster)** | "Ensure data exists" | Data lineage | Automatic |

Dagster tracks **data assets**, not tasks:
- `raw_exam_pdf` → `extracted_markdown` → `semantic_chunks` → `vector_embeddings`
- Implicit dependency graph inferred from code
- Freshness policies replace cron schedules

---

## 2. Dynamic Partitioning for File Ingestion

### 2.1 The Dynamic Partitions Pattern

Static partitioning fails for educational data where files arrive irregularly. Dynamic partitioning allows runtime partition creation:

```python
from dagster import DynamicPartitionsDefinition, asset

# Define dynamic partition set (initially empty)
exam_paper_partitions = DynamicPartitionsDefinition(name="exam_papers")

@asset(partitions_def=exam_paper_partitions)
def raw_pdf_content(context):
    """Asset representing binary content of specific exam paper."""
    partition_key = context.partition_key
    file_path = resolve_path(partition_key)
    with open(file_path, "rb") as f:
        return f.read()

@asset(partitions_def=exam_paper_partitions)
def extracted_markdown(context, raw_pdf_content):
    """Marker extraction - depends on raw PDF."""
    return marker.process_pdf(raw_pdf_content)
```

**Benefits:**
- Each exam paper has discrete asset lineage
- Failure in "Math_Paper_2023" doesn't block "Math_Paper_2024"
- Granular debugging and backfilling

### 2.2 Sensor-Driven Automation

Sensors detect new files and register partitions automatically:

```python
from dagster import sensor, RunRequest

@sensor(job=process_exam_job)
def new_exam_sensor(context):
    """Poll directory for new PDFs, register partitions."""
    current_files = list_files_in_directory()
    existing_partitions = context.instance.get_dynamic_partitions("exam_papers")

    new_files = [f for f in current_files if f not in existing_partitions]

    if new_files:
        # Register new partitions in Dagster's state
        context.instance.add_dynamic_partitions("exam_papers", new_files)

        # Request run for each new file
        for filename in new_files:
            yield RunRequest(
                run_key=filename,
                partition_key=filename
            )
```

**Workflow:**
1. Sensor polls source directory
2. Diffs against existing partitions
3. Registers new partition keys
4. Yields `RunRequest` for each new file

---

## 3. Asset Graph Architecture

### 3.1 The Document Processing Pipeline

```
raw_pdf_file (Binary Input)
    ↓
extracted_markdown (Marker Processing)
    ↓
semantic_chunks (CocoIndex Splitting)
    ↓
vector_embeddings (Sentence Transformer)
    ↓
knowledge_graph_episodes (Graphiti Ingestion)
```

### 3.2 Implementation

```python
from dagster import asset, AssetIn
import marker
from cocoindex import SplitRecursively, SentenceTransformerEmbed

@asset(partitions_def=exam_paper_partitions)
def extracted_markdown(context, raw_pdf_content) -> str:
    """Convert PDF to LaTeX-preserving Markdown."""
    return marker.process_pdf(raw_pdf_content)

@asset(partitions_def=exam_paper_partitions)
def semantic_chunks(context, extracted_markdown) -> list[str]:
    """Split Markdown into syntax-aware chunks."""
    return SplitRecursively(
        extracted_markdown,
        language="markdown",
        chunk_size=2000,
        chunk_overlap=500
    )

@asset(partitions_def=exam_paper_partitions)
def vector_embeddings(context, semantic_chunks) -> list[dict]:
    """Generate embeddings for each chunk."""
    embedder = SentenceTransformerEmbed(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    return [
        {"text": chunk, "embedding": embedder(chunk)}
        for chunk in semantic_chunks
    ]

@asset(partitions_def=exam_paper_partitions)
def knowledge_graph_episodes(context, extracted_markdown):
    """Ingest into Graphiti temporal graph."""
    from graphiti_core import Graphiti, EpisodeType

    client = Graphiti("falkor://localhost:6379")
    await client.add_episode(
        name=f"exam_{context.partition_key}",
        episode_body=extracted_markdown,
        source=EpisodeType.text,
        reference_time=extract_exam_date(context.partition_key),
        entity_types=[MathTheorem, ExamTopic]
    )
```

### 3.3 Memoization Benefits

When changing only the embedding model:
- `raw_pdf_content` - NOT recomputed
- `extracted_markdown` - NOT recomputed
- `semantic_chunks` - NOT recomputed
- `vector_embeddings` - RECOMPUTED (logic changed)
- `knowledge_graph_episodes` - NOT recomputed (independent)

---

## 4. Asset Factory Pattern for Metadata-Driven Pipelines

### 4.1 Dynamic Asset Generation

For pipelines with many sources (100+ scraping targets), generate assets programmatically:

```python
from dagster import Definitions, asset

def load_sources_from_duckdb() -> list[dict]:
    """Query DuckDB for active source configurations."""
    import duckdb
    conn = duckdb.connect("metadata.db")
    return conn.execute("""
        SELECT source_id, name, tool_driver, connection_spec, extraction_strategy
        FROM sources
        JOIN ingestion_configs USING (source_id)
        WHERE active = true
    """).fetchall()

def build_crawl_asset(config: dict):
    """Factory function to create crawler asset."""
    @asset(name=f"crawl_{config['name']}")
    def _crawl_asset(context):
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

        run_config = CrawlerRunConfig(**config['extraction_strategy'])
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=config['connection_spec']['url'],
                config=run_config
            )
        return result.markdown

    return _crawl_asset

# Generate assets at load time
sources = load_sources_from_duckdb()
generated_assets = [
    build_crawl_asset(s) for s in sources
    if s['tool_driver'] == 'crawl4ai'
]

defs = Definitions(assets=generated_assets)
```

### 4.2 Scaling with Generic Partitioned Assets

For thousands of sources, use a single partitioned asset instead:

```python
from dagster import DynamicPartitionsDefinition, asset, sensor

source_partitions = DynamicPartitionsDefinition(name="data_sources")

@asset(partitions_def=source_partitions)
def generic_crawler_job(context):
    """Single asset handles all crawling via partition key."""
    source_id = context.partition_key

    # Fetch config for this specific source
    config = fetch_config_from_duckdb(source_id)

    # Execute crawl with config
    result = execute_crawl(config)
    return result

@sensor(job=crawl_job)
def source_registry_sensor(context):
    """Monitor DuckDB for new sources."""
    active_sources = get_active_source_ids()
    existing = context.instance.get_dynamic_partitions("data_sources")

    new_sources = set(active_sources) - set(existing)
    if new_sources:
        context.instance.add_dynamic_partitions("data_sources", list(new_sources))
        for source_id in new_sources:
            yield RunRequest(partition_key=source_id)
```

---

## 5. CocoIndex Integration

### 5.1 Library vs Service Pattern

CocoIndex can run as a service with internal orchestration, but running "orchestrator within orchestrator" creates complexity. **Use CocoIndex as a library within Dagster assets.**

### 5.2 Semantic Chunking

CocoIndex's `SplitRecursively` uses Tree-sitter for syntax-aware splitting:

```python
@asset
def semantic_chunks(extracted_markdown: str) -> list[str]:
    """Syntax-aware chunking preserves LaTeX equations."""
    import cocoindex

    return cocoindex.SplitRecursively(
        text=extracted_markdown,
        language="markdown",  # Tree-sitter parser
        chunk_size=2000,
        chunk_overlap=500
    )
```

**Why Tree-sitter matters:**
- Recognizes code blocks (LaTeX `$$...$$`) as atomic units
- Respects header boundaries (`# Question 1`)
- Produces semantically coherent chunks

### 5.3 Hybrid Embedding Strategy

```python
@cocoindex.transform_flow()
def text_to_embedding(text: cocoindex.DataSlice[str]):
    """Reusable transform for indexing AND querying."""
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
    )

@asset
def vector_index(semantic_chunks: list[str]):
    """Build vector index with hybrid strategy."""
    import cocoindex

    # Textual embedding
    embeddings = [text_to_embedding(chunk) for chunk in chunks]

    # Preserve raw LaTeX as metadata
    records = [
        {"text": chunk, "embedding": emb, "latex": extract_latex(chunk)}
        for chunk, emb in zip(chunks, embeddings)
    ]

    cocoindex.collect(records, "research_vectors")
```

---

## 6. Graphiti Integration

### 6.1 Temporal Knowledge Graph

Graphiti enables bi-temporal queries:
- **Valid Time:** When the fact was true (exam date)
- **Transaction Time:** When fact was recorded

```python
@asset(partitions_def=exam_paper_partitions)
def temporal_knowledge_graph(context, extracted_markdown):
    """Ingest exam data with temporal context."""
    from graphiti_core import Graphiti, EpisodeType
    from pydantic import BaseModel, Field

    # Define ontology
    class MathTheorem(BaseModel):
        name: str = Field(description="Theorem name, e.g., Pythagoras")
        latex_def: str = Field(description="LaTeX definition")

    class ExamTopic(BaseModel):
        name: str = Field(description="Curriculum topic")
        code: str = Field(description="Curriculum code, e.g., C1.2")

    client = Graphiti("falkor://localhost:6379")

    await client.add_episode(
        name=f"exam_{context.partition_key}",
        episode_body=extracted_markdown,
        source=EpisodeType.text,
        reference_time=parse_exam_date(context.partition_key),
        entity_types=[MathTheorem, ExamTopic]  # Constrain extraction
    )
```

### 6.2 Entity Resolution

Graphiti performs LLM-based entity resolution:
- "Question 1" in Exam Paper links to "Question 1" in Marking Scheme
- "Maths" and "Mathematics" merge into single entity

### 6.3 Hybrid Search

```python
def search_knowledge_graph(query: str):
    """Combine semantic, keyword, and graph traversal."""
    client = Graphiti("falkor://localhost:6379")

    results = await client.search(
        query=query,
        search_type="hybrid",  # Semantic + BM25 + Graph
        limit=10
    )

    return results
```

---

## 7. Operational Patterns

### 7.1 Asset Checks

```python
from dagster import asset_check, AssetCheckResult

@asset_check(asset=extracted_markdown)
def latex_density_check(context, extracted_markdown):
    """Verify PDF extraction produced LaTeX."""
    latex_count = extracted_markdown.count("$$")
    density = latex_count / len(extracted_markdown)

    return AssetCheckResult(
        passed=density > 0.01,
        metadata={"latex_density": density}
    )
```

### 7.2 Retry Policies

```python
from dagster import RetryPolicy

@asset(
    partitions_def=exam_paper_partitions,
    retry_policy=RetryPolicy(max_retries=3, delay=30)
)
def extracted_markdown(raw_pdf_content):
    """Retry on transient failures."""
    return marker.process_pdf(raw_pdf_content)
```

### 7.3 Resource Configuration

```python
from dagster import resource, Definitions

@resource
def graphiti_resource(context):
    """Configurable Graphiti connection."""
    return Graphiti(context.resource_config["uri"])

defs = Definitions(
    assets=[...],
    resources={
        "graphiti": graphiti_resource.configured({
            "uri": "falkor://localhost:6379"
        })
    }
)
```

---

## 8. Deployment Architecture

### 8.1 Dockerized Stack

```yaml
services:
  dagster-daemon:
    image: dagster/dagster:latest
    command: dagster-daemon run

  dagster-webserver:
    image: dagster/dagster:latest
    command: dagster-webserver -h 0.0.0.0 -p 3000

  postgres:
    image: postgres:15
    # Shared storage for Dagster metadata + CocoIndex vectors

  falkordb:
    image: falkordb/falkordb:latest
    # Graph storage for Graphiti

  gpu-worker:
    image: custom/extraction-worker
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 8.2 Database Independence

- **Graphiti:** Swap Neo4j/FalkorDB via connection URI
- **CocoIndex:** Uses PostgreSQL + pgvector (vendor-neutral)
- **Marker:** Local GPU inference (no API dependency)

---

## 9. Implementation Priorities

### Phase 1: Core Pipeline
1. Implement Marker extraction asset
2. Add dynamic partitioning for file ingestion
3. Configure sensor for new file detection

### Phase 2: Semantic Intelligence
1. Integrate CocoIndex for syntax-aware chunking
2. Build vector embedding pipeline
3. Add hybrid embedding strategy

### Phase 3: Knowledge Graph
1. Deploy Graphiti with FalkorDB
2. Define domain ontology (Pydantic models)
3. Implement temporal episode ingestion

### Phase 4: Operational Maturity
1. Add asset checks for data quality
2. Configure retry policies
3. Implement monitoring/alerting

---

## References

- Dagster Partitioning: https://docs.dagster.io/guides/build/partitions-and-backfills
- Dagster Sensors: https://docs.dagster.io/guides/automate/sensors
- CocoIndex: https://cocoindex.io/docs/
- Graphiti: https://help.getzep.com/graphiti/
- Marker PDF: https://github.com/VikParuchuri/marker


> Source: `docs/data_engineering/dagster/Dagster Orchestration for Cocoindex, Graphiti.md`

# **Architectural Blueprint for Mathematical Knowledge Extraction: A Modular Orchestration Strategy Using Dagster, Cocoindex, and Graphiti**

## **1\. Introduction: The Imperative for Semantic Intelligence in Educational Assessment**

The digitalization of educational assessment creates a profound data engineering challenge: the conversion of unstructured, mathematically dense artifacts—exam papers, marking schemes, and curriculum standards—into a structured, queryable knowledge base. This transformation is not merely a matter of optical character recognition (OCR); it is a semantic reconstruction task that requires preserving the rigorous logical structure of mathematical notation, the hierarchical nature of curriculum standards, and the temporal evolution of assessment criteria.  
This report outlines a comprehensive architectural strategy for building a high-fidelity data pipeline capable of synthesizing these disparate artifacts. The core objective is to establish an intelligence layer that supports advanced retrieval, automated reasoning, and longitudinal analysis of educational performance without incurring the technical debt of monolithic systems or the risks of proprietary vendor lock-in.  
The proposed architecture is founded on three pillars of modern data engineering:

1. **Asset-Based Orchestration via Dagster:** Shifting the paradigm from imperative task execution to declarative data management, ensuring that the state of every exam paper and curriculum document is observable, reproducible, and verifiable.1  
2. **Incremental Vector Indexing via Cocoindex:** Leveraging a high-velocity, flow-based transformation engine to generate semantic embeddings for mathematical content, enabling "find questions like this" capabilities that transcend simple keyword matching.2  
3. **Temporal Knowledge Graphing via Graphiti:** Constructing a dynamic graph of entities (Theorems, Topics, Questions) that respects the dimension of time, allowing the system to reason about how curriculum standards and assessment rigor evolve over years.4

By decoupling the extraction logic—specifically utilizing open-source tools like **Marker** to handle the nuances of LaTeX and mathematical typography—from the storage and indexing layers, organizations can achieve a robust system. This report provides an exhaustive analysis of the design decisions, implementation strategies, and theoretical underpinnings required to execute this vision.

## ---

**2\. Theoretical Framework and Design Philosophy**

The complexity of mathematical content, combined with the stringent requirements for accuracy in an educational context, necessitates a departure from traditional "script-based" ETL (Extract, Transform, Load) pipelines. Instead, we adopt a software engineering approach applied to data: the "Functional Core, Imperative Shell" pattern, orchestrated within a Software-Defined Asset framework.

### **2.1 The "Functional Core, Imperative Shell" Pattern in Data Pipelines**

To ensure modularity and testability—key requirements for avoiding vendor lock-in—the architecture rigorously separates business logic from I/O operations.

#### **2.1.1 The Functional Core: Pure Mathematical Logic**

The "Functional Core" consists of pure, deterministic functions that contain the domain logic.6 In the context of this pipeline, the core is responsible for:

* **Text Cleaning:** Identifying and normalizing LaTeX strings (e.g., standardizing \\frac{a}{b} vs a \\over b).  
* **Entity Extraction:** Parsing a raw text block to identify potential "Theorem" or "Definition" entities based on linguistic patterns, without yet calling an external database.  
* **Data Structuring:** Transforming unstructured Markdown into Pydantic objects that conform to the system's ontology.

Crucially, code in the functional core never connects to a database, never calls an external API, and never reads from a file system. It takes data as input and returns data as output. This isolation means that if the vector database (Cocoindex) or the graph database (Graphiti) changes, the core logic of how a mathematical question is parsed remains untouched.8

#### **2.1.2 The Imperative Shell: Dagster as the Nervous System**

The "Imperative Shell" is responsible for the side effects: reading files, sending data to APIs, and managing state. **Dagster** serves as this shell. It manages the sensors that detect new exam papers, handles the connections to the Postgres database for Cocoindex, and orchestrates the API calls to the Graphiti backend.9 By treating Dagster as the shell, we ensure that the orchestration logic focuses on *when* and *where* to run computations, while the core python modules focus on *how* to process the mathematics.

### **2.2 Asset-Based Orchestration vs. Task-Based Workflows**

Traditional orchestrators (like Airflow) focus on *tasks*: "Run the extraction script." If the script succeeds, the task is green. However, this says nothing about the quality or freshness of the data produced.  
Dagster's **Asset-Based Orchestration** inverts this relationship. We define the *data assets* we expect to exist: the raw\_exam\_pdf, the extracted\_markdown, the semantic\_embeddings, and the knowledge\_graph\_nodes.1

* **Implicit Lineage:** Dagster automatically infers the dependency graph. If the extracted\_markdown asset depends on the raw\_exam\_pdf asset, Dagster knows that an update to the PDF necessitates a re-computation of the Markdown.  
* **Declarative Freshness:** Instead of scheduling a job at 3 AM, we define a freshness policy. The system constantly checks: "Is the vector index up to date with the latest exam papers?" If not, it triggers the necessary materializations.  
* **Partitioned State:** Educational data is naturally partitioned—by academic year, subject code, or exam board. Dagster’s native support for partitioning allows the pipeline to process a single exam paper (a partition) completely independently. This is critical for scalability; a failure in processing "Math Paper 2023" should not block the processing of "Math Paper 2024".10

### **2.3 Strategy for Avoiding Vendor Lock-In**

A core requirement of this research is modularity to prevent vendor lock-in. This is achieved through three strategic architectural decisions:

1. **Open Source Extraction Engines:** We reject proprietary extraction APIs (like Mathpix or Azure Document Intelligence) in favor of local, open-source models like **Marker**.11 This ensures that the capability to read the primary data source (PDFs) is owned by the organization, not rented.  
2. **Standardized Intermediate Formats:** The pipeline relies on universally readable formats for data interchange. Text is stored as Markdown with embedded LaTeX; structured data is passed as JSON. This prevents data from being trapped in a binary blob or a vendor-specific serialization format.  
3. **Abstraction via Pydantic:** Interactions with the knowledge graph are mediated through Pydantic models.13 We define a MathQuestion class in Python. Whether this object is eventually stored in Neo4j, FalkorDB, or a future graph database is an implementation detail handled by the connector layer, not the core logic.

## ---

**3\. The Data Plane: High-Fidelity Mathematical Extraction**

The foundation of the entire pipeline is the accurate extraction of content from PDF documents. In the domain of mathematics, this is non-trivial. Mathematical knowledge is encoded not just in alphanumeric text, but in spatial layout, specific distinct symbology, and two-dimensional structures (matrices, fractions, integrals).

### **3.1 The Challenge of Mathematical Typography**

A standard OCR tool might scan the equation $x \= \\frac{-b \\pm \\sqrt{b^2 \- 4ac}}{2a}$ and output "x \= \-b \+ Vb2 \- 4ac 2a", completely destroying the semantic meaning. The fraction bar, the square root scope, and the superscript are structural, not just textual.  
To build a "Mathematical Context," the extraction layer must recognize these visual cues and translate them into a semantic markup language, predominantly **LaTeX**. LaTeX allows the equation to be represented as x \= \\frac{-b \\pm \\sqrt{b^2 \- 4ac}}{2a}, a string that preserves the hierarchical relationships of the terms.

### **3.2 Comparative Analysis of Extraction Tools**

Deep research into the Python PDF ecosystem reveals a clear stratification of tools based on their ability to handle scientific notation.

| Tool | Primary Focus | Mathematical Fidelity | Performance (Speed) | License / Open Source | Verdict |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **PyPDF / PyPDF2** | PDF Manipulation (Split/Merge) | **None.** Extracts text stream only; destroys layout and formulas.14 | High | BSD (Open) | **Unsuitable.** |
| **PyMuPDF (Fitz)** | Rendering & Text Extraction | **Low.** Excellent for layout analysis (bounding boxes), but poor at formula recognition.14 | Very High | GNU GPL / Commercial | **Helper Only.** Use for metadata. |
| **Nougat** (Meta) | Academic/Scientific Papers | **High.** Transformer-based; converts PDF image directly to Markdown/LaTeX.15 | Low (Slow) | MIT (Open) | **Viable but Slow.** Good fallback. |
| **Mathpix** | STEM Content | **Very High.** Industry standard for math OCR. | High | Proprietary (API) | **Rejected.** Creates vendor lock-in.16 |
| **Marker** | Scientific Books/Papers | **High.** Deep learning pipeline for layout \+ OCR \+ LaTeX conversion.11 | High (\~10x Nougat) | GPL-3.0 (Open) | **Recommended.** Best balance. |

#### **3.2.1 Deep Dive: The Marker Advantage**

**Marker** represents the state-of-the-art for open-source scientific PDF extraction. Unlike **Nougat**, which uses a heavy end-to-end transformer model that can be slow and computationally expensive, Marker employs a pipeline approach:

1. **Layout Detection:** It first segments the page into text blocks, equations, tables, and images using object detection.  
2. **Selective OCR:** It applies OCR only to the text blocks.  
3. **Formula Recognition:** It uses a specialized model (often related to Nougat's architecture but optimized) specifically on the detected equation regions to generate LaTeX.12  
4. **Heuristics:** It applies post-processing heuristics to clean up headers, footers, and page numbers—artifacts that are notoriously problematic in exam papers.

Benchmarks indicate Marker is significantly faster (4x to 10x) than Nougat while maintaining comparable accuracy for mathematical content.11 This speed is critical when backfilling a decade's worth of exam papers. Furthermore, Marker natively outputs **Markdown**, which is the ideal input format for semantic chunking strategies (discussed in Section 5).

### **3.3 Handling Curriculum and Marking Schemes**

While exam papers are dense with equations, **Curriculum Standards** and **Marking Schemes** present different structural challenges.

* **Curriculum Documents:** These are deeply hierarchical. A specific learning objective (e.g., "Calculus \-\> Differentiation \-\> Chain Rule") is defined by its nesting depth. Marker's ability to output structured Markdown (using \#, \#\#, \#\#\# headers) allows the functional core to parse this hierarchy directly, reconstructing the tree structure of the curriculum.12  
* **Marking Schemes:** These are predominantly tabular. A row might contain "Question 1(a) | Answer: 5 | 2 Marks". Standard OCR often breaks tables into independent lines of text. Marker includes specific table recognition capabilities to output Markdown tables. However, for extremely complex, multi-page tables found in some marking schemes, the architecture allows for a "Strategy Pattern" in the extraction asset: if Marker's confidence is low, the system can fall back to a specialized table extraction library like gmft (Grid-Based PDF Table Extraction) or Table Transformer 15, wrapping this logic within the Dagster asset to maintain abstraction.

## ---

**4\. Orchestration Architecture: The Dagster Implementation**

Dagster is selected not merely as a task runner, but as a system for **Software-Defined Assets**. This section details how to implement the orchestration layer to handle the dynamic nature of file ingestion.

### **4.1 Dynamic Partitioning for File Ingestion**

In an educational data pipeline, the input dataset is never static. New exam papers are scanned, marking schemes are updated, and new curriculum documents are released. A static partitioning scheme (e.g., partitioning by "Day") is inefficient because files may arrive in irregular batches.  
We utilize **Dynamic Partitioning**, a powerful Dagster feature that allows the set of partitions (processing units) to be defined and grown at runtime.10  
We define a DynamicPartitionsDefinition named exam\_papers. The partition key will be the unique identifier of the file (e.g., the filename or a hash of the content).

Python

\# Conceptual Architecture for Dynamic Partitions  
from dagster import DynamicPartitionsDefinition, asset

\# Define the dynamic partition set.   
\# Initially empty, this will be populated by a Sensor.  
exam\_paper\_partitions \= DynamicPartitionsDefinition(name="exam\_papers")

@asset(partitions\_def=exam\_paper\_partitions)  
def raw\_pdf\_content(context):  
    """  
    Asset representing the binary content of a specific exam paper.  
    The partition\_key from the context determines which file to load.  
    """  
    partition\_key \= context.partition\_key  
    \# The imperative shell logic to read from the filesystem  
    file\_path \= resolve\_path(partition\_key)  
    with open(file\_path, "rb") as f:  
        return f.read()

This approach creates a discrete asset lineage for *every single exam paper*. If "Math\_Paper\_2023.pdf" fails to process due to a corrupted table, it appears as a failure for that specific partition. It does not block the pipeline for "Math\_Paper\_2024.pdf". This granularity is essential for debugging and backfilling.18

### **4.2 Event-Driven Architecture with Sensors**

To automate the population of these dynamic partitions, we employ **Dagster Sensors**.19 A sensor is a daemon that runs continuously, polling an external state (a local directory, an S3 bucket, or a Google Drive folder) to detect changes.  
The workflow for the new\_file\_sensor is as follows:

1. **Poll:** Check the source directory for PDF files.  
2. **Diff:** Compare the list of found files against the list of existing partitions in exam\_paper\_partitions.  
3. **Register:** For every new file found, explicitly add a new partition key to the exam\_paper\_partitions definition using context.instance.add\_dynamic\_partitions.20  
4. **Trigger:** Yield a RunRequest for the pipeline, specifically targeting the newly created partition key.

This ensures the pipeline is reactive. As soon as a file is dropped into the folder, the sensor wakes up, registers the new asset partition, and launches the processing job.

Python

@sensor(job=process\_exam\_job)  
def new\_exam\_sensor(context):  
    \# Imperative Shell: Interacting with the filesystem  
    current\_files \= list\_files\_in\_directory()  
      
    \# Check which partitions already exist  
    existing\_partitions \= context.instance.get\_dynamic\_partitions("exam\_papers")  
      
    new\_files \= \[f for f in current\_files if f not in existing\_partitions\]  
      
    if new\_files:  
        \# Register the new partitions in Dagster's state  
        context.instance.add\_dynamic\_partitions("exam\_papers", new\_files)  
          
        \# Request a run for each new file  
        for filename in new\_files:  
            yield RunRequest(  
                run\_key=filename, \# Idempotency key  
                partition\_key=filename \# The specific partition to materialize  
            )

### **4.3 The Asset Graph: Lineage and Dependencies**

The architecture visualizes the data flow as a graph of connected assets. This provides immediate observability into the state of the system.

1. **raw\_pdf\_file**: The binary input (Partitioned by filename).  
2. **extracted\_markdown**: The output of the **Marker** process. This asset depends on raw\_pdf\_file. Its computation involves running the Marker library on the binary input. The output is a .md string containing text and LaTeX equations.  
3. **semantic\_chunks**: A derived asset that splits the Markdown into semantic units (e.g., individual questions). This utilizes Cocoindex's splitting logic.  
4. **vector\_embeddings**: The numerical representation of the chunks, generated by Cocoindex.  
5. **knowledge\_graph\_episodes**: The structured entities and relationships extracted from the text, prepared for Graphiti ingestion.

By structuring the pipeline this way, we gain **Memoization**. If we change the embedding model (modifying the logic for vector\_embeddings), Dagster knows it does not need to re-run the expensive PDF-to-Markdown extraction (extracted\_markdown) because that asset has not changed. It only re-runs the downstream assets.

## ---

**5\. The Semantic Layer: Cocoindex Integration**

**Cocoindex** is chosen for the semantic layer because it is designed specifically as an *incremental* indexing framework, rather than just a passive vector database.2 It understands the concept of a "flow" of data.

### **5.1 Architecture: Library vs. Service Pattern**

Cocoindex usually operates as a standalone service with its own internal orchestration (cocoindex server). However, running "an orchestrator within an orchestrator" (Cocoindex inside Dagster) creates operational complexity and split-brain issues regarding state management.  
**Design Decision:** We will utilize Cocoindex primarily as a **Functional Library** within the Dagster assets.21 We will leverage its powerful Python API—specifically its text splitting and embedding functions—while letting Dagster manage the state and execution schedule.

### **5.2 Semantic Chunking with SplitRecursively**

Standard text splitters (like those in LangChain) often split by character count, which is disastrous for mathematics. Splitting a LaTeX equation $$\\int\_{a}^{b} f(x) dx$$ in the middle renders both halves semantically meaningless.  
Cocoindex provides a superior solution: SplitRecursively. This function leverages **Tree-sitter**, a parser generator that builds a concrete syntax tree for the source text.23

* We configure SplitRecursively with language="markdown".  
* Since the **Marker** extraction step produces valid Markdown, Tree-sitter understands the structure. It recognizes that a Code Block (which Marker uses for LaTeX blocks like $$...$$) is an atomic unit.  
* It respects header boundaries (\# Question 1), ensuring that a question and its sub-parts tend to stay together.

This "syntax-aware" chunking is vital for the mathematical context. It ensures that the vector embeddings generated in the next step represent coherent mathematical thoughts, not arbitrary text fragments.

### **5.3 Hybrid Embedding Strategy**

Embedding mathematical content is challenging because standard NLP models (like all-MiniLM-L6-v2) treat LaTeX variables ($x$, $y$, $\\alpha$) as generic tokens. They often fail to capture the *structural* similarity between $a^2+b^2=c^2$ and $x^2+y^2=z^2$.  
To mitigate this, the pipeline employs a **Hybrid Embedding Strategy** within the Cocoindex transform flow:

1. **Textual Embedding:** We use SentenceTransformerEmbed for the natural language component of the question (e.g., "Calculate the derivative of...").  
2. **Symbolic Preservation:** We do not rely solely on the vector for the math. The raw LaTeX string is preserved as metadata fields in the Cocoindex collect step.  
3. **Transform Flow:** We define a reusable @cocoindex.transform\_flow function that encapsulates this logic. This same function is used during *indexing* (to build the vector store) and during *querying* (to embed the user's search query), ensuring strictly consistent embedding geometry.22

Python

\# Reusable Transform Flow for Indexing AND Querying   
@cocoindex.transform\_flow()  
def text\_to\_embedding(text: cocoindex.DataSlice\[str\]):  
    return text.transform(  
        cocoindex.functions.SentenceTransformerEmbed(  
            model="sentence-transformers/all-MiniLM-L6-v2"  
        )  
    )

### **5.4 Incremental Updates via Custom Sources**

While we use Dagster for coarse-grained orchestration, Cocoindex shines at fine-grained incrementalism. If we process a "Marking Scheme" file that is 50 pages long, and only page 4 is corrected in a new version, we do not want to re-embed the other 49 pages.  
We can bridge this by using Cocoindex's **Postgres Source** or a **Custom Source**.25 The Dagster asset can write the extracted Markdown into a Postgres table (the "Staging Area"). Cocoindex is then configured to read from this table. Because Cocoindex tracks the modified\_time or offsets of the source data, it will automatically detect that only the row corresponding to "Page 4" has changed, and it will only re-compute the embeddings for that specific row. This hybrid approach uses Dagster for the macro-pipeline and Cocoindex for the micro-optimization of embedding costs.

## ---

**6\. The Knowledge Layer: Temporal Graph Construction with Graphiti**

While Cocoindex allows us to find *similar* questions, **Graphiti** allows us to find *related* concepts. It builds a structured Knowledge Graph (KG) that allows for reasoning. Graphiti is explicitly designed for **Temporal Knowledge Graphs**, making it the perfect tool for tracking how educational standards evolve over time.4

### **6.1 The "Episode" Abstraction**

Graphiti ingests data as "Episodes"—discrete events or documents.26 In our architecture, we map these to our domain artifacts:

* **Episode:** A single Exam Paper or Marking Scheme.  
* **Time:** The reference\_time of the episode is set to the exam date (e.g., "2023-06-15").

This temporal tagging is the key differentiator. It allows the system to construct a "Bi-Temporal" graph 27:

1. **Transaction Time:** When the data was added to the database.  
2. **Valid Time:** The real-world time the fact was true (the exam date).

This enables **Time Travel Queries**: *"Retrieve the definition of 'Matrix Multiplication' as it appeared in the 2015 curriculum versus the 2024 curriculum."* The graph will likely contain distinct nodes or evolving edges linked to these specific time windows, allowing the AI agent to discern the shift in pedagogical standards.

### **6.2 Ontology Engineering with Pydantic**

To prevent the graph from becoming a "soup" of disconnected nodes, we must enforce a schema. Graphiti allows the definition of custom entity and edge types using standard Python **Pydantic** models.13 This is how we inject domain expertise into the pipeline.  
We define a rigorous ontology for the mathematical domain:

Python

from pydantic import BaseModel, Field

\# Define Custom Entities  
class MathTheorem(BaseModel):  
    name: str \= Field(description="Name of the theorem, e.g., Pythagoras Theorem")  
    latex\_def: str \= Field(description="The mathematical definition in LaTeX")

class ExamTopic(BaseModel):  
    name: str \= Field(description="The curriculum topic, e.g., Differentiation")  
    code: str \= Field(description="The curriculum code, e.g., C1.2")

\# Define Graphiti Ingestion Logic  
await graphiti.add\_episode(  
    name="Math\_Paper\_2023",  
    episode\_body=extracted\_text,   
    source=EpisodeType.text,  
    reference\_time=exam\_date,  
    \# Enforce the ontology   
    entity\_types=   
)

By passing these models to add\_episode, we constrain the underlying LLM (which Graphiti uses for extraction) to look specifically for Theorems and Topics, ensuring high-quality, structured nodes.

### **6.3 Entity Resolution and Ground Truth**

A critical challenge is connecting the "Question" in the exam paper to the "Answer" in the marking scheme. These are separate documents.

* **Strategy:** We treat them as separate episodes.  
* **Resolution:** Graphiti employs LLM-based **Entity Resolution**.29 When it processes "Question 1" in the Marking Scheme, the LLM analyzes the context and recognizes it refers to the same entity as "Question 1" in the previously ingested Exam Paper episode. It merges or links these nodes.  
* **Enhancement:** We can explicitly model an edge type HAS\_ANSWER in our ontology. If the entity resolution is imperfect, we can implement a "Functional Core" post-processing step in Dagster that queries the graph for orphaned "Answers" and heuristically links them to "Questions" based on their ID (e.g., "Q1(a)") and temporal proximity.

### **6.4 Hybrid Retrieval Strategy**

For the end-user application (e.g., a "Math Tutor" bot), we utilize Graphiti's **Hybrid Search**.30 This combines:

1. **Semantic Search:** Using vectors to find conceptually similar nodes.  
2. **Keyword Search (BM25):** Essential for finding specific terms like "Eigenvector".  
3. **Graph Traversal:** Moving from a "Topic" node to all linked "Question" nodes.

This triangulation allows for complex queries: *"Find all geometry questions (Semantic) that involve 'circles' (Keyword) and appeared in exams linked to the '2023 Syllabus' (Graph Traversal)."*

## ---

**7\. Integrated Pipeline Data Flow**

The following describes the end-to-end flow of a single exam paper through the system.

### **7.1 Ingestion Phase**

1. **Sensor Activation:** The new\_exam\_sensor detects Math\_Exam\_2024.pdf in the monitored directory.  
2. **Partition Creation:** The sensor calls context.instance.add\_dynamic\_partitions to register "Math\_Exam\_2024".  
3. **Run Launch:** A RunRequest triggers the asset pipeline for this partition.

### **7.2 Extraction Phase (Asset: extracted\_markdown)**

1. **Execution:** The asset function executes. It retrieves the file path.  
2. **Functional Core Call:** It calls the extract\_math\_content(path) function.  
3. **Marker Pipeline:** Inside this function, the **Marker** library processes the PDF. It detects the layout, OCRs the text, converts formulas to LaTeX, and cleans headers/footers.  
4. **Materialization:** The resulting Markdown string is saved to object storage (S3/MinIO), and metadata (e.g., "LaTeX Equation Count: 45") is returned to Dagster.

### **7.3 Indexing Phase (Asset: vector\_index)**

1. **Input:** Reads the extracted\_markdown.  
2. **Chunking:** Calls Cocoindex.SplitRecursively to break the text into syntax-aware chunks.  
3. **Embedding:** Calls the text\_to\_embedding transform flow to generate vectors.  
4. **Storage:** Writes vectors and metadata to the Postgres vector store (via Cocoindex collector.export).

### **7.4 Knowledge Graph Phase (Asset: graph\_nodes)**

1. **Input:** Reads extracted\_markdown and metadata (Date).  
2. **Ontology Loading:** Loads the MathTheorem and ExamTopic Pydantic models.  
3. **Graphiti Ingestion:** Calls graphiti.add\_episode. The LLM extracts entities conforming to the Pydantic models.  
4. **Temporal Tagging:** The reference\_time is set to the exam date, placing the knowledge in the correct historical context.  
5. **Persistence:** Data is committed to the underlying graph database (Neo4j or FalkorDB).

## ---

**8\. Operational Strategy and Scalability**

### **8.1 Dockerized Deployment**

To ensure reproducibility and modularity, the entire stack should be deployed via Docker Compose or Kubernetes.

* **Service 1: Dagster Daemon & Webserver.**  
* **Service 2: Postgres** (Shared storage for Dagster metadata and Cocoindex vector store).  
* **Service 3: Neo4j / FalkorDB** (Storage for Graphiti).  
* **Service 4: GPU Worker.** The extraction (Marker) and embedding (Cocoindex) steps are compute-intensive. Dagster allows defining **Op Executors**. We can tag the extraction assets to run specifically on a worker node equipped with a GPU (e.g., NVIDIA A10G) to speed up the deep learning inference, while the sensor and graph logic run on a lightweight CPU node.

### **8.2 Database Independence**

The requirement to avoid vendor lock-in is satisfied at the storage layer:

* **Graphiti:** Abstracted via the Graphiti class. Swapping the backend from FalkorDB to Neo4j is a configuration change (changing the connection URI), not a code change.32  
* **Cocoindex:** Uses Postgres (with pgvector) as its default storage. Postgres is open-source, ubiquitous, and vendor-neutral.

### **8.3 Observability and Error Handling**

Dagster provides the operational "pane of glass."

* **Asset Checks:** We define data quality checks on the extracted\_markdown asset. Check: latex\_density \> 0.05. If a PDF yields no LaTeX, the check fails, alerting the engineer that the extraction likely failed (perhaps the PDF was a scanned image with no OCR text layer).  
* **Retry Policies:** Mathematical PDFs can be weird. We configure RetryPolicy(max\_retries=3) on the extraction asset to handle transient memory issues or LLM timeouts during graph extraction.

## **9\. Conclusion**

This architecture represents a rigorous, enterprise-grade approach to a complex unstructured data problem. By combining **Dagster's** robust state management with **Cocoindex's** incremental vectorization and **Graphiti's** temporal reasoning, we create a system that does more than just "read" exam papers—it "understands" them in the context of time and curriculum.  
The use of **Marker** ensures that the unique language of mathematics (LaTeX) is preserved, avoiding the semantic degradation common in generic OCR pipelines. The modular design, anchored by the "Functional Core" pattern and open standards (Markdown, JSON, Pydantic, Postgres), ensures that the organization owns its intelligence, free from proprietary API shackles. This is not just a search engine; it is a longitudinal analytical engine for educational data.

## **10\. Future Outlook & Recommendations**

* **Multimodal Expansion:** As models like GPT-4V improve, the pipeline can be upgraded to ingest diagrams and geometry figures. Cocoindex's support for multi-modal embeddings (e.g., ColPali) positions the architecture to handle this future requirement.33  
* **Feedback Loops:** Implementing a "Human-in-the-loop" asset in Dagster, where low-confidence extractions are flagged for manual review, would further enhance the integrity of the knowledge graph.  
* **Immediate Action:** Begin by implementing the "Extraction Asset" using Marker and verifying the LaTeX fidelity on a sample of 50 past papers. This is the foundational data asset upon which all downstream intelligence depends.

#### **Works cited**

1. Partitions in Data Pipelines \- Dagster, accessed December 4, 2025, [https://dagster.io/blog/partitioned-data-pipelines](https://dagster.io/blog/partitioned-data-pipelines)  
2. cocoindex \- PyPI, accessed December 4, 2025, [https://pypi.org/project/cocoindex/](https://pypi.org/project/cocoindex/)  
3. Overview | CocoIndex, accessed December 4, 2025, [https://cocoindex.io/docs/](https://cocoindex.io/docs/)  
4. Graphiti \- FalkorDB Docs, accessed December 4, 2025, [https://docs.falkordb.com/agentic-memory/graphiti.html](https://docs.falkordb.com/agentic-memory/graphiti.html)  
5. Graphiti: Knowledge Graph Memory for an Agentic World \- Neo4j, accessed December 4, 2025, [https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)  
6. Functional core \- Imperative shell: dealing with logic dependant on conditional & expensive IO operations, accessed December 4, 2025, [https://stackoverflow.com/questions/79792099/functional-core-imperative-shell-dealing-with-logic-dependant-on-conditional](https://stackoverflow.com/questions/79792099/functional-core-imperative-shell-dealing-with-logic-dependant-on-conditional)  
7. Simplify Your Code: Functional Core, Imperative Shell \- Google Testing Blog, accessed December 4, 2025, [https://testing.googleblog.com/2025/10/simplify-your-code-functional-core.html](https://testing.googleblog.com/2025/10/simplify-your-code-functional-core.html)  
8. Simplify Your Code: Functional Core, Imperative Shell : r/programming \- Reddit, accessed December 4, 2025, [https://www.reddit.com/r/programming/comments/1od6z2h/simplify\_your\_code\_functional\_core\_imperative/](https://www.reddit.com/r/programming/comments/1od6z2h/simplify_your_code_functional_core_imperative/)  
9. Do you use the "Functional core, imperative shell" approach when writing code in all PLs?, accessed December 4, 2025, [https://www.reddit.com/r/ExperiencedDevs/comments/1hwtpj1/do\_you\_use\_the\_functional\_core\_imperative\_shell/](https://www.reddit.com/r/ExperiencedDevs/comments/1hwtpj1/do_you_use_the_functional_core_imperative_shell/)  
10. Partitioning assets | Dagster Docs, accessed December 4, 2025, [https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets](https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets)  
11. Marker — a new PDF converter suitable for RAG : r/llm\_updated \- Reddit, accessed December 4, 2025, [https://www.reddit.com/r/llm\_updated/comments/19dtd7z/marker\_a\_new\_pdf\_converter\_suitable\_for\_rag/](https://www.reddit.com/r/llm_updated/comments/19dtd7z/marker_a_new_pdf_converter_suitable_for_rag/)  
12. marker-pdf 0.3.2 \- PyPI, accessed December 4, 2025, [https://pypi.org/project/marker-pdf/0.3.2/](https://pypi.org/project/marker-pdf/0.3.2/)  
13. Custom Entity and Edge Types | Zep Documentation, accessed December 4, 2025, [https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types](https://help.getzep.com/graphiti/core-concepts/custom-entity-and-edge-types)  
14. I Tested 7 Python PDF Extractors So You Don't Have To (2025 Edition) \- Aman Kumar, accessed December 4, 2025, [https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257](https://onlyoneaman.medium.com/i-tested-7-python-pdf-extractors-so-you-dont-have-to-2025-edition-c88013922257)  
15. A Comparative Study of PDF Parsing Tools Across Diverse Document Categories \- arXiv, accessed December 4, 2025, [https://arxiv.org/html/2410.09871v1](https://arxiv.org/html/2410.09871v1)  
16. Mathpix: Document conversion done right, accessed December 4, 2025, [https://mathpix.com/](https://mathpix.com/)  
17. Introducing Dynamic Definitions for Flexible Asset Partitioning \- Dagster, accessed December 4, 2025, [https://dagster.io/blog/dynamic-partitioning](https://dagster.io/blog/dynamic-partitioning)  
18. Launching a single RunRequest for a set of partitions from a schedule or sensor · dagster-io dagster · Discussion \#19457 \- GitHub, accessed December 4, 2025, [https://github.com/dagster-io/dagster/discussions/19457](https://github.com/dagster-io/dagster/discussions/19457)  
19. Sensors \- Dagster Docs, accessed December 4, 2025, [https://docs.dagster.io/guides/automate/sensors](https://docs.dagster.io/guides/automate/sensors)  
20. Get a DynamicPartitionsDefinition updated within a schedule definition before the RunRequest are fired \#20508 \- GitHub, accessed December 4, 2025, [https://github.com/dagster-io/dagster/discussions/20508](https://github.com/dagster-io/dagster/discussions/20508)  
21. Custom Functions | CocoIndex, accessed December 4, 2025, [https://cocoindex.io/docs/custom\_ops/custom\_functions](https://cocoindex.io/docs/custom_ops/custom_functions)  
22. CocoIndex Query Support, accessed December 4, 2025, [https://cocoindex.io/docs/query](https://cocoindex.io/docs/query)  
23. Functions | CocoIndex, accessed December 4, 2025, [https://cocoindex.io/docs/ops/functions](https://cocoindex.io/docs/ops/functions)  
24. Building Intelligent Codebase Indexing with CocoIndex: A Deep Dive into Semantic Code Search \- Medium, accessed December 4, 2025, [https://medium.com/@cocoindex.io/building-intelligent-codebase-indexing-with-cocoindex-a-deep-dive-into-semantic-code-search-e93ae28519c5](https://medium.com/@cocoindex.io/building-intelligent-codebase-indexing-with-cocoindex-a-deep-dive-into-semantic-code-search-e93ae28519c5)  
25. Incrementally Transform Structured \+ Unstructured Data from Postgres with AI \- CocoIndex, accessed December 4, 2025, [https://cocoindex.io/blogs/postgres-source](https://cocoindex.io/blogs/postgres-source)  
26. Adding Episodes \- Zep Documentation, accessed December 4, 2025, [https://help.getzep.com/graphiti/core-concepts/adding-episodes](https://help.getzep.com/graphiti/core-concepts/adding-episodes)  
27. Beyond Static Graphs: Engineering Evolving Relationships \- Zep, accessed December 4, 2025, [https://blog.getzep.com/beyond-static-knowledge-graphs/](https://blog.getzep.com/beyond-static-knowledge-graphs/)  
28. Graphiti (Knowledge Graph Agent Memory) Gets Custom Entity Types : r/LLMDevs \- Reddit, accessed December 4, 2025, [https://www.reddit.com/r/LLMDevs/comments/1j0ca03/graphiti\_knowledge\_graph\_agent\_memory\_gets\_custom/](https://www.reddit.com/r/LLMDevs/comments/1j0ca03/graphiti_knowledge_graph_agent_memory_gets_custom/)  
29. Building AI Agents with Knowledge Graph Memory: A Comprehensive Guide to Graphiti | by Saeed Hajebi | Medium, accessed December 4, 2025, [https://medium.com/@saeedhajebi/building-ai-agents-with-knowledge-graph-memory-a-comprehensive-guide-to-graphiti-3b77e6084dec](https://medium.com/@saeedhajebi/building-ai-agents-with-knowledge-graph-memory-a-comprehensive-guide-to-graphiti-3b77e6084dec)  
30. Searching the Graph \- Zep Documentation, accessed December 4, 2025, [https://help.getzep.com/v2/searching-the-graph](https://help.getzep.com/v2/searching-the-graph)  
31. Searching the Graph \- Zep Documentation, accessed December 4, 2025, [https://help.getzep.com/graphiti/working-with-data/searching](https://help.getzep.com/graphiti/working-with-data/searching)  
32. Graphiti MCP Server \- LobeHub, accessed December 4, 2025, [https://lobehub.com/mcp/getzep-graphiti-fastmcp](https://lobehub.com/mcp/getzep-graphiti-fastmcp)  
33. Featured Examples \- CocoIndex, accessed December 4, 2025, [https://cocoindex.io/docs/examples](https://cocoindex.io/docs/examples)

## Deployment — Google Cloud Platform


> Source: `docs/data_engineering/dagster/deploy/README.md`

View this example in the Dagster docs at https://docs.dagster.io/examples/deploy_docker.


> Source: `docs/data_engineering/dagster/Deploying Dagster to Google Cloud Platform _ Dagster Docs.md`

---
title: "Deploying Dagster to Google Cloud Platform | Dagster Docs"
source: "https://docs.dagster.io/deployment/oss/deployment-options/gcp"
author:
published:
created: 2025-12-30
description: "To deploy open source Dagster to GCP, Google Compute Engine (GCE) can host the Dagster webserver, Google Cloud SQL can store runs and events, and Google Cloud Storage (GCS) can act as an IO manager."
tags:
  - "clippings"
---
To deploy Dagster to GCP, Google Compute Engine (GCE) can host the Dagster webserver, Google Cloud SQL can store runs and events, and Google Cloud Storage (GCS) can act as an IO manager.

## Hosting the Dagster webserver or Dagster Daemon on GCE

To host the Dagster webserver or Dagster daemon on a bare VM or in Docker on GCE, see [Running Dagster as a service](https://docs.dagster.io/deployment/oss/deployment-options/deploying-dagster-as-a-service).

## Using Cloud SQL for run and event log storage

We recommend launching a Cloud SQL PostgreSQL instance for run and events data. You can configure the webserver to use Cloud SQL to run and events data by setting blocks in your `$DAGSTER_HOME/dagster.yaml` appropriately:

```python
storage:
  postgres:
    postgres_db:
      username: my_username
      password: my_password
      hostname: my_hostname
      db_name: my_database
      port: 5432
```

In this case, you'll want to ensure you provide the right connection strings for your Cloud SQL instance, and that the node or container hosting the webserver is able to connect to Cloud SQL.

Be sure that this file is present, and `_DAGSTER_HOME_` is set, on the node where the webserver is running.

Note that using Cloud SQL for run and event log storage does not require that the webserver be running in the cloud. If you are connecting a local webserver instance to a remote Cloud SQL storage, double check that your local node is able to connect to Cloud SQL.

## Using GCS for IO Management

You'll probably also want to configure a GCS bucket to store op outputs via persistent [IO Managers](https://docs.dagster.io/guides/build/io-managers). This enables reexecution, review and audit of op outputs, and cross-node cooperation (e.g., with the [`multiprocess_executor`](https://docs.dagster.io/api/dagster/execution#dagster.multiprocess_executor) or [`celery_executor`](https://docs.dagster.io/api/libraries/dagster-celery#dagster_celery.celery_executor)).

You'll first need to create a job using [`gcs_pickle_io_manager`](https://docs.dagster.io/api/libraries/dagster-gcp#dagster_gcp.gcs_pickle_io_manager) as its IO Manager (or [define a custom IO Manager](https://docs.dagster.io/guides/build/io-managers/defining-a-custom-io-manager)):

```python
from dagster_gcp.gcs.io_manager import gcs_pickle_io_manager
from dagster_gcp.gcs.resources import gcs_resource

import dagster as dg

@dg.job(
    resource_defs={
        "gcs": gcs_resource,
        "io_manager": gcs_pickle_io_manager,
    },
    config={
        "resources": {
            "io_manager": {
                "config": {
                    "gcs_bucket": "my-cool-bucket",
                    "gcs_prefix": "good/prefix-for-files-",
                }
            }
        }
    },
)
def gcs_job(): ...
```

With this in place, your job runs will store outputs on GCS in the location `gs://<bucket>/dagster/storage/<job run id>/files/<op name>.compute`.

## Dagster Docs — Core Concepts


> Source: `docs/data_engineering/dagster/Components _ Dagster Docs.md`

---
title: "Components | Dagster Docs"
source: "https://docs.dagster.io/dagster-basics-tutorial/custom-components"
author:
published:
created: 2025-12-12
description: "Defining custom components"
tags:
  - "clippings"
---
So far, we have built our pipeline out of existing `Definitions`, but this is not the only way to include `Definitions` in a Dagster project.

If we think about the code for our three assets (`customers`, `orders`, and `payments`), it is all very similar. Each asset performs the same action, turning an S3 file into a DuckDB table, while differing only in the URL path and table name.

These assets are a great candidate for a [custom component](https://docs.dagster.io/guides/build/components/creating-new-components). Components generate `Definitions` through a configuration layer. There are built-in components that let you integrate with common workflows (such as turning Python scripts into assets), or dynamically generate `Definitions` for tools like [dbt](https://docs.dagster.io/integrations/libraries/dbt) or [Fivetran](https://docs.dagster.io/integrations/libraries/fivetran). With custom components, you can define your own specific use cases.

In this step, you will use a custom component to streamline the development of similar assets and replace their `Definitions` in your project with a Component that can generate them from a a YAML configuration file instead.

![2048 resolution](https://docs.dagster.io/assets/images/components-f6b7b1846953643053de87560a4a6583.png)

## 1\. Scaffold a custom component

First, scaffold a custom component using `dg`:

```markdown
dg scaffold component Tutorial
```

```markdown
Creating module at: <YOUR PATH>/dagster-tutorial/src/dagster_tutorial/components
Scaffolded Dagster component at <YOUR PATH>/dagster-tutorial/src/dagster_tutorial/components/tutorial.py.
```

This adds a new directory, `components`, within `src/dagster_tutorial`:

```markdown
src
└── dagster_tutorial
    ├── __init__.py
    ├── components   # NEW
    │   ├── __init__.py
    │   └── tutorial.py
    ├── definitions.py
    └── defs
        ├── __init__.py
        ├── assets.py
        ├── resources.py
        └── schedules.py
```

This directory contains the files needed to define the custom component.

## 2\. Define the custom component

When designing a component, keep its interface in mind. In this case, the assets that the component will create share the following attributes:

- A DuckDB database shared across all assets.
- A list of ETL assets, each with a URL path and a table name.

The first step is to create a `dg.Model` for the ETL assets. `dg.Model` turns any class that inherits from it into a [Pydantic](https://docs.pydantic.dev/) model. This model is then used to implement the YAML interface from the component.

This model will contain the two attributes that define an asset:

```python
src/etl_tutorial/components/tutorial.pyimport dagster as dg

class ETL(dg.Model):
    url_path: str
    table: str
```

Next, add the interface to the `dg.Component` class. In this case, there will be a single attribute for the DuckDB database and a list of the `ETL` models you just defined:

```python
duckdb_database: str
    etl_steps: list[ETL]
```

The rest of the code will look very similar to the asset definitions you wrote earlier. The `build_defs` method constructs a `Definitions` object containing all the Dagster objects created by the component. Based on the interface defined at the class level, you will generate multiple ETL assets. The final Dagster object to include is the `resource` that the assets rely on, which can also be set with an attribute.

```python
src/etl_tutorial/components/tutorial.pyfrom dagster_duckdb import DuckDBResource

class Tutorial(dg.Component, dg.Model, dg.Resolvable):
    # The interface for the component
    duckdb_database: str
    etl_steps: list[ETL]

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        _etl_assets = []

        for etl in self.etl_steps:

            @dg.asset(
                name=etl.table,
            )
            def _table(duckdb: DuckDBResource):
                with duckdb.get_connection() as conn:
                    conn.execute(
                        f"""
                        create or replace table {etl.table} as (
                            select * from read_csv_auto('{etl.url_path}')
                        )
                        """
                    )

            _etl_assets.append(_table)

        return dg.Definitions(
            assets=_etl_assets,
            resources={"duckdb": DuckDBResource(database=self.duckdb_database)},
        )
```

Run the check again to ensure that the component code is correct:

```markdown
dg check defs
```

```markdown
All component YAML validated successfully.
All definitions loaded successfully.
```

## 3\. Scaffold the component definition

If you list your components again, you should see that the custom component is now registered:

```markdown
dg list components
```

```markdown
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Key                                           ┃ Summary                                                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ dagster.DefinitionsComponent                  │ An arbitrary set of Dagster definitions.                                    │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ dagster.DefsFolderComponent                   │ A component that represents a directory containing multiple Dagster         │
│                                               │ definition modules.                                                         │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ dagster.FunctionComponent                     │ Represents a Python function, alongside the set of assets or asset checks   │
│                                               │ that it is responsible for executing.                                       │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ dagster.PythonScriptComponent                 │ Represents a Python script, alongside the set of assets and asset checks    │
│                                               │ that it is responsible for executing.                                       │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ dagster.TemplatedSqlComponent                 │ A component which executes templated SQL from a string or file.             │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ dagster.UvRunComponent                        │ Represents a Python script, alongside the set of assets or asset checks     │
│                                               │ that it is responsible for executing.                                       │
├───────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────────────────┤
│ dagster_tutorial.components.tutorial.Tutorial │                                                                             │
└───────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────────────────┘
```

You can now scaffold definitions from it just like any other component:

```markdown
dg scaffold defs dagster_tutorial.components.tutorial.Tutorial tutorial
```

```markdown
Creating defs at <YOUR PATH>/dagster-tutorial/src/dagster_tutorial/defs/tutorial.
```

This adds a new directory, `tutorials`, within `defs`:

```markdown
src
└── dagster_tutorial
    ├── __init__.py
    ├── components
    │   ├── __init__.py
    │   └── tutorial.py
    ├── definitions.py
    └── defs
        ├── __init__.py
        ├── assets.py
        ├── resources.py
        ├── schedules.py
        └── tutorial   # NEW
            └── defs.yaml
```

## 4\. Configure the component

To configure the component, update the YAML file created when you scaffolded a definition from the component:

```yaml
src/dagster_tutorial/defs/tutorial/defs.yamltype: dagster_tutorial.components.tutorial.Tutorial

attributes:
  duckdb_database: /tmp/jaffle_platform.duckdb
  etl_steps:
    - url_path: https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_customers.csv
      table: customers
    - url_path: https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_orders.csv
      table: orders
    - url_path: https://raw.githubusercontent.com/dbt-labs/jaffle-shop-classic/refs/heads/main/seeds/raw_payments.csv
      table: payments
```

## 5\. Remove the old definitions

Before running `dg check` again, remove the `customers`, `orders`, and `payments` assets from `assets.py` and the `resource.py` file. The component is now responsible for generating these objects (otherwise there will be duplicate keys in the asset lineage).

```markdown
src
└── dagster_tutorial
    ├── __init__.py
    ├── components
    │   ├── __init__.py
    │   └── tutorial.py
    ├── definitions.py
    └── defs
        ├── __init__.py
        ├── assets.py   # UPDATED
        ├── schedules.py
        └── tutorial
            └── defs.yaml
```

## 6\. Materialize the assets

When you materialize your assets in the Dagster UI at [http://127.0.0.1:3000/assets](http://127.0.0.1:3000/assets), you should see that the asset graph looks the same as before.

## Summary

Congratulations! You've just built a fully functional, end-to-end data pipeline. This is no small feat! You've laid the foundation for a scalable, maintainable, and observable data platform.

- Join our [Slack community](https://dagster.io/slack).
- Continue learning with [Dagster University](https://courses.dagster.io/) courses.
- Start a [free trial of Dagster+](https://dagster.cloud/signup) for your own project.

Ask Dagster AI

> Source: `docs/data_engineering/dagster/Advanced config types _ Dagster Docs.md`

---
title: "Advanced config types | Dagster Docs"
source: "https://docs.dagster.io/guides/operate/configuration/advanced-config-types"
author:
published:
created: 2025-12-12
description: "Dagster's config system supports a variety of more advanced config types."
tags:
  - "clippings"
---
In some cases, you may want to define a more complex [config schema](https://docs.dagster.io/guides/operate/configuration/run-configuration) for your assets and ops. For example, you may want to define a config schema that takes in a list of files or complex data. In this guide, we'll walk through some common patterns for defining more complex config schemas.

Config fields can be annotated with metadata, which can be used to provide additional information about the field, using the Pydantic [`Field`](https://docs.dagster.io/api/dagster/config#dagster.Field) class.

For example, we can annotate a config field with a description, which will be displayed in the documentation for the config field. We can add a value range to a field, which will be validated when config is specified.

```python
import dagster as dg
from pydantic import Field

class MyMetadataConfig(dg.Config):
    person_name: str = Field(description="The name of the person to greet")
    age: int = Field(gt=0, lt=100, description="The age of the person to greet")

# errors, since age is not in the valid range!
MyMetadataConfig(person_name="Alice", age=200)
```

## Defaults and optional config fields

Config fields can have an attached default value. Fields with defaults are not required, meaning they do not need to be specified when constructing the config object.

For example, we can attach a default value of `"hello"` to the `greeting_phrase` field, and can construct `MyAssetConfig` without specifying a phrase. Fields which are marked as `Optional`, such as `person_name`, implicitly have a default value of `None`, but can also be explicitly set to `None` as in the example below:

```python
src/<project_name>/defs/assets.py
from typing import Optional
import dagster as dg
from pydantic import Field

class MyAssetConfig(dg.Config):
    person_name: Optional[str] = None

    # can pass default to pydantic.Field to attach metadata to the field
    greeting_phrase: str = Field(
        default="hello", description="The greeting phrase to use."
    )

@dg.asset
def greeting(config: MyAssetConfig) -> str:
    if config.person_name:
        return f"{config.greeting_phrase} {config.person_name}"
    else:
        return config.greeting_phrase

asset_result = dg.materialize(
    [greeting],
    run_config=dg.RunConfig({"greeting": MyAssetConfig()}),
)
```

### Required config fields

By default, fields which are typed as `Optional` are not required to be specified in the config, and have an implicit default value of `None`. If you want to require that a field be specified in the config, you may use an ellipsis (`...`) to [require that a value be passed](https://docs.pydantic.dev/usage/models/#required-fields).

```python
src/<project_name>/defs/assets.pyfrom typing import Optional
from collections.abc import Callable
import dagster as dg
from pydantic import Field

class MyAssetConfig(dg.Config):
    # ellipsis indicates that even though the type is Optional,
    # an input is required
    person_first_name: Optional[str] = ...

    # ellipsis can also be used with pydantic.Field to attach metadata
    person_last_name: Optional[Callable] = Field(
        default=..., description="The last name of the person to greet"
    )

@dg.asset
def goodbye(config: MyAssetConfig) -> str:
    full_name = f"{config.person_first_name} {config.person_last_name}".strip()
    if full_name:
        return f"Goodbye, {full_name}"
    else:
        return "Goodbye"

# errors, since person_first_name and person_last_name are required
goodbye(MyAssetConfig())

# works, since both person_first_name and person_last_name are provided
goodbye(MyAssetConfig(person_first_name="Alice", person_last_name=None))
```

## Basic data structures

Basic Python data structures can be used in your config schemas along with nested versions of these data structures. The data structures which can be used are:

- `List`
- `Dict`
- `Mapping`

For example, we can define a config schema that takes in a list of user names and a mapping of user names to user scores.

```python
src/<project_name>/defs/assets.pyimport dagster as dg

class MyDataStructuresConfig(dg.Config):
    user_names: list[str]
    user_scores: dict[str, int]

@dg.asset
def scoreboard(config: MyDataStructuresConfig): ...

result = dg.materialize(
    [scoreboard],
    run_config=dg.RunConfig(
        {
            "scoreboard": MyDataStructuresConfig(
                user_names=["Alice", "Bob"],
                user_scores={"Alice": 10, "Bob": 20},
            )
        }
    ),
)
```

## Nested schemas

Schemas can be nested in one another, or in basic Python data structures.

Here, we define a schema which contains a mapping of user names to complex user data objects.

```python
src/<project_name>/defs/assets.pyimport dagster as dg

class UserData(dg.Config):
    age: int
    email: str
    profile_picture_url: str

class MyNestedConfig(dg.Config):
    user_data: dict[str, UserData]

@dg.asset
def average_age(config: MyNestedConfig): ...

result = dg.materialize(
    [average_age],
    run_config=dg.RunConfig(
        {
            "average_age": MyNestedConfig(
                user_data={
                    "Alice": UserData(
                        age=10,
                        email="alice@gmail.com",
                        profile_picture_url=...,
                    ),
                    "Bob": UserData(
                        age=20,
                        email="bob@gmail.com",
                        profile_picture_url=...,
                    ),
                }
            )
        }
    ),
)
```

## Permissive schemas

By default, `Config` schemas are strict, meaning that they will only accept fields that are explicitly defined in the schema. This can be cumbersome if you want to allow users to specify arbitrary fields in their config. For this purpose, you can use the `PermissiveConfig` base class, which allows arbitrary fields to be specified in the config.

```python
src/<project_name>/defs/assets.py
import dagster as dg
from typing import Optional
import requests

class FilterConfig(dg.PermissiveConfig):
    title: Optional[str] = None
    description: Optional[str] = None

@dg.asset
def filtered_listings(config: FilterConfig):
    # extract all config fields, including those not defined in the schema
    url_params = config.dict()
    return requests.get("https://my-api.com/listings", params=url_params).json()

# can pass in any fields, including those not defined in the schema
filtered_listings(FilterConfig(title="hotel", beds=4))
```

## Union types

Union types are supported using Pydantic [discriminated unions](https://docs.pydantic.dev/usage/types/#discriminated-unions-aka-tagged-unions). Each union type must be a subclass of [`Config`](https://docs.dagster.io/api/dagster/config#dagster.Config). The `discriminator` argument to [`Field`](https://docs.dagster.io/api/dagster/config#dagster.Field) specifies the field that will be used to determine which union type to use. Discriminated unions provide comparable functionality to the `Selector` type in the legacy Dagster config APIs.

Here, we define a config schema which takes in a `pet` field, which can be either a `Cat` or a `Dog`, as indicated by the `pet_type` field.

```python
src/<project_name>/defs/assets.py
import dagster as dg
from pydantic import Field
from typing import Union
from typing import Literal

class Cat(dg.Config):
    pet_type: Literal["cat"] = "cat"
    meows: int

class Dog(dg.Config):
    pet_type: Literal["dog"] = "dog"
    barks: float

class ConfigWithUnion(dg.Config):
    pet: Union[Cat, Dog] = Field(discriminator="pet_type")

@dg.asset
def pet_stats(config: ConfigWithUnion):
    if isinstance(config.pet, Cat):
        return f"Cat meows {config.pet.meows} times"
    else:
        return f"Dog barks {config.pet.barks} times"

result = dg.materialize(
    [pet_stats],
    run_config=dg.RunConfig(
        {
            "pet_stats": ConfigWithUnion(
                pet=Cat(meows=10),
            )
        }
    ),
)
```

### YAML and config dictionary representations of union types

The YAML or config dictionary representation of a discriminated union is structured slightly differently than the Python representation. In the YAML representation, the discriminator key is used as the key for the union type's dictionary. For example, a `Cat` object would be represented as:

```yaml
pet:
  cat:
    meows: 10
```

In the config dictionary representation, the same pattern is used:

```python
{
    "pet": {
        "cat": {
            "meows": 10,
        }
    }
}
```

## Enum types

Python enums which subclass `Enum` are supported as config fields. Here, we define a schema that takes in a list of users, whose roles are specified as enum values:

```python
src/<project_name>/defs/jobs.py
import dagster as dg
from enum import Enum

class UserPermissions(Enum):
    GUEST = "guest"
    MEMBER = "member"
    ADMIN = "admin"

class ProcessUsersConfig(dg.Config):
    users_list: dict[str, UserPermissions]

@dg.op
def process_users(config: ProcessUsersConfig):
    for user, permission in config.users_list.items():
        if permission == UserPermissions.ADMIN:
            print(f"{user} is an admin")

@dg.job
def process_users_job():
    process_users()

op_result = process_users_job.execute_in_process(
    run_config=dg.RunConfig(
        {
            "process_users": ProcessUsersConfig(
                users_list={
                    "Bob": UserPermissions.GUEST,
                    "Alice": UserPermissions.ADMIN,
                }
            )
        }
    ),
)
```

### YAML and config dictionary representations of enum types

The YAML or config dictionary representation of a Python enum uses the enum's name. For example, a YAML specification of the user list above would be:

```yaml
users_list:
  Bob: GUEST
  Alice: ADMIN
```

In the config dictionary representation, the same pattern is used:

```python
{
    "users_list": {
        "Bob": "GUEST",
        "Alice": "ADMIN",
    }
}
```

## Validated config fields

Config fields can have custom validation logic applied using [Pydantic validators](https://docs.pydantic.dev/usage/validators). Pydantic validators are defined as methods on the config class, and are decorated with the `@validator` decorator. These validators are triggered when the config class is instantiated. In the case of config defined at runtime, a failing validator will not prevent the launch button from being pressed, but will raise an exception and prevent run start.

Here, we define some validators on a configured user's name and username, which will throw exceptions if incorrect values are passed in the launchpad or from a schedule or sensor.

```python
src/<project_name>/defs/jobs.py
    import dagster as dg
    from pydantic import validator

    class UserConfig(dg.Config):
        name: str
        username: str

        @validator("name")
        def name_must_contain_space(cls, v):
            if " " not in v:
                raise ValueError("must contain a space")
            return v.title()

        @validator("username")
        def username_alphanumeric(cls, v):
            assert v.isalnum(), "must be alphanumeric"
            return v

    executed = {}

    @dg.op
    def greet_user(config: UserConfig) -> None:
        print(f"Hello {config.name}!")
        executed["greet_user"] = True

    @dg.job
    def greet_user_job() -> None:
        greet_user()

    # Input is valid, so this will work
    op_result = greet_user_job.execute_in_process(
        run_config=dg.RunConfig(
            {"greet_user": UserConfig(name="Alice Smith", username="alice123")}
        ),
    )

    # Name has no space, so this will fail
    op_result = greet_user_job.execute_in_process(
        run_config=dg.RunConfig(
            {"greet_user": UserConfig(name="John", username="johndoe44")}
        ),
    )
```

Ask Dagster AI

> Source: `docs/data_engineering/dagster/Run configuration _ Dagster Docs.md`

---
title: "Run configuration | Dagster Docs"
source: "https://docs.dagster.io/guides/operate/configuration/run-configuration"
author:
published:
created: 2025-12-12
description: "Dagster Job run configuration allows providing parameters to jobs at the time they're executed."
tags:
  - "clippings"
---
When you launch a job that materializes, executes, or instantiates a configurable entity, such as an asset, op, or resource, you can provide *run configuration* for that entity. Within the function that defines the entity, you can access the passed-in configuration through the `config` parameter. Typically, the provided run configuration values correspond to a *configuration schema* attached to the asset, op, or resource definition. Dagster validates the run configuration against the schema and proceeds only if validation is successful.

A common use of configuration is for a [schedule](https://docs.dagster.io/guides/automate/schedules) or [sensor](https://docs.dagster.io/guides/automate/sensors) to provide configuration to the job run it is launching. For example, a daily schedule might provide the day it's running on to one of the assets as a config value, and that asset might use that config value to decide what day's data to read.

## Defining configurable parameters for an asset, op, or job

You can specify configurable parameters accepted by an asset, op, or job by defining a config model subclass of [`Config`](https://docs.dagster.io/api/dagster/config#dagster.Config) and a `config` parameter to the corresponding asset or op function. These config models utilize [Pydantic](https://docs.pydantic.dev/), a popular Python library for data validation and serialization.

During execution, the specified config is accessed within the body of the asset, op, or job with the `config` parameter.

These examples showcase the most basic config types that can be used. For more information on the set of config types Dagster supports, see [the advanced config types documentation](https://docs.dagster.io/guides/operate/configuration/advanced-config-types).

## Defining configurable parameters for a resource

Configurable parameters for a resource are defined by specifying attributes for a resource class, which subclasses [`ConfigurableResource`](https://docs.dagster.io/api/dagster/resources#dagster.ConfigurableResource). The below resource defines a configurable connection URL, which can be accessed in any methods defined on the resource:

```python
import dagster as dg

class Engine:
    def execute(self, query: str): ...

def get_engine(connection_url: str) -> Engine:
    return Engine()

class MyDatabaseResource(dg.ConfigurableResource):
    connection_url: str

    def query(self, query: str):
        return get_engine(self.connection_url).execute(query)

@dg.definitions
def resources() -> dg.Definitions:
    return dg.Definitions(
        resources={
            # To send a query to the database, you can call my_db_resource.query("QUERY HERE")
            # in the asset, op, or job where you reference my_db_resource
            "my_db_resource": MyDatabaseResource(connection_url="")
        }
    )
```

For more information on using resources, see the [External resources documentation](https://docs.dagster.io/guides/build/external-resources).

## Providing config values at runtime

To execute a job or materialize an asset that specifies config, you'll need to provide values for its parameters. How you provide these values depends on the interface you use: Python, the Dagster UI, or the command line (CLI).

## Using environment variables with config

Assets and ops can be configured using environment variables by passing an [`EnvVar`](https://docs.dagster.io/api/dagster/resources#dagster.EnvVar) when constructing a config object. This is useful when the value is sensitive or may vary based on environment. If using Dagster+, environment variables can be [set up directly in the UI](https://docs.dagster.io/guides/operate/configuration/using-environment-variables-and-secrets).

```python
src/<project_name>/defs/assets.pyimport dagster as dg

from .resources import MyAssetConfig

@dg.asset
def greeting(config: MyAssetConfig) -> str:
    return f"hello {config.person_name}"

asset_result = dg.materialize(
    [greeting],
    run_config=dg.RunConfig(
        {"greeting": MyAssetConfig(person_name=dg.EnvVar("PERSON_NAME"))}
    ),
)
```

For more information on using environment variables in Dagster, see [Using environment variables and secrets in Dagster code](https://docs.dagster.io/guides/operate/configuration/using-environment-variables-and-secrets).

## Validation

Dagster validates any provided run config against the corresponding Pydantic model. It will abort execution with a [`DagsterInvalidConfigError`](https://docs.dagster.io/api/dagster/errors#dagster.DagsterInvalidConfigError) or Pydantic `ValidationError` if validation fails. For example, both of the following will fail, because there is no `nonexistent_config_value` in the config schema:

```python
src/<project_name>/defs/assets.pyimport dagster as dg

from .resources import MyAssetConfig

@dg.asset
def greeting(config: MyAssetConfig) -> str:
    return f"hello {config.person_name}"

asset_result = dg.materialize(
    [greeting],
    run_config=dg.RunConfig({"greeting": MyAssetConfig(nonexistent_config_value=1)}),
)
```

Config is a powerful tool for making Dagster pipelines more flexible and observable. For a deeper dive into the supported config types, see the [advanced config types documentation](https://docs.dagster.io/guides/operate/configuration/advanced-config-types). For more information on using resources, which are a powerful way to encapsulate reusable logic, see the [resources documentation](https://docs.dagster.io/guides/build/external-resources).

Ask Dagster AI

> Source: `docs/data_engineering/dagster/Creating workspaces to manage multiple projects _ Dagster Docs.md`

---
title: "Creating workspaces to manage multiple projects | Dagster Docs"
source: "https://docs.dagster.io/guides/build/projects/workspaces/creating-workspaces"
author:
published:
created: 2025-12-12
description: "Manage multiple isolated Dagster projects by creating a workspace directory with the create-dagster command."
tags:
  - "clippings"
---
If you need to collaborate with multiple teams, or work with conflicting dependencies that require isolation from each other, you can scaffold a workspace directory that contains multiple projects, each with their own separate Python environment, while still being able to access all of your assets across every project in a single instance of the Dagster UI or `dg` CLI.

A workspace directory contains a root [`dg.toml` file](https://docs.dagster.io/guides/build/projects/workspaces/dg-toml) with workspace-level settings, and a `projects` directory with one or more projects. It also contains a Python environment in a `deployments/local` folder that can be used for running `dg` commands locally against the workspace.

When a `dg` command runs in a workspace, it will create a subprocess for each project using that project's virtual environment, and communicate with each process through an API layer. The diagram below demonstrates a workspace with two projects, as well as their virtual environments.

![Diagram showing the virtual environments used by a workspace and 2 projects](https://docs.dagster.io/assets/images/workspace-venvs-a1f94cade8ebd825028a704a52bce0ef.png)

## Creating a new workspace and first project

To scaffold a new workspace called `dagster-workspace`, run `uvx create-dagster@latest workspace` and respond yes to the prompt to run `uv sync` after scaffolding:

```markdown
uvx create-dagster workspace dagster-workspace && cd dagster-workspace
```

The scaffolded workspace includes a `projects` folder, which is currently empty, and a `deployments` folder, which includes a `local` folder with a `pyproject.toml` file that specifies an environment for running `dg` commands locally against your workspace.

Next, enter the directory and activate the virtual environment for the `local` environment:

```markdown
source deployments/local/.venv/bin/activate
```

Now we'll create a project inside our workspace called `project-1`. Run `uvx create-dagster@latest project` with the path of the project:

```markdown
uvx create-dagster project projects/project-1
```

```markdown
Creating a Dagster project at /.../dagster-workspace/projects/project-1.
Scaffolded files for Dagster project at /.../dagster-workspace/projects/project-1.
A \`uv\` installation was detected. Run \`uv sync\`? This will create a uv.lock file and the virtual environment you need to activate in order to work on this project. If you wish to use a non-uv package manager, choose "n". (y/n) [y]: Running \`uv sync --group dev\`...
...
```

This will create a new Python environment for this project and associate that project with the workspace.

### Workspace structure

The new workspace has the following structure:

```markdown
tree
```

```markdown
.
├── deployments
│   └── local
│       ├── pyproject.toml
│       └── uv.lock
├── dg.toml
└── projects
    └── project-1
        ├── pyproject.toml
        ├── src
        │   └── project_1
        │       ├── __init__.py
        │       ├── definitions.py
        │       └── defs
        │           └── __init__.py
        ├── tests
        │   └── __init__.py
        └── uv.lock

...
```

The `dg.toml` file for the `dagster-workspace` folder contains a `directory_type = "workspace"` setting that marks this directory as a workspace:

```toml
dagster-workspace/dg.tomldirectory_type = "workspace"

[workspace]

[[workspace.projects]]
path = "projects/project-1"
```

The `project-1` directory contains a `pyproject.toml` file with a `tool.dg.directory_type = "project"` section that defines it as a `dg` project:

```toml
dagster-workspace/projects/project-1/pyproject.toml...
[tool.dg]
directory_type = "project"

[tool.dg.project]
root_module = "project_1"
...
```

## Adding a second project to the workspace

As noted above, environments are scoped per project. `dg` commands will only use the environment of `project-1` when you are inside the `project-1` directory.

Let's create another project:

```markdown
uvx create-dagster project projects/project-2
```

```markdown
Creating a Dagster project at /.../dagster-workspace/projects/project-2.
Scaffolded files for Dagster project at /.../dagster-workspace/projects/project-2.
A \`uv\` installation was detected. Run \`uv sync\`? This will create a uv.lock file and the virtual environment you need to activate in order to work on this project. If you wish to use a non-uv package manager, choose "n". (y/n) [y]: Running \`uv sync --group dev\`...
...
```

Now there are two projects. You can list them with:

```markdown
dg list project
```

```markdown
projects/project-1
projects/project-2
```

The workspace now has the following structure:

Finally, let's load our two projects with `dg dev`. When you run `dg dev` from the workspace root, it will automatically recognize the projects in your workspace and launch each project in a separate process in its virtual environment found in the `.venv` folder in the project.

```markdown
dg dev
```

![](https://docs.dagster.io/assets/images/two-projects-a9d77c4661a67b8435ab48ad6aa8c0eb.png)

Ask Dagster AI

> Source: `docs/data_engineering/dagster/Using environment variables and secrets in Dagster code _ Dagster Docs.md`

---
title: "Using environment variables and secrets in Dagster code | Dagster Docs"
source: "https://docs.dagster.io/guides/operate/configuration/using-environment-variables-and-secrets"
author:
published:
created: 2025-12-12
description: "Dagster environment variables allow you to define various configuration options for your Dagster application and securely set up secrets."
tags:
  - "clippings"
---
Environment variables, which are key-value pairs configured outside your source code, allow you to dynamically modify application behavior depending on environment.

Using environment variables, you can define various configuration options for your Dagster application and securely set up secrets. For example, instead of hard-coding database credentials - which is bad practice and cumbersome for development - you can use environment variables to supply user details. This allows you to parameterize your pipeline without modifying code or insecurely storing sensitive data.

## Declaring environment variables

How environment variables are declared depends on whether you're developing locally or have already deployed your Dagster project.

## Accessing environment variables

In this section, we'll demonstrate how to access environment variables once they've been declared. There are two ways to do this:

- [In Python code](https://docs.dagster.io/guides/operate/configuration/#in-python-code)
- [From Dagster configuration](https://docs.dagster.io/guides/operate/configuration/#from-dagster-configuration), which incorporates environment variables into the Dagster config system

### In Python code

To access environment variables in your code, you can either use the [`os.getenv`](https://docs.python.org/3/library/os.html#os.getenv) function or the Dagster [`EnvVar`](https://docs.dagster.io/api/dagster/resources#dagster.EnvVar) class.

- **When you use `os.getenv`**, the variable's value is retrieved when Dagster loads the code location and **will** be visible in the UI.
- **When you use EnvVar**, the variable's value is retrieved at runtime and **won't** be visible in the UI.

Using the `EnvVar` approach has a few unique benefits:

- **Improved observability.** The UI will display information about configuration values sourced from environment variables.
- **Secret values are hidden in the UI.** Secret values are hidden in the Launchpad, Resources page, and other places where configuration is displayed.
- **Simplified testing.** Because you can provide string values directly to configuration rather than environment variables, testing may be easier.

#### os.getenv function

Below is an example of retrieving an environment variable with `os.getenv`:

```python
import os

database_name = os.getenv("DATABASE_NAME")
```

You can also use `os.getenv` to access [built-in environment variables for Dagster+](https://docs.dagster.io/deployment/dagster-plus/management/environment-variables/built-in):

```python
import os

deployment_name = os.getenv("DAGSTER_CLOUD_DEPLOYMENT_NAME")
```

For a real-world example, see the [Dagster+ branch deployments example](https://docs.dagster.io/guides/operate/configuration/#dagster-branch-deployments).

#### Dagster EnvVar class

To use the `EnvVar` approach, call the `get_value()` method on the Dagster [`EnvVar`](https://docs.dagster.io/api/dagster/resources#dagster.EnvVar) class:

```python
import dagster as dg

database_name = dg.EnvVar('DATABASE_NAME').get_value()
```

### From Dagster configuration

[Configurable Dagster objects](https://docs.dagster.io/guides/operate/configuration/run-configuration) (such as ops, assets, resources, I/O managers, and so on) can accept configuration from environment variables with `EnvVar`. These environment variables are retrieved at launch time, rather than on initialization as with `os.getenv`.

## Handling secrets

Using environment variables to provide secrets ensures sensitive information won't be visible in your code or the launchpad in the UI. In Dagster, we recommend using [configuration](https://docs.dagster.io/guides/operate/configuration/run-configuration) and [resources](https://docs.dagster.io/guides/build/external-resources) to manage secrets.

A resource is typically used to connect to an external service or system, such as a database. Resources can be configured separately from your assets, allowing you to define them once and reuse them as needed.

Let's take a look at an example that creates a resource called `SomeResource` and supplies it to assets. Let's start by looking at the resource:

```python
src/<project_name>/defs/resources.pyimport dagster as dg

class SomeResource(dg.ConfigurableResource): ...

@dg.definitions
def defs() -> dg.Definitions:
    return dg.Definitions(
        resources={"some_resource": SomeResource(access_token="foo")},
    )
```

Let's review what's happening here:

- This code creates a resource named `SomeResource`
- By subclassing [`ConfigurableResource`](https://docs.dagster.io/api/dagster/resources#dagster.ConfigurableResource) and specifying the `access_token` field, we're telling Dagster that we want to be able to configure the resource with an `access_token` parameter, which is a string value

By including a reference to `SomeResource` in a `@dg.definitions` -decorated function, we make that resource available to assets defined elsewhere in the `src/<project_name>/defs` directory:

```python
src/<project_name>/defs/assets.pyimport dagster as dg

from .resources import SomeResource

@dg.asset
def my_asset(some_resource: SomeResource) -> None: ...
```

As storing secrets in configuration is bad practice, we'll use an environment variable:

```python
src/<project_name>/defs/resources.pyimport dagster as dg

class SomeResource(dg.ConfigurableResource): ...

@dg.definitions
def defs() -> dg.Definitions:
    return dg.Definitions(
        resources={
            "some_resource": SomeResource(access_token=dg.EnvVar("MY_ACCESS_TOKEN"))
        },
    )
```

In this code, we pass configuration information to the resource when we construct it. In this example, we're telling Dagster to load the `access_token` from the `MY_ACCESS_TOKEN` environment variable by wrapping it in `dg.EnvVar`.

## Parameterizing pipeline behavior

Using environment variables, you define how your code should execute at runtime.

### Per-environment configuration

In this example, we'll demonstrate how to use different I/O manager configurations for `local` and `production` environments using [configuration](https://docs.dagster.io/guides/operate/configuration/run-configuration) (specifically the configured API) and [resources](https://docs.dagster.io/guides/build/external-resources).

This example is adapted from the [Transitioning data pipelines from development to production guide](https://docs.dagster.io/guides/operate/dev-to-prod):

```python
src/<project_name>/defs/resources.pyimport os

from dagster_snowflake_pandas import SnowflakePandasIOManager

import dagster as dg

def resources_by_deployment() -> dict:
    return {
        "local": {
            "snowflake_io_manager": SnowflakePandasIOManager(
                account="abc1234.us-east-1",
                user=dg.EnvVar("DEV_SNOWFLAKE_USER"),
                password=dg.EnvVar("DEV_SNOWFLAKE_PASSWORD"),
                database="LOCAL",
                schema=dg.EnvVar("DEV_SNOWFLAKE_SCHEMA"),
            ),
        },
        "production": {
            "snowflake_io_manager": SnowflakePandasIOManager(
                account="abc1234.us-east-1",
                user="system@company.com",
                password=dg.EnvVar("SYSTEM_SNOWFLAKE_PASSWORD"),
                database="PRODUCTION",
                schema="HACKER_NEWS",
            ),
        },
    }

@dg.definitions
def resources() -> dg.Definitions:
    deployment_name = os.getenv("DAGSTER_DEPLOYMENT", "local")
    return dg.Definitions(resources=resources_by_deployment()[deployment_name])
```

Let's review what's happening here:

- We've created a dictionary of resource definitions called `resources`, with sections for `local` and `production` environments. In this example, we're using a [Pandas Snowflake I/O manager](https://docs.dagster.io/api/libraries/dagster-snowflake-pandas).
- For both `local` and `production`, we constructed the I/O manager using environment-specific run configuration.
- Following the `resources` dictionary, we define the `deployment_name` variable, which determines the current executing environment. This variable defaults to `local`, ensuring that `DAGSTER_DEPLOYMENT=PRODUCTION` must be set to use the `production` configuration.

### Dagster+ branch deployments

You can determine the current deployment type ([branch deployment](https://docs.dagster.io/deployment/dagster-plus/deploying-code/branch-deployments) or [full deployment](https://docs.dagster.io/deployment/dagster-plus/deploying-code/full-deployments)) at runtime with the `DAGSTER_CLOUD_IS_BRANCH_DEPLOYMENT` environment variable. Using this information, you can write code that executes differently when in a branch deployment or a full deployment.

```python
def get_current_env():
  is_branch_depl = os.getenv("DAGSTER_CLOUD_IS_BRANCH_DEPLOYMENT") == "1"
  assert is_branch_depl != None  # env var must be set
  return "branch" if is_branch_depl else "prod"
```

This function checks the value of `DAGSTER_CLOUD_IS_BRANCH_DEPLOYMENT` and, if equal to `1`, returns a variable with the value of `branch`. This indicates that the current deployment is a branch deployment. Otherwise, the deployment is a full deployment and `is_branch_depl` will be returned with a value of `prod`.

## Troubleshooting

| Error | Description | Solution |
| --- | --- | --- |
| **You have attempted to fetch the environment variable "\[variable\]" which is not set. In order for this execution to succeed it must be set in this environment.** | Surfacing when a run is launched in the UI, this error means that an environment variable set using [`StringSource`](https://docs.dagster.io/api/dagster/config#dagster.StringSource) could not be found in the executing environment. | Verify that the environment variable is named correctly and accessible in the environment. - **If developing locally and using a `.env` file**, try reloading the workspace in the UI. The workspace must be reloaded any time this file is modified for the UI to be aware of the changes. - **If using Dagster+**: - Verify that the environment variable is [scoped to the environment and code location](https://docs.dagster.io/deployment/dagster-plus/management/environment-variables/dagster-ui#scope) if using the built-in secrets manager 	- Verify that the environment variable was correctly configured and added to your [agent's configuration](https://docs.dagster.io/deployment/dagster-plus/management/environment-variables/agent-config) |
| **No environment variables in `.env` file.** | Dagster located and attempted to load a local `.env` file while launching `dagster-webserver`, but couldn't find any environment variables in the file. | If this is unexpected, verify that your `.env` is correctly formatted and located in the same folder where you're running `dagster-webserver`. |

Ask Dagster AI

> Source: `docs/data_engineering/dagster/Manage concurrency of Dagster assets, jobs, and Dagster instances _ Dagster Docs.md`

---
title: "Manage concurrency of Dagster assets, jobs, and Dagster instances | Dagster Docs"
source: "https://docs.dagster.io/guides/operate/managing-concurrency"
author:
published:
created: 2025-12-12
description: "How to limit the number of runs a job, or assets for an instance of Dagster."
tags:
  - "clippings"
---
This guide covers managing concurrency of Dagster assets, jobs, and Dagster instances to help prevent performance problems and downtime.

## Limit the number of total runs that can be in progress at the same time

- Dagster Core, add the following to your [dagster.yaml](https://docs.dagster.io/deployment/oss/dagster-yaml)
- In Dagster+, add the following to your [full deployment settings](https://docs.dagster.io/deployment/dagster-plus/deploying-code/full-deployments/full-deployment-settings-reference)
```yaml
concurrency:
  runs:
    max_concurrent_runs: 15
```

## Limit the number of assets or ops actively executing across all runs

You can assign assets and ops to concurrency pools which allow you to limit the number of in progress op executions across all runs. You first assign your asset or op to a concurrency pool using the `pool` keyword argument.

```python
src/<project_name>/defs/assets.pyimport dagster as dg

@dg.asset(pool="foo")
def my_asset():
    pass

@dg.op(pool="bar")
def my_op():
    pass

@dg.op(pool="barbar")
def my_downstream_op(inp):
    return inp

@dg.graph_asset
def my_graph_asset():
    return my_downstream_op(my_op())
```

You should be able to verify that you have set the pool correctly by viewing the details pane for the asset or op in the Dagster UI.

![Viewing the pool tag](https://docs.dagster.io/assets/images/asset-pool-tag-fd5900b211765e971bd379b0395edc67.png)

Once you have assigned your assets and ops to a concurrency pool, you can configure a pool limit for that pool in your deployment by using the [Dagster UI](https://docs.dagster.io/guides/operate/webserver) or the [`dagster` CLI](https://docs.dagster.io/api/clis/cli).

To specify a limit for the pool "database" using the UI, navigate to the `Deployments` → `Concurrency` settings page and click the `Add pool limit` button:

![Setting the pool limit](https://docs.dagster.io/assets/images/add-pool-ui-202927770b0febe9c7129b682a0ac3e6.png)

To specify a limit for the pool "database" using the `dagster` CLI, use:

```markdown
dagster instance concurrency set database 1
```

## Limit the number of runs that can be in progress for a set of ops

You can also use concurrency pools to limit the number of in progress runs containing those assets or ops. You can follow the steps in the [Limit the number of assets or ops actively in execution across all runs](https://docs.dagster.io/guides/operate/#limit-the-number-of-assets-or-ops-actively-executing-across-all-runs) section to assign your assets and ops to pools and to configure the desired limit.

Once you have assigned your assets and ops to your pool, you can change your deployment settings to set the pool enforcement granularity. To limit the total number of runs containing a specific op at any given time (instead of the total number of ops actively executing), we need to set the pool granularity to `run`.

- Dagster Core, add the following to your [dagster.yaml](https://docs.dagster.io/deployment/oss/dagster-yaml)
- In Dagster+, add the following to your [deployment settings](https://docs.dagster.io/deployment/dagster-plus/deploying-code/full-deployments/full-deployment-settings-reference)
```yaml
concurrency:
  pools:
    granularity: 'run'
```

Without this granularity set, the default granularity is set to the `op`. This means that for a pool `foo` with a limit `1`, we enforce that only one op is executing at a given time across all runs, but the number of runs in progress is unaffected by the pool limit.

### Setting a default limit for concurrency pools

- Dagster+: Edit the `concurrency` config in deployment settings via the [Dagster+ UI](https://docs.dagster.io/guides/operate/webserver) or the [`dagster-cloud` CLI](https://docs.dagster.io/api/clis/dagster-cloud-cli).
- Dagster Open Source: Use your instance's [dagster.yaml](https://docs.dagster.io/deployment/oss/dagster-yaml)
```yaml
concurrency:
  pools:
    default_limit: 1
```

## Limit the number of runs that can be in progress by run tag

You can also limit the number of in progress runs by run tag. This is useful for limiting sets of runs independent of which assets or ops it is executing. For example, you might want to limit the number of in-progress runs for a particular schedule. Or, you might want to limit the number of in-progress runs for all backfills.

```yaml
concurrency:
  runs:
    tag_concurrency_limits:
      - key: 'dagster/sensor_name'
        value: 'my_cool_sensor'
        limit: 5
      - key: 'dagster/backfill'
        limit: 10
```

### Limit the number of runs that can be in progress by unique tag value

To apply separate limits to each unique value of a run tag, set a limit for each unique value using `applyLimitPerUniqueValue`. For example, instead of limiting the number of backfill runs across all backfills, you may want to limit the number of runs for each backfill in progress:

```yaml
concurrency:
  runs:
    tag_concurrency_limits:
      - key: 'dagster/backfill'
        value:
          applyLimitPerUniqueValue: true
        limit: 10
```

## Limit the number of ops concurrently executing for a single run

While pool limits allow you to [limit the number of ops executing across all runs](https://docs.dagster.io/guides/operate/#limit-the-number-of-assets-or-ops-actively-executing-across-all-runs), to limit the number of ops executing *within a single run*, you need to configure your [run executor](https://docs.dagster.io/guides/operate/run-executors). You can limit concurrency for ops and assets in runs, by using `max_concurrent` in the run config, either in Python or using the Launchpad in the Dagster UI.

### Limit concurrent execution for a specific job

```python
src/<project_name>/defs/assets.pyimport time

import dagster as dg

@dg.asset
def first_asset(context: dg.AssetExecutionContext):
    time.sleep(75)
    context.log.info("first asset executing")

@dg.asset
def second_asset(context: dg.AssetExecutionContext):
    time.sleep(75)
    context.log.info("second asset executing")

@dg.asset
def third_asset(context: dg.AssetExecutionContext):
    time.sleep(75)
    context.log.info("third asset executing")

# limits concurrent asset execution for \`my_job\` runs to 2, overrides the limit set on the Definitions object
my_job = dg.define_asset_job(
    name="my_job",
    selection=[first_asset, second_asset, third_asset],
    executor_def=dg.multiprocess_executor.configured({"max_concurrent": 2}),
)
```

### Limit concurrent execution for all runs in a code location

```python
src/<project_name>/defs/executor.pyimport dagster as dg

@dg.definitions
def executor() -> dg.Definitions:
    return dg.Definitions(
        executor=dg.multiprocess_executor.configured({"max_concurrent": 4})
    )
```

## Prevent runs from starting if another run is already occurring (advanced)

You can use Dagster's rich metadata to use a schedule or a sensor to only start a run when there are no currently running jobs.

```python
src/<project_name>/defs/assets.pyimport time

import dagster as dg

@dg.asset
def first_asset(context: dg.AssetExecutionContext):
    # sleep so that the asset takes some time to execute
    time.sleep(75)
    context.log.info("First asset executing")

my_job = dg.define_asset_job("my_job", [first_asset])

@dg.schedule(
    job=my_job,
    # Runs every minute to show the effect of the concurrency limit
    cron_schedule="* * * * *",
)
def my_schedule(context):
    # Find runs of the same job that are currently running
    run_records = context.instance.get_run_records(
        dg.RunsFilter(
            job_name="my_job",
            statuses=[
                dg.DagsterRunStatus.QUEUED,
                dg.DagsterRunStatus.NOT_STARTED,
                dg.DagsterRunStatus.STARTING,
                dg.DagsterRunStatus.STARTED,
            ],
        )
    )
    # skip a schedule run if another run of the same job is already running
    if len(run_records) > 0:
        return dg.SkipReason(
            "Skipping this run because another run of the same job is already running"
        )
    return dg.RunRequest()
```

## Troubleshooting

When limiting concurrency, you might run into some issues until you get the configuration right.

### Runs going to STARTED status and skipping QUEUED

If you are running a version older than `1.10.0`, you may need to manually configure your deployment to enable run queueing by setting the `run_queue` key in your instance's settings. In the Dagster UI, navigate to **Deployment > Configuration** and verify that the `run_queue` key is set.

### Runs remaining in QUEUED status

The possible causes for runs remaining in `QUEUED` status depend on whether you're using Dagster+ or Dagster Open Source.

Ask Dagster AI

> Source: `docs/data_engineering/dagster/Data Ingestion Patterns_ Push, Pull & Poll Explained _ Dagster.md`

---
title: "Data Ingestion Patterns: Push, Pull & Poll Explained | Dagster"
source: "https://dagster.io/blog/data-ingestion-patterns-when-to-use-push-pull-and-poll"
author:
published:
created: 2025-12-24
description: "Learn when to use push, pull, and poll data ingestion patterns with practical code examples in Dagster. Build reliable, scalable data pipelines with the right pattern for your use case."
tags:
  - "clippings"
---
### A practical guide to choosing between push, pull, and poll data ingestion patterns. With real Dagster code examples to help you build reliable, maintainable pipelines.

## Ingestion Woes

First things are usually first. Often, the discourse around data engineering centers on high-performance tools and the latest AI benchmarks. However, when it comes to data engineering, getting your data to work is non-trivial and requires more engineering effort than you expect.

Most teams treat ingestion as an afterthought, building one-off solutions that don't scale. When a source changes its API, when a partner misses a delivery, when you need to backfill historical data, you're stuck debugging custom code instead of leveraging proven patterns.

Solving ingestion from source systems by hand rolling your own solution is a data engineering right of passage. You should try to do it at least once, and you will gain a greater appreciation for managed solutions like Fivetran and open-source ones like Sling and dlt.

## Why Ingestion Patterns Matter

### The Foundation of Everything

Data ingestion is the entry point for your entire data platform. Every downstream operation: transformation, modeling, analytics, machine learning, and AI depends on data arriving reliably, on time, and in the right format. Get ingestion wrong, and you're fighting fires downstream forever.

What makes it tricky is that you are often more beholden to systems that don't have analytics in mind. Data APIs that aren't idempotent, inconsistent authentication processes, and figuring out how deletes are handled. Because of this, you, as the data engineer, need to engineer solutions that work around these constraints to provide high-quality data to downstream processes.

### The Three Fundamental Patterns

Most data ingestion approaches fall into three fundamental patterns: **Push**, **Pull**, and **Poll**. Each reflects a different approach to data flow, ownership, and operational responsibility. I created an example projec using these different methods [here](https://github.com/dagster-io/dagster/tree/master/examples/ingestion-patterns).

**Push-based ingestion:** The source system initiates the transfer. You're the passive receiver. This approach works well when you have contractual agreements with data providers, but it relinquishes control over timing and volume. The most common pattern is for a vendor to dump data into durable object storage, such as Amazon S3.

**Pull-based ingestion:** Your platform initiates the transfer. You control [schedules](https://docs.dagster.io/concepts/automation/schedules), data windows, and backfills. This is the default for most data engineering teams, but it requires source systems to expose APIs or support queries.

**Polling-based ingestion:** You frequently check for new data, requesting only changes since the last check. This enables near real-time architectures but adds complexity around state management and duplicate handling.

Most of the time, the source system you are working with determines which pattern you are going to use

### Why This Matters Now

Modern data platforms ingest from dozens of sources: SaaS tools, partner databases, internal applications, and streaming services. Without consistent patterns, you end up with:

\- **Inconsistent error handling:** Some sources retry automatically, others fail silently

\- **No visibility:** Different monitoring approaches for each source

\- **Maintenance burden:** Custom code for every integration

\- **Data quality issues:** Inconsistent validation and schema management

The right pattern, applied consistently, gives you reliability, observability, and maintainability. Having the wrong or no pattern can lead to technical debt and operational headaches.

## Understanding Push, Pull, and Poll

### Push-Based Ingestion

In push-based ingestion, the data producer initiates the transfer, sending data to your platform without an explicit request. The source system controls timing, volume, and format.

**When to use push:**

\- You have contractual agreements with data providers

\- Sources can deliver data via webhooks or direct API calls

\- Real-time or near-real-time delivery is required

\- You want to minimize compute costs (source pays for delivery)

**Advantages:**

\- Immediate delivery when data is available

\- Source system controls timing and cadence

\- Lower compute costs (no polling overhead)

\- Works well for event-driven architectures

**Challenges:**

\- Less control over timing and volume

\- Must handle bursts and spikes gracefully

\- Schema drift from source changes

\- Requires robust error handling and idempotency

### Pull-Based Ingestion

Pull-based ingestion is controlled by your platform. You initiate the import process, requesting data from the source at regular intervals or on demand.

**When to use pull:**

\- You need control over schedules and data windows

\- Source systems provide APIs or support direct queries

\- Historical backfills and retroactive corrections are common

\- Data freshness requirements are predictable

**Advantages**:

\- Full control over timing, volume, and scope

\- Easy to implement backfills and replays

\- Standardized scheduling and error handling

\- Works well with batch processing architectures

**Challenges:**

\- Must handle duplicate data if reprocessing

\- Risk of missing records due to scheduling issues

\- Requires explicit tracking of extracted data

\- Source system must be queryable or expose APIs

### Polling-Based Ingestion

Polling combines push and pull: you frequently check for new data, but request only changes or updates since the last check rather than entire datasets.

**When to use polling:**

\- Near real-time or event-driven responsiveness is required

\- Working with message queues (Kafka, Pulsar) or change data capture (CDC)

\- Need precise control over data flow with low latency

\- Source systems support incremental queries or event streams

**Advantages:**

\- Responsive architectures with low end-to-end latency

\- Precise control over data flow

\- Efficient processing (only new data)

\- Works well with streaming and event-driven architectures

**Challenges**:

\- Must reliably record state (offsets, timestamps, markers)

\- Handle missed or duplicate messages

\- Manage variations in poll intervals or failures

\- More complex than simple pull patterns

## Practical Implementation: Building Ingestion Patterns with Dagster

### Setting Up Push-Based Ingestion

Push-based ingestion in Dagster typically involves exposing an API endpoint that receives data from external sources. You'll utilize Dagster's [resources](https://docs.dagster.io/concepts/resources) to handle incoming requests and [assets](https://docs.dagster.io/concepts/assets), processing the data accordingly.

```python
from datetime import datetime
from typing import Any

import dagster as dg
import pandas as pd
from dagster_duckdb import DuckDBResource

from ingestion_patterns.resources import WebhookStorageResource

class WebhookPayloadConfig(dg.Config):
    """Configuration for webhook payload processing."""

    source_id: str = "default"
    validate_schema: bool = True

@dg.asset
def process_webhook_data(
    context: dg.AssetExecutionContext,
    config: WebhookPayloadConfig,
    duckdb: DuckDBResource,
    webhook_storage: WebhookStorageResource,
) -> dict[str, Any]:
    """Process data received via webhook push and store in DuckDB.

    This asset processes pending webhook payloads from storage,
    validates them, ensures idempotency, and stores in DuckDB.
    """
    # Retrieve pending payloads for this source using the resource
    pending = webhook_storage.get_pending_payloads(config.source_id)

    if not pending:
        context.log.info(f"No pending payloads for source: {config.source_id}")
        return {"processed": [], "count": 0, "duplicates": 0}

    context.log.info(f"Processing {len(pending)} pending payloads from {config.source_id}")

    processed = []
    duplicates = 0
    invalid = 0

    # Track processed IDs for idempotency
    seen_ids: set[str] = set()

    for payload in pending:
        # Validate required fields
        if config.validate_schema:
            if not _validate_payload_schema(payload):
                context.log.warning(f"Invalid payload schema: {payload.get('id', 'unknown')}")
                invalid += 1
                continue

        # Idempotency check: skip if we've already processed this ID
        payload_id = payload.get("id")
        if payload_id is None:
            context.log.warning("Payload missing ID field")
            invalid += 1
            continue

        if payload_id in seen_ids:
            context.log.warning(f"Duplicate payload ID: {payload_id}")
            duplicates += 1
            continue

        seen_ids.add(str(payload_id))

        # Process the payload
        processed_item = {
            "id": payload_id,
            "source": config.source_id,
            "timestamp": payload.get("timestamp"),
            "data": str(payload.get("data", {})),  # Convert dict to string for DuckDB
            "processed_at": datetime.now().isoformat(),
            "run_id": context.run.run_id,
        }

        processed.append(processed_item)

    # Clear processed payloads from storage using the resource
    webhook_storage.clear_payloads(config.source_id)

    # Store processed payloads in DuckDB
    total_count = 0
    if processed:
        webhook_df = pd.DataFrame(processed)
        with duckdb.get_connection() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS ingestion")
            conn.register("webhook_df", webhook_df)
            # Check if table exists
            table_exists = conn.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='ingestion' AND table_name='webhook_data'"
            ).fetchone()
            if table_exists:
                conn.execute("INSERT INTO ingestion.webhook_data SELECT * FROM webhook_df")
            else:
                conn.execute("CREATE TABLE ingestion.webhook_data AS SELECT * FROM webhook_df")

            result = conn.execute("SELECT COUNT(*) FROM ingestion.webhook_data").fetchone()
            total_count = result[0] if result else 0
        context.log.info(f"Stored {len(processed)} payloads in ingestion.webhook_data")

    context.log.info(
        f"Processed {len(processed)} payloads, {duplicates} duplicates, {invalid} invalid"
    )

    context.add_output_metadata(
        {
            "processed_count": len(processed),
            "total_in_storage": total_count,
            "duplicates": duplicates,
            "invalid": invalid,
        }
    )

    return {
        "processed": processed,
        "count": len(processed),
        "duplicates": duplicates,
        "invalid": invalid,
    }

def _validate_payload_schema(payload: dict[str, Any]) -> bool:
    """Validate that payload has required schema fields."""
    required_fields = ["id", "timestamp", "data"]
    return all(field in payload for field in required_fields)
```

**Key considerations:**

\- Implement idempotency using unique identifiers from source

\- Use queues or storage buffers to handle bursts

\- Validate schema and data quality at ingestion time

\- Log all incoming payloads for observability

### Setting Up Pull-Based Ingestion

Pull-based ingestion gives you full control. You schedule assets to run at specific intervals, query source systems, and track what you've already processed.

```python
from datetime import datetime, timedelta
from typing import Any

import dagster as dg
import pandas as pd
from dagster._core.events import StepMaterializationData
from dagster_duckdb import DuckDBResource

from ingestion_patterns.resources import APIClientResource

class PullIngestionConfig(dg.Config):
    """Configuration for pull-based ingestion."""

    start_date: str | None = None  # ISO format
    end_date: str | None = None  # ISO format
    batch_size: int = 1000

@dg.asset
def extract_source_data(
    context: dg.AssetExecutionContext,
    config: PullIngestionConfig,
    duckdb: DuckDBResource,
    api_client: APIClientResource,
) -> pd.DataFrame:
    """Pull data from source system via API.

    This asset determines the date range to extract (defaulting to last 24 hours
    or using provided dates), queries the API, and returns a DataFrame.
    """
    # Determine date range
    end_date = datetime.now()

    # Try to get last successful extraction time from previous run
    last_event = context.instance.get_latest_materialization_event(context.asset_key)

    if last_event and last_event.dagster_event and not config.start_date:
        # Use last successful extraction time as start
        mat_data = last_event.dagster_event.event_specific_data
        if isinstance(mat_data, StepMaterializationData):
            metadata = mat_data.materialization.metadata
            if "last_extracted_timestamp" in metadata:
                timestamp_value = metadata["last_extracted_timestamp"].value
                start_date = datetime.fromisoformat(str(timestamp_value))
            else:
                start_date = end_date - timedelta(days=1)
        else:
            start_date = end_date - timedelta(days=1)
    elif config.start_date:
        start_date = datetime.fromisoformat(config.start_date)
    else:
        start_date = end_date - timedelta(days=1)

    if config.end_date:
        end_date = datetime.fromisoformat(config.end_date)

    context.log.info(f"Pulling data from {start_date} to {end_date}")

    # Pull data from API using the resource
    records = api_client.get_records(start_date, end_date)

    if not records:
        context.log.info("No new records found")
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Store raw data in DuckDB
    with duckdb.get_connection() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS ingestion")
        conn.register("raw_df", df)
        # Check if table exists
        table_exists = conn.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema='ingestion' AND table_name='raw_extract'"
        ).fetchone()
        if table_exists:
            conn.execute("INSERT INTO ingestion.raw_extract SELECT * FROM raw_df")
        else:
            conn.execute("CREATE TABLE ingestion.raw_extract AS SELECT * FROM raw_df")
        context.log.info(f"Stored {len(df)} records in ingestion.raw_extract")

    # Store metadata for next run
    context.add_output_metadata(
        {
            "record_count": len(df),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "last_extracted_timestamp": end_date.isoformat(),
        }
    )

    context.log.info(f"Extracted {len(df)} records")
    return df

@dg.asset_check(asset=extract_source_data)
def validate_extracted_data(
    context: dg.AssetCheckExecutionContext,
    extract_source_data: pd.DataFrame,
) -> dg.AssetCheckResult:
    """Validate extracted data quality.

    This asset check performs data quality checks:
    - Schema validation (required columns present)
    - Duplicate detection
    - Data type validation
    - Completeness checks (no nulls in required fields)
    """
    if extract_source_data.empty:
        return dg.AssetCheckResult(
            passed=True,
            metadata={"reason": "No data to validate"},
        )

    df = extract_source_data

    # Check required columns
    required_columns = ["id", "timestamp", "value"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        return dg.AssetCheckResult(
            passed=False,
            metadata={"missing_columns": missing},
            description=f"Missing required columns: {missing}",
        )

    # Check for duplicates
    duplicates = df.duplicated(subset=["id"])
    duplicate_count = int(duplicates.sum()) if duplicates.any() else 0

    # Check for nulls in required fields
    null_counts = df[required_columns].isnull().sum().to_dict()
    has_nulls = any(count > 0 for count in null_counts.values())

    # Determine pass/fail
    # We pass if there are no missing columns (duplicates and nulls are warnings)
    passed = len(missing) == 0

    return dg.AssetCheckResult(
        passed=passed,
        metadata={
            "record_count": len(df),
            "duplicate_count": duplicate_count,
            "null_counts": null_counts,
            "has_nulls": has_nulls,
        },
        description=(
            f"Validated {len(df)} records. Duplicates: {duplicate_count}, Has nulls: {has_nulls}"
        ),
    )

@dg.asset
def load_to_storage(
    context: dg.AssetExecutionContext,
    extract_source_data: pd.DataFrame,
    duckdb: DuckDBResource,
) -> dict[str, Any]:
    """Load extracted data to final storage table in DuckDB.

    This asset loads data after extraction. The validate_extracted_data
    asset check runs alongside to verify data quality.
    """
    if extract_source_data.empty:
        context.log.info("No data to load")
        return {"loaded": 0}

    df = extract_source_data

    # Clean data before loading: remove duplicates
    original_count = len(df)
    df = df.drop_duplicates(subset=["id"], keep="first")
    duplicates_removed = original_count - len(df)
    if duplicates_removed > 0:
        context.log.info(f"Removed {duplicates_removed} duplicate records")

    # Load to final table in DuckDB
    with duckdb.get_connection() as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS ingestion")
        conn.register("final_df", df)
        # Check if table exists
        table_exists = conn.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema='ingestion' AND table_name='final_data'"
        ).fetchone()
        if table_exists:
            conn.execute("INSERT INTO ingestion.final_data SELECT * FROM final_df")
        else:
            conn.execute("CREATE TABLE ingestion.final_data AS SELECT * FROM final_df")

        # Get total count
        result = conn.execute("SELECT COUNT(*) FROM ingestion.final_data").fetchone()
        total_count = result[0] if result else 0

    context.log.info(f"Loaded {len(df)} records to ingestion.final_data")

    context.add_output_metadata(
        {
            "loaded_count": len(df),
            "duplicates_removed": duplicates_removed,
            "total_in_storage": total_count,
            "load_timestamp": datetime.now().isoformat(),
        }
    )

    return {
        "loaded": len(df),
        "total": total_count,
        "timestamp": datetime.now().isoformat(),
    }
```

**Key considerations:**

\- Track last processed timestamp or ID to avoid duplicates

\- Implement incremental extraction when possible

\- Handle API rate limits and retries

\- Use Dagster's scheduling for predictable cadence

### Setting Up Polling-Based Ingestion

Polling requires maintaining state between runs. You'll track offsets, timestamps, or unique markers to ensure you only process new data.

```python
import json
from datetime import datetime
from typing import Any

import dagster as dg
import pandas as pd
from dagster._core.events import StepMaterializationData
from dagster_duckdb import DuckDBResource

from ingestion_patterns.resources import KafkaConsumerResource

class PollingConfig(dg.Config):
    """Configuration for polling-based ingestion."""

    kafka_topic: str = "transactions"
    poll_interval_seconds: int = 60
    max_records_per_poll: int = 100

@dg.asset
def poll_kafka_events(
    context: dg.AssetExecutionContext,
    config: PollingConfig,
    kafka_consumer: KafkaConsumerResource,
) -> dict[str, Any]:
    """Poll Kafka topic for new events since last checkpoint.

    This asset maintains state (last processed offset) and only processes
    new messages, ensuring idempotency and efficiency.
    """
    # Load last processed offset from previous materialization
    last_event = context.instance.get_latest_materialization_event(context.asset_key)

    start_offset = 0
    if last_event and last_event.dagster_event:
        # Extract offset from last materialization metadata
        mat_data = last_event.dagster_event.event_specific_data
        if isinstance(mat_data, StepMaterializationData):
            metadata = mat_data.materialization.metadata
            if "last_offset" in metadata:
                offset_value = metadata["last_offset"].value
                start_offset = int(str(offset_value)) + 1

    context.log.info(f"Polling from offset {start_offset}")

    # Poll for messages using the resource
    messages = kafka_consumer.poll_messages(
        topic=config.kafka_topic,
        timeout_seconds=config.poll_interval_seconds,
        max_records=config.max_records_per_poll,
        context=context,
    )

    if not messages:
        context.log.info("No new messages")
        return {
            "messages": [],
            "last_offset": start_offset - 1,
            "count": 0,
        }

    # Parse and validate messages
    parsed_messages = []
    seen_event_ids: set[str] = set()  # For idempotency

    for msg in messages:
        # Exception handling acceptable here: json.loads API uses exceptions for
        # invalid JSON (no way to LBYL check JSON validity without parsing)
        try:
            value = json.loads(msg["value"])
        except json.JSONDecodeError as e:
            context.log.warning(f"Failed to parse message at offset {msg['offset']}: {e}")
            continue

        event_id = value.get("event_id")

        # Idempotency check: skip if weve seen this event ID
        if event_id in seen_event_ids:
            context.log.warning(f"Duplicate event ID: {event_id}")
            continue

        seen_event_ids.add(event_id)

        parsed_messages.append(
            {
                "offset": msg["offset"],
                "partition": msg["partition"],
                "event_id": event_id,
                "event_type": value.get("event_type"),
                "data": value,
                "kafka_timestamp": msg["timestamp"],
            }
        )

    last_processed_offset = messages[-1]["offset"]

    context.log.info(
        f"Processed {len(parsed_messages)} messages, last offset: {last_processed_offset}"
    )

    # Store metadata for next run
    context.add_output_metadata(
        {
            "message_count": len(parsed_messages),
            "last_offset": last_processed_offset,
            "start_offset": start_offset,
            "poll_timestamp": datetime.now().isoformat(),
        }
    )

    return {
        "messages": parsed_messages,
        "last_offset": last_processed_offset,
        "count": len(parsed_messages),
    }

@dg.asset
def process_kafka_events(
    context: dg.AssetExecutionContext,
    poll_kafka_events: dict[str, Any],
    duckdb: DuckDBResource,
) -> dict[str, Any]:
    """Process polled Kafka events and store in DuckDB.

    This asset takes the polled messages and processes them,
    applying business logic and validation, then stores in DuckDB.
    """
    messages = poll_kafka_events.get("messages", [])

    if not messages:
        context.log.info("No messages to process")
        return {"processed": [], "count": 0}

    processed = []
    errors = []

    for msg in messages:
        # LBYL: Validate required fields exist before processing
        if "data" not in msg:
            context.log.error(f"Event {msg.get('event_id')} missing 'data' field")
            errors.append(
                {
                    "event_id": msg.get("event_id"),
                    "error": "Missing 'data' field",
                    "offset": msg.get("offset"),
                }
            )
            continue

        event_data = msg["data"]

        # LBYL: Validate transaction amount before processing
        amount = event_data.get("amount", 0)
        if amount < 0:
            context.log.error(f"Event {msg.get('event_id')} has invalid amount: {amount}")
            errors.append(
                {
                    "event_id": msg.get("event_id"),
                    "error": f"Invalid amount: {amount}",
                    "offset": msg.get("offset"),
                }
            )
            continue

        processed_item = {
            "event_id": msg["event_id"],
            "event_type": msg["event_type"],
            "amount": amount,
            "processed_at": datetime.now().isoformat(),
            "kafka_offset": msg["offset"],
        }

        processed.append(processed_item)

    # Store processed events in DuckDB
    if processed:
        events_df = pd.DataFrame(processed)
        with duckdb.get_connection() as conn:
            conn.execute("CREATE SCHEMA IF NOT EXISTS ingestion")
            conn.register("events_df", events_df)
            # Check if table exists
            table_exists = conn.execute(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='ingestion' AND table_name='kafka_events'"
            ).fetchone()
            if table_exists:
                conn.execute("INSERT INTO ingestion.kafka_events SELECT * FROM events_df")
            else:
                conn.execute("CREATE TABLE ingestion.kafka_events AS SELECT * FROM events_df")

            result = conn.execute("SELECT COUNT(*) FROM ingestion.kafka_events").fetchone()
            total_count = result[0] if result else 0
        context.log.info(f"Stored {len(processed)} events in ingestion.kafka_events")
    else:
        total_count = 0

    context.log.info(f"Processed {len(processed)} events, {len(errors)} errors")

    context.add_output_metadata(
        {
            "processed_count": len(processed),
            "total_in_storage": total_count,
            "error_count": len(errors),
            "errors": errors if errors else None,
        }
    )

    return {
        "processed": processed,
        "count": len(processed),
        "errors": errors,
    }
```

**Key considerations:**

\- Maintain state reliably (offsets, timestamps, markers)

\- Handle duplicate messages gracefully

\- Implement idempotency at the message level

\- Use sensors for responsive polling intervals

## Choosing the Right Pattern

### When to Use Push

Choose push when:

\- Source systems can deliver data proactively (webhooks, direct API calls)

\- You have contractual agreements with data providers

\- Real-time or near real-time delivery is required

\- You want to minimize compute costs (source pays for delivery)

**Trade-offs:** Less control over timing, must handle bursts, requires robust error handling.

### When to Use Pull

Choose pull when:

\- You need full control over schedules and data windows

\- Source systems provide APIs or support direct queries

\- Historical backfills and retroactive corrections are common

\- Data freshness requirements are predictable

**Trade-offs:** Must handle duplicates, risk of missing records, requires explicit tracking.

### When to Use Poll

Choose poll when:

\- Near real-time or event-driven responsiveness is required

\- Working with message queues or change data capture

\- Need precise control over data flow with low latency

\- Source systems support incremental queries or event streams

**Trade-offs:** More complex state management, must handle duplicates, requires reliable checkpointing.

### Hybrid Approaches

Most production systems use multiple patterns:

\- **Push for real-time events:** Webhooks, streaming data

\- **Pull for batch processing:** Scheduled extracts, API polling

\- **Poll for event streams:** Kafka, CDC, message queues

The key is consistency: use the same error handling, observability, and idempotency patterns across all approaches.

## Best Practices

### Idempotency: The Foundation of Reliable Ingestion

Idempotency is one of those words you see written down but never said. Anyway, it's the guarantee that processing the same input multiple times yields identical results is essential regardless of the ingestion pattern. Without it, retries, out-of-order delivery, or operator-initiated reprocessing can corrupt downstream data.

**How to implement:**

\- Track natural or synthetic keys (transaction IDs, timestamps)

\- Use window boundaries for batch processing

\- Implement deduplication logic that excludes already-processed records

\- Test idempotency explicitly: run the same ingestion twice and verify identical results

**Common pitfall**: Assuming your source system guarantees uniqueness. Always implement idempotency at the ingestion layer, even if the source claims to be idempotent.

### Schema Management

Schema drift is the unexpected format changes from source systems that breaks downstream pipelines. Proactive schema management and data quality checks minimize the disruption.

**How to implement:**

\- Validate schemas at ingestion time

\- Use schema registries for contract enforcement

\- Log schema changes and alert on unexpected modifications

\- Version your schemas and handle migrations gracefully

**Common pitfall:** Assuming schemas never change. They always do, especially with external sources.

### Observability and Monitoring

You can't fix what you can't see. Detailed logging, metric tracking, and failure alerting should cover all ingestion stages.

**What to monitor:**

\- Ingestion volume and latency

\- Error rates and failure modes

\- Schema validation failures

\- Duplicate detection rates

\- Source system availability

**Common pitfall:** Only monitoring success/failure. Monitor data quality, latency, and volume trends to catch issues before they become problems.

## Building Reliable Ingestion

Data ingestion patterns ultimately shape your operational model, your ability to scale, and your team's quality of life. Push, pull, and poll each have their place, and the best platforms use all three strategically.

The pattern you choose determines how much complexity you own versus how much you push to source systems. But regardless of pattern, the fundamentals remain: idempotency, schema management, observability, and error handling.

Some (most) of the time, the ROI just doesn’t work to build and *maintain* your own ingestion pipelines. Developing your own ingestion pipelines is a valuable engineering exercise, and everyone should have the opportunity to do it at least once. After that, though, you are taking time away from doing high-value engineering work, since the raw data in your data platform has to go through at least a few steps before being useful. That's why we would recommend that you check out managed solutions like [Fivetran](https://docs.dagster.io/integrations/libraries/fivetran) and [Airbyte](https://docs.dagster.io/integrations/libraries/airbyte) and open source solutions like [dlt](https://docs.dagster.io/integrations/libraries/dlt) and [sling](https://docs.dagster.io/integrations/libraries/sling). We use a mix of approaches in our [internal data platform](https://github.com/dagster-io/dagster-open-platform).

## Latest writings

The latest news, technologies, and resources from our team.

[View all posts](https://dagster.io/blog/#)

## Dagster Docs — ML & Real-Time


> Source: `docs/data_engineering/dagster/Building machine learning pipelines with Dagster _ Dagster Docs.md`

---
title: "Building machine learning pipelines with Dagster | Dagster Docs"
source: "https://docs.dagster.io/guides/build/ml-pipelines/ml-pipeline"
author:
published:
created: 2025-12-12
description: "Deploying and maintaining your machine learning pipelines in production using Dagster."
tags:
  - "clippings"
---
In this guide, we’ll walk you through how to take your machine learning models and deploy and maintain them in production using Dagster, reliably and efficiently.

We will work through building a machine learning pipeline, including using assets for different elements, how to automate model training, and monitoring your model's drift.

## Before you begin

This guide assumes you have familiarity with machine learning concepts and several Dagster concepts, including [asset definitions](https://docs.dagster.io/guides/build/assets/defining-assets) and [jobs](https://docs.dagster.io/guides/build/jobs).

## Benefits of building machine learning pipelines in Dagster

- Dagster makes iterating on machine learning models and testing easy, and it is designed to use during the development process.
- Dagster has a lightweight execution model means you can access the benefits of an orchestrator, like re-executing from the middle of a pipeline and parallelizing steps while you're experimenting.
- Dagster models data assets, not just tasks, so it understands the upstream and downstream data dependencies.
- Dagster is a one-stop shop for both the data transformations and the models that depend on the data transformations.

## Machine learning development

If you are already using Dagster for your ETL pipelines, it is a natural progression to build out and test your models in Dagster.

For this guide, we will be using Hacker News data. The machine learning model we will walk through takes the Hacker News stories and uses the titles to predict the number of comments that a story will generate. This will be a supervised model since we have the number of comments for all the previous stories.

The assets graph will look like this at the end of this guide (click to expand):

![ML asset DAG](https://docs.dagster.io/assets/images/ml_asset_dag-26a20f94de6668813cf7a3f6e7b84c2a.png)

### Ingesting data

First, we will create an asset that retrieves the most recent Hacker News records.

```python
import requests
import dagster as dg
import pandas as pd

@dg.asset
def hackernews_stories():
    # Get the max ID number from hacker news
    latest_item = requests.get(
        "https://hacker-news.firebaseio.com/v0/maxitem.json"
    ).json()
    # Get items based on story ids from the HackerNews items endpoint
    results = []
    scope = range(latest_item - 1000, latest_item)
    for item_id in scope:
        item = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
        ).json()
        results.append(item)
    # Store the results in a dataframe and filter on stories with valid titles
    df = pd.DataFrame(results)
    if len(df) > 0:
        df = df[df.type == "story"]
        df = df[~df.title.isna()]

    return df
```

### Transforming data

Now that we have a dataframe with all valid stories, we want to transform that data into something our machine learning model will be able to use.

The first step is taking the dataframe and splitting it into a [training and test set](https://en.wikipedia.org/wiki/Training,_validation,_and_test_data_sets). In some of your models, you also might choose to have an additional split for a validation set. The reason we split the data is so that we can have a test and/or a validation dataset that is independent of the training set. We can then use that dataset to see how well our model did.

```python
from sklearn.model_selection import train_test_split
import dagster as dg

@dg.multi_asset(outs={"training_data": dg.AssetOut(), "test_data": dg.AssetOut()})
def training_test_data(hackernews_stories):
    X = hackernews_stories.title
    y = hackernews_stories.descendants
    # Split the dataset to reserve 20% of records as the test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    return (X_train, y_train), (X_test, y_test)
```

Next, we will take both the training and test data subsets and [tokenize the titles](https://en.wikipedia.org/wiki/Lexical_analysis) e.g. take the words and turn them into columns with the frequency of terms for each record to create [features](https://en.wikipedia.org/wiki/Feature_\(machine_learning\)) for the data. To do this, we will be using the training set to fit the tokenizer. In this case, we are using [TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html) and then transforming both the training and test set based on that tokenizer.

```python
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

@dg.multi_asset(
    outs={"tfidf_vectorizer": dg.AssetOut(), "transformed_training_data": dg.AssetOut()}
)
def transformed_train_data(training_data):
    X_train, y_train = training_data
    # Initiate and fit the tokenizer on the training data and transform the training dataset
    vectorizer = TfidfVectorizer()
    transformed_X_train = vectorizer.fit_transform(X_train)
    transformed_X_train = transformed_X_train.toarray()
    y_train = y_train.fillna(0)
    transformed_y_train = np.array(y_train)
    return vectorizer, (transformed_X_train, transformed_y_train)

@dg.asset
def transformed_test_data(test_data, tfidf_vectorizer):
    X_test, y_test = test_data
    # Use the fitted tokenizer to transform the test dataset
    transformed_X_test = tfidf_vectorizer.transform(X_test)
    y_test = y_test.fillna(0)
    transformed_y_test = np.array(y_test)
    return transformed_X_test, transformed_y_test
```

We also transformed the dataframes into NumPy arrays and removed `nan` values to prepare the data for training.

### Training the model

At this point, we have `X_train`, `y_train`, `X_test`, and `y_test` ready to go for our model. To train our model, we can use any number of models from libraries like [sklearn](https://scikit-learn.org/), [TensorFlow](https://www.tensorflow.org/), and [PyTorch](https://pytorch.org/).

In our example, we will train an [XGBoost model](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor) to predict a numerical value.

### Evaluating our results

In our model assets, we evaluated each of the models on the test data and in this case, got the [score](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor.score) derived from comparing the predicted to actual results. Next, to predict the results, we'll create another asset that runs inference on the model more frequently than the model is re-trained.

Depending on what the objective of your ML model is, you can use this data to set alerts, save model performance history, and trigger retraining.

## Where to go from here

- [Managing machine learning models with Dagster](https://docs.dagster.io/guides/build/ml-pipelines/managing-ml) - This guide reviews ways to manage and maintain your machine learning (ML) models in Dagster
- Dagster integrates with [MLflow](https://docs.dagster.io/api/libraries/dagster-mlflow) that can be used to keep track of your models
- Dagster integrates with [Weights & Biases](https://docs.dagster.io/api/libraries/dagster-wandb). For an example that demonstrates how to use W&B's artifacts with Dagster, see the [Dagster repository](https://github.com/dagster-io/dagster/tree/master/examples/with_wandb).

> Source: `docs/data_engineering/dagster/Managing machine learning models with Dagster _ Dagster Docs.md`

---
title: "Managing machine learning models with Dagster | Dagster Docs"
source: "https://docs.dagster.io/guides/build/ml-pipelines/managing-ml"
author:
published:
created: 2025-12-12
description: "Managing and maintaining your machine learning (ML) models in Dagster."
tags:
  - "clippings"
---
This guide reviews ways to manage and maintain your machine learning (ML) models in Dagster.

Machine learning models are highly dependent on data at a point in time and must be managed to ensure they produce the same results as when you were in the development phase. In this guide, you'll learn how to:

- Automate training of your model when new data is available or when you want to use your model for predictions
- Integrate metadata about your model into the Dagster UI to display info about your model's performance

## Machine learning operations (MLOps)

You might have thought about your data sources, feature sets, and the best model for your use case. Inevitably, you start thinking about how to make this process sustainable and operational and deploy it to production. You want to make the machine learning pipeline self-sufficient and have confidence that the model you built is performing the way you expect. Thinking about machine learning operations, or MLOps, is the process of making your model maintainable and repeatable for a production use case.

### Automating ML model maintenance

Whether you have a large or small model, Dagster can help automate data refreshes and model training based on your business needs.

Declarative Automation can be used to update a machine learning model when the upstream data is updated. This can be done by setting the [`AutomationCondition`](https://docs.dagster.io/api/dagster/assets#dagster.AutomationCondition) to `eager`, which means that our machine learning model asset will be refreshed anytime our data asset is updated.

```python
import dagster as dg

@dg.asset
def my_data(): ...

@dg.asset(automation_condition=dg.AutomationCondition.eager())
def my_ml_model(my_data): ...
```

Some machine learning models might be more cumbersome to retrain; it also might be less important to update them as soon as new data arrives. For this, the `on_cron` condition may be used, which will cause the asset to be updated on a given cron schedule, but only after all of its upstream dependencies have been updated.

```python
import dagster as dg

@dg.asset
def my_other_data(): ...

@dg.asset(automation_condition=dg.AutomationCondition.on_cron("0 9 * * *"))
def my_other_ml_model(my_other_data): ...
```

### Monitoring

Integrating your machine learning models into Dagster allows you to see when the model and its data dependencies were refreshed, or when a refresh process has failed. By using Dagster to monitor performance changes and process failures on your ML model, it becomes possible to set up remediation paths, such as automated model retraining, that can help resolve issues like model drift.

In this example, the model is being evaluated against the previous model’s accuracy. If the model’s accuracy has improved, the model is returned for use in downstream steps, such as inference or deploying to production.

```python
import dagster as dg
from sklearn import linear_model
import numpy as np
from sklearn.model_selection import train_test_split

@dg.asset(output_required=False)
def conditional_machine_learning_model(context: dg.AssetExecutionContext):
    X, y = np.random.randint(5000, size=(5000, 2)), range(5000)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42
    )
    reg = linear_model.LinearRegression()
    reg.fit(X_train, y_train)

    # Get the model accuracy from metadata of the previous materilization of this machine learning model
    instance = context.instance
    materialization = instance.get_latest_materialization_event(
        dg.AssetKey(["conditional_machine_learning_model"])
    )
    if materialization is None:
        yield dg.Output(
            reg, metadata={"model_accuracy": float(reg.score(X_test, y_test))}
        )

    else:
        previous_model_accuracy = None
        if materialization.asset_materialization and isinstance(
            materialization.asset_materialization.metadata["model_accuracy"].value,
            float,
        ):
            previous_model_accuracy = float(
                materialization.asset_materialization.metadata["model_accuracy"].value
            )
        new_model_accuracy = reg.score(X_test, y_test)
        if (
            previous_model_accuracy is None
            or new_model_accuracy > previous_model_accuracy
        ):
            yield dg.Output(reg, metadata={"model_accuracy": float(new_model_accuracy)})
```

A [sensor](https://docs.dagster.io/guides/automate/sensors) can be set up that triggers if an asset fails to materialize. Alerts can be customized and sent through e-mail or natively through Slack. In this example, a Slack message is sent anytime the `ml_job` fails.

```python
import dagster as dg
from dagster_slack import make_slack_on_run_failure_sensor

ml_job = dg.define_asset_job("ml_training_job", selection=[ml_model])

slack_on_run_failure = make_slack_on_run_failure_sensor(
    channel="#ml_monitor_channel",
    slack_token=slack_token,
    monitored_jobs=([ml_job]),
)
```

Understanding the performance of your ML model is critical to both the model development process and production. [Metadata](https://docs.dagster.io/guides/build/assets/metadata-and-tags) can significantly enhance the usability of the Dagster UI to show what’s going on in a specific asset. Using metadata in Dagster is flexible, can be used for tracking evaluation metrics, and viewing the training accuracy progress over training iterations as a graph.

One of the easiest ways to utilize Dagster’s metadata is by using a dictionary to track different metrics that are relevant for an ML model.

Another way is to store relevant data for a single training iteration as a graph that you can view directly from the Dagster UI. In this example, a function is defined that uses data produced by a machine learning model to plot an evaluation metric as the model goes through the training process and render that in the Dagster UI.

Dagster’s [`MetadataValue`](https://docs.dagster.io/api/dagster/metadata#dagster.MetadataValue) types enable types such as tables, URLs, notebooks, Markdown, etc. In the following example, the Markdown metadata type is used to generate plots. Each plot will show a specific evaluation metric’s performance throughout each training iteration also known as an epoch during the training cycle.

```python
import dagster as dg
import seaborn
import matplotlib.pyplot as plt
import base64
from io import BytesIO

def make_plot(eval_metric):
    plt.clf()
    training_plot = seaborn.lineplot(eval_metric)
    fig = training_plot.get_figure()
    buffer = BytesIO()
    fig.savefig(buffer)
    image_data = base64.b64encode(buffer.getvalue())
    return dg.MetadataValue.md(f"![img](data:image/png;base64,{image_data.decode()})")
```

In this example, a dictionary is used called `metadata` to store the Markdown plots and the score value in Dagster.

In the Dagster UI, the `xgboost_comments_model` has the metadata rendered. Numerical values, such as the `score (mean_absolute_error)` will be logged and plotted for each materialization, which can be useful to understand the score over time for machine learning models.

![Managing ML in the UI](https://docs.dagster.io/assets/images/managing_ml_ui-2944f895ce0916e41c8e28a8b1d145b7.png)

The Markdown plots are also available to inspect the evaluation metrics during the training cycle by clicking on **\[Show Markdown\]**:

![Markdown plot in the UI](https://docs.dagster.io/assets/images/plot_ui-55e26b07af931b531609ddac95986fa1.png)

## Tracking model history

Viewing previous versions of a machine learning model can be useful to understand the evaluation history or referencing a model that was used for inference. Using Dagster will enable you to understand:

- What data was used to train the model
- When the model was refreshed
- The code version and ML model version was used to generate the predictions used for predicted values

In Dagster, each time an asset is materialized, the metadata and model are stored. Dagster registers the code version, data version and source data for each asset, so understanding what data was used to train a model is linked.

In the screenshot below, each materialization of `xgboost_comments_model` and the path for where each iteration of the model is stored.

![Asset materialization for xgboost_components_model](https://docs.dagster.io/assets/images/assets_materilization-33b59a34b7238658cafc1012410ed84f.png)

Any plots generated through the asset's metadata can be viewed in the metadata section. In this example, the plots of `score (mean_absolute_error)` are available for analysis.

![Metadata plot](https://docs.dagster.io/assets/images/metadata_plot-ecd504c22d1e0709b4c79659aedb4f0b.png)

> Source: `docs/data_engineering/dagster/Real-time system _ Dagster Docs.md`

---
title: "Real-time system | Dagster Docs"
source: "https://docs.dagster.io/examples/reference-architectures/real-time"
author:
published:
created: 2025-12-20
description: "A real-time system that detects abandoned carts and sends notifications to a marketing platform."
tags:
  - "clippings"
---
## Objective

Build an abandoned cart notification system that ingests customer data (Postgres) alongside real-time cart data (Kafka). A real-time view (ClickHouse) calculates which users have cart items that haven't been included in an order within the past hour. Newly identified abandoned carts are then sent downstream to the marketing platform (Braze).

## Architecture

    <svg id="mermaid-svg-9156476" width="100%" xmlns="http://www.w3.org/2000/svg" class="flowchart" style="max-width: 642.9166870117188px;" viewBox="0 0 642.9166870117188 274" role="graphics-document document" aria-roledescription="flowchart-v2"><g><marker id="mermaid-svg-9156476_flowchart-v2-pointEnd" class="marker flowchart-v2" viewBox="0 0 10 10" refX="5" refY="5" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" class="arrowMarkerPath" style="stroke-width: 1px; stroke-dasharray: 1px, 0px;"></path></marker><marker id="mermaid-svg-9156476_flowchart-v2-pointStart" class="marker flowchart-v2" viewBox="0 0 10 10" refX="4.5" refY="5" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" orient="auto"><path d="M 0 5 L 10 10 L 10 0 z" class="arrowMarkerPath" style="stroke-width: 1px; stroke-dasharray: 1px, 0px;"></path></marker><marker id="mermaid-svg-9156476_flowchart-v2-circleEnd" class="marker flowchart-v2" viewBox="0 0 10 10" refX="11" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto"><circle cx="5" cy="5" r="5" class="arrowMarkerPath" style="stroke-width: 1px; stroke-dasharray: 1px, 0px;"></circle></marker><marker id="mermaid-svg-9156476_flowchart-v2-circleStart" class="marker flowchart-v2" viewBox="0 0 10 10" refX="-1" refY="5" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto"><circle cx="5" cy="5" r="5" class="arrowMarkerPath" style="stroke-width: 1px; stroke-dasharray: 1px, 0px;"></circle></marker><marker id="mermaid-svg-9156476_flowchart-v2-crossEnd" class="marker cross flowchart-v2" viewBox="0 0 11 11" refX="12" refY="5.2" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto"><path d="M 1,1 l 9,9 M 10,1 l -9,9" class="arrowMarkerPath" style="stroke-width: 2px; stroke-dasharray: 1px, 0px;"></path></marker><marker id="mermaid-svg-9156476_flowchart-v2-crossStart" class="marker cross flowchart-v2" viewBox="0 0 11 11" refX="-1" refY="5.2" markerUnits="userSpaceOnUse" markerWidth="11" markerHeight="11" orient="auto"><path d="M 1,1 l 9,9 M 10,1 l -9,9" class="arrowMarkerPath" style="stroke-width: 2px; stroke-dasharray: 1px, 0px;"></path></marker><g class="root"><g class="clusters"></g><g class="edgePaths"><path d="M127.067,60L131.233,60C135.4,60,143.733,60,151.4,60C159.067,60,166.067,60,169.567,60L173.067,60" id="L_PG_DL_0" class="edge-thickness-thick edge-pattern-solid edge-thickness-normal edge-pattern-solid flowchart-link" style=";" data-edge="true" data-et="edge" data-id="L_PG_DL_0" data-points="W3sieCI6MTI3LjA2NjY2NTY0OTQxNDA2LCJ5Ijo2MH0seyJ4IjoxNTIuMDY2NjY1NjQ5NDE0MDYsInkiOjYwfSx7IngiOjE3Ny4wNjY2NjU2NDk0MTQwNiwieSI6NjB9XQ==" marker-end="url(#mermaid-svg-9156476_flowchart-v2-pointEnd)"></path><path d="M287.067,60L291.233,60C295.4,60,303.733,60,312.467,63.744C321.201,67.488,330.335,74.976,334.901,78.72L339.468,82.464" id="L_DL_CH_0" class="edge-thickness-thick edge-pattern-solid edge-thickness-normal edge-pattern-solid flowchart-link" style=";" data-edge="true" data-et="edge" data-id="L_DL_CH_0" data-points="W3sieCI6Mjg3LjA2NjY2NTY0OTQxNDA2LCJ5Ijo2MH0seyJ4IjozMTIuMDY2NjY1NjQ5NDE0MDYsInkiOjYwfSx7IngiOjM0Mi41NjE3OTY1MTAzNzQ0LCJ5Ijo4NX1d" marker-end="url(#mermaid-svg-9156476_flowchart-v2-pointEnd)"></path><path d="M282.067,214L287.067,214C292.067,214,302.067,214,311.634,210.256C321.201,206.512,330.335,199.024,334.901,195.28L339.468,191.536" id="L_KF_CH_0" class="edge-thickness-thick edge-pattern-solid edge-thickness-normal edge-pattern-solid flowchart-link" style=";" data-edge="true" data-et="edge" data-id="L_KF_CH_0" data-points="W3sieCI6MjgyLjA2NjY2NTY0OTQxNDA2LCJ5IjoyMTR9LHsieCI6MzEyLjA2NjY2NTY0OTQxNDA2LCJ5IjoyMTR9LHsieCI6MzQyLjU2MTc5NjUxMDM3NDQsInkiOjE4OX1d" marker-end="url(#mermaid-svg-9156476_flowchart-v2-pointEnd)"></path><path d="M474.917,137L479.083,137C483.25,137,491.583,137,499.25,137C506.917,137,513.917,137,517.417,137L520.917,137" id="L_CH_BZ_0" class="edge-thickness-thick edge-pattern-solid edge-thickness-normal edge-pattern-solid flowchart-link" style=";" data-edge="true" data-et="edge" data-id="L_CH_BZ_0" data-points="W3sieCI6NDc0LjkxNjY3MTc1MjkyOTcsInkiOjEzN30seyJ4Ijo0OTkuOTE2NjcxNzUyOTI5NywieSI6MTM3fSx7IngiOjUyNC45MTY2NzE3NTI5Mjk3LCJ5IjoxMzd9XQ==" marker-end="url(#mermaid-svg-9156476_flowchart-v2-pointEnd)"></path></g><g class="edgeLabels"><g class="edgeLabel"><g class="label" data-id="L_PG_DL_0" transform="translate(0, 0)"></g></g><g class="edgeLabel"><g class="label" data-id="L_DL_CH_0" transform="translate(0, 0)"></g></g><g class="edgeLabel"><g class="label" data-id="L_KF_CH_0" transform="translate(0, 0)"></g></g><g class="edgeLabel"><g class="label" data-id="L_CH_BZ_0" transform="translate(0, 0)"></g></g></g><g class="nodes"><g class="node default" id="flowchart-PG-0" transform="translate(67.53333282470703, 60)"><rect class="basic label-container" style="" x="-59.53333282470703" y="-52" width="119.06666564941406" height="104"></rect><g class="label" style="" transform="translate(-29.53333282470703, -37)"><rect></rect><foreignObject width="59.06666564941406" height="74"><img xmlns="http://www.w3.org/1999/xhtml" src="https://docs.dagster.io/images/examples/icons/postgres.svg" width="50" height="50"></foreignObject></g></g> <g class="node default" id="flowchart-CH-1" transform="translate(405.9916687011719, 137)"><rect class="basic label-container" style="" x="-68.92500305175781" y="-52" width="137.85000610351562" height="104"></rect><g class="label" style="" transform="translate(-38.92500305175781, -37)"><rect></rect><foreignObject width="77.85000610351562" height="74"><img xmlns="http://www.w3.org/1999/xhtml" src="https://docs.dagster.io/images/examples/icons/clickhouse.svg" width="50" height="50"></foreignObject></g></g> <g class="node default" id="flowchart-DL-2" transform="translate(232.06666564941406, 60)"><rect class="basic label-container" style="" x="-55" y="-52" width="110" height="104"></rect><g class="label" style="" transform="translate(-25, -37)"><rect></rect><foreignObject width="50" height="74"><img xmlns="http://www.w3.org/1999/xhtml" src="https://docs.dagster.io/images/examples/icons/dlthub.jpeg" width="50" height="50"></foreignObject></g></g> <g class="node default" id="flowchart-KF-3" transform="translate(232.06666564941406, 214)"><rect class="basic label-container" style="" x="-50" y="-52" width="100" height="104"></rect><g class="label" style="" transform="translate(-20, -37)"><rect></rect><foreignObject width="40" height="74"><img xmlns="http://www.w3.org/1999/xhtml" src="https://docs.dagster.io/images/examples/icons/kafka.svg" width="50" height="50"></foreignObject></g></g> <g class="node default" id="flowchart-BZ-4" transform="translate(579.9166717529297, 137)"><rect class="basic label-container" style="" x="-55" y="-52" width="110" height="104"></rect><g class="label" style="" transform="translate(-25, -37)"><rect></rect><foreignObject width="50" height="74"><img xmlns="http://www.w3.org/1999/xhtml" src="https://docs.dagster.io/images/examples/icons/braze.svg" width="50" height="50"></foreignObject></g></g></g></g></g></svg>

## Dagster Architecture

![2048 resolution](https://docs.dagster.io/assets/images/real-time-da239c1c2885e7edfaddabcdd8691979.png)

### 1\. Postgres ingestion with dlt

The integration between Postgres and Clickhouse is defined in dlt via YAML configuration in the code alongside the Dagster code. Dagster executes dlt on a schedule to extract stateful customer data into Clickhouse.

**Dagster Features**

- [Dagster dlt](https://docs.dagster.io/integrations/libraries/dlt)
- [Schedules](https://docs.dagster.io/guides/automate/schedules)

---

### 2\. Kafka ingestion

Real-time data on carts is brought into Clickhouse from the Kafka topic.

**Dagster Features**

- [Declarative Automation](https://docs.dagster.io/guides/automate/declarative-automation)

---

### 3\. Abandoned cart materialization

The customer data is combined with the real-time cart data to identify users who have not acted on their cart within the last hour. This materialized view lives in Clickhouse (which can be managed with a custom resource), capturing only abandoned carts from the last 3 hours to prevent the view from growing too large over time.

**Dagster Features**

- [Resources](https://docs.dagster.io/guides/build/external-resources)

---

### 4\. Notifications sent to the marketing tool

A sensor checks the abandoned cart view in Clickhouse for new abandoned carts which are sent to Braze via their API.

**Dagster Features**

- [Sensors](https://docs.dagster.io/guides/automate/sensors)

## Dagster Docs — Integrations (Official)


> Source: `docs/data_engineering/dagster/dlt (dagster-dlt) _ Dagster Docs.md`

---
title: "dlt (dagster-dlt) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-dlt"
author:
published:
created: 2025-12-12
description: "dlt (dagster-dlt) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
This library provides a Dagster integration with [dlt](https://dlthub.com/).

For more information on getting started, see the [Dagster & dlt](https://docs.dagster.io/integrations/libraries/dlt) documentation.

## Component

`class` dagster\_dlt.DltLoadCollectionComponent [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/components/dlt_load_collection/component.py#L71)

Expose one or more dlt loads to Dagster as assets.

execute [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/components/dlt_load_collection/component.py#L143)

Executes the dlt pipeline for the selected resources.

This method can be overridden in a subclass to customize the pipeline execution behavior, such as adding custom logging, validation, or error handling.

Parameters:

- **context** – The asset execution context provided by Dagster
- **dlt\_pipeline\_resource** – The DagsterDltResource used to run the dlt pipeline

Yields: Events from the dlt pipeline execution (e.g., AssetMaterialization, MaterializeResult)

Example:

Override this method to add custom logging during pipeline execution:

```python
from dagster_dlt import DltLoadCollectionComponent
from dagster import AssetExecutionContext

class CustomDltLoadCollectionComponent(DltLoadCollectionComponent):
    def execute(self, context, dlt_pipeline_resource):
        context.log.info("Starting dlt pipeline execution")
        yield from super().execute(context, dlt_pipeline_resource)
        context.log.info("dlt pipeline execution completed")
```

get\_asset\_spec [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/components/dlt_load_collection/component.py#L89)

Generates an AssetSpec for a given dlt resource.

This method can be overridden in a subclass to customize how dlt resources are converted to Dagster asset specs. By default, it delegates to the configured DagsterDltTranslator.

Parameters: **data** – The DltResourceTranslatorData containing information about the dlt source and resource being loadedReturns: An AssetSpec that represents the dlt resource as a Dagster asset

Example:

Override this method to add custom tags based on resource properties:

```python
from dagster_dlt import DltLoadCollectionComponent
from dagster import AssetSpec

class CustomDltLoadCollectionComponent(DltLoadCollectionComponent):
    def get_asset_spec(self, data):
        base_spec = super().get_asset_spec(data)
        return base_spec.replace_attributes(
            tags={
                **base_spec.tags,
                "source": data.source_name,
                "resource": data.resource_name
            }
        )
```

To use the dlt component, see the [dlt component integration guide](https://docs.dagster.io/integrations/libraries/dlt).

### YAML configuration

When you scaffold a dlt component definition, the following `defs.yaml` configuration file will be created:

```yaml
type: dagster_dlt.DltLoadCollectionComponent

attributes:
  loads:
    - source: .loads.my_load_source
      pipeline: .loads.my_load_pipeline
```

## Assets

@dagster\_dlt.dlt\_assets [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/asset_decorator.py#L56)

Asset Factory for using data load tool (dlt).

Parameters:

- **dlt\_source** (*DltSource*) – The DltSource to be ingested.
- **dlt\_pipeline** (*Pipeline*) – The dlt Pipeline defining the destination parameters.
- **name** (*Optional* *\[**str**\]**,* *optional*) – The name of the op.
- **group\_name** (*Optional* *\[**str**\]**,* *optional*) – The name of the asset group.
- **dagster\_dlt\_translator** ([*DagsterDltTranslator*](https://docs.dagster.io/api/libraries/#dagster_dlt.DagsterDltTranslator)*,* *optional*) – Customization object for defining asset parameters from dlt resources.
- **partitions\_def** (*Optional* *\[*[*PartitionsDefinition*](https://docs.dagster.io/api/dagster/partitions#dagster.PartitionsDefinition)*\]*) – Optional partitions definition.
- **backfill\_policy** (*Optional* *\[*[*BackfillPolicy*](https://docs.dagster.io/api/dagster/partitions#dagster.BackfillPolicy)*\]*) – If a partitions\_def is defined, this determines how to execute backfills that target multiple partitions. If a time window partition definition is used, this parameter defaults to a single-run policy.
- **op\_tags** (*Optional* *\[**Mapping* *\[**str**,* *Any**\]**\]*) – The tags for the underlying op.
- **pool** (*Optional* *\[**str**\]*) – A string that identifies the concurrency pool that governs the dlt assets’ execution.

Examples:

Loading Hubspot data to Snowflake with an auto materialize policy using the dlt verified source:

```python
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets

class HubspotDagsterDltTranslator(DagsterDltTranslator):
    @public
    def get_auto_materialize_policy(self, resource: DltResource) -> Optional[AutoMaterializePolicy]:
        return AutoMaterializePolicy.eager().with_rules(
            AutoMaterializeRule.materialize_on_cron("0 0 * * *")
        )

@dlt_assets(
    dlt_source=hubspot(include_history=True),
    dlt_pipeline=pipeline(
        pipeline_name="hubspot",
        dataset_name="hubspot",
        destination="snowflake",
        progress="log",
    ),
    name="hubspot",
    group_name="hubspot",
    dagster_dlt_translator=HubspotDagsterDltTranslator(),
)
def hubspot_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)
```

Loading Github issues to snowflake:

```python
from dagster_dlt import DagsterDltResource, dlt_assets

@dlt_assets(
    dlt_source=github_reactions(
        "dagster-io", "dagster", items_per_page=100, max_items=250
    ),
    dlt_pipeline=pipeline(
        pipeline_name="github_issues",
        dataset_name="github",
        destination="snowflake",
        progress="log",
    ),
    name="github",
    group_name="github",
)
def github_reactions_dagster_assets(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(context=context)
```

dagster\_dlt.build\_dlt\_asset\_specs [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/asset_decorator.py#L21)

Build a list of asset specs from a dlt source and pipeline.

Parameters:

- **dlt\_source** (*DltSource*) – dlt source object
- **dlt\_pipeline** (*Pipeline*) – dlt pipeline object
- **dagster\_dlt\_translator** (*Optional* *\[*[*DagsterDltTranslator*](https://docs.dagster.io/api/libraries/#dagster_dlt.DagsterDltTranslator)*\]*) – Allows customizing how to map dlt project to asset keys and asset metadata.

Returns: List\[AssetSpec\] list of asset specs from dlt source and pipeline

`class` dagster\_dlt.DagsterDltTranslator [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L24)

get\_asset\_key [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L91)

Defines asset key for a given dlt resource key and dataset name.

This method can be overridden to provide custom asset key for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: AssetKey of Dagster asset derived from dlt resource

get\_auto\_materialize\_policy [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L121)

Defines resource specific auto materialize policy.

This method can be overridden to provide custom auto materialize policy for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: The auto-materialize policy for a resourceReturn type: Optional\[AutoMaterializePolicy\]

get\_automation\_condition [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L153)

Defines resource specific automation condition.

This method can be overridden to provide custom automation condition for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: The automation condition for a resourceReturn type: Optional\[[AutomationCondition](https://docs.dagster.io/api/dagster/assets#dagster.AutomationCondition)\]

get\_deps\_asset\_keys [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L188)

Defines upstream asset dependencies given a dlt resource.

Defaults to a concatenation of resource.source\_name and resource.name.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: The Dagster asset keys upstream of dlt\_resource\_key.Return type: Iterable\[[AssetKey](https://docs.dagster.io/api/dagster/assets#dagster.AssetKey)\]

get\_description [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L225)

A method that takes in a dlt resource returns the Dagster description of the resource.

This method can be overridden to provide a custom description for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: The Dagster description for the dlt resource.Return type: Optional\[str\]

get\_group\_name [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L258)

A method that takes in a dlt resource and returns the Dagster group name of the resource.

This method can be overridden to provide a custom group name for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: A Dagster group name for the dlt resource.Return type: Optional\[str\]

get\_kinds [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L370)

A method that takes in a dlt resource and returns the kinds which should be attached. Defaults to the destination type and “dlt”.

This method can be overridden to provide custom kinds for a dlt resource.

Parameters:

- **resource** (*DltResource*) – dlt resource
- **destination** (*Destination*) – dlt destination

Returns: The kinds of the asset.Return type: Set\[str\]

Defines resource specific metadata.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: The custom metadata entries for this resource.Return type: Mapping\[str, Any\]

get\_owners [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/translator.py#L312)

A method that takes in a dlt resource and returns the Dagster owners of the resource.

This method can be overridden to provide custom owners for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: A sequence of Dagster owners for the dlt resource.Return type: Optional\[Sequence\[str\]\]

A method that takes in a dlt resource and returns the Dagster tags of the structure.

This method can be overridden to provide custom tags for a dlt resource.

Parameters: **resource** (*DltResource*) – dlt resourceReturns: A dictionary representing the Dagster tags for the dlt resource.

Return type: Optional\[Mapping\[str, str\]\]

## Resources

`class` dagster\_dlt.DagsterDltResource [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py#L29)

run [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-dlt/dagster_dlt/resource.py#L176)

Runs the dlt pipeline with subset support.

Parameters:

- **context** (*Union* *\[*[*OpExecutionContext*](https://docs.dagster.io/api/dagster/execution#dagster.OpExecutionContext)*,* [*AssetExecutionContext*](https://docs.dagster.io/api/dagster/execution#dagster.AssetExecutionContext)*\]*) – Asset or op execution context
- **dlt\_source** (*Optional* *\[**DltSource**\]*) – optional dlt source if resource is used from an @op
- **dlt\_pipeline** (*Optional* *\[**Pipeline**\]*) – optional dlt pipeline if resource is used from an @op
- **dagster\_dlt\_translator** (*Optional* *\[*[*DagsterDltTranslator*](https://docs.dagster.io/api/libraries/#dagster_dlt.DagsterDltTranslator)*\]*) – optional dlt translator if resource is used from an @op
- **\*\*kwargs** (*dict* *\[**str**,* *Any**\]*) – Keyword args passed to pipeline run method

Returns: An iterator of MaterializeResult or AssetMaterializationReturn type: DltEventIterator\[DltEventType\]

> Source: `docs/data_engineering/dagster/duckdb (dagster-duckdb) _ Dagster Docs.md`

---
title: "duckdb (dagster-duckdb) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-duckdb"
author:
published:
created: 2025-12-12
description: "duckdb (dagster-duckdb) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
This library provides an integration with the [DuckDB](https://duckdb.org/) database.

Related Guides:

- [Using Dagster with DuckDB guide](https://docs.dagster.io/integrations/libraries/duckdb)
- [DuckDB I/O manager reference](https://docs.dagster.io/integrations/libraries/duckdb/reference)

dagster\_duckdb.DuckDBIOManager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-duckdb/dagster_duckdb/io_manager.py#L137)

Base class for an IO manager definition that reads inputs from and writes outputs to DuckDB.

Examples:

```python
from dagster_duckdb import DuckDBIOManager
from dagster_duckdb_pandas import DuckDBPandasTypeHandler

class MyDuckDBIOManager(DuckDBIOManager):
    @staticmethod
    def type_handlers() -> Sequence[DbTypeHandler]:
        return [DuckDBPandasTypeHandler()]

@asset(
    key_prefix=["my_schema"]  # will be used as the schema in duckdb
)
def my_table() -> pd.DataFrame:  # the name of the asset will be the table name
    ...

Definitions(
    assets=[my_table],
    resources={"io_manager": MyDuckDBIOManager(database="my_db.duckdb")}
)
```

You can set a default schema to store the assets using the `schema` configuration value of the DuckDB I/O Manager. This schema will be used if no other schema is specified directly on an asset or op.

```python
Definitions(
    assets=[my_table],
    resources={"io_manager": MyDuckDBIOManager(database="my_db.duckdb", schema="my_schema")}
)
```

On individual assets, you an also specify the schema where they should be stored using metadata or by adding a `key_prefix` to the asset key. If both `key_prefix` and metadata are defined, the metadata will take precedence.

```python
@asset(
    key_prefix=["my_schema"]  # will be used as the schema in duckdb
)
def my_table() -> pd.DataFrame:
    ...

@asset(
    metadata={"schema": "my_schema"}  # will be used as the schema in duckdb
)
def my_other_table() -> pd.DataFrame:
    ...
```

For ops, the schema can be specified by including a “schema” entry in output metadata.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> pd.DataFrame:
    ...
```

If none of these is provided, the schema will default to “public”.

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the In or AssetIn.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: pd.DataFrame):
    # my_table will just contain the data from column "a"
    ...
```

Set DuckDB configuration options using the connection\_config field. See [https://duckdb.org/docs/sql/configuration.html](https://duckdb.org/docs/sql/configuration.html) for all available settings.

```python
Definitions(
    assets=[my_table],
    resources={"io_manager": MyDuckDBIOManager(database="my_db.duckdb",
                                               connection_config={"arrow_large_buffer_size": True})}
)
```

dagster\_duckdb.DuckDBResource ResourceDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-duckdb/dagster_duckdb/resource.py#L11)

Resource for interacting with a DuckDB database.

Examples:

```python
from dagster import Definitions, asset
from dagster_duckdb import DuckDBResource

@asset
def my_table(duckdb: DuckDBResource):
    with duckdb.get_connection() as conn:
        conn.execute("SELECT * from MY_SCHEMA.MY_TABLE")

Definitions(
    assets=[my_table],
    resources={"duckdb": DuckDBResource(database="path/to/db.duckdb")}
)
```

## Legacy

dagster\_duckdb.build\_duckdb\_io\_manager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-duckdb/dagster_duckdb/io_manager.py#L25)

Builds an IO manager definition that reads inputs from and writes outputs to DuckDB.

Parameters:

- **type\_handlers** (*Sequence* *\[**DbTypeHandler**\]*) – Each handler defines how to translate between DuckDB tables and an in-memory type - e.g. a Pandas DataFrame. If only one DbTypeHandler is provided, it will be used as the default\_load\_type.
- **default\_load\_type** (*Type*) – When an input has no type annotation, load it as this type.

Returns: IOManagerDefinition

Examples:

```python
from dagster_duckdb import build_duckdb_io_manager
from dagster_duckdb_pandas import DuckDBPandasTypeHandler

@asset(
    key_prefix=["my_schema"]  # will be used as the schema in duckdb
)
def my_table() -> pd.DataFrame:  # the name of the asset will be the table name
    ...

duckdb_io_manager = build_duckdb_io_manager([DuckDBPandasTypeHandler()])

Definitions(
    assets=[my_table]
    resources={"io_manager" duckdb_io_manager.configured({"database": "my_db.duckdb"})}
)
```

You can set a default schema to store the assets using the `schema` configuration value of the DuckDB I/O Manager. This schema will be used if no other schema is specified directly on an asset or op.

```python
Definitions(
    assets=[my_table]
    resources={"io_manager" duckdb_io_manager.configured(
        {"database": "my_db.duckdb", "schema": "my_schema"} # will be used as the schema
    )}
)
```

On individual assets, you an also specify the schema where they should be stored using metadata or by adding a `key_prefix` to the asset key. If both `key_prefix` and metadata are defined, the metadata will take precedence.

```python
@asset(
    key_prefix=["my_schema"]  # will be used as the schema in duckdb
)
def my_table() -> pd.DataFrame:
    ...

@asset(
    metadata={"schema": "my_schema"}  # will be used as the schema in duckdb
)
def my_other_table() -> pd.DataFrame:
    ...
```

For ops, the schema can be specified by including a “schema” entry in output metadata.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> pd.DataFrame:
    ...
```

If none of these is provided, the schema will default to “public”.

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the In or AssetIn.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: pd.DataFrame):
    # my_table will just contain the data from column "a"
    ...
```

> Source: `docs/data_engineering/dagster/github (dagster-github) _ Dagster Docs.md`

---
title: "github (dagster-github) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-github"
author:
published:
created: 2025-12-12
description: "github (dagster-github) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
This library provides an integration with GitHub Apps, to support performing various automation operations within your github repositories and with the tighter permissions scopes that github apps allow for vs using a personal token.

Presently, it provides a thin wrapper on the [github v4 graphql API](https://developer.github.com/v4).

To use this integration, you’ll first need to create a GitHub App for it.

1. **Create App**: Follow the instructions in [https://developer.github.com/apps/quickstart-guides/setting-up-your-development-environment/](https://developer.github.com/apps/quickstart-guides/setting-up-your-development-environment), You will end up with a private key and App ID, which will be used when configuring the `dagster-github` resource. **Note** you will need to grant your app the relevent permissions for the API requests you want to make, for example to post issues it will need read/write access for the issues repository permission, more info on GitHub application permissions can be found [here](https://developer.github.com/v3/apps/permissions)
2. **Install App**: Follow the instructions in [https://developer.github.com/apps/quickstart-guides/setting-up-your-development-environment/#step-7-install-the-app-on-your-account](https://developer.github.com/apps/quickstart-guides/setting-up-your-development-environment/#step-7-install-the-app-on-your-account)
3. **Find your installation\_id**: You can pull this from the GitHub app administration page, `https://github.com/apps/<app-name>/installations/<installation_id>`. **Note** if your app is installed more than once you can also programatically retrieve these IDs. Sharing your App ID and Installation ID is fine, but make sure that the Private Key for your app is stored securily.

## Posting Issues

Now, you can create issues in GitHub from Dagster with the GitHub resource:

```python
import os

from dagster import job, op
from dagster_github import GithubResource

@op
def github_op(github: GithubResource):
    github.get_client().create_issue(
        repo_name='dagster',
        repo_owner='dagster-io',
        title='Dagster\'s first github issue',
        body='this open source thing seems like a pretty good idea',
    )

@job(resource_defs={
     'github': GithubResource(
         github_app_id=os.getenv('GITHUB_APP_ID'),
         github_app_private_rsa_key=os.getenv('GITHUB_PRIVATE_KEY'),
         github_installation_id=os.getenv('GITHUB_INSTALLATION_ID')
 )})
def github_job():
    github_op()

github_job.execute_in_process()
```

Run the above code, and you’ll see the issue appear in GitHub:

GitHub enterprise users can provide their hostname in the run config. Provide `github_hostname` as part of your github config like below.

```python
GithubResource(
    github_app_id=os.getenv('GITHUB_APP_ID'),
    github_app_private_rsa_key=os.getenv('GITHUB_PRIVATE_KEY'),
    github_installation_id=os.getenv('GITHUB_INSTALLATION_ID'),
    github_hostname=os.getenv('GITHUB_HOSTNAME'),
)
```

By provisioning `GithubResource` as a Dagster resource, you can post to GitHub from within any asset or op execution.

## Executing GraphQL queries

```python
import os

from dagster import job, op
from dagster_github import github_resource

@op
def github_op(github: GithubResource):
    github.get_client().execute(
        query="""
        query get_repo_id($repo_name: String!, $repo_owner: String!) {
            repository(name: $repo_name, owner: $repo_owner) {
                id
            }
        }
        """,
        variables={"repo_name": repo_name, "repo_owner": repo_owner},
    )

@job(resource_defs={
     'github': GithubResource(
         github_app_id=os.getenv('GITHUB_APP_ID'),
         github_app_private_rsa_key=os.getenv('GITHUB_PRIVATE_KEY'),
         github_installation_id=os.getenv('GITHUB_INSTALLATION_ID')
 )})
def github_job():
    github_op()

github_job.execute_in_process()
```

## Resources

`class` dagster\_github.resources.GithubClient [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L104)

A client for interacting with the GitHub API.

This client handles authentication and provides methods for making requests to the GitHub API using an authenticated session.

Parameters:

- **client** (*requests.Session*) – The HTTP session used for making requests.
- **app\_id** (*int*) – The GitHub App ID.
- **app\_private\_rsa\_key** (*str*) – The private RSA key for the GitHub App.
- **default\_installation\_id** (*Optional* *\[**int**\]*) – The default installation ID for the GitHub App.
- **hostname** (*Optional* *\[**str**\]*) – The GitHub hostname, defaults to None.
- **installation\_tokens** (*Dict* *\[**Any**,* *Any**\]*) – A dictionary to store installation tokens.
- **app\_token** (*Dict* *\[**str**,* *Any**\]*) – A dictionary to store the app token.

create\_issue [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L291)

Create a new issue in the specified GitHub repository.

This method first retrieves the repository ID using the provided repository name and owner, then creates a new issue in that repository with the given title and body.

Parameters:

- **repo\_name** (*str*) – The name of the repository where the issue will be created.
- **repo\_owner** (*str*) – The owner of the repository where the issue will be created.
- **title** (*str*) – The title of the issue.
- **body** (*str*) – The body content of the issue.
- **installation\_id** (*Optional* *\[**int**\]*) – The installation ID to use for authentication.

Returns: The response data from the GitHub API containing the created issue details.Return type: Dict\[str, Any\]Raises: **RuntimeError** – If there are errors in the response from the GitHub API.

create\_pull\_request [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L383)

Create a new pull request in the specified GitHub repository.

This method creates a pull request from the head reference (branch) to the base reference (branch) in the specified repositories. It uses the provided title and body for the pull request description.

Parameters:

- **base\_repo\_name** (*str*) – The name of the base repository where the pull request will be created.
- **base\_repo\_owner** (*str*) – The owner of the base repository.
- **base\_ref\_name** (*str*) – The name of the base reference (branch) to which the changes will be merged.
- **head\_repo\_name** (*str*) – The name of the head repository from which the changes will be taken.
- **head\_repo\_owner** (*str*) – The owner of the head repository.
- **head\_ref\_name** (*str*) – The name of the head reference (branch) from which the changes will be taken.
- **title** (*str*) – The title of the pull request.
- **body** (*Optional* *\[**str**\]*) – The body content of the pull request. Defaults to None.
- **maintainer\_can\_modify** (*Optional* *\[**bool**\]*) – Whether maintainers can modify the pull request. Defaults to None.
- **draft** (*Optional* *\[**bool**\]*) – Whether the pull request is a draft. Defaults to None.
- **installation\_id** (*Optional* *\[**int**\]*) – The installation ID to use for authentication.

Returns: The response data from the GitHub API containing the created pull request details.Return type: Dict\[str, Any\]Raises: **RuntimeError** – If there are errors in the response from the GitHub API.

create\_ref [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L334)

Create a new reference (branch) in the specified GitHub repository.

This method first retrieves the repository ID and the source reference (branch or tag) using the provided repository name, owner, and source reference. It then creates a new reference (branch) in that repository with the given target name.

Parameters:

- **repo\_name** (*str*) – The name of the repository where the reference will be created.
- **repo\_owner** (*str*) – The owner of the repository where the reference will be created.
- **source** (*str*) – The source reference (branch or tag) from which the new reference will be created.
- **target** (*str*) – The name of the new reference (branch) to be created.
- **installation\_id** (*Optional* *\[**int**\]*) – The installation ID to use for authentication.

Returns: The response data from the GitHub API containing the created reference details.Return type: Dict\[str, Any\]Raises: **RuntimeError** – If there are errors in the response from the GitHub API.

execute [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L235)

Execute a GraphQL query against the GitHub API.

This method sends a POST request to the GitHub API with the provided GraphQL query and optional variables. It ensures that the appropriate installation token is included in the request headers.

Parameters:

- **query** (*str*) – The GraphQL query string to be executed.
- **variables** (*Optional* *\[**Dict* *\[**str**,* *Any**\]**\]*) – Optional variables to include in the query.
- **headers** (*Optional* *\[**Dict* *\[**str**,* *Any**\]**\]*) – Optional headers to include in the request.
- **installation\_id** (*Optional* *\[**int**\]*) – The installation ID to use for authentication.

Returns: The response data from the GitHub API.Return type: Dict\[str, Any\]Raises:

- **RuntimeError** – If no installation ID is provided and no default installation ID is set.
- **requests.exceptions.HTTPError** – If the request to the GitHub API fails.

get\_installations [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L173)

Retrieve the list of installations for the authenticated GitHub App.

This method makes a GET request to the GitHub API to fetch the installations associated with the authenticated GitHub App. It ensures that the app token is valid and includes it in the request headers.

Parameters: **headers** (*Optional* *\[**Dict* *\[**str**,* *Any**\]**\]*) – Optional headers to include in the request.Returns: A dictionary containing the installations data.Return type: Dict\[str, Any\]Raises: **requests.exceptions.HTTPError** – If the request to the GitHub API fails.

dagster\_github.resources.GithubResource ResourceDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L449)

A resource configuration class for GitHub integration.

This class provides configuration fields for setting up a GitHub Application, including the application ID, private RSA key, installation ID, and hostname.

Parameters:

- **github\_app\_id** (*int*) – The GitHub Application ID. For more information, see [https://developer.github.com/apps/](https://developer.github.com/apps/).
- **github\_app\_private\_rsa\_key** (*str*) – The private RSA key text for the GitHub Application. For more information, see [https://developer.github.com/apps/](https://developer.github.com/apps/).
- **github\_installation\_id** (*Optional* *\[**int**\]*) – The GitHub Application Installation ID. Defaults to None. For more information, see [https://developer.github.com/apps/](https://developer.github.com/apps/).
- **github\_hostname** (*Optional* *\[**str**\]*) – The GitHub hostname. Defaults to api.github.com. For more information, see [https://developer.github.com/apps/](https://developer.github.com/apps/).

## Legacy

dagster\_github.resources.github\_resource ResourceDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/libraries/dagster-github/dagster_github/resources.py#L523)

> Source: `docs/data_engineering/dagster/graphql (dagster-graphql) _ Dagster Docs.md`

---
title: "graphql (dagster-graphql) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-graphql"
author:
published:
created: 2025-12-12
description: "graphql (dagster-graphql) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
## Python Client

`class` dagster\_graphql.DagsterGraphQLClient [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/client.py#L38)

Official Dagster Python Client for GraphQL.

Utilizes the gql library to dispatch queries over HTTP to a remote Dagster GraphQL Server

As of now, all operations on this client are synchronous.

Intended usage:

```python
client = DagsterGraphQLClient("localhost", port_number=3000)
status = client.get_run_status(**SOME_RUN_ID**)
```

Parameters:

- **hostname** (*str*) – Hostname for the Dagster GraphQL API, like localhost or YOUR\_ORG\_HERE.dagster.cloud.
- **port\_number** (*Optional* *\[**int**\]*) – Port number to connect to on the host. Defaults to None.
- **transport** (*Optional* *\[**Transport**\]**,* *optional*) – A custom transport to use to connect to the GraphQL API with (e.g. for custom auth). Defaults to None.
- **use\_https** (*bool**,* *optional*) – Whether to use https in the URL connection string for the GraphQL API. Defaults to False.
- **timeout** (*int*) – Number of seconds before requests should time out. Defaults to 60.
- **headers** (*Optional* *\[**Dict* *\[**str**,* *str**\]**\]*) – Additional headers to include in the request. To use this client in Dagster Cloud, set the “Dagster-Cloud-Api-Token” header to a user token generated in the Dagster Cloud UI.

Raises: **ConnectionError** – if the client cannot connect to the host.

get\_run\_status [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/client.py#L302)

Get the status of a given Pipeline Run.

Parameters: **run\_id** (*str*) – run id of the requested pipeline run.Raises:

- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"PipelineNotFoundError"****,** **message****)** – if the requested run id is not found
- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"PythonError"****,** **message****)** – on internal framework errors

Returns: returns a status Enum describing the state of the requested pipeline runReturn type: [DagsterRunStatus](https://docs.dagster.io/api/dagster/internals#dagster.DagsterRunStatus)

reload\_repository\_location [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/client.py#L328)

Reloads a Dagster Repository Location, which reloads all repositories in that repository location.

This is useful in a variety of contexts, including refreshing the Dagster UI without restarting the server.

Parameters: **repository\_location\_name** (*str*) – The name of the repository locationReturns: Object with information about the result of the reload requestReturn type: [ReloadRepositoryLocationInfo](https://docs.dagster.io/api/libraries/#dagster_graphql.ReloadRepositoryLocationInfo)

shutdown\_repository\_location [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/client.py#L370)

Shuts down the server that is serving metadata for the provided repository location.

This is primarily useful when you want the server to be restarted by the compute environment in which it is running (for example, in Kubernetes, the pod in which the server is running will automatically restart when the server is shut down, and the repository metadata will be reloaded)

Parameters: **repository\_location\_name** (*str*) – The name of the repository locationReturns: Object with information about the result of the reload requestReturn type: ShutdownRepositoryLocationInfo

submit\_job\_execution [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/client.py#L245)

Submits a job with attached configuration for execution.

Parameters:

- **job\_name** (*str*) – The job’s name
- **repository\_location\_name** (*Optional* *\[**str**\]*) – The name of the repository location where the job is located. If omitted, the client will try to infer the repository location from the available options on the Dagster deployment. Defaults to None.
- **repository\_name** (*Optional* *\[**str**\]*) – The name of the repository where the job is located. If omitted, the client will try to infer the repository from the available options on the Dagster deployment. Defaults to None.
- **run\_config** (*Optional* *\[**Union* *\[*[*RunConfig*](https://docs.dagster.io/api/dagster/config#dagster.RunConfig)*,* *Mapping* *\[**str**,* *Any**\]**\]**\]*) – This is the run config to execute the job with. Note that runConfigData is any-typed in the GraphQL type system. This type is used when passing in an arbitrary object for run config. However, it must conform to the constraints of the config schema for this job. If it does not, the client will throw a DagsterGraphQLClientError with a message of JobConfigValidationInvalid. Defaults to None.
- **tags** (*Optional* *\[**Dict* *\[**str**,* *Any**\]**\]*) – A set of tags to add to the job execution.
- **op\_selection** (*Optional* *\[**Sequence* *\[**str**\]**\]*) – A list of ops to execute.
- **asset\_selection** (*Optional* *\[**Sequence* *\[**CoercibleToAssetKey**\]**\]*) – A list of asset keys to execute.

Raises:

- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"InvalidStepError"****,** **invalid\_step\_key****)** – the job has an invalid step
- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"InvalidOutputError"****,** **body=error\_object****)** – some solid has an invalid output within the job. The error\_object is of type dagster\_graphql.InvalidOutputErrorInfo.
- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"RunConflict"****,** **message****)** – a DagsterRunConflict occured during execution. This indicates that a conflicting job run already exists in run storage.
- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"PipelineConfigurationInvalid"****,** **invalid\_step\_key****)** – the run\_config is not in the expected format for the job
- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"JobNotFoundError"****,** **message****)** – the requested job does not exist
- [DagsterGraphQLClientError](https://docs.dagster.io/api/libraries/#dagster_graphql.DagsterGraphQLClientError) **DagsterGraphQLClientError** **(****"PythonError"****,** **message****)** – an internal framework error occurred

Returns: run id of the submitted pipeline runReturn type: str

`exception` dagster\_graphql.DagsterGraphQLClientError [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/utils.py#L5)

`class` dagster\_graphql.InvalidOutputErrorInfo [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/utils.py#L78)

This class gives information about an InvalidOutputError from submitting a pipeline for execution from GraphQL.

Parameters:

- **step\_key** (*str*) – key of the step that failed
- **invalid\_output\_name** (*str*) – the name of the invalid output from the given step

`class` dagster\_graphql.ReloadRepositoryLocationInfo [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/utils.py#L28)

This class gives information about the result of reloading a Dagster repository location with a GraphQL mutation.

Parameters:

- **status** ([*ReloadRepositoryLocationStatus*](https://docs.dagster.io/api/libraries/#dagster_graphql.ReloadRepositoryLocationStatus)) – The status of the reload repository location mutation
- **failure\_type** – (Optional\[str\], optional): the failure type if status == ReloadRepositoryLocationStatus.FAILURE. Can be one of ReloadNotSupported, RepositoryLocationNotFound, or RepositoryLocationLoadFailure. Defaults to None.
- **message** (*Optional* *\[**str**\]**,* *optional*) – the failure message/reason if status == ReloadRepositoryLocationStatus.FAILURE. Defaults to None.

`class` dagster\_graphql.ReloadRepositoryLocationStatus [\[source\]](https://github.com/dagster-io/dagster/blob/master/python_modules/dagster-graphql/dagster_graphql/client/utils.py#L11)

This enum describes the status of a GraphQL mutation to reload a Dagster repository location.

Parameters: **Enum** (*str*) – can be either ReloadRepositoryLocationStatus.SUCCESS or ReloadRepositoryLocationStatus.FAILURE.

> Source: `docs/data_engineering/dagster/iceberg (dagster-iceberg) _ Dagster Docs.md`

---
title: "iceberg (dagster-iceberg) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-iceberg"
author:
published:
created: 2025-12-12
description: "iceberg (dagster-iceberg) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
This library provides an integration with the [Iceberg](https://iceberg.apache.org/) table format.

For more information on getting started, see the [Dagster & Iceberg](https://docs.dagster.io/integrations/libraries/iceberg) documentation.

**Note:** This is a community-supported integration. For support, see the [Dagster Community Integrations repository](https://github.com/dagster-io/community-integrations/tree/main/libraries/dagster-iceberg).

## I/O Managers

dagster\_iceberg.io\_manager.arrow.PyArrowIcebergIOManager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/io_manager/arrow.py#L56)

An I/O manager definition that reads inputs from and writes outputs to Iceberg tables using PyArrow.

Examples:

```python
import pandas as pd
import pyarrow as pa
from dagster import Definitions, asset
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.arrow import PyArrowIcebergIOManager

CATALOG_URI = "sqlite:////home/vscode/workspace/.tmp/examples/select_columns/catalog.db"
CATALOG_WAREHOUSE = (
    "file:///home/vscode/workspace/.tmp/examples/select_columns/warehouse"
)

resources = {
    "io_manager": PyArrowIcebergIOManager(
        name="test",
        config=IcebergCatalogConfig(
            properties={"uri": CATALOG_URI, "warehouse": CATALOG_WAREHOUSE}
        ),
        namespace="dagster",
    )
}

@asset
def iris_dataset() -> pa.Table:
    pa.Table.from_pandas(
        pd.read_csv(
            "https://docs.dagster.io/assets/iris.csv",
            names=[
                "sepal_length_cm",
                "sepal_width_cm",
                "petal_length_cm",
                "petal_width_cm",
                "species",
            ],
        )
    )

defs = Definitions(assets=[iris_dataset], resources=resources)
```

If you do not provide a schema, Dagster will determine a schema based on the assets and ops using the I/O manager. For assets, the schema will be determined from the asset key, as in the above example. For ops, the schema can be specified by including a “schema” entry in output metadata. If none of these is provided, the schema will default to “public”. The I/O manager will check if the namespace exists in the Iceberg catalog. It does not automatically create the namespace if it does not exist.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> pa.Table:
    ...
```

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the `In` or `AssetIn`.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: pa.Table):
    # my_table will just contain the data from column "a"
    ...
```

dagster\_iceberg.io\_manager.daft.DaftIcebergIOManager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/io_manager/daft.py#L54)

An I/O manager definition that reads inputs from and writes outputs to Iceberg tables using Daft.

Examples:

```python
import daft as da
import pandas as pd
from dagster import Definitions, asset
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.daft import DaftIcebergIOManager

CATALOG_URI = "sqlite:////home/vscode/workspace/.tmp/examples/select_columns/catalog.db"
CATALOG_WAREHOUSE = (
    "file:///home/vscode/workspace/.tmp/examples/select_columns/warehouse"
)

resources = {
    "io_manager": DaftIcebergIOManager(
        name="test",
        config=IcebergCatalogConfig(
            properties={"uri": CATALOG_URI, "warehouse": CATALOG_WAREHOUSE}
        ),
        namespace="dagster",
    )
}

@asset
def iris_dataset() -> da.DataFrame:
    return da.from_pandas(
        pd.read_csv(
            "https://docs.dagster.io/assets/iris.csv",
            names=[
                "sepal_length_cm",
                "sepal_width_cm",
                "petal_length_cm",
                "petal_width_cm",
                "species",
            ],
        )
    )

defs = Definitions(assets=[iris_dataset], resources=resources)
```

If you do not provide a schema, Dagster will determine a schema based on the assets and ops using the I/O manager. For assets, the schema will be determined from the asset key, as in the above example. For ops, the schema can be specified by including a “schema” entry in output metadata. If none of these is provided, the schema will default to “public”. The I/O manager will check if the namespace exists in the Iceberg catalog. It does not automatically create the namespace if it does not exist.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> da.DataFrame:
    ...
```

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the `In` or `AssetIn`.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: da.DataFrame):
    # my_table will just contain the data from column "a"
    ...
```

dagster\_iceberg.io\_manager.pandas.PandasIcebergIOManager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/io_manager/pandas.py#L43)

An I/O manager definition that reads inputs from and writes outputs to Iceberg tables using pandas.

Examples:

```python
import pandas as pd
from dagster import Definitions, asset
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.pandas import PandasIcebergIOManager

CATALOG_URI = "sqlite:////home/vscode/workspace/.tmp/examples/select_columns/catalog.db"
CATALOG_WAREHOUSE = (
    "file:///home/vscode/workspace/.tmp/examples/select_columns/warehouse"
)

resources = {
    "io_manager": PandasIcebergIOManager(
        name="test",
        config=IcebergCatalogConfig(
            properties={"uri": CATALOG_URI, "warehouse": CATALOG_WAREHOUSE}
        ),
        namespace="dagster",
    )
}

@asset
def iris_dataset() -> pd.DataFrame:
    return pd.read_csv(
        "https://docs.dagster.io/assets/iris.csv",
        names=[
            "sepal_length_cm",
            "sepal_width_cm",
            "petal_length_cm",
            "petal_width_cm",
            "species",
        ],
    )

defs = Definitions(assets=[iris_dataset], resources=resources)
```

If you do not provide a schema, Dagster will determine a schema based on the assets and ops using the I/O manager. For assets, the schema will be determined from the asset key, as in the above example. For ops, the schema can be specified by including a “schema” entry in output metadata. If none of these is provided, the schema will default to “public”. The I/O manager will check if the namespace exists in the Iceberg catalog. It does not automatically create the namespace if it does not exist.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> pd.DataFrame:
    ...
```

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the `In` or `AssetIn`.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: pd.DataFrame):
    # my_table will just contain the data from column "a"
    ...
```

dagster\_iceberg.io\_manager.polars.PolarsIcebergIOManager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/io_manager/polars.py#L58)

An I/O manager definition that reads inputs from and writes outputs to Iceberg tables using Polars.

Examples:

If you do not provide a schema, Dagster will determine a schema based on the assets and ops using the I/O manager. For assets, the schema will be determined from the asset key, as in the above example. For ops, the schema can be specified by including a “schema” entry in output metadata. If none of these is provided, the schema will default to “public”. The I/O manager will check if the namespace exists in the Iceberg catalog. It does not automatically create the namespace if it does not exist.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> pl.DataFrame:
    ...
```

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the `In` or `AssetIn`.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: pl.DataFrame):
    # my_table will just contain the data from column "a"
    ...
```

dagster\_iceberg.io\_manager.spark.SparkIcebergIOManager IOManagerDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/io_manager/spark.py#L145)

An I/O manager definition that reads inputs from and writes outputs to Iceberg tables using PySpark.

This I/O manager is only designed to work with Spark Connect.

Example:

```python
from dagster import Definitions, asset
from dagster_iceberg.io_manager.spark import SparkIcebergIOManager
from pyspark.sql import SparkSession
from pyspark.sql.connect.dataframe import DataFrame

resources = {
    "io_manager": SparkIcebergIOManager(
        catalog_name="test",
        namespace="dagster",
        remote_url="spark://localhost",
    )
}

@asset
def iris_dataset() -> DataFrame:
    spark = SparkSession.builder.remote("sc://localhost").getOrCreate()
    return spark.read.csv(
        "https://docs.dagster.io/assets/iris.csv",
        schema=(
            "sepal_length_cm FLOAT, "
            "sepal_width_cm FLOAT, "
            "petal_length_cm FLOAT, "
            "petal_width_cm FLOAT, "
            "species STRING"
        ),
    )

defs = Definitions(assets=[iris_dataset], resources=resources)
```

## Resources

dagster\_iceberg.resource.IcebergTableResource ResourceDefinition [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/resource.py#L11)

Resource for interacting with a PyIceberg table.

Example:

```python
from dagster import Definitions, asset
from dagster_iceberg import IcebergTableResource

@asset
def my_table(iceberg_table: IcebergTableResource):
    df = iceberg_table.load().to_pandas()

warehouse_path = "/path/to/warehouse"

defs = Definitions(
    assets=[my_table],
    resources={
        "iceberg_table": IcebergTableResource(
            name="my_catalog",
            config=IcebergCatalogConfig(
                properties={
                    "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.db",
                    "warehouse": f"file://{warehouse_path}",
                }
            ),
            table="my_table",
            namespace="my_namespace",
        )
    },
)
```

## Config

`class` dagster\_iceberg.config.IcebergCatalogConfig [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/config.py#L14)

Configuration for Iceberg Catalogs.

See the [Catalogs section](https://py.iceberg.apache.org/configuration/#catalogs) for configuration options.

You can configure the Iceberg IO manager:

1. Using a `.pyiceberg.yaml` configuration file.
2. Through environment variables.
3. Using the `IcebergCatalogConfig` configuration object.

For more information about the first two configuration options, see [Setting Configuration Values](https://py.iceberg.apache.org/configuration/#setting-configuration-values).

Example:

```python
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.arrow import PyArrowIcebergIOManager

warehouse_path = "/path/to/warehouse"

io_manager = PyArrowIcebergIOManager(
    name="my_catalog",
    config=IcebergCatalogConfig(
        properties={
            "uri": f"sqlite:///{warehouse_path}/pyiceberg_catalog.db",
            "warehouse": f"file://{warehouse_path}",
        }
    ),
    namespace="my_namespace",
)
```

## Base Classes

`class` dagster\_iceberg.io\_manager.base.IcebergIOManager [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/io_manager/base.py#L105)

Base class for an I/O manager definition that reads inputs from and writes outputs to Iceberg tables.

Examples:

```python
import pandas as pd
import pyarrow as pa
from dagster import Definitions, asset
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.arrow import PyArrowIcebergIOManager

CATALOG_URI = "sqlite:////home/vscode/workspace/.tmp/examples/select_columns/catalog.db"
CATALOG_WAREHOUSE = (
    "file:///home/vscode/workspace/.tmp/examples/select_columns/warehouse"
)

resources = {
    "io_manager": PyArrowIcebergIOManager(
        name="test",
        config=IcebergCatalogConfig(
            properties={"uri": CATALOG_URI, "warehouse": CATALOG_WAREHOUSE}
        ),
        namespace="dagster",
    )
}

@asset
def iris_dataset() -> pa.Table:
    pa.Table.from_pandas(
        pd.read_csv(
            "https://docs.dagster.io/assets/iris.csv",
            names=[
                "sepal_length_cm",
                "sepal_width_cm",
                "petal_length_cm",
                "petal_width_cm",
                "species",
            ],
        )
    )

defs = Definitions(assets=[iris_dataset], resources=resources)
```

If you do not provide a schema, Dagster will determine a schema based on the assets and ops using the I/O manager. For assets, the schema will be determined from the asset key, as in the above example. For ops, the schema can be specified by including a “schema” entry in output metadata. If none of these is provided, the schema will default to “public”. The I/O manager will check if the namespace exists in the Iceberg catalog. It does not automatically create the namespace if it does not exist.

```python
@op(
    out={"my_table": Out(metadata={"schema": "my_schema"})}
)
def make_my_table() -> pa.Table:
    ...
```

To only use specific columns of a table as input to a downstream op or asset, add the metadata “columns” to the `In` or `AssetIn`.

```python
@asset(
    ins={"my_table": AssetIn("my_table", metadata={"columns": ["a"]})}
)
def my_table_a(my_table: pa.Table):
    # my_table will just contain the data from column "a"
    ...
```

To select a write mode, set the `write_mode` key in the asset definition metadata or at runtime via output metadata. Write mode set at runtime takes precedence over the one set in the definition metadata. Valid modes are `append`, `overwrite`, and `upsert`; default is `overwrite`.

```python
# set at definition time via definition metadata
@asset(
    metadata={"write_mode": "append"}
)
def my_table_a(my_table: pa.Table):
    return my_table

# set at runtime via output metadata
@asset
def my_table_a(context: AssetExecutionContext, my_table: pa.Table):
    # my_table will be written with append mode
    context.add_output_metadata({"write_mode": "append"})
    return my_table
```

To use upsert mode, set `write_mode` to `upsert` and provide `upsert_options` in asset definition metadata or output metadata. The `upsert_options` dictionary should contain `join_cols` (list of columns to join on),`when_matched_update_all` (boolean), and `when_not_matched_insert_all` (boolean). Upsert options set at runtime take precedence over those set in definition metadata.

```python
# set at definition time via definition metadata
@asset(
    metadata={
        "write_mode": "upsert",
        "upsert_options": {
            "join_cols": ["id"],
            "when_matched_update_all": True,
            "when_not_matched_insert_all": True,
        }
    }
)
def my_table_upsert(my_table: pa.Table):
    return my_table

# set at runtime via output metadata (overrides definition metadata)
@asset(
    metadata={
        "write_mode": "upsert",
        "upsert_options": {
            "join_cols": ["id"],
            "when_matched_update_all": True,
            "when_not_matched_insert_all": False,
        }
    }
)
def my_table_upsert_dynamic(context: AssetExecutionContext, my_table: pa.Table):
    # Override upsert options at runtime
    context.add_output_metadata({
        "upsert_options": {
            "join_cols": ["id", "timestamp"],
            "when_matched_update_all": False,
            "when_not_matched_insert_all": False,
        }
    })
    return my_table
```

`class` dagster\_iceberg.handler.IcebergBaseTypeHandler [\[source\]](https://github.com/dagster-io/dagster/blob/master/docs/.tox/sphinx-mdx-vercel/lib/python3.11/site-packages/dagster_iceberg/handler.py#L35)

Base class for a type handler that reads inputs from and writes outputs to Iceberg tables.

> Source: `docs/data_engineering/dagster/datadog (dagster-datadog) _ Dagster Docs.md`

---
title: "datadog (dagster-datadog) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-datadog"
author:
published:
created: 2025-12-12
description: "datadog (dagster-datadog) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
This library provides an integration with Datadog, to support publishing metrics to Datadog from within Dagster ops.

We use the Python [datadogpy](https://github.com/DataDog/datadogpy) library. To use it, you’ll first need to create a DataDog account and get both [API and Application keys](https://docs.datadoghq.com/account_management/api-app-keys).

The integration uses [DogStatsD](https://docs.datadoghq.com/developers/dogstatsd), so you’ll need to ensure the datadog agent is running on the host you’re sending metrics from.

dagster\_datadog.DatadogResource ResourceDefinition

This resource is a thin wrapper over the [dogstatsd library](https://datadogpy.readthedocs.io/en/latest/).

As such, we directly mirror the public API methods of DogStatsd here; you can refer to the [Datadog documentation](https://docs.datadoghq.com/developers/dogstatsd/) for how to use this resource.

Examples:

```python
@op
def datadog_op(datadog_resource: DatadogResource):
    datadog_client = datadog_resource.get_client()
    datadog_client.event('Man down!', 'This server needs assistance.')
    datadog_client.gauge('users.online', 1001, tags=["protocol:http"])
    datadog_client.increment('page.views')
    datadog_client.decrement('page.views')
    datadog_client.histogram('album.photo.count', 26, tags=["gender:female"])
    datadog_client.distribution('album.photo.count', 26, tags=["color:blue"])
    datadog_client.set('visitors.uniques', 999, tags=["browser:ie"])
    datadog_client.service_check('svc.check_name', datadog_client.WARNING)
    datadog_client.timing("query.response.time", 1234)

    # Use timed decorator
    @datadog_client.timed('run_fn')
    def run_fn():
        pass

    run_fn()

@job
def job_for_datadog_op() -> None:
    datadog_op()

job_for_datadog_op.execute_in_process(
    resources={"datadog_resource": DatadogResource(api_key="FOO", app_key="BAR")}
)
```

## Legacy

dagster\_datadog.datadog\_resource ResourceDefinition

This legacy resource is a thin wrapper over the [dogstatsd library](https://datadogpy.readthedocs.io/en/latest/).

Prefer using [`DatadogResource`](https://docs.dagster.io/api/libraries/#dagster_datadog.DatadogResource).

As such, we directly mirror the public API methods of DogStatsd here; you can refer to the [DataDog documentation](https://docs.datadoghq.com/developers/dogstatsd/) for how to use this resource.

Examples:

```python
@op(required_resource_keys={'datadog'})
def datadog_op(context):
    dd = context.resources.datadog

    dd.event('Man down!', 'This server needs assistance.')
    dd.gauge('users.online', 1001, tags=["protocol:http"])
    dd.increment('page.views')
    dd.decrement('page.views')
    dd.histogram('album.photo.count', 26, tags=["gender:female"])
    dd.distribution('album.photo.count', 26, tags=["color:blue"])
    dd.set('visitors.uniques', 999, tags=["browser:ie"])
    dd.service_check('svc.check_name', dd.WARNING)
    dd.timing("query.response.time", 1234)

    # Use timed decorator
    @dd.timed('run_fn')
    def run_fn():
        pass

    run_fn()

@job(resource_defs={'datadog': datadog_resource})
def dd_job():
    datadog_op()

result = dd_job.execute_in_process(
    run_config={'resources': {'datadog': {'config': {'api_key': 'YOUR_KEY', 'app_key': 'YOUR_KEY'}}}}
)
```

> Source: `docs/data_engineering/dagster/mlflow (dagster-mlflow) _ Dagster Docs.md`

---
title: "mlflow (dagster-mlflow) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-mlflow"
author:
published:
created: 2025-12-12
description: "mlflow (dagster-mlflow) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
dagster\_mlflow.mlflow\_tracking ResourceDefinition

This resource initializes an MLflow run that’s used for all steps within a Dagster run.

This resource provides access to all of mlflow’s methods as well as the mlflow tracking client’s methods.

Usage:

1. Add the mlflow resource to any ops in which you want to invoke mlflow tracking APIs.
2. Add the end\_mlflow\_on\_run\_finished hook to your job to end the MLflow run when the Dagster run is finished.

Examples:

```python
from dagster_mlflow import end_mlflow_on_run_finished, mlflow_tracking

@op(required_resource_keys={"mlflow"})
def mlflow_op(context):
    mlflow.log_params(some_params)
    mlflow.tracking.MlflowClient().create_registered_model(some_model_name)

@end_mlflow_on_run_finished
@job(resource_defs={"mlflow": mlflow_tracking})
def mlf_example():
    mlflow_op()

# example using an mlflow instance with s3 storage
mlf_example.execute_in_process(run_config={
    "resources": {
        "mlflow": {
            "config": {
                "experiment_name": my_experiment,
                "mlflow_tracking_uri": "http://localhost:5000",

                # if want to run a nested run, provide parent_run_id
                "parent_run_id": an_existing_mlflow_run_id,

                # if you want to resume a run or avoid creating a new run in the resource init,
                # provide mlflow_run_id
                "mlflow_run_id": an_existing_mlflow_run_id,

                # env variables to pass to mlflow
                "env": {
                    "MLFLOW_S3_ENDPOINT_URL": my_s3_endpoint,
                    "AWS_ACCESS_KEY_ID": my_aws_key_id,
                    "AWS_SECRET_ACCESS_KEY": my_secret,
                },

                # env variables you want to log as mlflow tags
                "env_to_tag": ["DOCKER_IMAGE_TAG"],

                # key-value tags to add to your experiment
                "extra_tags": {"super": "experiment"},
            }
        }
    }
})
```

dagster\_mlflow.end\_mlflow\_on\_run\_finished HookDefinition

> Source: `docs/data_engineering/dagster/postgresql (dagster-postgres) _ Dagster Docs.md`

---
title: "postgresql (dagster-postgres) | Dagster Docs"
source: "https://docs.dagster.io/api/libraries/dagster-postgres"
author:
published:
created: 2025-12-12
description: "postgresql (dagster-postgres) Dagster API | Comprehensive Python API documentation for Dagster, the data orchestration platform. Learn how to build, test, and maintain data pipelines with our detailed guides and examples."
tags:
  - "clippings"
---
dagster\_postgres.PostgresEventLogStorage `=` <class 'dagster\_postgres.event\_log.event\_log.PostgresEventLogStorage'>

Postgres-backed event log storage.

Users should not directly instantiate this class; it is instantiated by internal machinery when `dagster-webserver` and `dagster-graphql` load, based on the values in the `dagster.yaml` file in `$DAGSTER_HOME`. Configuration of this class should be done by setting values in that file.

To use Postgres for all of the components of your instance storage, you can add the following block to your `dagster.yaml`:

dagster.yaml

```yaml
storage:
  postgres:
    postgres_db:
      username: my_username
      password: my_password
      hostname: my_hostname
      db_name: my_database
      port: 5432
```

If you are configuring the different storage components separately and are specifically configuring your event log storage to use Postgres, you can add a block such as the following to your `dagster.yaml`:

dagster.yaml

```yaml
event_log_storage:
  module: dagster_postgres.event_log
  class: PostgresEventLogStorage
  config:
    postgres_db:
      username: { username }
      password: { password }
      hostname: { hostname }
      db_name: { db_name }
      port: { port }
```

Note that the fields in this config are [`StringSource`](https://docs.dagster.io/api/dagster/config#dagster.StringSource) and [`IntSource`](https://docs.dagster.io/api/dagster/config#dagster.IntSource) and can be configured from environment variables.

dagster\_postgres.PostgresRunStorage `=` <class 'dagster\_postgres.run\_storage.run\_storage.PostgresRunStorage'>

Postgres-backed run storage.

Users should not directly instantiate this class; it is instantiated by internal machinery when `dagster-webserver` and `dagster-graphql` load, based on the values in the `dagster.yaml` file in `$DAGSTER_HOME`. Configuration of this class should be done by setting values in that file.

To use Postgres for all of the components of your instance storage, you can add the following block to your `dagster.yaml`:

dagster.yaml

```yaml
storage:
  postgres:
    postgres_db:
      username: my_username
      password: my_password
      hostname: my_hostname
      db_name: my_database
      port: 5432
```

If you are configuring the different storage components separately and are specifically configuring your run storage to use Postgres, you can add a block such as the following to your `dagster.yaml`:

dagster.yaml

```yaml
run_storage:
  module: dagster_postgres.run_storage
  class: PostgresRunStorage
  config:
    postgres_db:
      username: { username }
      password: { password }
      hostname: { hostname }
      db_name: { db_name }
      port: { port }
```

Note that the fields in this config are [`StringSource`](https://docs.dagster.io/api/dagster/config#dagster.StringSource) and [`IntSource`](https://docs.dagster.io/api/dagster/config#dagster.IntSource) and can be configured from environment variables.

dagster\_postgres.PostgresScheduleStorage `=` <class 'dagster\_postgres.schedule\_storage.schedule\_storage.PostgresScheduleStorage'>

Postgres-backed run storage.

Users should not directly instantiate this class; it is instantiated by internal machinery when `dagster-webserver` and `dagster-graphql` load, based on the values in the `dagster.yaml` file in `$DAGSTER_HOME`. Configuration of this class should be done by setting values in that file.

To use Postgres for all of the components of your instance storage, you can add the following block to your `dagster.yaml`:

dagster.yaml

```yaml
storage:
  postgres:
    postgres_db:
      username: my_username
      password: my_password
      hostname: my_hostname
      db_name: my_database
      port: 5432
```

If you are configuring the different storage components separately and are specifically configuring your schedule storage to use Postgres, you can add a block such as the following to your `dagster.yaml`:

dagster.yaml

```yaml
schedule_storage:
  module: dagster_postgres.schedule_storage
  class: PostgresScheduleStorage
  config:
    postgres_db:
      username: { username }
      password: { password }
      hostname: { hostname }
      db_name: { db_name }
      port: { port }
```

Note that the fields in this config are [`StringSource`](https://docs.dagster.io/api/dagster/config#dagster.StringSource) and [`IntSource`](https://docs.dagster.io/api/dagster/config#dagster.IntSource) and can be configured from environment variables.

## Dagster MCP Integration


> Source: `docs/data_engineering/dagster/How the Dagster MCP allows you to write better code.md`

---
title: "How the Dagster MCP allows you to write better code"
source: "https://dagster.io/blog/dagsters-mcp-server"
author:
published:
created: 2025-12-28
description: "Dagster releases its MCP server, enabling seamless AI assistant integration with data pipelines through Anthropic's Model Context Protocol standard for better automation."
tags:
  - "clippings"
---
### We are announcing the release of our MCP server, enabling AI assistants like Cursor to seamlessly integrate with Dagster projects through Model Context Protocol, unlocking composable workflows across your entire data stack.

When Anthropic [announced MCP in late 2024](https://www.anthropic.com/news/model-context-protocol), the initial reaction was one of cautious optimism. AI was evolving so quickly that it wasn’t immediately clear what MCP would mean in practice. But as its implications became clearer, even competitors like OpenAI adopted the protocol.

Since then, other companies have released their own MCP servers. At Dagster, we built our first MCP server earlier this year but chose to wait before releasing it, ensuring it would integrate seamlessly with our recent platform improvements.

Today, we’re excited to make the Dagster MCP server publicly available. It complements everything we’ve been building over the years and opens up new possibilities for writing better, more maintainable code.

## What is MCP?

The Model Context Protocol (MCP) is an open standard developed by Anthropic to connect large language models (LLMs) with external data sources in a secure, standardized way. In Anthropic’s own words:

> “The Model Context Protocol is an open standard that enables developers to build secure, two-way connections between their data sources and AI-powered tools. It provides a universal, open standard for connecting AI systems with data sources, replacing fragmented integrations with a single protocol. The result is a simpler, more reliable way to give AI systems access to the data they need.”

LLMs are powerful at generating coherent language, but on their own, they:

- Lack real-time, accurate, and domain-specific knowledge.
- Have no native ability to interact with databases, APIs, or tools.  
	Rely entirely on what they were trained on which becomes outdated quickly.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d873_AD_4nXfZQaVyxL9-C2LWHRqcSF1wG2L73q7kDgjMS49Hg6R9LPEPKB5DmcalW9UHZs6rS-X0UvsKI2lbQFUGjXfdiOOcjND8F-IF4vAwv6uG9bHuo1ooTFmSSy9_5Jvh3fAQKfWa2VTTUw.png)

To remain relevant and useful, LLMs must pull information from external sources. When an LLM “searches the web” or queries a knowledge base, it’s functioning as an AI agent, reasoning about what data it needs, where to get it, and how to integrate it into its output.

This approach is powerful but creates challenges:

- **Complexity:** Each LLM must manage custom integrations for every data source.
- **Fragility:** Data sources change, breaking integrations over time.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d86a_AD_4nXepjXGDZNBV5stsyCTdshNzZN_EwTmZCTa1MY53NFw7oFvgpXSCn4PgqTjODC1ihOHQQtkuXpl5-Ltlk6JNMPzsKYugl4K4P4OE9g36gG5LFE8FbPK5i2pOQsVKlO3Rr3k3_o7kzA.png)

MCP standardizes the connection between AI agents and external services. Instead of every AI system learning how to talk to every data source, the external service provides an MCP interface.

Benefits of this approach:

- **Interoperability:** Any MCP-compatible AI can instantly integrate with the service.
- **Reduced Maintenance:** The service owner maintains the MCP interface, ensuring accuracy and reliability.
- **Future-proofing:** As AI systems evolve, the MCP layer stays consistent.

MCP shifts the integration burden from the AI agent to the service, making the ecosystem simpler, more reliable, and easier to maintain.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d870_AD_4nXc4YdjBlCXBGvO5_R4F8gb4K7OKC8VxnQZh3uVPpnr_ePbQBLwDEwiAVfnolbz7EksWA3e_XGe8OONfxAKfmIZUidqOoHqE_FJFLj2HFB7-j89gLc-CI6ZE51Hb-6Uz9ZpfbOmrSQ.png)

## Dagster’s MCP Server

So where does Dagster’s MCP fit into all of this, and why does it work so well with our recent features?

If you’ve been following Dagster this year, you know we’re excited about [dg](https://docs.dagster.io/api/dg/dg-cli) and [Dagster Components](https://docs.dagster.io/guides/build/components). These abstractions sit on top of core Dagster objects (such as assets) and make it much easier to build new features or integrate with tools and workflows, often with minimal code.

This combination, a rich core library that can do just about anything, paired with opinionated tooling, is a perfect match for MCP. With a well-documented, structured library, MCP can gain a deep understanding of Dagster’s capabilities. By exposing streamlined code interfaces with tighter guardrails, you can have more confidence in the quality and safety of the code it returns.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d867_AD_4nXd41RW_85lr1eUGBVS-NQIpR7NguDV91ohibtpvcpD7OPOWwBVqwtN_5Zrz54dTkACBDR-ELda5PiSjCtfSRyej28aaQ31bkjCKiZFZwZSAOez4uv9VowHxZ2tE_NvTxbcfvsL97A.png)

Let’s look at a real-world example. Say you’re using [Cursor](https://www.cursor.so/) and want to start a new Dagster project.

> “Can you scaffold me a new Dagster project named example-project”

With the Dagster MCP configured, Cursor knows where to route requests and translates them to the correct \` [dg](https://docs.dagster.io/guides/labs/dg) \` CLI commands as needed. In this case Cursor would know that it is more efficient to use \`uvx -U create-dagster\` to generate a project than generating all the code itself.

![](https://cdn.prod.website-files.com/681399f654933b29e12fb8e4/68962c883127c0c6df70d86d_AD_4nXenn0HiF8L2Je5A-Am3fzn1q3ccZUjAupPOnAdS47seq07MNsDvuz-0YzSa4DNPrh9K9iAw7WcMYvaU3oWp2Tht3M4WPTDm30yn1XDv6Rywcj-phOyMz7psO4tDNa-f3k531qNNRA.png)

### Composability

What makes the Dagster MCP exciting is that it’s not a one-off integration, it’s composable. If you’re using other tools in your data stack, like dbt, Snowflake, Airbyte, or any service that exposes an MCP interface, your AI assistant can seamlessly interact with all of them together.

> “Can you add dbt to my Dagster project”

Without \`dg\` and components, many LLMs could handle this request by generating code directly. But that approach comes with higher risk: more potential for errors, plus the added cost of processing large amounts of context.

With Dagster MCP, the AI instead guides you toward simple \`dg\` commands to scaffold an integration for a dbt project. This generates just a few lines of YAML needed to configure what is needed. From there, you can use the AI agent to make any necessary changes at the YAML layer, keeping your code clean, concise, and maintainable.

This interoperability unlocks a powerful new way of working: one where AI agents operate across your entire stack, coordinating multiple tools through a shared, universal protocol. Instead of stitching together brittle point-to-point integrations or ad-hoc scripts, you get a unified, extensible interface for building and automating sophisticated workflows, accelerating development while maintaining flexibility and control.

## Trying it out

The best part? You don’t need to be a Cursor user to benefit from the Dagster MCP. As more AI tools adopt MCP, the value of having an MCP-compatible interface to your project will only grow. Standardization in the AI space means better interoperability, more reliable automation, and faster iteration.

You can install the MCP server right now through the **dg\[mcp\]** package, and easily enable it within your tool using **dg mcp configure**.

## Latest writings

The latest news, technologies, and resources from our team.

[View all posts](https://dagster.io/blog/#)

## Integration: Dagster + DuckLake


> Source: `docs/data_engineering/dagster/dagster_ducklake.md`

# dagster-ducklake

A dagster module that provides integration with [ducklake](https://ducklake.select/)

## Installation

The `dagster_ducklake` module is available as a PyPI package - install with your preferred python
environment manager (We recommend [uv](https://github.com/astral-sh/uv)).

```
source .venv/bin/activate
uv pip install dagster-ducklake
```

## Example Usage

```python
import dagster as dg

@dg.asset
def my_ducklake_asset(ddb: DuckDBConnectionProvider):
    with ddb.duckdb_connect() as con:
        query = "select * from table"

        df = con.query(query).df()
        df.head()
```

## Resource initialization

```python
{
    "ducklake": DuckLakeResource(
        metadata_backend=PostgresConfig(
            host="db.mycorp.com",
            port=5432,
            database="ducklake_catalog",
            user=dg.EnvVar("POSTGRES_USER"),
            password=dg.EnvVar("POSTGRES_PASSWORD"),
        ),
        storage_backend=S3Config(
            endpoint_url="objectstore.mycorp.com",
            bucket="duckpond-dev",
            prefix="stage",
            aws_access_key_id=dg.EnvVar("OBJECT_STORE_USER"),
            aws_secret_access_key=dg.EnvVar("OBJECT_STORE_PASSWORD"),
            region=dg.EnvVar("OBJECT_STORE_REGION"),
            use_ssl=True,
            url_style="path",
        ),
        alias="stage",
        plugins=["postgres", "httpfs", "ducklake"],
    ),
}

```

## Development

The `Makefile` provides the tools required to test and lint your local installation

```sh
make test
make ruff
make check
```


> Source: `docs/data_engineering/dagster/dagster-ducklake/README.md`

# dagster-ducklake

A dagster module that provides integration with [ducklake](https://ducklake.select/)

## Installation

The `dagster_ducklake` module is available as a PyPI package - install with your preferred python
environment manager (We recommend [uv](https://github.com/astral-sh/uv)).

```
source .venv/bin/activate
uv pip install dagster-ducklake
```

## Example Usage

```python
import dagster as dg

@dg.asset
def my_ducklake_asset(ddb: DuckDBConnectionProvider):
    with ddb.duckdb_connect() as con:
        query = "select * from table"

        df = con.query(query).df()
        df.head()
```

## Resource initialization

```python
{
    "ducklake": DuckLakeResource(
        metadata_backend=PostgresConfig(
            host="db.mycorp.com",
            port=5432,
            database="ducklake_catalog",
            user=dg.EnvVar("POSTGRES_USER"),
            password=dg.EnvVar("POSTGRES_PASSWORD"),
        ),
        storage_backend=S3Config(
            endpoint_url="objectstore.mycorp.com",
            bucket="duckpond-dev",
            prefix="stage",
            aws_access_key_id=dg.EnvVar("OBJECT_STORE_USER"),
            aws_secret_access_key=dg.EnvVar("OBJECT_STORE_PASSWORD"),
            region=dg.EnvVar("OBJECT_STORE_REGION"),
            use_ssl=True,
            url_style="path",
        ),
        alias="stage",
        plugins=["postgres", "httpfs", "ducklake"],
    ),
}

```

## Development

The `Makefile` provides the tools required to test and lint your local installation

```sh
make test
make ruff
make check
```


## Integration: Dagster + Iceberg


> Source: `docs/data_engineering/dagster/dagster_iceberg.md`

![dagster-iceberg](docs/assets/dagster-iceberg-main.png)

> ⚠️ This project has [preview status](https://docs.dagster.io/api/api-lifecycle)

[Dagster](https://dagster.io/) IO manager for managing [Iceberg](https://iceberg.apache.org/) tables with [PyIceberg](https://github.com/apache/iceberg-python).

## Examples

See:

- [example with postgresql catalog](https://github.com/JasperHG90/dagster-pyiceberg-example-postgres)
- [example with Polaris catalog](https://github.com/JasperHG90/dagster-pyiceberg-example-polaris)

## Installation

See [Installing dagster-iceberg](https://jasperhg90.github.io/community-integrations/installation/).

## Documentation

Documentation can be built locally by cloning this repository, navigating to the 'dagster-iceberg' folder, and running `make docs`. It is also available on [here](https://jasperhg90.github.io/community-integrations/).

## Features

Available features can be found [here](https://jasperhg90.github.io/community-integrations/features/).

## Status

This library is currently in development and has [preview status](https://docs.dagster.io/api/api-lifecycle).


> Source: `docs/data_engineering/dagster/dagster-iceberg/README.md`

![dagster-iceberg](docs/assets/dagster-iceberg-main.png)

> ⚠️ This project has [preview status](https://docs.dagster.io/api/api-lifecycle)

[Dagster](https://dagster.io/) IO manager for managing [Iceberg](https://iceberg.apache.org/) tables with [PyIceberg](https://github.com/apache/iceberg-python).

## Examples

See:

- [example with postgresql catalog](https://github.com/JasperHG90/dagster-pyiceberg-example-postgres)
- [example with Polaris catalog](https://github.com/JasperHG90/dagster-pyiceberg-example-polaris)

## Installation

See [Installing dagster-iceberg](https://jasperhg90.github.io/community-integrations/installation/).

## Documentation

Documentation can be built locally by cloning this repository, navigating to the 'dagster-iceberg' folder, and running `make docs`. It is also available on [here](https://jasperhg90.github.io/community-integrations/).

## Features

Available features can be found [here](https://jasperhg90.github.io/community-integrations/features/).

## Status

This library is currently in development and has [preview status](https://docs.dagster.io/api/api-lifecycle).


> Source: `docs/data_engineering/dagster/dagster-iceberg/docs/index.md`

# dagster-iceberg

!!! warning "Under construction"

    This repository is currently under construction

Dagster IO manager for managing Iceberg tables using [PyIceberg](https://github.com/apache/iceberg-python).

## Example projects

See:

- [example with postgresql catalog](https://github.com/JasperHG90/dagster-iceberg-example-postgres)
- [example with Polaris catalog](https://github.com/JasperHG90/dagster-iceberg-example-polaris)


> Source: `docs/data_engineering/dagster/dagster-iceberg/docs/quickstart.md`

# Quickstart

!!! warning "Iceberg catalog"

    PyIceberg requires a catalog backend. A SQLite catalog is used here for illustrative purposes. Do not use this in a production setting.

## Step 1: Defining the I/O manager

To use dagster-iceberg as an I/O manager, you add it to your `Definition`:

```py linenums="1"
from dagster import Definitions
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.arrow import PyArrowIcebergIOManager

CATALOG_URI = "sqlite:////home/vscode/workspace/.tmp/dag/warehouse/catalog.db"
CATALOG_WAREHOUSE = "file:///home/vscode/workspace/.tmp/dag/warehouse"


resources = {
    "io_manager": PyArrowIcebergIOManager(
        name="test",
        config=IcebergCatalogConfig(
            properties={"uri": CATALOG_URI, "warehouse": CATALOG_WAREHOUSE}
        ),
        namespace="dagster",
    )
}


defs = Definitions(
    assets=[iris_dataset],
    resources=resources
)
```

## Step 2: Store a Dagster asset as an Iceberg table

```py linenums="1"
import pandas as pd

from dagster import asset


@asset
def iris_dataset() -> pd.DataFrame:
    return pd.read_csv(
        "https://docs.dagster.io/assets/iris.csv",
        names=[
            "sepal_length_cm",
            "sepal_width_cm",
            "petal_length_cm",
            "petal_width_cm",
            "species",
        ],
    )
```

## Step 3: Load Iceberg tables in downstream assets

Dagster and the I/O manager allow you to load the data stored in Iceberg tables into downstream assets:

```py linenums="1"
import pandas as pd

from dagster import asset

# this example uses the iris_dataset asset from Step 2

@asset
def iris_cleaned(iris_dataset: pd.DataFrame) -> pd.DataFrame:
    return iris_dataset.dropna().drop_duplicates()
```


> Source: `docs/data_engineering/dagster/dagster-iceberg/docs/installation.md`

# Installing dagster-iceberg

This library is available on pypi.

The following extras are available:

- daft (for interoperability with Daft dataframes)
- polars (for interoperability with Polars dataframes)
- pandas (for interoperability with Pandas dataframes)

Pyarrow is installed as a default dependency, so that IO Manager is always available.


> Source: `docs/data_engineering/dagster/dagster-iceberg/docs/features.md`

# Features

## Supported catalog backends

`dagster-iceberg` supports all catalog backends that are available through `pyiceberg`. See overview and configuration options [here](https://py.iceberg.apache.org/configuration/#catalogs).

## Configuration

`dagster-iceberg` supports setting configuration values using a `.pyiceberg.yaml` configuration file and environment variables. For more information, see the [PyIceberg documentation](https://py.iceberg.apache.org/configuration/#setting-configuration-values).

You may also pass your catalog configuration through use of the `IcebergCatalogConfig` object, e.g:

```python
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.arrow import PyArrowIcebergIOManager

io_manager = PyArrowIcebergIOManager(
    name=catalog_name,
    config=IcebergCatalogConfig(properties={
        "uri": "postgresql+psycopg2://pyiceberg:pyiceberg@postgres/catalog",
        "warehouse": f"file://path/to/warehouse",
    }),
    namespace=namespace,
)
```

## Implemented engines

The following engines are currently implemented.

- [arrow](https://arrow.apache.org/docs/python/index.html)
- [daft](https://www.getdaft.io/)
- [pandas](https://pandas.pydata.org/)
- [polars](https://pola.rs/)

## PyIceberg Features

The table below shows which PyIceberg features are currently available.

| Feature | Supported | Link | Comment |
|---|---|---|---|
| Add existing files | ❌ | https://py.iceberg.apache.org/api/#add-files | Useful for existing partitions that users don't want to re-materialize/re-compute. |
| Schema evolution | ✅ | https://py.iceberg.apache.org/api/#schema-evolution | More complicated than e.g. delta lake since updates require diffing input table with existing Iceberg table. This is implemented by checking the schema of incoming data, dropping any columns that no longer exist in the data schema, and then using the `union_by_name()` method to merge the current schema with the table schema. Current implementation has a chance of creating a race condition when e.g. partition A tries to write to a table that has not yet processed a schema update. Should be covered by retrying when writing. |
| Sort order | ❌ | https://shorturl.at/TycZN | Currently limited support in PyIceberg. Sort ordering is supported when creating a table from an Iceberg schema (one must pass the source_id which can be inferred from a PyArrow schema but this is shaky). However, we cannot simply update a sort ordering like a partition or schema spec. |
| PyIceberg commit retries | ✅ | https://github.com/apache/iceberg-python/pull/330 https://github.com/apache/iceberg-python/issues/269 | PR to add this to PyIceberg is open. Will probably be merged for an upcoming release. Added a custom retry function using Tenacity for the time being. |
| Partition evolution | ✅ | https://py.iceberg.apache.org/api/#partition-evolution | Create, Update, Delete partitions by updating the Dagster partitions definition. |
| Table properties | ✅ | https://py.iceberg.apache.org/api/#table-properties | Added as metadata on an asset. NB: config options are not checked explicitly because users can add any key-value pair to a table. Available properties [here](https://py.iceberg.apache.org/configuration/#tables). |
| Snapshot properties | ✅ | https://py.iceberg.apache.org/api/#snapshot-properties | Useful for correlating Dagster runs to snapshots by adding tags to snapshot. Not configurable by end-user. |
| Upsert | ✅ | https://py.iceberg.apache.org/api/#upsert | Update existing rows and insert new rows in a single operation. Configure via `write_mode: "upsert"` and `upsert_options` in asset metadata. |


> Source: `docs/data_engineering/dagster/dagster-iceberg/docs/reference.md`

# dagster-iceberg integration reference

This reference page provides information for working with dagster-iceberg.

!!! warning "Iceberg catalog"

    Iceberg requires a catalog backend. A SQLite catalog is used here for illustrative purposes. Do not use this in a production setting. For more information and for catalog configuration settings, visit the [Iceberg documentation](https://py.iceberg.apache.org/configuration/#catalogs).

## Selecting specific columns in a downstream asset

At times, you might prefer not to retrieve an entire table for a downstream asset. The Iceberg I/O manager allows you to load specific columns by providing metadata related to the downstream asset.

```python title="docs/snippets/select_columns.py" linenums="1"
--8<-- "docs/snippets/select_columns.py"
```

In this example, we focus exclusively on the columns containing sepal data from the `iris_dataset` table. To select specific columns, we can include metadata in the input asset. This is done using the `metadata` parameter of the `AssetIn` that loads the `iris_dataset` asset within the `ins` parameter. We provide the key `columns` along with a list of the desired column names.

When Dagster materializes `sepal_data` and retrieves the `iris_dataset` asset via the Iceberg I/O manager, it will only extract the `sepal_length_cm` and `sepal_width_cm` columns from the `iris/iris_dataset` table and deliver them to `sepal_data` as a Pandas DataFrame.

---

## Storing partitioned assets

The Iceberg I/O manager facilitates the storage and retrieval of partitioned data. To effectively manage data in the Iceberg table, it is essential for the Iceberg I/O manager to identify the column that specifies the partition boundaries. This information allows the I/O manager to formulate the appropriate queries for selecting or replacing data.

In the subsequent sections, we will outline how the I/O manager generates these queries for various partition types.

!!! info "Partition dimensions"

    For partitioning to function correctly, the partition dimension must correspond to one of the partition columns defined in the Iceberg table. Tables created through the I/O manager will be set up accordingly.

=== "Storing static partitioned assets"

    To save static partitioned assets in your Iceberg table, you need to set the `partition_expr` metadata on the asset. This informs the Iceberg I/O manager which column holds the partition data:

    ```python title="docs/snippets/partitions_static.py" linenums="1"
    --8<-- "docs/snippets/partitions_static.py"
    ```

    Dagster uses the `partition_expr` metadata to create the necessary function parameters when retrieving the partition in the downstream asset. For static partitions, this is roughly equivalent to the following SQL query:

    ```sql
    SELECT *
    WHERE [partition_expr] in ([selected partitions])
    ```

    A partition must be specified when materializing the above assets, as explained in the [Materializing partitioned assets](/concepts/partitions-schedules-sensors/partitioning-assets#materializing-partitioned-assets) documentation. For instance, the query used to materialize the `Iris-setosa` partition of the assets would be:

    ```sql
    SELECT *
    WHERE species = 'Iris-setosa'
    ```

=== "Storing time-partitioned assets"

    Like static partitioned assets, you can specify `partition_expr` metadata on the asset to tell the Iceberg I/O manager which column contains the partition data:

    ```python title="docs/snippets/partitions_time.py" linenums="1"
    --8<-- "docs/snippets/partitions_time.py"
    ```

    Dagster uses the `partition_expr` metadata to craft the `SELECT` statement when loading the correct partition in the downstream asset. When loading a dynamic partition, the following statement is used:

    ```sql
    SELECT *
    WHERE [partition_expr] = [partition_start]
    ```

    A partition must be selected when materializing the above assets, as described in the [Materializing partitioned assets](/concepts/partitions-schedules-sensors/partitioning-assets#materializing-partitioned-assets) documentation. The `[partition_start]` and `[partition_end]` bounds are of the form `YYYY-MM-DD HH:MM:SS`. In this example, the query when materializing the `2023-01-02` partition of the above assets would be:

    ```sql
    SELECT *
    WHERE time = '2023-01-02 00:00:00'
    ```

=== "Storing multi-partitioned assets"

    The Iceberg I/O manager can also store data partitioned on multiple dimensions. To do this, specify the column for each partition as a dictionary of `partition_expr` metadata:

    ```python title="docs/snippets/partitions_multiple.py" linenums="1"
    --8<-- "docs/snippets/partitions_multiple.py"
    ```

    Dagster uses the `partition_expr` metadata to craft the `SELECT` statement when loading the correct partition in a downstream asset. For multi-partitions, Dagster concatenates the `WHERE` statements described in the above sections to craft the correct `SELECT` statement.

    A partition must be selected when materializing the above assets, as described in the [Materializing partitioned assets](/concepts/partitions-schedules-sensors/partitioning-assets#materializing-partitioned-assets) documentation. For example, when materializing the `2023-01-02|Iris-setosa` partition of the above assets, the following query will be used:

    ```sql
    SELECT *
    WHERE species = 'Iris-setosa'
      AND time = '2023-01-02 00:00:00'
    ```

---

## Storing tables in multiple schemas

You may want to have different assets stored in different Iceberg schemas. The Iceberg I/O manager allows you to specify the schema in several ways.

If you want all of your assets to be stored in the same schema, you can specify the schema as configuration to the I/O manager.

If you want to store assets in different schemas, you can specify the schema as part of the asset's key:

```python title="docs/snippets/multiple_schemas.py" linenums="1"
--8<-- "docs/snippets/multiple_schemas.py"
```

In this example, the `iris_dataset` asset will be stored in the `IRIS` schema, and the `daffodil_dataset` asset will be found in the `DAFFODIL` schema.

!!! info "Specifying a schema"

    The two options for specifying schema are mutually exclusive. If you provide{" "}
    <code>schema</code> configuration to the I/O manager, you cannot also provide
    it via the asset key and vice versa. If no <code>schema</code> is provided,
    either from configuration or asset keys, the default schema{" "}
    <code>public</code> will be used.

---

## Using the Iceberg I/O manager with other I/O managers

You may have assets that you don't want to store in Iceberg. You can provide an I/O manager to each asset using the `io_manager_key` parameter in the <PyObject object="asset" decorator /> decorator:

```python title="docs/snippets/multiple_io_managers.py" linenums="1"
--8<-- "docs/snippets/multiple_io_managers.py"
```

In this example:

- The `iris_dataset` asset uses the I/O manager bound to the key `warehouse_io_manager` and `iris_plots` uses the I/O manager bound to the key `blob_io_manager`
- In the <PyObject object="Definitions" /> object, we supply the I/O managers for those keys
- When the assets are materialized, the `iris_dataset` will be stored in Iceberg, and `iris_plots` will be saved in Amazon S3

---

## Storing and loading PyArrow, Pandas, or Polars DataFrames with Iceberg

The Iceberg I/O manager also supports storing and loading PyArrow and Polars DataFrames.

=== "PyArrow Tables"

    The `Iceberg` package relies heavily on Apache Arrow for efficient data transfer, so PyArrow is natively supported.

    You can use `PyArrowIcebergIOManager` to read and write iceberg tables:

    ```python title="docs/snippets/io_manager_pyarrow.py" linenums="1"
    --8<-- "docs/snippets/io_manager_pyarrow.py"
    ```

=== "Pandas DataFrames"

     You can use `PandasIcebergIOManager` to read and write iceberg tables using Pandas:

    ```python title="docs/snippets/io_manager_pandas.py" linenums="1"
    --8<-- "docs/snippets/io_manager_pandas.py"
    ```

=== "Polars DataFrames"

     You can use the `PolarsIcebergIOManager` to read and write iceberg tables using Polars using a full lazily optimized query engine:

    ```python title="docs/snippets/io_manager_polars.py" linenums="1"
    --8<-- "docs/snippets/io_manager_polars.py"
    ```

=== "Daft DataFrames"

     You can use the `DaftIcebergIOManager` to read and write iceberg tables using Daft using a full lazily optimized query engine:

    ```python title="docs/snippets/io_manager_daft.py" linenums="1"
    --8<-- "docs/snippets/io_manager_daft.py"
    ```

---

## Executing custom SQL commands with the Iceberg resource

In addition to the Iceberg I/O manager, Dagster also provides a Iceberg resource for executing custom SQL queries.

```python title="docs/snippets/Iceberg_resource.py" linenums="1"
--8<-- "docs/snippets/Iceberg_resource.py"
```

In this example, we attach the Iceberg resource to the small_petals asset. In the body of the asset function, we use the `load()` method to retrieve the Iceberg `Table` object, which can then be used for further processing.

For more information on the Iceberg resource, see the Iceberg resource API docs.

---

## Configuring table behavior using table properties

Iceberg tables support table properties to configure table behavior. You can see a full list of properties [here](https://py.iceberg.apache.org/configuration/).

Use asset metadata to set table properties:

```python title="docs/snippets/table_properties.py" linenums="1"
--8<-- "docs/snippets/table_properties.py"
```

---

## Using upsert mode to update and insert data

The Iceberg I/O manager supports upsert operations, which allow you to update existing rows and insert new rows in a single operation. This is useful for maintaining slowly changing dimensions or incrementally updating tables.

### Upsert options
Upsert options can be set at deployment time via asset definition metadata, or dynamically at runtime via output metadata. Upsert options set at runtime via `context.add_output_metadata()` take precedence over those set in definition metadata.

**Required**:
  - **join_cols**: list[str] - list of columns that make up the join key for the upsert operation

**Optional**:
  - **when_matched_update_all**: bool - Whether to update rows in the target table that join with the dataframe being upserted (default True)
  - **when_not_matched_insert_all**: bool - Whether to insert all rows from the upsert dataframe that do not join with the target table (default True)


To use upsert mode, set the `write_mode` to `"upsert"` and provide `upsert_options` in the asset or output metadata:

```python
import pyarrow as pa
from dagster import asset, AssetExecutionContext

@asset(
    metadata={
        "write_mode": "upsert",
        "upsert_options": {
            "join_cols": ["id"],  # Columns to join on for matching
            "when_matched_update_all": True,  # Update all columns when matched
            "when_not_matched_insert_all": True,  # Insert all columns when not matched
        }
    }
)
def user_profiles(context: AssetExecutionContext) -> pa.Table:
    # Returns a table with user profiles
    # Rows with matching 'id' will be updated
    # Rows with new 'id' values will be inserted
    return pa.table({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "updated_at": ["2024-01-01", "2024-01-02", "2024-01-03"]
    })
```

You can also override upsert options at runtime using output metadata:

```python
@asset(
    metadata={
        "write_mode": "upsert",
        "upsert_options": {
            "join_cols": ["id"],
            "when_matched_update_all": True,
            "when_not_matched_insert_all": True,
        }
    }
)
def user_profiles_dynamic(context: AssetExecutionContext) -> pa.Table:
    # Override upsert options at runtime based on business logic
    if context.run.tags.get("update_mode") == "id_and_timestamp":
        context.add_output_metadata({
            "upsert_options": {
                "join_cols": ["id", "timestamp"],  # Join on multiple columns
                "when_matched_update_all": False,
                "when_not_matched_insert_all": False,
            }
        })

    return pa.table({
        "id": [1, 2, 3],
        "timestamp": ["2024-01-01", "2024-01-01", "2024-01-01"],
        "name": ["Alice", "Bob", "Charlie"],
    })
```

You can use the `UpsertOptions` `BaseModel` subclass to represent upsert options metadata to provide deployment-time type validation:

```python
from dagster_iceberg.config import UpsertOptions

@asset(
    metadata={
        "write_mode": "upsert",
        "upsert_options": UpsertOptions(
            join_cols=["id", "timestamp"],
            when_matched_update_all=True,
            when_not_matched_insert_all=True,
        )
    }
)
def my_table_typed_upsert(context: AssetExecutionContext, my_table: pa.Table):
    context.add_output_metadata({"upsert_options": UpsertOptions(
                join_cols=["id", "timestamp"],
                when_matched_update_all=True,
                when_not_matched_insert_all=False,
            )
        }
    )
```

---

## Allowing updates to schema and partitions

By default, assets will error when you change the partition spec (e.g. if you change a partition from hourly to daily) or the schema (e.g. when you add a column). You can allow updates to an asset's partition spec and/or schema by adding the following configuration options to the asset metadata:

```python
@asset(
    partitions_def=MultiPartitionsDefinition(
        {
            "date": DailyPartitionsDefinition(start_date="2023-01-01"),
            "species": StaticPartitionDefinition(
                ["Iris-setosa", "Iris-virginica", "Iris-versicolor"]
            ),
        }
    ),
    metadata={
        "partition_expr": {"date": "time", "species": "species"},
        "partition_spec_update_mode": "update",
        "schema_update_mode": "update"
    },
)
def iris_dataset_partitioned(context) -> pd.DataFrame:
    ...
```

---

## Using the custom DB IO Manager

The `dagster-iceberg` library leans heavily on Dagster's `DbIOManager` implementation. This IO manager comes with some limitations, however, such as the lack of support for various [partition mappings](https://docs.dagster.io/_apidocs/partitions#partition-mapping). A custom (experimental) `DbIOManager` implementation is available that supports partition mappings as long as any time-based partition is *consecutive* and static partitions are of string type. You can enable it as follows:

```python
from dagster_iceberg.config import IcebergCatalogConfig
from dagster_iceberg.io_manager.arrow import PyArrowIcebergIOManager


PyArrowIcebergIOManager(
    name="my_catalog",
    config=IcebergCatalogConfig(properties={...}),
    namespace="my_schema",
    db_io_manager="custom"
)
```

For example, a `MultiToSingleDimensionPartitionMapping` is supported:

```python
@asset(
    key_prefix=["my_schema"],
    partitions_def=daily_partitions_def,
    ins={
        "multi_partitioned_asset": AssetIn(
            ["my_schema", "multi_partitioned_asset_1"],
            partition_mapping=MultiToSingleDimensionPartitionMapping(
                partition_dimension_name="date"
            ),
        )
    },
    metadata={
        "partition_expr": "date_column",
    },
)
def single_partitioned_asset_date(multi_partitioned_asset: pa.Table) -> pa.Table:
    ...
```

But a `SpecificPartitionsPartitionMapping` is not because these dates are not consecutive:

```python
@asset(
    partitions_def=multi_partition_with_letter,
    key_prefix=["my_schema"],
    metadata={"partition_expr": {"time": "time", "letter": "letter"}},
    ins={
        "multi_partitioned_asset": AssetIn(
            ["my_schema", "multi_partitioned_asset_1"],
            partition_mapping=MultiPartitionMapping(
                {
                    "color": DimensionPartitionMapping(
                        dimension_name="letter",
                        partition_mapping=StaticPartitionMapping(
                            {"blue": "a", "red": "b", "yellow": "c"}
                        ),
                    ),
                    "date": DimensionPartitionMapping(
                        dimension_name="date",
                        partition_mapping=SpecificPartitionsPartitionMapping(
                            ["2022-01-01", "2024-01-01"]
                        ),
                    ),
                }
            ),
        )
    },
)
def mapped_multi_partition(
    context: AssetExecutionContext, multi_partitioned_asset: pa.Table
) -> pa.Table:
    ...
```


## Integration: Dagster + Modal


> Source: `docs/data_engineering/dagster/dagster-modal/README.md`

# dagster-modal

Leverage the scalable compute platform of Modal from your Dagster pipelines.

## Setup

```sh
uv venv create
source .venv/bin/activate
```

```sh
make install
```

## Test

```sh
make test
```

## Build

```sh
make build
```


## Integration: Dagster + SQLMesh


> Source: `docs/data_engineering/dagster/dagster-sqlmesh/README.md`

# dagster-sqlmesh

_WARNING: THIS IS A WORK IN PROGRESS_

SQLMesh library for dagster integration.

## Current features

* A `@sqlmesh_assets` decorator akin to `dagster-dbt`'s `@dbt_assets` decorator.
* A `SQLMeshResource` that allows you to call sqlmesh from inside an asset
  (likely one defined by the `@sqlmesh_assets` decorator)
* A `SQLMeshDagsterTranslator` that allows customizing the translation of
  sqlmesh models into dagster assets.

## Basic Usage

This dagster sqlmesh adapter is intended to work in a similar pattern to that of
`dagster-dbt` in the most basic case by using the `@sqlmesh_assets`

Assuming that your sqlmesh project is located in a directory `/home/foo/sqlmesh_project`, this is how you'd setup your dagster assets:

```python
from dagster import (
    AssetExecutionContext,
    Definitions,
)
from dagster_sqlmesh import sqlmesh_assets, SQLMeshContextConfig, SQLMeshResource

sqlmesh_config = SQLMeshContextConfig(path="/home/foo/sqlmesh_project", gateway="name-of-your-gateway")

@sqlmesh_assets(environment="dev", config=sqlmesh_config)
def sqlmesh_project(context: AssetExecutionContext, sqlmesh: SQLMeshResource):
    yield from sqlmesh.run(context)

defs = Definitions(
    assets=[sqlmesh_project],
    resources={
        "sqlmesh": SQLMeshResource(config=sqlmesh_config),
    },
)
```

## Advanced Usage

### Custom Translator

The translator is centrally configured and ensures consistency across all components. You can customize the translator by specifying a custom class in the config:

```python
from dagster_sqlmesh import SQLMeshDagsterTranslator

class CustomSQLMeshTranslator(SQLMeshDagsterTranslator):
    def get_asset_key_str(self, fqn: str) -> str:
        # Custom asset key generation logic
        return f"custom_prefix__{super().get_asset_key_str(fqn)}"

# Configure with custom translator
sqlmesh_config = SQLMeshContextConfig(
    path="/home/foo/sqlmesh_project", 
    gateway="name-of-your-gateway",
    translator_class_name="your_module.CustomSQLMeshTranslator"
)

@sqlmesh_assets(environment="dev", config=sqlmesh_config)
def sqlmesh_project(context: AssetExecutionContext, sqlmesh: SQLMeshResource):
    yield from sqlmesh.run(context)
```

This approach ensures that both the `SQLMeshResource` and the `@sqlmesh_assets` decorator use the same translator instance, preventing inconsistencies. The translator is created using `config.get_translator()` and passed to all components that need it, including the `DagsterSQLMeshEventHandler`.


## Contributing

_We are very open to contributions!_

In order to build the project you'll need the following:

* python 3.11 or 3.12
* node 18+
* pnpm 8+

_Note: this is a python project but some of our dependent tools are in typescript. As such all this is needed_

### Installing

The project uses Make commands to simplify the development setup process. To get started:

```bash
make init
```

This will:
- Set up a Python virtual environment with Python 3.12
- Install all Python dependencies
- Install Node.js dependencies via pnpm

_Note: All Make commands automatically use the correct virtual environment - you don't need to activate it manually._

To upgrade dependencies:
```bash
make upgrade-python-deps  # Upgrade Python dependencies
make upgrade-node-deps   # Upgrade Node.js dependencies
```

### Running tests

We have tests that should work entirely locally. You may see a `db.db` file appear in the root of the repository when these tests are run. It can be safely ignored or deleted.

To run tests:

```bash
make test
```

### Running the "sample" dagster project

In the `sample/dagster_project` directory, is a minimal dagster project with the
accompanying sqlmesh project from `sample/sqlmesh_project` configured as an
asset. To run the sample dagster project deployment with a UI:

```bash
make dagster-dev 
```
or 
```bash
make dev
```

If you'd like to materialize the dagster assets quickly on the CLI:

```bash
make dagster-materialize
```

_Note: The sqlmesh project that is in the sample folder has a dependency on a
table that doesn't exist by default within the defined duckdb database. You'll
notice there's a `test_source` asset in the dagster project. This asset will
automatically populate that table in duckdb so that the sqlmesh project can be
run properly. Before you run any materializations against the sqlmesh related
assets in dagster, ensure that you've run the `test_source` at least once._

## Future Plans

* Create a new "loader" for sqlmesh and dagster definitions to allow for
  automatic creation of administrative jobs for sqlmesh (e.g. migrations).
  Additionally, we may want to have this generate assets outside of the
  `multi_asset` paradigm within dagster such that assets can have independent
  partitions. There is an existing issue for this in [dagster
  itself](https://github.com/dagster-io/dagster/issues/14228).

## Integration: Dagster + Evidence


> Source: `docs/data_engineering/dagster/dagster-evidence/README.md`

# dagster-evidence

`dagster-evidence` provides a Dagster Component that integrates with [evidence](https://evidence.dev/), an open-source tool for building data apps.

## Test

```sh
make test
```

## Build

```sh
make build
```


## Integration: Dagster + DSPy


> Source: `docs/data_engineering/dagster/dagster-dspy/Readme.md`

# Economic Data Project

An end-to-end data application that ingests, transforms, and analyzes economic and financial market data using modern open-source tools. The application combines traditional data engineering workflows with AI-powered analysis agents to provide insights into economic cycles, market trends, and asset allocation strategies.

## Tools and Technologies

### Core Frameworks
- **Dagster**: Orchestration framework for data pipelines, asset management, schedules, and sensors
  - [Dagster Documentation](https://docs.dagster.io)
- **dbt**: SQL-based transformation framework for data modeling and analytics
  - [dbt Documentation](https://docs.getdbt.com)
- **DSPy**: Framework for building and optimizing AI agents with LLMs
  - [DSPy Documentation](https://dspy-docs.vercel.app)
- **DuckDB/MotherDuck**: Embedded analytical database with cloud sync capabilities
  - [DuckDB Documentation](https://duckdb.org/docs)
  - [MotherDuck Documentation](https://motherduck.com/docs)

### Supporting Technologies
- **Polars**: High-performance dataframe library
  - [Polars Documentation](https://docs.pola.rs)
- **Sling**: Data replication tool for syncing between databases
  - [Sling Documentation](https://docs.slingdata.io)
- **BigQuery**: Cloud data warehouse for replication target
  - [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- **Python**: Primary programming language (3.10-3.13)

## Data Sources

All data is sourced from publicly available APIs:

### Economic Data
- **Federal Reserve Economic Data (FRED)**: Comprehensive economic indicators including GDP, inflation, employment, housing, trade, and financial conditions
  - [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)
- **Bureau of Labor Statistics (BLS)**: Employment and labor market data
  - [BLS API Documentation](https://www.bls.gov/developers/api_signature.htm)
- **Census Bureau**: Population and demographic data
  - [Census Bureau API Documentation](https://www.census.gov/data/developers/data-sets.html)

### Market Data
- **Market Stack API**: Stock market data for major indices, sectors, global markets, currencies, fixed income, and commodities
  - [Market Stack API Documentation](https://marketstack.com/documentation)
- **Treasury Yields**: U.S. Treasury bond yield curve data
- **Realtor.com**: Housing market inventory and pricing data
  - [Realtor.com Research Data](https://www.realtor.com/research/data/)

## Project Structure

```
economic-data-project/
├── macro_agents/                    # Main Dagster project
│   ├── src/macro_agents/
│   │   ├── definitions.py            # Central Dagster definitions
│   │   └── defs/
│   │       ├── ingestion/           # Data ingestion assets
│   │       │   ├── fred.py          # FRED economic data
│   │       │   ├── bls.py           # Bureau of Labor Statistics
│   │       │   ├── market_stack.py  # Market data API
│   │       │   └── treasury_yields.py
│   │       ├── transformation/     # Data transformation
│   │       │   ├── dbt.py           # dbt integration
│   │       │   └── financial_condition_index.py
│   │       ├── agents/              # AI analysis agents (DSPy)
│   │       │   ├── analysis_agent.py
│   │       │   ├── economic_cycle_analyzer.py
│   │       │   ├── asset_allocation_analyzer.py
│   │       │   └── backtesting.py
│   │       ├── resources/           # Dagster resources
│   │       │   ├── motherduck.py   # DuckDB/MotherDuck connection
│   │       │   ├── fred.py          # FRED API resource
│   │       │   └── market_stack.py  # Market Stack API resource
│   │       ├── replication/         # Data replication
│   │       │   └── sling.py         # Sling replication to BigQuery
│   │       └── schedules.py         # Dagster schedules, sensors, jobs
│   └── tests/                       # Test suite
├── dbt_project/                     # dbt transformation project
│   ├── dbt_project.yml              # dbt configuration
│   ├── profiles.yml                 # Connection profiles
│   └── models/
│       ├── staging/                 # Staging layer models
│       ├── government/              # Government data models
│       ├── markets/                 # Market data models
│       ├── commodities/             # Commodity data models
│       └── analysis/                # Analysis layer models
├── dagster_cloud.yaml               # Dagster Cloud deployment config
└── makefile                         # Build and automation commands
```

## Data Flow

### 1. Ingestion Layer (Dagster Assets)
Raw data assets pull from external APIs and store in DuckDB/MotherDuck:
- **FRED Data**: Partitioned by 70+ economic series codes, scheduled weekly
- **Market Data**: Partitioned by ticker and month for indices, sectors, commodities, currencies
- **Treasury Yields**: Daily yield curve data
- **Housing Data**: Inventory and pricing data from BLS and Realtor.com

### 2. Transformation Layer (dbt Models)
SQL-based transformations organized in layers:
- **Staging**: Standardizes and cleans raw data (`stg_*` models)
- **Government**: Aggregates economic indicators (`fred_*`, `housing_*` models)
- **Markets**: Analyzes market returns and summaries (`*_summary`, `*_analysis_return` models)
- **Commodities**: Commodity-specific analysis
- **Analysis**: Combines economic and market data for advanced analytics (`base_historical_analysis`, `leading_econ_return_indicator`)

### 3. AI Analysis Layer (DSPy Agents)
AI-powered analysis agents that operate on transformed data:
- **Economic Cycle Analysis**: Identifies economic phases (expansion, peak, contraction, trough)
- **Asset Allocation**: Generates portfolio recommendations based on economic conditions
- **Backtesting**: Tests investment strategies against historical data
- **Model Evaluation**: Continuous improvement of AI models using DSPy metrics

### 4. Replication Layer (Sling)
Replicates transformed data from MotherDuck to BigQuery for downstream consumption.

## Environment Variables

Create a `.env` file in the `macro_agents` directory with the following variables:

### Required
- `MODEL_NAME`: OpenAI model to use (e.g., `gpt-4-turbo-preview`, `gpt-3.5-turbo`)
- `OPENAI_API_KEY`: OpenAI API authentication key
- `FRED_API_KEY`: Federal Reserve Economic Data API key
- `MARKETSTACK_API_KEY`: Market Stack API key
- `MOTHERDUCK_TOKEN`: MotherDuck authentication token (for cloud sync)

### Optional (Development)
- `ENVIRONMENT`: Environment setting (`dev` or `prod`, defaults to `dev`)
- `DBT_TARGET`: dbt target environment (`local`, `dev`, or `prod`, defaults to `local`)
- `DBT_PROJECT_DIR`: Path to dbt project directory (auto-detected if not set)

### Optional (Production/Replication)
- `MOTHERDUCK_DATABASE`: MotherDuck database name
- `MOTHERDUCK_PROD_SCHEMA`: MotherDuck production schema
- `BIGQUERY_PROJECT_ID`: Google Cloud project ID for BigQuery
- `BIGQUERY_LOCATION`: BigQuery dataset location
- `BIGQUERY_DATASET`: BigQuery dataset name
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to Google Cloud service account credentials JSON file
- `CENSUS_API_KEY`: Census Bureau API key (if using Census data)

## Quick Start

### Prerequisites
- Python 3.10-3.13
- uv (recommended) or pip for package management
- DuckDB and MotherDuck account (for cloud sync)
- API keys for data sources
- OpenAI API key for AI agents

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd economic-data-project
```

2. **Install dependencies**
```bash
cd macro_agents
uv sync  # or pip install -e .[dev]
```

3. **Install dbt packages**
```bash
cd ../dbt_project
dbt deps
```

4. **Set up environment variables**
Create a `.env` file in the `macro_agents` directory with required variables (see Environment Variables section above).

5. **Validate setup**
```bash
# Test Dagster definitions
cd macro_agents
dg check defs

# Test dbt models
cd ../dbt_project
dbt compile
dbt parse
```

### Running Locally

**Start Dagster UI:**
```bash
cd macro_agents
dagster dev
```
Navigate to `http://localhost:3000` to view and materialize assets.

**Run dbt models manually:**
```bash
cd dbt_project
dbt run          # Run all models
dbt run --select staging.*  # Run specific layer
```

**Run tests:**
```bash
cd macro_agents
pytest tests/ -v
# Or use the makefile
make test
```

## Deployment

The project is configured for deployment on Dagster Cloud using the `dagster_cloud.yaml` configuration file. The deployment builds from the `macro_agents` directory and uses `macro_agents.definitions` as the entry point.

## Development

### Common Commands

```bash
# Run tests
make test

# Lint Python code
make ruff

# Lint SQL code
make lint

# Fix SQL linting issues
make fix

# Run pre-PR checks (linting, type checking, tests, security scans)
make pre-pr
```

### First Run Workflow

1. **Materialize ingestion assets** - Start with FRED data or Market Stack data via Dagster UI
2. **Run dbt transformations** - Transform raw data through staging → marts → analysis layers (automated via eager assets)
3. **Run analysis agents** - Execute DSPy agents on transformed data via Dagster UI
4. **View results** - Check DuckDB/MotherDuck for analysis outputs

## Automation

- **Ingestion Assets**: Scheduled weekly on Mondays at midnight (FRED data)
- **dbt Models**: Eager automation (run automatically when upstream data changes)
- **Analysis Agents**: On-demand or scheduled via Dagster jobs
- **Replication**: Monthly partitioned replication to BigQuery via Sling

## Testing

Test suite located in `macro_agents/tests/`:
- Unit tests for analysis agents
- Integration tests for end-to-end workflows
- Tests for Dagster asset descriptions
- Tests for dbt model descriptions
- Resource and schedule tests

Run tests using `make test` or `pytest tests/ -v` from the `macro_agents` directory.


## Original Sources

- `docs/data_engineering/dagster/Advanced config types _ Dagster Docs.md`
- `docs/data_engineering/dagster/Building machine learning pipelines with Dagster _ Dagster Docs.md`
- `docs/data_engineering/dagster/Components _ Dagster Docs.md`
- `docs/data_engineering/dagster/Creating workspaces to manage multiple projects _ Dagster Docs.md`
- `docs/data_engineering/dagster/Dagster Orchestration for Cocoindex, Graphiti.md`
- `docs/data_engineering/dagster/dagster_ducklake.md`
- `docs/data_engineering/dagster/dagster_iceberg.md`
- `docs/data_engineering/dagster/dagster-api-quick-reference.md`
- `docs/data_engineering/dagster/dagster-design-patterns-research.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/claude.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/create-custom-dagster-component/SKILL.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/references/assets.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/references/automation.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/references/etl-patterns.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/references/project-structure.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/references/resources.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/references/testing.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-development/SKILL.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dagster-init/SKILL.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dbt-development/dbt_examples.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dbt-development/dbt_skill.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/dignified-python/SKILL.md`
- `docs/data_engineering/dagster/dagster-dspy/.claude/skills/git-pr-workflow/SKILL.md`
- `docs/data_engineering/dagster/dagster-dspy/Readme.md`
- `docs/data_engineering/dagster/dagster-ducklake/README.md`
- `docs/data_engineering/dagster/dagster-evidence/README.md`
- `docs/data_engineering/dagster/dagster-iceberg/CHANGELOG.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/code_reference.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/development.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/features.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/index.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/installation.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/quickstart.md`
- `docs/data_engineering/dagster/dagster-iceberg/docs/reference.md`
- `docs/data_engineering/dagster/dagster-iceberg/README.md`
- `docs/data_engineering/dagster/dagster-modal/CHANGELOG.md`
- `docs/data_engineering/dagster/dagster-modal/README.md`
- `docs/data_engineering/dagster/dagster-openapi-research.md`
- `docs/data_engineering/dagster/dagster-orchestration.md`
- `docs/data_engineering/dagster/dagster-research-2024-2025.md`
- `docs/data_engineering/dagster/dagster-research.md`
- `docs/data_engineering/dagster/dagster-sqlmesh/CHANGELOG.md`
- `docs/data_engineering/dagster/dagster-sqlmesh/README.md`
- `docs/data_engineering/dagster/dagster.md`
- `docs/data_engineering/dagster/Data Ingestion Patterns_ Push, Pull & Poll Explained _ Dagster.md`
- `docs/data_engineering/dagster/datadog (dagster-datadog) _ Dagster Docs.md`
- `docs/data_engineering/dagster/deploy/README.md`
- `docs/data_engineering/dagster/Deploying Dagster to Google Cloud Platform _ Dagster Docs.md`
- `docs/data_engineering/dagster/dlt (dagster-dlt) _ Dagster Docs.md`
- `docs/data_engineering/dagster/duckdb (dagster-duckdb) _ Dagster Docs.md`
- `docs/data_engineering/dagster/github (dagster-github) _ Dagster Docs.md`
- `docs/data_engineering/dagster/graphql (dagster-graphql) _ Dagster Docs.md`
- `docs/data_engineering/dagster/How the Dagster MCP allows you to write better code.md`
- `docs/data_engineering/dagster/iceberg (dagster-iceberg) _ Dagster Docs.md`
- `docs/data_engineering/dagster/KCG_SUMMARY.md`
- `docs/data_engineering/dagster/Manage concurrency of Dagster assets, jobs, and Dagster instances _ Dagster Docs.md`
- `docs/data_engineering/dagster/Managing machine learning models with Dagster _ Dagster Docs.md`
- `docs/data_engineering/dagster/mlflow (dagster-mlflow) _ Dagster Docs.md`
- `docs/data_engineering/dagster/postgresql (dagster-postgres) _ Dagster Docs.md`
- `docs/data_engineering/dagster/Real-time system _ Dagster Docs.md`
- `docs/data_engineering/dagster/Run configuration _ Dagster Docs.md`
- `docs/data_engineering/dagster/Using environment variables and secrets in Dagster code _ Dagster Docs.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
