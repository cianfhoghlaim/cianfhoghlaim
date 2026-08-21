# Component-Based Architecture Summary

## Overview

The sruth data pipelines now use a **component-based architecture** that enables:
- Declarative YAML configuration
- Multi-environment support (dev/staging/prod)
- Reusable components across flows
- Automatic dependency management

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    YAML Component Layer                     │
│  (Declarative configuration with env var substitution)       │
├─────────────────────────────────────────────────────────────┤
│                    Dagster Component Layer                  │
│  (dg.Component + dg.Model for schema-based config)         │
├─────────────────────────────────────────────────────────────┤
│                      Shared Libraries                       │
│  (DLT sources, observability, storage, browser stack)      │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                      │
│  (Lakekeeper, Garage/R2, DuckDB, PostgreSQL)               │
└─────────────────────────────────────────────────────────────┘
```

## Component Types

### 1. DLTAssetComponent
Wraps DLT sources into Dagster assets with partitioning support.

```yaml
component: sruth.shared.dagster.components.DLTAssetComponent
attributes:
  asset_key: ["curriculum", "pages"]
  source_module: "sruth.oideachais.dlt_sources.curriculum_source"
  pipeline_name: "curriculum_pipeline"
  partitions:
    subject: {type: "static", values: ["math", "english", "irish"]}
    language: {type: "static", values: ["en", "ga"]}
```

### 2. IcebergIOComponent
Iceberg I/O manager with Lakekeeper catalog integration.

```yaml
component: sruth.shared.dagster.components.IcebergIOComponent
attributes:
  catalog_uri: "${LAKEKEEPER_CATALOG_URI}"
  warehouse: "${ICEBERG_WAREHOUSE}"
  namespace: "curriculum"
```

### 3. BrowserScrapeComponent
Browser scraping with circuit breaker fallback.

```yaml
component: sruth.shared.dagster.components.BrowserScrapeComponent
attributes:
  urls: ["https://examinations.ie/"]
  extract_instruction: "Extract PDF links with metadata"
  browser_backend: "stagehand"
```

## File Structure

```
sruth/shared/
├── dlt/
│   ├── __init__.py
│   ├── sources.py          # BaseSource, RESTSource, BrowserSource
│   └── destinations.py     # get_dlt_destination(), get_iceberg_destination()
├── dagster/
│   ├── __init__.py
│   ├── resources.py        # LakeKeeperResource, BrowserResource
│   ├── factories.py        # dlt_asset_factory(), multi_partition_factory()
│   └── components/
│       ├── __init__.py
│       ├── dlt_component.py       # DLTAssetComponent, DLTSourceComponent
│       ├── iceberg_component.py   # IcebergIOComponent, DuckDBComponent
│       ├── browser_component.py   # BrowserScrapeComponent, BrowserResourceComponent
│       ├── loader.py              # load_components_from_yaml()
│       └── yaml/
│           ├── README.md          # Component documentation
│           ├── examinations_scraper.yaml
│           ├── curriculum_asset.yaml
│           ├── iceberg_io.yaml
│           ├── ncca_rest_source.yaml
│           ├── multi_environment.yaml
│           └── example_pipeline.yaml
├── storage/
│   ├── __init__.py
│   └── unified_storage.py   # UnifiedStorage, get_storage()
└── observability/
    ├── __init__.py
    └── unified_tracer.py    # UnifiedTracer, get_tracer()
```

## Usage Example

### 1. Define Component in YAML

```yaml
# my_component.yaml
component: sruth.shared.dagster.components.DLTAssetComponent
attributes:
  asset_key: ["data", "source"]
  source_module: "my_project.dlt_sources.my_source"
  pipeline_name: "my_pipeline"
```

### 2. Load in Python

```python
# definitions.py
from dagster import Definitions
from sruth.shared.dagster.components.loader import load_components_from_yaml

defs = load_components_from_yaml("my_component.yaml")
```

### 3. Run with Environment

```bash
export SRUTH_ENV=production
dagster dev
```

## Environment Variable Patterns

| Variable | Purpose | Default |
|----------|---------|---------|
| `SRUTH_ENV` | Environment selector | `local` |
| `LAKEKEEPER_CATALOG_URI` | Iceberg catalog | `http://lakekeeper:8181` |
| `ICEBERG_WAREHOUSE` | Warehouse location | `s3://garage/warehouse` |
| `GARAGE_ENDPOINT_URL` | S3 endpoint | `http://garage:3900` |
| `LANGFUSE_PUBLIC_KEY` | Langfuse auth | - |
| `LANGFUSE_SECRET_KEY` | Langfuse auth | - |

## Key Features

### 1. Multi-Dimensional Partitioning
```yaml
partitions:
  cycle: {type: "static", values: ["junior", "senior"]}
  subject: {type: "static", values: ["math", "english"]}
  language: {type: "static", values: ["en", "ga"]}
```
Creates assets for each combination (2 × 3 × 2 = 12 partitions)

### 2. Environment-Specific Overrides
```yaml
environments:
  development:
    partitions:
      subject: {values: ["math"]}  # Single subject for dev
```

### 3. Auto-Discovery
Components are auto-discovered via `dg.Component` inheritance and
Python module scanning.

### 4. Type-Safe Configuration
All components use `dg.Model` for Pydantic-style validation.

## Migration Path

### From Manual Assets to Components

**Before (Manual):**
```python
@asset(key=["curriculum", "pages"])
def curriculum_asset(context):
    pipeline = dlt.pipeline(...)
    result = pipeline.run(source)
    return MaterializeResult(...)
```

**After (Component):**
```yaml
component: sruth.shared.dagster.components.DLTAssetComponent
attributes:
  asset_key: ["curriculum", "pages"]
  source_module: "sruth.oideachais.dlt_sources.curriculum_source"
  pipeline_name: "curriculum_pipeline"
```

### Benefits of Component Approach

1. **Declarative**: Configuration in YAML, not code
2. **Reusable**: Components shared across flows
3. **Environment-Aware**: Easy dev/staging/prod configs
4. **Type-Safe**: Schema validation via Pydantic
5. **Observable**: Built-in tracing and metrics

## Next Steps

1. **Add `.dlt/` configs** to all sruth flows
2. **Create source modules** for each data source
3. **Migrate existing assets** to component definitions
4. **Set up environment configs** for dev/staging/prod
5. **Enable observability** (Langfuse, MLflow, Datadog)

## References

- DLT Docs: https://dlthub.com/docs/hub/features/project/overview
- Dagster Components: https://docs.dagster.io/api/dagster/components
- DuckLake: https://ducklake.select/docs/stable/duckdb/usage/connecting
- Lakekeeper: https://docs.lakekeeper.io/docs/nightly/configuration/
