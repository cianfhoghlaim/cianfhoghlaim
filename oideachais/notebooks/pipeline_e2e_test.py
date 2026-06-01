import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import duckdb
    import os
    from dotenv import load_dotenv
    load_dotenv() # Load your AWS keys from .env
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    # Configure DuckDB to use the local Garage S3 endpoint
    con.execute("SET s3_endpoint='localhost:3900';")
    con.execute("SET s3_use_ssl=false;")
    con.execute("SET s3_url_style='path';")
    con.execute(f"SET s3_access_key_id='{os.environ.get('AWS_ACCESS_KEY_ID')}';")
    con.execute(f"SET s3_secret_access_key='{os.environ.get('AWS_SECRET_ACCESS_KEY')}';")
    con.execute("SET s3_region='garage';")
    # Query the processed partitions directly from S3
    query = """
        SELECT cycle, subject, language, count(*) as pages_extracted 
        FROM read_parquet('s3://ducklake/oideachais/curriculum/curriculum_pages/*.parquet') 
        GROUP BY cycle, subject, language
        LIMIT 10;
    """
    print(con.execute(query).df())
    return


@app.cell
def _():
    import os
    import sys

    # Add data_platform to path to import Dagster definitions
    sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), 'oideachais/data_platform')))
    try:
        from dagster_defs.definitions import defs
    except ImportError:
        defs = None

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
    return SentenceTransformer, boto3, defs, lancedb, mo, pd


@app.cell
def _(mo):
    # Configure Services
    AWS_ENDPOINT = "http://localhost:3900"
    AWS_ACCESS_KEY = "GK8126ec04258979d6abd12d8e"
    AWS_SECRET_KEY = "0c3ec792597afad234d35f2dcf788e4e88cde3378e12525c2f8d1708b89af70e"

    mo.md(f"""
    ## 1. Infrastructure Status

    - **Garage S3:** Configured at `{AWS_ENDPOINT}`
    - **Pipeline Catalog:** Will attach via DLT `curriculum_unified` pipeline
    """)
    return AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY


@app.cell
def _(defs, mo):
    if not defs:
        ui_controls = mo.md("❌ Cannot load Dagster definitions. Ensure you are running this from the repository root.")
        cycle_dropdown = None
        partition_input = None
        run_extraction_btn = None
        run_pdf_btn = None
        run_all_btn = None
    else:
        # Setup Dropdowns for Pipeline Triggers
        cycle_dropdown = mo.ui.dropdown(
            options=["curriculum_junior_cycle", "curriculum_senior_cycle"],
            value="curriculum_junior_cycle",
            label="Education Cycle"
        )

        partition_input = mo.ui.text(
            value="en|english",
            label="Partition Key (language|subject)"
        )

        run_extraction_btn = mo.ui.run_button(label="1. Run Curriculum Extraction (DLT -> DuckLake)")
        run_pdf_btn = mo.ui.run_button(label="2. Run PDF Processing (DuckLake -> Garage S3 & OCR)")
        run_all_btn = mo.ui.run_button(label="⚠️ Run ENTIRE Cycle (Test limit: 2 subjects)")

        ui_controls = mo.vstack([
            mo.md("## 2. Trigger Pipelines"),
            mo.md("Use these controls to execute the Dagster pipelines directly from this notebook. It uses local scraping caches where available."),
            mo.hstack([cycle_dropdown, partition_input]),
            mo.hstack([run_extraction_btn, run_pdf_btn, run_all_btn])
        ])
    return (
        cycle_dropdown,
        partition_input,
        run_all_btn,
        run_extraction_btn,
        run_pdf_btn,
        ui_controls,
    )


@app.cell
def _(ui_controls):
    ui_controls
    return


@app.cell
def _(
    cycle_dropdown,
    defs,
    mo,
    partition_input,
    run_all_btn,
    run_extraction_btn,
    run_pdf_btn,
):
    mo.stop(not (run_extraction_btn and (run_extraction_btn.value or run_pdf_btn.value or run_all_btn.value)), mo.md("*Awaiting pipeline trigger...*"))

    logs = []
    try:
        if run_extraction_btn.value:
            job_name = cycle_dropdown.value
            partition = partition_input.value
            logs.append(mo.md(f"⏳ Executing **{job_name}** for partition `{partition}`..."))
            job = defs.get_job_def(job_name)
            result = job.execute_in_process(partition_key=partition)
            if result.success:
                logs.append(mo.md(f"✅ Successfully extracted `{partition}` to DuckLake!"))
            else:
                logs.append(mo.md(f"❌ Pipeline failed. Check terminal for logs."))

        if run_pdf_btn.value:
            logs.append(mo.md(f"⏳ Executing **pdf_processing** (Downloads + Docling OCR)..."))
            job = defs.get_job_def("pdf_processing")
            result = job.execute_in_process()
            if result.success:
                logs.append(mo.md(f"✅ Successfully downloaded and processed PDFs to Garage S3!"))
            else:
                logs.append(mo.md(f"❌ PDF processing failed."))

        if run_all_btn.value:
            job_name = cycle_dropdown.value
            job = defs.get_job_def(job_name)
            partitions = job.partitions_def.get_partition_keys()
            logs.append(mo.md(f"⏳ Executing **{job_name}** for ALL {len(partitions)} partitions..."))
            success_count = 0
            for p in partitions[:2]: # LIMIT FOR SAFETY IN NOTEBOOK
                logs.append(mo.md(f"Running `{p}`..."))
                res = job.execute_in_process(partition_key=p)
                if res.success: success_count += 1
            logs.append(mo.md(f"✅ Finished test run of {success_count} partitions. *(Notebook execution limited to 2 partitions to prevent freezing. Use Dagster UI for full backfills).*"))

    except Exception as e:
        logs.append(mo.md(f"❌ Exception: `{e}`"))

    log_output = mo.vstack(logs)
    return (log_output,)


@app.cell
def _(log_output):
    log_output
    return


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

    ducklake_ui = mo.vstack([
        mo.md(f"### 3. DuckLake/DLT Verification\n{ducklake_status}"),
        mo.ui.table(df_pages, selection=None)
    ])
    return (ducklake_ui,)


@app.cell
def _(ducklake_ui):
    ducklake_ui
    return


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

    garage_ui = mo.md(f"## 4. Garage S3 Verification\n{garage_status}")
    return (garage_ui,)


@app.cell
def _(garage_ui):
    garage_ui
    return


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

    lancedb_ui = mo.vstack([
        mo.md(f"## 5. LanceDB Vector Verification\n{lance_status}"),
        search_ui
    ])
    return (lancedb_ui,)


@app.cell
def _(lancedb_ui):
    lancedb_ui
    return


if __name__ == "__main__":
    app.run()
