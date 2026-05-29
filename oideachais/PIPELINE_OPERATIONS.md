# Oideachais Data Pipeline Operations

This guide outlines how to execute the end-to-end curriculum data pipelines using Dagster and verify that the data has correctly propagated through the unified Lakehouse architecture (Garage, DuckLake, and LanceDB).

## 1. Running the Dagster Pipelines

The data platform uses Dagster for orchestration. To start the local development server:

```bash
cd data_platform
uv run dagster dev -m oideachais.data_platform.dagster_defs.definitions
```

1. Open the Dagster UI at [http://localhost:3000](http://localhost:3000).
2. Navigate to **Assets** or **Jobs**.
3. To run the full curriculum extraction for a specific cycle (e.g., Senior Cycle):
   - Go to the `curriculum_senior_cycle_job` or select the `ireland/curriculum/senior_cycle` asset.
   - Click **Materialize** and provide the required partition (e.g., `en|english`).
4. To process the downloaded PDFs:
   - Run the `pdf_processing` job, which executes `pdf_downloads` followed by `pdf_extracted_text` (Docling OCR).

## 2. Verifying Garage (S3 Object Storage)

Garage acts as the S3-compatible backend for both DuckLake (Parquet metadata) and raw artifact storage (PDFs).

You can verify the data using the `aws` CLI configured for the local endpoint:
```bash
export AWS_ACCESS_KEY_ID=lakehouse
export AWS_SECRET_ACCESS_KEY=devpassword
export AWS_ENDPOINT_URL=http://localhost:3900

# List the DuckLake bucket contents
aws s3 ls s3://ducklake/oideachais/
```

*Expected Output:* You should see directories containing `.parquet` files for your datasets (e.g., `curriculum_staging`, `curriculum`).

## 3. Verifying DuckLake (Postgres Catalog + DuckDB)

DuckLake uses PostgreSQL to maintain ACID transactions and table metadata, while pointing to the Parquet files in Garage S3. 

To query the data, you can attach the Postgres catalog directly using DuckDB:

```python
import duckdb

con = duckdb.connect()

# Install and load extensions
con.execute("INSTALL httpfs; LOAD httpfs;")
con.execute("INSTALL postgres; LOAD postgres;")

# Configure S3 for Garage
con.execute("SET s3_endpoint='localhost:3900';")
con.execute("SET s3_use_ssl=false;")
con.execute("SET s3_url_style='path';")
con.execute("SET s3_access_key_id='lakehouse';")
con.execute("SET s3_secret_access_key='devpassword';")
con.execute("SET s3_region='garage';")

# Attach DuckLake Catalog (assuming lakehouse-postgres is mapped to 5433 locally)
catalog_uri = "postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais"
con.execute(f"ATTACH '{catalog_uri}' AS ducklake (TYPE POSTGRES);")

# Query the Extracted Pages
print(con.execute("SELECT cycle, subject, language, count(*) FROM ducklake.oideachais.curriculum_pages GROUP BY cycle, subject, language;").fetchall())
```

*Note:* In local Dagster dev mode when `USE_DUCKLAKE=false`, it will write to a local DuckDB file (e.g., `curriculum_unified.duckdb`) instead of the remote Postgres catalog.

## 4. Verifying the Lance Namespace (Vector Embeddings)

The Lance Namespace sidecar adapts Iceberg catalog requests for LanceDB, enabling vector search over the parsed OCR documents.

**Verify Sidecar Health:**
```bash
curl http://localhost:8182/health
```

**Verify LanceDB Tables (Python):**
Once the `embedding_assets` are triggered in Dagster, you can query LanceDB to verify the embeddings exist:

```python
import lancedb

# Connect to the LanceDB bucket in Garage S3
db = lancedb.connect("s3://lance/oideachais/", 
    storage_options={
        "endpoint_url": "http://localhost:3900",
        "aws_access_key_id": "lakehouse",
        "aws_secret_access_key": "devpassword",
        "region": "garage"
    }
)

print(db.table_names())
table = db.open_table("curriculum_embeddings")
print(f"Total embedded chunks: {table.count_rows()}")
```
