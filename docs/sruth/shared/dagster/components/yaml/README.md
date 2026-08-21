# Dagster YAML Component Definitions

This directory contains YAML component definitions for sruth pipelines.

## Component Examples

### 1. Browser Scraping Asset

```yaml
# browser_scraping_component.yaml
component: sruth.shared.dagster.components.BrowserScrapeComponent
attributes:
  asset_key: ["sec", "exam_papers"]
  asset_name: "exam_papers"
  group_name: "scraping"
  description: "SEC exam papers from examinations.ie"

  urls:
    - "https://www.examinations.ie/exammaterialarchive/"
  extract_instruction: "Extract all PDF links for exam papers, including year, subject, and level"
  extract_formats: ["markdown", "json", "links"]

  browser_backend: "stagehand"
  headless: true
  partition_by_url: true
```

### 2. DLT Asset with Partitions

```yaml
# curriculum_asset_component.yaml
component: sruth.shared.dagster.components.DLTAssetComponent
attributes:
  asset_key: ["ireland", "curriculum", "pages"]
  asset_name: "curriculum_pages"
  group_name: "curriculum"
  description: "Irish curriculum pages from NCCA"

  source_module: "sruth.oideachais.dlt_sources.curriculum_source"
  pipeline_name: "curriculum_pipeline"
  dataset_name: "curriculum"
  write_disposition: "merge"
  primary_key: "url"

  partitions:
    cycle:
      type: "static"
      values: ["junior_cycle", "senior_cycle"]
    subject:
      type: "static"
      values: ["mathematics", "english", "irish", "science", "history"]
    language:
      type: "static"
      values: ["en", "ga"]

  max_retries: 3
  retry_delay: 30
  enable_langfuse: true
```

### 3. Iceberg I/O Manager

```yaml
# iceberg_io_component.yaml
component: sruth.shared.dagster.components.IcebergIOComponent
attributes:
  name: "iceberg_io"
  catalog_uri: "${LAKEKEEPER_CATALOG_URI:-http://lakekeeper:8181}"
  warehouse: "${ICEBERG_WAREHOUSE:-s3://garage/warehouse}"
  namespace: "curriculum"

  s3_endpoint: "${GARAGE_ENDPOINT_URL:-http://garage:3900}"
  s3_access_key: "${GARAGE_ACCESS_KEY:-garage_key}"
  s3_secret_key: "${GARAGE_SECRET_KEY:-garage_secret}"
  s3_region: "${AWS_REGION:-garage}"
  s3_use_ssl: false

  compute_kind: "polars"
  table_properties:
    write.format.default: "parquet"
    write.compression-codec: "zstd"
    write.parquet.page-size-bytes: "2097152"
```

### 4. REST API Source

```yaml
# rest_api_source_component.yaml
component: sruth.shared.dagster.components.DLTSourceComponent
attributes:
  name: "ncca_api"
  source_type: "rest"

  base_url: "https://curriculumonline.ie/api"
  auth_type: "none"
  headers:
    Accept: "application/json"

  paginator_type: "page"
  page_param: "page"
  page_size: 50

  cursor_param: "cursor"
```

### 5. Multi-Environment Pipeline

```yaml
# pipeline_environments.yaml
environments:
  development:
    iceberg_io:
      catalog_uri: "http://localhost:8181"
      warehouse: "s3://localhost:9000/warehouse"
      namespace: "dev"

    browser:
      headless: false
      timeout: 60.0

    observability:
      langfuse:
        enabled: false

  production:
    iceberg_io:
      catalog_uri: "${LAKEKEEPER_CATALOG_URI}"
      warehouse: "${ICEBERG_WAREHOUSE}"
      namespace: "production"

    browser:
      headless: true
      timeout: 30.0

    observability:
      langfuse:
        enabled: true
        public_key: "${LANGFUSE_PUBLIC_KEY}"
        secret_key: "${LANGFUSE_SECRET_KEY}"
```

## Usage

### In Dagster Definitions

```python
# definitions.py
from dagster import Definitions, Config

# Load component from YAML
defs = Definitions(
    # Assets from components
    assets=load_assets_from_yaml_component("browser_scraping_component.yaml"),
    # Resources from components
    resources=load_resources_from_yaml_component("iceberg_io_component.yaml"),
)
```

### Via CLI

```bash
# List components
dagster dev show-components

# Load specific component
dagster dev --component yaml/browser_scraping_component.yaml

# Validate component
dagster dev validate-component yaml/browser_scraping_component.yaml
```

## Environment Variables

Components use environment variable substitution with defaults:

```yaml
# Format: ${VAR_NAME:-default_value}
catalog_uri: "${LAKEKEEPER_CATALOG_URI:-http://lakekeeper:8181}"
```

Required variables (no default) will fail if unset:

```yaml
api_key: "${API_KEY}"  # Fails if API_KEY not set
```
