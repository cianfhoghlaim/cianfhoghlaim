# Lakehouse Notebooks

Interactive notebooks demonstrating the unified data lakehouse architecture.

## Prerequisites

Install required dependencies:

```bash
pip install marimo duckdb lancedb requests
pip install "dlt[ducklake,motherduck]"
```

## Running Notebooks

### Interactive Mode

```bash
marimo edit notebooks/lakehouse_pipeline.py
```

### Run Mode (Read-only)

```bash
marimo run notebooks/lakehouse_pipeline.py
```

## Notebooks

### `lakehouse_pipeline.py`

Demonstrates the full local/remote data pipeline:

1. **Data Ingestion**: Using dlt to fetch Hacker News stories
2. **SQL Catalog**: DuckLake for table metadata (local PostgreSQL or PlanetScale)
3. **Query Engine**: DuckDB for analytics
4. **Vector Catalog**: Lance Namespace for vector table registration
5. **Object Storage**: Garage S3 (local) or Cloudflare R2 (remote)

## Local Development

Start the lakehouse stack:

```bash
docker compose up -d
```

Services available:
- **Garage S3**: http://localhost:3900
- **Lakekeeper**: http://localhost:8181
- **Lance Namespace**: http://localhost:8182

## Environment Variables

### Local Development

```bash
# PostgreSQL (for DuckLake catalog)
export LOCAL_HOST=localhost
export LOCAL_PORT=5432
export LOCAL_USER=ducklake_user
export LOCAL_PASSWORD=ducklake_password
export LOCAL_DBNAME=ducklake_catalog

# Garage S3
export AWS_ENDPOINT_URL=http://localhost:3900
export AWS_ACCESS_KEY_ID=lakehouse
export AWS_SECRET_ACCESS_KEY=devpassword
export AWS_REGION=garage

# Lance Namespace
export LANCE_NAMESPACE_URL=http://localhost:8182
```

### Remote Production

```bash
# MotherDuck
export MOTHERDUCK_TOKEN=your-token

# PlanetScale PostgreSQL
export PLANETSCALE_HOST=aws.connect.psdb.cloud
export PLANETSCALE_USER=lakehouse
export PLANETSCALE_PASSWORD=your-password
export PLANETSCALE_DBNAME=lakehouse

# Cloudflare R2
export R2_ACCESS_KEY_ID=your-key
export R2_SECRET_ACCESS_KEY=your-secret
export R2_ACCOUNT_ID=your-account
export R2_BUCKET_NAME=lakehouse

# Remote Lance Namespace
export LANCE_NAMESPACE_URL=https://lance-api.cianfhoghlaim.ie
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Pipeline (dlt)                      │
│  @dlt.resource → pipeline.run() → destination               │
└─────────────────────┬───────────────────────────────────────┘
                      │
            ┌─────────┴─────────┐
            │                   │
      ┌─────▼─────┐       ┌─────▼─────┐
      │ DuckLake  │       │ Lance NS  │
      │ (SQL)     │       │ (Vector)  │
      └─────┬─────┘       └─────┬─────┘
            │                   │
      ┌─────▼─────────────────▼─────┐
      │       Iceberg Catalog        │
      │       (Lakekeeper)           │
      └─────────────┬────────────────┘
                    │
      ┌─────────────▼────────────────┐
      │        Object Storage         │
      │   Garage (local) / R2 (cloud) │
      └───────────────────────────────┘
```

## Key Patterns

### 1. Local-to-Cloud Migration

```python
# LOCAL: Validate with DuckLake
pipeline = dlt.pipeline(
    destination="ducklake",
    dataset_name="my_data"
)

# REMOTE: Deploy to MotherDuck (same code, different destination)
pipeline = dlt.pipeline(
    destination="motherduck",
    dataset_name="my_data"
)
```

### 2. Lance "Trojan Horse"

Register Lance tables in Iceberg catalog:

```python
import requests

# Create namespace
requests.post("http://localhost:8182/namespaces", json={
    "namespace": ["embeddings"]
})

# Register Lance table (appears as Iceberg with table_type=lance)
requests.post("http://localhost:8182/namespaces/embeddings/tables", json={
    "name": "articles",
    "location": "s3://lance/embeddings/articles"
})
```

### 3. DuckDB + DuckLake

```sql
INSTALL ducklake;
LOAD ducklake;

-- Attach to PostgreSQL-backed catalog
ATTACH 'ducklake:postgres:host=localhost dbname=ducklake_catalog'
    AS lakehouse (DATA_PATH 'ducklake_data/');

-- Query tables
SELECT * FROM lakehouse.schema.table;
```
