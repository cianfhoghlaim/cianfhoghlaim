import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")

@app.cell
def _():
    import os
    import sys
    import json
    import time
    import pathlib

    # ──────────────────────────────────────────────────────────────────────
    # Path setup: make oideachais.data_platform importable
    # ──────────────────────────────────────────────────────────────────────
    _platform = os.path.abspath(os.path.join(os.getcwd(), "oideachais/data_platform"))
    if _platform not in sys.path:
        sys.path.insert(0, _platform)

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

    mo.md("""
    # 🚀 Oideachais Mission Control

    Interactive command center for managing, visualizing, and testing the
    curriculum data platform.

    ## Architecture

    | Layer | Technology | Local | Production |
    |-------|-----------|-------|------------|
    | **Orchestration** | Dagster | `dagster dev` | Dagster Cloud |
    | **Ingestion** | DLT | DuckDB fallback | DuckLake (S3 + PostgreSQL) |
    | **Storage** | DuckLake | Garage S3 + local PostgreSQL | Cloudflare R2 + PlanetScale |
    | **Vectors** | LanceDB | `s3://lance/oideachais/` | R2 + Lance Cloud |
    | **Browser** | Stagehand | Local Browser Grid | Browserbase Cloud |

    DLT pipelines write via `safe_dlt_run()` which serialises all DuckDB
    writes through a `SerialDatabaseExecutor` to prevent concurrency
    segfaults. Destination switching is controlled by two env vars:

    - **`USE_DUCKLAKE`** (`true`/`false`): Toggle DuckLake vs plain DuckDB
    - **`DLT_ENVIRONMENT`** (`local`/`production`): Toggle Garage S3 vs R2
    """)

    return (
        SentenceTransformer, alt, boto3, defs, dlt, duckdb, json, lancedb,
        mo, os, pd, pathlib, sys, time,
    )

@app.cell
def _(mo, os):
    # ──────────────────────────────────────────────────────────────────────
    # Infrastructure configuration
    # ──────────────────────────────────────────────────────────────────────
    # These credentials come from `mise` hooks or .infisical.env injection.
    # NEVER create manual .env files — add to .infisical.env template instead.
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("GARAGE_ACCESS_KEY_ID", "GK8126ec04258979d6abd12d8e")
    AWS_SECRET_KEY = os.getenv("GARAGE_SECRET_ACCESS_KEY", "0c3ec792597afad234d35f2dcf788e4e88cde3378e12525c2f8d1708b89af70e")
    LITELLM_ENDPOINT = os.getenv("LITELLM_ENDPOINT", "http://localhost:4000/v1")
    DLT_PIPELINES_DIR = os.path.abspath(os.path.join(os.getcwd(), "oideachais/data_platform/.dlt"))
    DUCKDB_PATH = os.path.abspath(os.path.join(os.getcwd(), "oideachais/data_platform/curriculum_unified.duckdb"))

    mo.md("### ⚙️ Configuration Loaded").center()
    return AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, DLT_PIPELINES_DIR, DUCKDB_PATH, LITELLM_ENDPOINT


