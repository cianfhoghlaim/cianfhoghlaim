import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")

@app.cell
def _():
    import os
    import sys
    import json
    import time
    
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
    import altair as alt
    import dlt
    from sentence_transformers import SentenceTransformer

    mo.md("""
    # 🚀 Oideachais Mission Control

    Interactive command center for managing, visualizing, and testing the entire curriculum data platform.
    """)
    return (
        SentenceTransformer,
        alt,
        boto3,
        defs,
        dlt,
        duckdb,
        json,
        lancedb,
        mo,
        os,
        pd,
        sys,
        time,
    )

@app.cell
def _(mo, os):
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("GARAGE_ACCESS_KEY_ID", "GK8126ec04258979d6abd12d8e")
    AWS_SECRET_KEY = os.getenv("GARAGE_SECRET_ACCESS_KEY", "0c3ec792597afad234d35f2dcf788e4e88cde3378e12525c2f8d1708b89af70e")
    LITELLM_ENDPOINT = os.getenv("LITELLM_ENDPOINT", "http://localhost:4000/v1")
    return AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, LITELLM_ENDPOINT

@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, boto3, duckdb, lancedb, mo):
    def check_health():
        status = {}
        
        try:
            s3 = boto3.client('s3', endpoint_url=AWS_ENDPOINT, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name='garage')
            s3.list_buckets()
            status['Garage S3'] = "✅ Online"
        except Exception:
            status['Garage S3'] = "❌ Offline"
            
        try:
            con = duckdb.connect()
            con.execute("ATTACH 'oideachais/data_platform/curriculum_unified.duckdb' AS ducklake;")
            status['DuckLake Catalog'] = "✅ Online (Local)"
        except Exception:
            status['DuckLake Catalog'] = "❌ Offline"
            
        try:
            db = lancedb.connect("s3://lance/oideachais/", storage_options={"endpoint_url": AWS_ENDPOINT, "aws_access_key_id": AWS_ACCESS_KEY, "aws_secret_access_key": AWS_SECRET_KEY, "region": "garage"})
            db.list_tables()
            status['LanceDB S3'] = "✅ Online"
        except Exception:
            status['LanceDB S3'] = "❌ Offline"

        return status

    health = check_health()
    
    health_ui = mo.vstack([
        mo.md("### 🚦 Infrastructure Health"),
        mo.md("\n".join([f"- **{k}:** {v}" for k, v in health.items()]))
    ])
    return check_health, health, health_ui

@app.cell
def _(defs, mo):
    if not defs:
        available_jobs = ["N/A"]
    else:
        available_jobs = [j.name for j in defs.jobs if j.name.startswith("curriculum_") or j.name == "pdf_processing"]
        
    job_dropdown = mo.ui.dropdown(
        options=available_jobs,
        value="curriculum_junior_cycle" if "curriculum_junior_cycle" in available_jobs else available_jobs[0],
        label="1. Select Dagster Job:"
    )
    return available_jobs, job_dropdown

@app.cell
def _(defs, job_dropdown, mo):
    if defs and job_dropdown.value != "N/A":
        active_job = defs.get_job_def(job_dropdown.value)
        if hasattr(active_job, 'partitions_def') and active_job.partitions_def:
            p_keys = [str(k) for k in active_job.partitions_def.get_partition_keys()]
        else:
            p_keys = []
    else:
        active_job = None
        p_keys = []
        
    partition_dropdown = mo.ui.dropdown(
        options=p_keys if p_keys else ["N/A"],
        value=p_keys[0] if p_keys else "N/A",
        label="2. Select Partition (if applicable):"
    )

    run_btn = mo.ui.run_button(label="🚀 Execute Job In-Process")
    generate_cmd_btn = mo.ui.button(label="💻 Generate CLI Command (For heavy jobs)")
    return active_job, generate_cmd_btn, p_keys, partition_dropdown, run_btn

@app.cell
def _(
    active_job,
    generate_cmd_btn,
    job_dropdown,
    mo,
    partition_dropdown,
    run_btn,
):
    orchestrator_ui = mo.vstack([
        mo.md("### ⚙️ Dagster Orchestrator"),
        mo.md("Execute DLT ingestion or PDF processing pipelines locally. Uses cached scraped data if `USE_LOCAL_SCRAPES=true`."),
        job_dropdown,
        partition_dropdown,
        mo.hstack([run_btn, generate_cmd_btn])
    ])
    
    logs = []
    has_part = partition_dropdown.value != "N/A"
    
    if generate_cmd_btn.value:
        cmd = f"uv run dagster job execute -m oideachais.data_platform.dagster_defs.definitions -j {job_dropdown.value}"
        if has_part:
            cmd += f" --tags '{{\"dagster/partition\": \"{partition_dropdown.value}\"}}'"
        logs.append(mo.md(f"**Run this in your terminal:**\n```bash\n{cmd}\n```"))
    
    if run_btn.value and active_job:
        with mo.status.spinner(f"Executing {job_dropdown.value}..."):
            try:
                if has_part:
                    res = active_job.execute_in_process(partition_key=partition_dropdown.value)
                else:
                    res = active_job.execute_in_process()
                    
                if res.success:
                    logs.append(mo.md(f"✅ **Success!** Job `{job_dropdown.value}` completed."))
                else:
                    logs.append(mo.md(f"❌ **Failed!** Job `{job_dropdown.value}` encountered errors."))
            except Exception as e:
                logs.append(mo.md(f"💥 **Exception:** `{e}`"))
                
    orchestrator_panel = mo.vstack([orchestrator_ui, mo.vstack(logs)])
    return cmd, has_part, logs, orchestrator_panel, orchestrator_ui, res

