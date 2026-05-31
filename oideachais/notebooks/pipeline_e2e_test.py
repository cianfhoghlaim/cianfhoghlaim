import marimo

__generated_with = "0.10.14"
app = marimo.App(width="medium")

@app.cell
def _():
    import os
    import marimo as mo
    import duckdb
    import lancedb
    import boto3
    import pandas as pd
    from sentence_transformers import SentenceTransformer

    mo.md("""
    # E2E Pipeline Testing

    This notebook tests the data engineering pipelines end-to-end, validating Garage S3, DuckLake Postgres, and LanceDB Vector Store integration.
    """)
    return boto3, duckdb, lancedb, mo, os, pd, SentenceTransformer

@app.cell
def _(duckdb, mo):
    # Configure Services
    AWS_ENDPOINT = "http://localhost:3900"
    AWS_ACCESS_KEY = "lakehouse"
    AWS_SECRET_KEY = "devpassword"

    # Configure DuckDB Connection to S3/Postgres
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL postgres; LOAD postgres;")

    con.execute(f"SET s3_endpoint='{AWS_ENDPOINT.replace('http://', '')}';")
    con.execute("SET s3_use_ssl=false;")
    con.execute("SET s3_url_style='path';")
    con.execute(f"SET s3_access_key_id='{AWS_ACCESS_KEY}';")
    con.execute(f"SET s3_secret_access_key='{AWS_SECRET_KEY}';")
    con.execute("SET s3_region='garage';")

    # Try to attach remote ducklake catalog, fallback to local duckdb file
    try:
        catalog_uri = "postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais"
        con.execute(f"ATTACH '{catalog_uri}' AS ducklake (TYPE POSTGRES);")
        catalog_type = "PostgreSQL (Remote)"
    except Exception as e:
        con.execute("ATTACH 'curriculum_unified.duckdb' AS ducklake;")
        catalog_type = "DuckDB File (Local)"

    mo.md(f"""
    ## 1. Infrastructure Status

    - **Garage S3:** Connected to `{AWS_ENDPOINT}`
    - **DuckLake Catalog:** Attached via `{catalog_type}`
    """)
    return AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, catalog_type, catalog_uri, con

@app.cell
def _(con, mo, pd):
    # Verify DuckLake Extraction
    query = """
    SELECT cycle, subject, language, count(*) as pages 
    FROM ducklake.curriculum_pages 
    GROUP BY cycle, subject, language 
    ORDER BY pages DESC
    """

    try:
        df_pages = con.execute(query).df()
        ducklake_status = "✅ Data successfully extracted to DuckLake"
    except Exception as e:
        df_pages = pd.DataFrame({"error": [str(e)]})
        ducklake_status = f"❌ DuckLake extraction failed or pending: {e}"

    mo.vstack([
        mo.md(f"### 2. DuckLake Verification\n{ducklake_status}"),
        mo.ui.table(df_pages, selection=None)
    ])
    return df_pages, ducklake_status, query

@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, boto3, mo):
    # Verify Garage S3 PDF Storage
    s3 = boto3.client(
        "s3",
        endpoint_url=AWS_ENDPOINT,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name="garage"
    )

    try:
        objects = s3.list_objects_v2(Bucket="ducklake", Prefix="oideachais/downloads/")
        if "Contents" in objects:
            pdf_count = len([obj for obj in objects["Contents"] if obj["Key"].endswith(".pdf")])
            garage_status = f"✅ Found {pdf_count} PDFs in Garage S3 (`s3://ducklake/oideachais/downloads/`)"
        else:
            garage_status = "⚠️ Garage S3 bucket is empty. Did the `pdf_downloads` job run?"
    except Exception as e:
        garage_status = f"❌ Garage S3 connection failed: {e}"

    mo.md(f"### 3. Garage S3 Verification\n{garage_status}")
    return garage_status, objects, pdf_count, s3

@app.cell
def _(
    AWS_ACCESS_KEY,
    AWS_ENDPOINT,
    AWS_SECRET_KEY,
    SentenceTransformer,
    lancedb,
    mo,
):
    # Verify LanceDB Vector Indexing
    LANCEDB_URI = "s3://lance/oideachais/"

    # Local HF embedding model (fallback or primary depending on environment)
    model_name = "all-MiniLM-L6-v2"

    try:
        # Connect to LanceDB stored in Garage S3
        db = lancedb.connect(
            LANCEDB_URI, 
            storage_options={
                "endpoint_url": AWS_ENDPOINT,
                "aws_access_key_id": AWS_ACCESS_KEY,
                "aws_secret_access_key": AWS_SECRET_KEY,
                "region": "garage"
            }
        )
        tables = db.table_names()
        
        if "curriculum_embeddings" in tables:
            table = db.open_table("curriculum_embeddings")
            row_count = table.count_rows()
            lance_status = f"✅ LanceDB Connected. Table `curriculum_embeddings` has {row_count} vector chunks."
            
            # Load local model and run a test query
            mo.md("Loading local embedding model...")
            model = SentenceTransformer(model_name)
            query_str = "What is the structure of the leaving cert biology exam?"
            query_vector = model.encode(query_str)
            
            # Search
            results = table.search(query_vector).limit(3).to_pandas()
            search_ui = mo.vstack([
                mo.md(f"**Test Query:** '{query_str}'"),
                mo.ui.table(results[["text", "_distance"]], selection=None) if not results.empty else mo.md("No semantic results found.")
            ])
            
        else:
            lance_status = f"⚠️ LanceDB Connected, but `curriculum_embeddings` table not found. Available tables: {tables}"
            search_ui = mo.md("")

    except Exception as e:
        lance_status = f"❌ LanceDB Verification Failed: {e}"
        search_ui = mo.md("")

    mo.vstack([
        mo.md(f"### 4. LanceDB Vector Verification\n{lance_status}"),
        search_ui
    ])
    return (
        LANCEDB_URI,
        db,
        lance_status,
        model,
        model_name,
        query_str,
        query_vector,
        results,
        search_ui,
        table,
        tables,
    )

if __name__ == "__main__":
    app.run()