@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, mo, os, duckdb, lancedb):
    def check_health():
        status = {}

        try:
            s3 = boto3.client('s3', endpoint_url=AWS_ENDPOINT, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY, region_name='garage')
            buckets = s3.list_buckets()
            bucket_names = [b['Name'] for b in buckets.get('Buckets', [])]
            status['Garage S3'] = f"✅ Online ({len(bucket_names)} buckets)"
        except Exception as e:
            status['Garage S3'] = f"❌ Offline ({e})"

        try:
            import psycopg
            conn = psycopg.connect(os.environ.get("DUCKLAKE_CATALOG_URI", "postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais"))
            conn.execute("SELECT 1")
            conn.close()
            status['PostgreSQL Catalog'] = "✅ Online"
        except ImportError:
            try:
                import psycopg2
                conn = psycopg2.connect(os.environ.get("DUCKLAKE_CATALOG_URI", "postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais"))
                conn.cursor().execute("SELECT 1")
                conn.close()
                status['PostgreSQL Catalog'] = "✅ Online"
            except Exception as e:
                status['PostgreSQL Catalog'] = f"❌ Offline ({e})"
        except Exception as e:
            status['PostgreSQL Catalog'] = f"❌ Offline ({e})"

        try:
            con = duckdb.connect()
            con.execute("SELECT 1 AS test")
            status['DuckDB (local)'] = "✅ Online"
            con.close()
        except Exception as e:
            status['DuckDB (local)'] = f"❌ Error ({e})"

        try:
            db = lancedb.connect(f"s3://lance/oideachais/", storage_options={"endpoint_url": AWS_ENDPOINT, "aws_access_key_id": AWS_ACCESS_KEY, "aws_secret_access_key": AWS_SECRET_KEY, "region": "garage"})
            tables = db.list_tables()
            status['LanceDB S3'] = f"✅ Online ({len(tables)} tables)"
        except Exception as e:
            status['LanceDB S3'] = f"❌ Offline ({e})"

        try:
            import requests
            r = requests.get("http://localhost:3900", timeout=2)
            status['Browser Grid'] = "✅ Online"
        except Exception:
            try:
                import subprocess
                result = subprocess.run(["docker", "inspect", "--format={{.State.Status}}", "browser-grid"], capture_output=True, text=True, timeout=5)
                if "running" in result.stdout:
                    status['Browser Grid'] = "✅ Running (Docker)"
                else:
                    status['Browser Grid'] = "❌ Stopped"
            except Exception:
                status['Browser Grid'] = "⚠️ Unknown"

        try:
            r = requests.get("http://localhost:8080/api/v1/health", timeout=3)
            if r.status_code < 400:
                status['Stagehand Proxy'] = "✅ Online"
            else:
                status['Stagehand Proxy'] = f"⚠️ Status {r.status_code}"
        except Exception:
            status['Stagehand Proxy'] = "⚠️ Not detected"

        return status

    import requests  # noqa: E402 — needed for Stagehand proxy health check
    health = check_health()

    health_ui = mo.vstack([
        mo.md("### 🚦 Infrastructure Health"),
        mo.md("\n".join([f"- **{k}:** {v}" for k, v in health.items()])),
        mo.md("> All services must be ✅ before running pipelines. "
              "Use `mise` hooks or `docker compose up -d` in `infrastructure/` "
              "to start missing services."),
    ])
    return check_health, health, health_ui


@app.cell
def _(defs, mo):
    # ──────────────────────────────────────────────────────────────────────
    # Dagster Orchestrator
    # ──────────────────────────────────────────────────────────────────────
    # Available jobs:
    #   curriculum_early_childhood, curriculum_primary,
    #   curriculum_junior_cycle, curriculum_senior_cycle,
    #   curriculum_short_courses, pdf_processing,
    #   sec_examinations_leaving_certificate,
    #   sec_examinations_junior_cycle,
    #   sec_examinations_leaving_certificate_applied
    #
    # Jobs use MultiPartitionsDefinition(subject, language|material_type).
    # Run specific partitions via:
    #   dg launch --assets ireland/curriculum/senior_cycle \
    #     --partition "mathematics|en"
    #   dg launch --assets ireland/exam_materials/leaving_certificate \
    #     --partition "exam_papers|mathematics"
    #
    if not defs:
        available_jobs = ["N/A"]
    else:
        available_jobs = sorted([j.name for j in defs.jobs])

    job_dropdown = mo.ui.dropdown(
        options=available_jobs,
        value=available_jobs[0] if available_jobs != ["N/A"] else "N/A",
        label="1. Select Dagster Job:",
    )
    return available_jobs, job_dropdown


@app.cell
def _(defs, job_dropdown, mo):
    if defs and job_dropdown.value != "N/A":
        active_job = defs.get_job_def(job_dropdown.value)
        if hasattr(active_job, 'partitions_def') and active_job.partitions_def:
            p_keys = sorted([str(k) for k in active_job.partitions_def.get_partition_keys()])
        else:
            p_keys = []
    else:
        active_job = None
        p_keys = []

    partition_dropdown = mo.ui.dropdown(
        options=p_keys if p_keys else ["N/A"],
        value=p_keys[0] if p_keys else "N/A",
        label="2. Select Partition (if applicable):",
    )

    # Year range for exam materials: configurable for ExamMaterialsConfig
    year_start = mo.ui.number(value=2020, label="Year start:", min_value=1999, max_value=2025)
    year_end = mo.ui.number(value=2024, label="Year end:", min_value=1999, max_value=2025)

    run_btn = mo.ui.run_button(label="🚀 Execute Job In-Process")
    generate_cmd_btn = mo.ui.button(label="💻 Generate CLI Command (For heavy jobs)")
    return active_job, generate_cmd_btn, p_keys, partition_dropdown, run_btn, year_end, year_start