@app.cell
def _(alt, dlt, mo, pd):
    try:
        pipeline = dlt.attach("curriculum_unified")
        with pipeline.sql_client() as client:
            with client.execute_query("SELECT cycle, subject, language, count(*) as pages FROM curriculum.curriculum_pages GROUP BY cycle, subject, language") as cursor:
                cols = [c[0] for c in cursor.description] if cursor.description else []
                df_pages = pd.DataFrame(cursor.fetchall(), columns=cols)
                
            with client.execute_query("SELECT status, count(*) as count FROM curriculum.pdf_downloads GROUP BY status") as cursor:
                cols2 = [c[0] for c in cursor.description] if cursor.description else []
                df_pdfs = pd.DataFrame(cursor.fetchall(), columns=cols2)
                
        if not df_pages.empty:
            chart = alt.Chart(df_pages).mark_bar().encode(
                x='sum(pages):Q',
                y=alt.Y('subject:N', sort='-x'),
                color='cycle:N',
                tooltip=['cycle', 'subject', 'language', 'pages']
            ).properties(width=600, height=400, title="Curriculum Pages by Subject & Cycle")
            chart_ui = mo.ui.altair_chart(chart)
        else:
            chart_ui = mo.md("*No curriculum page data found.*")
            
        analytics_ui = mo.vstack([
            mo.md("### 📊 DuckLake Analytics"),
            mo.hstack([
                mo.vstack([mo.md("**Data Browser**"), mo.ui.table(df_pages, page_size=10)]),
                mo.vstack([mo.md("**PDF Download Status**"), mo.ui.table(df_pdfs)])
            ]),
            chart_ui
        ])
    except Exception as e:
        analytics_ui = mo.md(f"⚠️ Analytics unavailable (Pipeline might not be initialized): {e}")
        chart = None
        chart_ui = None
        client = None
        cols = None
        cols2 = None
        cursor = None
        df_pages = pd.DataFrame()
        df_pdfs = pd.DataFrame()
        pipeline = None
        
    return analytics_ui, chart, chart_ui, client, cols, cols2, cursor, df_pages, df_pdfs, pipeline

@app.cell
def _(mo):
    search_input = mo.ui.text(label="Search Query:", value="leaving cert biology markings")
    model_selector = mo.ui.dropdown(
        options=["Local: all-MiniLM-L6-v2", "LiteLLM: Gemma-4", "LiteLLM: Qwen-VL"],
        value="Local: all-MiniLM-L6-v2",
        label="Embedding Model:"
    )
    search_btn = mo.ui.run_button(label="🔍 Semantic Search")
    
    search_controls = mo.vstack([
        mo.md("### 🧠 LanceDB Multimodal Search"),
        mo.hstack([model_selector, search_input]),
        search_btn
    ])
    return model_selector, search_btn, search_controls, search_input

@app.cell
def _(
    AWS_ACCESS_KEY,
    AWS_ENDPOINT,
    AWS_SECRET_KEY,
    SentenceTransformer,
    lancedb,
    mo,
    model_selector,
    search_btn,
    search_controls,
    search_input,
):
    search_results = []
    
    if search_btn.value:
        with mo.status.spinner("Vectorizing query and searching LanceDB..."):
            try:
                db = lancedb.connect("s3://lance/oideachais/", storage_options={"endpoint_url": AWS_ENDPOINT, "aws_access_key_id": AWS_ACCESS_KEY, "aws_secret_access_key": AWS_SECRET_KEY, "region": "garage"})
                tables = db.list_tables()
                if "curriculum_embeddings" in tables:
                    table = db.open_table("curriculum_embeddings")
                    
                    if "Local" in model_selector.value:
                        model = SentenceTransformer("all-MiniLM-L6-v2")
                        vec = model.encode(search_input.value)
                    else:
                        search_results.append(mo.md(f"⚠️ **{model_selector.value}** via LiteLLM is selected. Using mock random vector for now until LiteLLM is booted."))
                        import numpy as np
                        vec = np.random.rand(384).astype(np.float32)
                        
                    s_res = table.search(vec).limit(5).to_pandas()
                    if not s_res.empty:
                        display_df = s_res[["text", "_distance"]] if "text" in s_res.columns else s_res
                        search_results.append(mo.ui.table(display_df, page_size=5))
                    else:
                        search_results.append(mo.md("*No results found.*"))
                else:
                    search_results.append(mo.md(f"⚠️ Table `curriculum_embeddings` not found. Available tables: {tables}"))
            except Exception as e:
                search_results.append(mo.md(f"❌ Search Error: `{e}`"))
                
    search_panel = mo.vstack([search_controls, mo.vstack(search_results)])
    return db, display_df, model, s_res, search_panel, search_results, table, tables, vec

@app.cell
def _(analytics_ui, health_ui, mo, orchestrator_panel, search_panel):
    tabs = mo.ui.tabs({
        "🚦 Health": health_ui,
        "⚙️ Orchestrator": orchestrator_panel,
        "📊 Analytics": analytics_ui,
        "🧠 Search": search_panel
    })
    
    tabs
    return tabs,

if __name__ == "__main__":
    app.run()
