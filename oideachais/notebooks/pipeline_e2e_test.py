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
def _(mo):
    # Configure Services
    AWS_ENDPOINT = "http://localhost:3900"
    AWS_ACCESS_KEY = "GK8126ec04258979d6abd12d8e"
    AWS_SECRET_KEY = "0c3ec792597afad234d35f2dcf788e4e88cde3378e12525c2f8d1708b89af70e"
    
    # We will use DLT directly to query the data destination (DuckDB or Postgres)
    # as it abstracts away the connection details.
    
    mo.md(f"""
    ## 1. Infrastructure Status
    
    - **Garage S3:** Configured at `{AWS_ENDPOINT}`
    - **Pipeline Catalog:** Will attach via DLT `curriculum_unified` pipeline
    """)
    return AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY

@app.cell
def _(mo, pd):
    import dlt

    try:
        pipeline = dlt.attach("curriculum_unified")
        with pipeline.sql_client() as client:
            query = """
            SELECT cycle, subject, language, count(*) as pages 
            FROM curriculum.curriculum_pages 
            GROUP BY cycle, subject, language 
            ORDER BY pages DESC
            """
            with client.execute_query(query) as cursor:
                columns = [col[0] for col in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                
            df_pages = pd.DataFrame(rows, columns=columns)
            ducklake_status = "✅ Data successfully queried via DLT pipeline"
    except Exception as e:
        df_pages = pd.DataFrame({"error": [str(e)]})
        ducklake_status = f"❌ Pipeline connection failed: {e}"

    mo.vstack([
        mo.md(f"### 2. DuckLake/DLT Verification\n{ducklake_status}"),
        mo.ui.table(df_pages, selection=None)
    ])
    return df_pages, dlt, ducklake_status, pipeline, query

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