@app.cell
def _(
    active_job,
    defs,
    generate_cmd_btn,
    job_dropdown,
    mo,
    os,
    partition_dropdown,
    run_btn,
    year_end,
    year_start,
):
    orchestrator_ui = mo.vstack([
        mo.md("""### ⚙️ Dagster Orchestrator

Execute DLT ingestion or PDF processing pipelines locally.

**Destination control:**
- Set `USE_DUCKLAKE=false` (env) → writes to local DuckDB (fast, single-threaded)
- Set `USE_DUCKLAKE=true` (default) → writes to DuckLake (Garage S3 + PostgreSQL)

**Scrape control:**
- Set `USE_LOCAL_SCRAPES=true` → uses cached data from `stedding/ingest_queue/`
- Unset or `false` → live browser/Firecrawl scraping

**Key DLT patterns:**
- `safe_dlt_run(pipeline, source)` — serialises writes to prevent DuckDB segfaults
- `write_disposition="merge"` + `primary_key=["pdf_url"]` — incremental dedup
- `create_pipeline(name, dataset)` — factory that picks destination from env vars
"""),
        job_dropdown,
        partition_dropdown,
        mo.hstack([year_start, year_end]),
        mo.hstack([run_btn, generate_cmd_btn])
    ])

    logs = []
    has_part = partition_dropdown.value != "N/A"

    if generate_cmd_btn.value:
        years = list(range(int(year_start.value), int(year_end.value) + 1))
        cmd = f"uv run dagster job execute -m oideachais.data_platform.dagster_defs.definitions -j {job_dropdown.value}"
        if has_part:
            cmd += f" --tags '{{\"dagster/partition\": \"{partition_dropdown.value}\"}}'"
        if "examination" in job_dropdown.value:
            cmd += f"\n# Year config: {years}"
            cmd += f"\n# Set env: USE_DUCKLAKE=false for local DuckDB fallback"
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
                    # Show materialization metadata
                    for event in res.all_events:
                        if event.event_type_value == "ASSET_MATERIALIZATION":
                            md = event.event_specific_data.materialization.metadata or {}
                            rows = md.get("rows_loaded")
                            if rows:
                                logs.append(mo.md(f"  📊 Rows loaded: {rows.value if hasattr(rows, 'value') else rows}"))
                else:
                    logs.append(mo.md(f"❌ **Failed!** Job `{job_dropdown.value}` encountered errors."))
            except Exception as e:
                logs.append(mo.md(f"💥 **Exception:** `{e}`"))

    orchestrator_panel = mo.vstack([orchestrator_ui, mo.vstack(logs)])
    return cmd, has_part, logs, orchestrator_panel, orchestrator_ui, res


