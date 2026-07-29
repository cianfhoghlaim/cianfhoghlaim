# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "lancedb>=0.20",
#     "boto3>=1.34",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "dlt>=1.0",
#     "sentence-transformers>=3.0",
#     "requests>=2.31",
# ]
# ///
"""Oideachais Mission Control — BIEP v4.

Interactive command center for managing, visualising, and testing the
British-Isles Education pipeline (MotherDuck + DuckLake lakehouse,
Garage S3, LanceDB BGE-M3 vector index).

All credentials are hydrated by the mise directory hook from the
Infisical `dev-baile` vault. No hard-coded secrets in this notebook.
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="wide")


@app.cell
def _():
    import os
    import marimo as mo
    import duckdb
    import lancedb
    import boto3
    import pandas as pd
    import altair as alt
    import dlt_sources

    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    LITELLM_ENDPOINT = os.getenv("LITELLM_ENDPOINT", "http://localhost:4000/v1")

    mo.md(
        f"""
        # 🚀 BIEP Mission Control

        Interactive command center for the British-Isles Education
        pipeline — 6 LC subjects + gov.ie circulars, end to end.

        ## Architecture

        | Layer | Technology | Local | Production |
        |-------|-----------|-------|------------|
        | **Orchestration** | Dagster | `dagster dev` | Dagster Cloud |
        | **Ingestion** | DLT | DuckDB fallback | DuckLake (Garage S3 + PostgreSQL) |
        | **Storage** | DuckLake | Garage S3 + local PostgreSQL | Cloudflare R2 + PlanetScale |
        | **Vectors** | LanceDB | `s3://lance/oideachais/` | R2 + Lance Cloud |
        | **Embedder** | BGE-M3 | local SentenceTransformer | LiteLLM-routed |

        ## DLT pipeline contract

        DLT pipelines write via ``safe_dlt_run()`` which serialises all
        DuckDB writes through a ``SerialDatabaseExecutor`` to prevent
        concurrency segfaults. Destination switching is controlled by
        two env vars:

        - ``USE_DUCKLAKE`` (``true``/``false``): toggle DuckLake vs plain DuckDB
        - ``MOTHERDUCK_MODE`` (``managed``/``byob``/``byoc``): DuckLake hosting
        """
    )
    return (
        AWS_ACCESS_KEY,
        AWS_ENDPOINT,
        AWS_SECRET_KEY,
        LITELLM_ENDPOINT,
        alt,
        boto3,
        dlt,
        duckdb,
        lancedb,
        mo,
        os,
        pd,
    )


@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, mo, os, duckdb, lancedb):
    def check_health() -> dict:
        status = {}

        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=AWS_ENDPOINT,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY,
                region_name="garage",
            )
            buckets = s3.list_buckets()
            bucket_names = [b["Name"] for b in buckets.get("Buckets", [])]
            status["Garage S3"] = f"✅ Online ({len(bucket_names)} buckets)"
        except Exception as e:
            status["Garage S3"] = f"❌ Offline ({e})"

        try:
            db = lancedb.connect(
                "s3://lance/oideachais/",
                storage_options={
                    "endpoint_url": AWS_ENDPOINT,
                    "aws_access_key_id": AWS_ACCESS_KEY,
                    "aws_secret_access_key": AWS_SECRET_KEY,
                    "region": "garage",
                },
            )
            tables = db.list_tables()
            status["LanceDB S3"] = f"✅ Online ({len(tables)} tables)"
        except Exception as e:
            status["LanceDB S3"] = f"❌ Offline ({e})"

        try:
            import requests

            r = requests.get("http://localhost:9223/json/version", timeout=2)
            status["Browser Grid (9223)"] = (
                "✅ Online" if r.status_code < 400 else f"⚠️ HTTP {r.status_code}"
            )
        except Exception:
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        "--format={{.State.Status}}",
                        "browser-grid",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if "running" in result.stdout:
                    status["Browser Grid"] = "✅ Running (Docker)"
                else:
                    status["Browser Grid"] = "❌ Stopped"
            except Exception:
                status["Browser Grid"] = "⚠️ Unknown"

        try:
            token = os.environ.get("MOTHERDUCK_TOKEN", "")
            if token:
                duckdb.sql(f"SET motherduck_token='{token}'")
                con = ibis.duckdb.connect("md:cianfhoghlaim")
                con.execute("SELECT 1 AS test").fetchone()
                con.close()
                status["md:cianfhoghlaim"] = "✅ Online"
            else:
                status["md:cianfhoghlaim"] = "⚠️ MOTHERDUCK_TOKEN unset"
        except Exception as e:
            status["md:cianfhoghlaim"] = f"❌ Offline ({e})"

        return status

    health = check_health()
    health_ui = mo.vstack([
        mo.md("### 🚦 Infrastructure health"),
        mo.md("\n".join(f"- **{k}:** {v}" for k, v in health.items())),
        mo.md(
            "> All services must be ✅ before running pipelines. "
            "Use `mise` hooks or `docker compose up -d` in `infrastructure/` "
            "to start missing services."
        ),
    ])
    return check_health, health, health_ui


@app.cell
def _(mo, os):
    """Dagster Orchestrator tab — introspect available jobs only."""
    job_options: list[str] = ["N/A"]
    try:
        from cianfhoghlaim.orchestration.definitions import defs

        job_options = sorted([j.name for j in defs.jobs])
    except Exception:
        try:
            import subprocess

            out = subprocess.run(
                ["uv", "run", "dg", "list", "jobs"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            job_options = sorted(
                line.strip() for line in out.stdout.splitlines() if line.strip()
            ) or ["N/A"]
        except Exception:
            pass

    job_dropdown = mo.ui.dropdown(
        options=job_options,
        value=job_options[0] if job_options != ["N/A"] else "N/A",
        label="Select Dagster job (for introspection only):",
    )
    generate_cmd_btn = mo.ui.button(label="💻 Generate CLI Command (for heavy jobs)")

    mo.md(
        f"""
        ### ⚙️ Dagster Orchestrator

        Discovers jobs from ``cianfhoghlaim.orchestration.definitions``.
        Triggering jobs from the notebook is intentionally disabled — use
        the Dagster UI for full backfills.

        Discovered jobs (first 10): `{job_options[:10]}`
        """
    )
    return generate_cmd_btn, job_dropdown, job_options


@app.cell
def _(alt, dlt, mo, pd):
    """DuckLake analytics — query the BIEP `curriculum_pages` table."""
    use_ducklake = True  # v4 default
    df_pages = pd.DataFrame()
    df_pdfs = pd.DataFrame()
    err: str | None = None

    try:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            import duckdb

            duckdb.sql(f"SET motherduck_token='{token}'")
            con = ibis.duckdb.connect("md:cianfhoghlaim")
            df_pages = con.execute(
                """
                SELECT cycle, subject, language, count(*) AS pages
                FROM cianfhoghlaim.curriculum.curriculum_pages
                GROUP BY cycle, subject, language
                ORDER BY pages DESC
                """
            ).fetchdf()
            df_pdfs = con.execute(
                """
                SELECT status, count(*) AS n
                FROM cianfhoghlaim.curriculum.pdf_downloads
                GROUP BY status
                ORDER BY n DESC
                """
            ).fetchdf()
            con.close()
        else:
            err = "MOTHERDUCK_TOKEN unset — read BIEP tables from the Dagster UI instead."
    except Exception as e:
        err = str(e)

    chart_ui = mo.md(
        "*No curriculum page data yet. Run a curriculum Dagster job first.*"
    )
    if not df_pages.empty:
        chart = (
            alt.Chart(df_pages)
            .mark_bar()
            .encode(
                x="sum(pages):Q",
                y=alt.Y("subject:N", sort="-x"),
                color="cycle:N",
                tooltip=["cycle", "subject", "language", "pages"],
            )
            .properties(
                width=600, height=400, title="Curriculum pages by subject & cycle"
            )
        )
        chart_ui = mo.ui.altair_chart(chart)

    analytics_ui = mo.vstack([
        mo.md("### 📊 BIEP lakehouse analytics — curriculum"),
        mo.hstack([
            mo.vstack([mo.md("**Curriculum pages**"), mo.ui.table(df_pages, page_size=10)]),
            mo.vstack([mo.md("**PDF download status**"), mo.ui.table(df_pdfs)]),
        ]),
        chart_ui,
        mo.md(f"⚠️ {err}" if err else ""),
    ])
    return alt, analytics_ui, chart, chart_ui, con, df_pages, df_pdfs, err


@app.cell
def _(alt, dlt, mo, pd):
    """Exam materials analytics."""
    df_exams = pd.DataFrame()
    df_urls = pd.DataFrame()
    err: str | None = None
    try:
        token = os.environ.get("MOTHERDUCK_TOKEN", "")
        if token:
            import duckdb

            duckdb.sql(f"SET motherduck_token='{token}'")
            con = ibis.duckdb.connect("md:cianfhoghlaim")
            df_exams = con.execute(
                """
                SELECT level, subject, material_type, status, count(*) AS n
                FROM cianfhoghlaim.examinations.all_exam_materials
                GROUP BY level, subject, material_type, status
                ORDER BY n DESC
                """
            ).fetchdf()
            df_urls = con.execute(
                """
                SELECT level, subject, count(*) AS urls
                FROM cianfhoghlaim.examinations.all_exam_materials
                WHERE pdf_url IS NOT NULL AND pdf_url != ''
                GROUP BY level, subject
                ORDER BY urls DESC
                """
            ).fetchdf()
            con.close()
    except Exception as e:
        err = str(e)

    exam_chart_ui = mo.md(
        "*No exam materials data yet. Run a SEC examinations job first.*"
    )
    if not df_exams.empty:
        exam_chart = (
            alt.Chart(df_exams)
            .mark_bar()
            .encode(
                x="sum(n):Q",
                y=alt.Y("subject:N", sort="-x"),
                color="material_type:N",
                tooltip=["level", "subject", "material_type", "status", "n"],
            )
            .properties(
                width=600, height=400, title="Exam materials by subject & type"
            )
        )
        exam_chart_ui = mo.ui.altair_chart(exam_chart)

    exam_analytics = mo.vstack([
        mo.md("### 📝 BIEP exam materials analytics"),
        mo.hstack([
            mo.vstack([mo.md("**Materials summary**"), mo.ui.table(df_exams, page_size=10)]),
            mo.vstack([mo.md("**PDF URLs discovered**"), mo.ui.table(df_urls, page_size=10)]),
        ]),
        exam_chart_ui,
        mo.md(f"⚠️ {err}" if err else ""),
    ])
    return (
        con, df_exams, df_urls, err, exam_analytics, exam_chart, exam_chart_ui,
    )


@app.cell
def _(mo, os):
    """Standalone DLT pipeline runner — disabled in v4 (use Dagster UI)."""
    mo.md(
        """
        ### 🔧 Standalone DLT Pipeline Runner — disabled in v4

        Running DLT pipelines from a notebook bricks the Garage S3
        single-tenant (concurrent DuckDB segfaults). Use the Dagster UI
        for full backfills; this notebook only surfaces the available
        destinations + pipelines:

        | Pipeline | Destination |
        |----------|-------------|
        | `biep_curriculum_unified` | DuckLake (Garage S3 + PostgreSQL) |
        | `biep_exam_materials_lc` | DuckLake (Garage S3 + PostgreSQL) |
        | `biep_pdf_download` | DuckLake (Garage S3 + PostgreSQL) |

        Override with ``USE_DUCKLAKE=false`` for a local DuckDB file at
        ``cianfhoghlaim/.dlt/<pipeline>/<dataset>.duckdb``.
        """
    )
    return


@app.cell
def _(mo, os, pathlib):
    """Destination verifier — confirms DLT data has landed in DuckLake."""
    verify_btn = mo.ui.run_button(label="🔍 Verify destinations")

    if verify_btn.value:
        import duckdb as _duckdb

        verify_results: list = []
        # 1. Local DuckDB fallback files
        dlt_dir = pathlib.Path(os.getcwd()) / "cianfhoghlaim" / ".dlt"
        if dlt_dir.exists():
            for db_file in dlt_dir.rglob("*.duckdb"):
                size_mb = db_file.stat().st_size / (1024 * 1024)
                try:
                    con = _duckdb.connect(str(db_file), read_only=True)
                    schemas = [
                        s[0]
                        for s in con.execute(
                            "SELECT schema_name FROM information_schema.schemata "
                            "WHERE schema_name NOT IN ('information_schema', 'pg_catalog')"
                        ).fetchall()
                    ]
                    tables: list[str] = []
                    for s in schemas:
                        try:
                            t = [
                                x[0]
                                for x in con.execute(
                                    f"SELECT table_name FROM information_schema.tables "
                                    f"WHERE table_schema = '{s}'"
                                ).fetchall()
                            ]
                            tables.extend([f"{s}.{x}" for x in t])
                        except Exception:
                            pass
                    con.close()
                    verify_results.append(
                        mo.md(f"✅ **{db_file.name}** ({size_mb:.1f} MB) — tables: {tables[:6]}…")
                    )
                except Exception as e:
                    verify_results.append(
                        mo.md(f"⚠️ **{db_file.name}** ({size_mb:.1f} MB) — error: {e}")
                    )
        else:
            verify_results.append(
                mo.md("📁 `cianfhoghlaim/.dlt/` — not yet created.")
            )

        mo.vstack([
            mo.md("### 🔍 Destination verifier (local DuckDB fallback)"),
            mo.vstack(verify_results),
        ])
    else:
        mo.md("Click *Verify destinations* to scan the local `.dlt/` directory.")
    return verify_btn, verify_results


@app.cell
def _(mo):
    # Embedder options resolved via MODEL_REGISTRY (the
    # centralized-model-registry openspec change). Render the
    # full ``embedder`` family so the operator can pick between
    # the canonical bge-m3, the english-only bge-large-en-v1.5,
    # and the lightweight MiniLM-L6-v2.
    try:
        from meaisinfhoghlaim.models import MODEL_REGISTRY
        _embedder_keys = [
            entry.key for entry in MODEL_REGISTRY.filter(family="embedder")
        ]
    except Exception:  # noqa: BLE001 — registry unavailable in dev
        _embedder_keys = ["BAAI/bge-m3", "all-MiniLM-L6-v2"]

    search_input = mo.ui.text(
        label="Search query:", value="leaving cert biology markings"
    )
    model_selector = mo.ui.dropdown(
        options=_embedder_keys,
        value=_embedder_keys[0] if _embedder_keys else "BAAI/bge-m3",
        label="Embedding model",
    )
    search_btn = mo.ui.run_button(label="🔍 Semantic search")
    mo.vstack([
        mo.md("### 🧠 LanceDB BGE-M3 search"),
        mo.hstack([model_selector, search_input]),
        search_btn,
    ])
    return model_selector, search_btn, search_input


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY,
    lancedb, mo, model_selector, search_btn, search_input,
):
    search_results: list = []

    if search_btn.value:
        with mo.status.spinner("Vectorising query and searching LanceDB…"):
            try:
                db = lancedb.connect(
                    "s3://lance/oideachais/",
                    storage_options={
                        "endpoint_url": AWS_ENDPOINT,
                        "aws_access_key_id": AWS_ACCESS_KEY,
                        "aws_secret_access_key": AWS_SECRET_KEY,
                        "region": "garage",
                    },
                )
                tables = db.list_tables()
                if "biep_curriculum_embeddings" in tables:
                    table = db.open_table("biep_curriculum_embeddings")
                    if "bge" in model_selector.value.lower():
                        from sentence_transformers import SentenceTransformer

                        model = SentenceTransformer("BAAI/bge-m3")
                        vec = model.encode(search_input.value)
                    else:
                        import numpy as np

                        vec = np.random.rand(384).astype(np.float32)

                    s_res = table.search(vec).limit(5).to_pandas()
                    if not s_res.empty:
                        display_cols = [
                            c for c in ["text", "_distance", "subject"] if c in s_res.columns
                        ]
                        search_results.append(mo.ui.table(s_res[display_cols], page_size=5))
                    else:
                        search_results.append(mo.md("*No results found.*"))
                else:
                    search_results.append(
                        mo.md(
                            f"⚠️ `biep_curriculum_embeddings` not found. "
                            f"Available: {tables}"
                        )
                    )
            except Exception as e:
                search_results.append(mo.md(f"❌ Search error: `{e}`"))

    search_panel = mo.vstack([mo.vstack(search_results)])
    return db, model, s_res, search_panel, search_results, table, tables, vec


@app.cell
def _(analytics_ui, exam_analytics, health_ui, mo, search_panel, verify_btn):
    tabs = mo.ui.tabs({
        "🚦 Health": health_ui,
        "📊 Curriculum": analytics_ui,
        "📝 Exams": exam_analytics,
        "🔍 Destinations": mo.vstack([verify_btn]),
        "🧠 Search": search_panel,
    })
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()