@app.cell
def _(alt, dlt, mo, os, pd, DLT_PIPELINES_DIR):
    # ──────────────────────────────────────────────────────────────────────
    # DuckLake Analytics — query both curriculum and exam materials
    # ──────────────────────────────────────────────────────────────────────
    # DLT stores data in datasets. With DuckLake, data lives as Parquet in
    # S3 with a PostgreSQL catalog. With DuckDB fallback, it's in a local
    # .duckdb file. The same SQL queries work either way.
    #
    # Dataset names:
    #   curriculum_unified → curriculum.curriculum_pages, curriculum.curriculum_pdfs, ...
    #   exam_materials      → examinations.exam_papers, examinations.marking_schemes, ...
    # ──────────────────────────────────────────────────────────────────────

    use_ducklake = os.environ.get("USE_DUCKLAKE", "true").lower() == "true"
    pipeline_name = "curriculum_unified"

    try:
        pipeline = dlt.attach(pipeline_name)
        with pipeline.sql_client() as client:
            # Curriculum pages
            with client.execute_query("SELECT cycle, subject, language, count(*) as pages FROM curriculum.curriculum_pages GROUP BY cycle, subject, language ORDER BY pages DESC") as cursor:
                cols = [c[0] for c in cursor.description] if cursor.description else []
                df_pages = pd.DataFrame(cursor.fetchall(), columns=cols) if cols else pd.DataFrame()

            # PDF downloads
            with client.execute_query("SELECT status, count(*) as count FROM curriculum.pdf_downloads GROUP BY status ORDER BY count DESC") as cursor:
                cols2 = [c[0] for c in cursor.description] if cursor.description else []
                df_pdfs = pd.DataFrame(cursor.fetchall(), columns=cols2) if cols2 else pd.DataFrame()

        if not df_pages.empty:
            chart = alt.Chart(df_pages).mark_bar().encode(
                x='sum(pages):Q',
                y=alt.Y('subject:N', sort='-x'),
                color='cycle:N',
                tooltip=['cycle', 'subject', 'language', 'pages']
            ).properties(width=600, height=400, title="Curriculum Pages by Subject & Cycle")
            chart_ui = mo.ui.altair_chart(chart)
        else:
            chart_ui = mo.md("*No curriculum page data yet. Run a curriculum job first.*")

        analytics_ui = mo.vstack([
            mo.md("""### 📊 DuckLake Analytics — Curriculum

            Data is written via DLT pipelines to DuckLake (S3+PostgreSQL) or
            DuckDB fallback. Use `dlt.attach('curriculum_unified')` to query
            the same dataset that Dagster assets write to.

            **Pipeline mapping:**
            - `curriculum_unified` → `curriculum.curriculum_pages`, `curriculum.curriculum_pdfs`
            - `exam_materials` → `examinations.exam_papers`, `examinations.marking_schemes`, `examinations.all_exam_materials`
            """),
            mo.hstack([
                mo.vstack([mo.md("**Curriculum Pages**"), mo.ui.table(df_pages, page_size=10)]),
                mo.vstack([mo.md("**PDF Download Status**"), mo.ui.table(df_pdfs)]),
            ]),
            chart_ui
        ])
    except Exception as e:
        analytics_ui = mo.md(f"⚠️ Analytics unavailable (Pipeline might not be initialized): {e}")
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
def _(alt, dlt, mo, os, pd, DLT_PIPELINES_DIR):
    # ──────────────────────────────────────────────────────────────────────
    # Exam Materials Analytics
    # ──────────────────────────────────────────────────────────────────────
    # The exam_materials DLT pipeline writes to the `examinations` dataset.
    # Tables: exam_papers, marking_schemes, all_exam_materials
    #
    # Key design decisions:
    # - MultiPartition(subject, material_type) — no year dimension
    #   (years are a Config parameter, not a partition key)
    # - write_disposition="merge" + primary_key=["pdf_url"] — incremental dedup
    # - USE_LOCAL_SCRAPES=true skips Stagehand browser entirely for testing
    # ──────────────────────────────────────────────────────────────────────

    try:
        exam_pipeline = dlt.attach("exam_materials")
        with exam_pipeline.sql_client() as client:
            # All exam materials
            try:
                with client.execute_query("SELECT level, subject, material_type, status, count(*) as count FROM examinations.all_exam_materials GROUP BY level, subject, material_type, status ORDER BY count DESC") as cursor:
                    cols = [c[0] for c in cursor.description] if cursor.description else []
                    df_exams = pd.DataFrame(cursor.fetchall(), columns=cols) if cols else pd.DataFrame()
            except Exception:
                df_exams = pd.DataFrame()

            # PDF URLs discovered
            try:
                with client.execute_query("SELECT level, subject, count(*) as urls FROM examinations.all_exam_materials WHERE pdf_url IS NOT NULL AND pdf_url != '' GROUP BY level, subject ORDER BY urls DESC") as cursor:
                    cols2 = [c[0] for c in cursor.description] if cursor.description else []
                    df_urls = pd.DataFrame(cursor.fetchall(), columns=cols2) if cols2 else pd.DataFrame()
            except Exception:
                df_urls = pd.DataFrame()

        if not df_exams.empty:
            exam_chart = alt.Chart(df_exams).mark_bar().encode(
                x='sum(count):Q',
                y=alt.Y('subject:N', sort='-x'),
                color='material_type:N',
                tooltip=['level', 'subject', 'material_type', 'status', 'count']
            ).properties(width=600, height=400, title="Exam Materials by Subject & Type")
            exam_chart_ui = mo.ui.altair_chart(exam_chart)
        else:
            exam_chart_ui = mo.md("*No exam materials data yet. Run an exam job first.*")

        exam_analytics = mo.vstack([
            mo.md("""### 📊 Exam Materials Analytics

            Exam material data is written via the `exam_materials` DLT pipeline
            to the `examinations` dataset. Each Dagster asset writes:

            - `exam_papers` → past exam papers (material_type='paper')
            - `marking_schemes` → marking schemes (material_type='marking_scheme')
            - `all_exam_materials` → union of both (used by pdf_downloader)

            **Partition keys** are `material_type|subject`, e.g. `exam_papers|mathematics`.
            Years are controlled by `ExamMaterialsConfig.years` run config.
            """),
            mo.hstack([
                mo.vstack([mo.md("**Materials Summary**"), mo.ui.table(df_exams, page_size=10)]),
                mo.vstack([mo.md("**PDF URLs Discovered**"), mo.ui.table(df_urls, page_size=10)]),
            ]),
            exam_chart_ui,
        ])
    except Exception as e:
        exam_analytics = mo.md(f"⚠️ Exam materials not yet initialized: `{e}`\n\nRun `sec_examinations_leaving_certificate` job to populate data.")
        exam_chart_ui = None
        df_exams = pd.DataFrame()
        df_urls = pd.DataFrame()

    return df_exams, df_urls, exam_analytics, exam_chart_ui, exam_pipeline


@app.cell
def _(mo, os):
    # ──────────────────────────────────────────────────────────────────────
    # Standalone DLT Pipeline Runner
    # ──────────────────────────────────────────────────────────────────────
    # Run DLT pipelines directly (outside Dagster) for quick testing.
    #
    # Destination control:
    #   USE_DUCKLAKE=true  → DuckLake (Garage S3 + PostgreSQL catalog)
    #   USE_DUCKLAKE=false → Local DuckDB (.dlt/exam_materials/examinations.duckdb)
    #
    # Key functions:
    #   create_pipeline(name, dataset) → picks destination from env vars
    #   safe_dlt_run(pipeline, source) → serialised writes via SerialDatabaseExecutor
    #   get_dlt_destination() → returns DuckLake or DuckDB destination object
    # ──────────────────────────────────────────────────────────────────────

    dlt_mode = mo.ui.dropdown(
        options=["exam_materials_lc", "exam_materials_jc", "curriculum_test", "pdf_download"],
        value="exam_materials_lc",
        label="DLT Pipeline:",
    )

    dlt_years = mo.ui.array(
        [mo.ui.checkbox(label=str(y), value=(2024 <= y <= 2024)) for y in range(2020, 2025)],
        label="Years (exam materials only):"
    )

    dlt_ducklake_toggle = mo.ui.switch(
        value=os.environ.get("USE_DUCKLAKE", "true").lower() == "true",
        label="Use DuckLake (true) or local DuckDB (false)",
    )

    dlt_run_btn = mo.ui.run_button(label="▶ Run DLT Pipeline Directly")

    dlt_runner_ui = mo.vstack([
        mo.md("""### 🔧 Standalone DLT Pipeline Runner

        Run DLT pipelines directly (outside Dagster orchestrator) for testing.
        Useful for debugging ingestion before wiring into Dagster assets.

        **Pipeline → Destination mapping:**

        | Pipeline | Dataset | Tables |
        |----------|---------|--------|
        | `exam_materials_lc` | `examinations` | `exam_papers`, `marking_schemes`, `all_exam_materials` |
        | `exam_materials_jc` | `examinations` | same tables, different data |
        | `curriculum_test` | `curriculum` | `curriculum_pages`, `curriculum_pdfs` |
        | `pdf_download` | `curriculum` | `pdf_downloads`, `pdf_download_errors` |

        **When `USE_DUCKLAKE=false`** (recommended for testing):
        - Data writes to `.dlt/{pipeline_name}/{dataset_name}.duckdb`
        - No Garage S3 or PostgreSQL required
        - Single-threaded writes via `SerialDatabaseExecutor`
        """),
        dlt_mode,
        mo.hstack(dlt_years),
        dlt_ducklake_toggle,
        dlt_run_btn,
    ])

    dlt_logs = []

    if dlt_run_btn.value:
        from oideachais.data_platform.dlt_utils import create_pipeline, safe_dlt_run, get_dlt_destination, get_duckdb_fallback_destination
        from pathlib import Path

        os.environ["USE_DUCKLAKE"] = str(dlt_ducklake_toggle.value).lower()

        selected_years = [int(y) for i, y in enumerate(range(2020, 2025)) if dlt_years[i].value]

        try:
            with mo.status.spinner(f"Running {dlt_mode.value}..."):
                if dlt_mode.value.startswith("exam_materials"):
                    from oideachais.data_platform.dlt_sources.ireland.examinations import (
                        leaving_certificate_source, junior_cycle_exams_source,
                    )
                    level = "leaving_certificate" if "lc" in dlt_mode.value else "junior_cycle"
                    src_fn = leaving_certificate_source if level == "leaving_certificate" else junior_cycle_exams_source

                    pipeline = create_pipeline("exam_materials", "examinations")
                    source = src_fn(
                        subjects=["mathematics"],
                        years=selected_years if selected_years else [2024],
                        material_types=["exam_papers", "marking_schemes"],
                    )
                    load_info = safe_dlt_run(pipeline, source)
                    dlt_logs.append(mo.md(f"✅ **{dlt_mode.value}** completed.\n\n**Load ID:** `{load_info.loads_ids[0] if load_info.loads_ids else 'unknown'}`"))

                    # Show row counts
                    for pkg in load_info.load_packages:
                        for job in (pkg.jobs.values() if isinstance(pkg.jobs, dict) else pkg.jobs):
                            if hasattr(job, 'metrics') and job.metrics:
                                rows = getattr(job.metrics, 'rows_count', 0) or 0
                                dlt_logs.append(mo.md(f"  📊 {job.job_id}: {rows} rows"))

                elif dlt_mode.value == "curriculum_test":
                    from oideachais.data_platform.dlt_sources.ireland.curriculum_source import curriculum_source

                    pipeline = create_pipeline("curriculum_unified", "curriculum")
                    source = curriculum_source(cycle="senior_cycle", subject="mathematics", language="en")
                    load_info = safe_dlt_run(pipeline, source)
                    dlt_logs.append(mo.md(f"✅ **curriculum_test** completed.\n\n**Load ID:** `{load_info.loads_ids[0] if load_info.loads_ids else 'unknown'}`"))

                elif dlt_mode.value == "pdf_download":
                    from oideachais.data_platform.dlt_sources.ireland.pdf_downloader import pdf_download_source

                    duckdb_path = str(Path(os.getcwd()) / "oideachais/data_platform/curriculum_unified.duckdb")
                    pipeline = create_pipeline("curriculum_unified", "curriculum")
                    source = pdf_download_source(duckdb_path=duckdb_path, max_files=10)
                    load_info = safe_dlt_run(pipeline, source)
                    dlt_logs.append(mo.md(f"✅ **pdf_download** completed.\n\n**Load ID:** `{load_info.loads_ids[0] if load_info.loads_ids else 'unknown'}`"))

        except Exception as e:
            dlt_logs.append(mo.md(f"💥 **Exception:** `{e}`"))

    dlt_runner_panel = mo.vstack([dlt_runner_ui, mo.vstack(dlt_logs)])
    return dlt_logs, dlt_mode, dlt_runner_panel, dlt_runner_ui, dlt_run_btn, dlt_years, dlt_ducklake_toggle


@app.cell
def _(mo, os, pathlib):
    # ──────────────────────────────────────────────────────────────────────
    # Destination Verifier
    # ──────────────────────────────────────────────────────────────────────
    # Verify that data has landed in the expected destination:
    #   1. DuckDB fallback (.dlt/*/examinations.duckdb)
    #   2. Garage S3 buckets (s3://ducklake/oideachais/)
    #   3. Filesystem export (downloads/structured_export/)
    #   4. Downloaded PDFs (downloads/examinations/, downloads/curriculum_pdfs/)
    # ──────────────────────────────────────────────────────────────────────

    verify_btn = mo.ui.run_button(label="🔍 Verify Destinations")

    verify_results = []

    if verify_btn.value:
        import duckdb as _duckdb
        import boto3 as _boto3

        # 1. Check DuckDB fallback files
        dlt_dir = pathlib.Path(os.getcwd()) / "oideachais/data_platform" / ".dlt"
        for db_pattern in ["**/*.duckdb"]:
            for db_file in dlt_dir.glob(db_pattern):
                size_mb = db_file.stat().st_size / (1024 * 1024)
                try:
                    con = _duckdb.connect(str(db_file), read_only=True)
                    schemas = [s[0] for s in con.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog')").fetchall()]
                    tables = []
                    for s in schemas:
                        try:
                            t = [x[0] for x in con.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{s}'").fetchall()]
                            tables.extend([f"{s}.{x}" for x in t])
                        except Exception:
                            pass
                    con.close()
                    verify_results.append(mo.md(f"✅ **{db_file.name}** ({size_mb:.1f} MB) — Tables: {tables}"))
                except Exception as e:
                    verify_results.append(mo.md(f"⚠️ **{db_file.name}** ({size_mb:.1f} MB) — Error: {e}"))

        # 2. Check Garage S3
        try:
            s3 = _boto3.client('s3',
                endpoint_url=os.environ.get("AWS_ENDPOINT_URL", "http://localhost:3900"),
                aws_access_key_id=os.environ.get("GARAGE_ACCESS_KEY_ID", "GK8126ec04258979d6abd12d8e"),
                aws_secret_access_key=os.environ.get("GARAGE_SECRET_ACCESS_KEY", "0c3ec792597afad234d35f2dcf788e4e88cde3378e12525c2f8d1708b89af70e"),
                region_name='garage')

            buckets = s3.list_buckets()
            for b in buckets.get('Buckets', []):
                name = b['Name']
                try:
                    objs = s3.list_objects_v2(Bucket=name, MaxKeys=5)
                    count = objs.get('KeyCount', 0)
                    verify_results.append(mo.md(f"✅ **s3://{name}/** — {count}+ objects"))
                except Exception as e:
                    verify_results.append(mo.md(f"⚠️ **s3://{name}/** — Error listing: {e}"))
        except Exception as e:
            verify_results.append(mo.md(f"❌ Garage S3 unavailable: {e}"))

        # 3. Check downloaded PDFs
        for pdf_dir in ["downloads/curriculum_pdfs", "downloads/examinations", "downloads/structured_export"]:
            p = pathlib.Path(os.getcwd()) / pdf_dir
            if p.exists():
                pdfs = list(p.rglob("*.pdf"))
                total_size = sum(f.stat().st_size for f in pdfs) / (1024 * 1024)
                verify_results.append(mo.md(f"✅ **{pdf_dir}/** — {len(pdfs)} PDFs ({total_size:.1f} MB)"))
            else:
                verify_results.append(mo.md(f"📁 **{pdf_dir}/** — not yet created"))

    verify_ui = mo.vstack([
        mo.md("""### 🔍 Destination Verifier

        Checks that DLT pipeline data has landed in expected destinations:

        | Destination | Storage | Control |
        |-------------|---------|---------|
        | DuckDB fallback | Local `.dlt/` directory | `USE_DUCKLAKE=false` |
        | DuckLake | Garage S3 + PostgreSQL | `USE_DUCKLAKE=true` |
        | Filesystem export | `downloads/structured_export/` | `EXPORT_TO_FILESYSTEM=true` |
        | PDF downloads | `downloads/curriculum_pdfs/`, `downloads/examinations/` | pdf_downloader |
        """),
        verify_btn,
        mo.vstack(verify_results),
    ])
    return verify_btn, verify_results, verify_ui


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
                        import numpy as np
                        vec = np.random.rand(384).astype(np.float32)

                    s_res = table.search(vec).limit(5).to_pandas()
                    if not s_res.empty:
                        display_df = s_res[["text", "_distance"]] if "text" in s_res.columns else s_res
                        search_results.append(mo.ui.table(display_df, page_size=5))
                    else:
                        search_results.append(mo.md("*No results found.*"))
                else:
                    search_results.append(mo.md(f"⚠️ Table `curriculum_embeddings` not found. Available: {tables}"))
            except Exception as e:
                search_results.append(mo.md(f"❌ Search Error: `{e}`"))

    search_panel = mo.vstack([search_controls, mo.vstack(search_results)])
    return db, display_df, model, s_res, search_panel, search_results, table, tables, vec


@app.cell
def _(analytics_ui, dlt_runner_panel, exam_analytics, health_ui, mo, orchestrator_panel, search_panel, verify_ui):
    tabs = mo.ui.tabs({
        "🚦 Health": health_ui,
        "⚙️ Orchestrator": orchestrator_panel,
        "🔧 DLT Runner": dlt_runner_panel,
        "📊 Curriculum": analytics_ui,
        "📝 Exams": exam_analytics,
        "🔍 Destinations": verify_ui,
        "🧠 Search": search_panel,
    })

    tabs
    return tabs,


if __name__ == "__main__":
    app.run()