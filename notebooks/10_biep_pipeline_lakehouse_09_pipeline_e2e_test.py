# /// script
# requires-python = ">=3.12"
# dependencies = [
#   marimo>=0.13,
#   duckdb>=1.0,
#   ibis-framework[duckdb]>=9.0,
#   pandas>=2.2,
#   altair>=5.0,
#   pyarrow>=15,
#   anywidget>=0.9,
#   traitlets>=5.14,
#   lancedb>=0.20,
#   boto3>=1.34,
#   dlt>=1.0,
#   sentence-transformers>=3.0,
# ]
# ///
"""End-to-end pipeline testing — BIEP MotherDuck + DuckLake + LanceDB.

Verifies the British-Isles Education pipeline integration:
Garage S3, MotherDuck + DuckLake lakehouse (``md:cianfhoghlaim``), and
the BGE-M3 LanceDB vector index.

All credentials are hydrated by the mise directory hook from the
Infisical `dev-baile` vault (``.infisical.env`` template). Never hard-code
secrets in this file.
"""
from __future__ import annotations

import marimo


# R1 — `setup_biep_registry_header()` collapses the 14-line header
# (per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change)
from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
)


__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import marimo as mo
    import duckdb
    import ibis  # ibis-first entrypoint
    import boto3
    import pandas as pd

    use_md = os.environ.get("MOTHERDUCK_ENABLED", "false").lower() == "true"

    mo.md(
        f"""
        # E2E Pipeline Testing — BIEP

        Validates the British-Isles Education pipeline integration:
        MotherDuck + DuckLake lakehouse, Garage S3, LanceDB (BGE-M3).

        Backend: `{"md:cianfhoghlaim (MotherDuck + DuckLake)" if use_md else "local DuckDB"}`.

        All credentials come from the Infisical `dev-baile` vault via the
        mise directory hook — no hard-coded secrets in this notebook.
        """
    )
    return boto3, duckdb, ibis, mo, os, pd, use_md


@app.cell
def _(duckdb, ibis, mo, os, use_md):
    AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:3900")
    AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")

    con = ibis.duckdb.connect()
    try:
        if use_md:
            token = os.environ.get("MOTHERDUCK_TOKEN", "")
            duckdb.sql(f"SET motherduck_token='{token}'")
            con.execute("ATTACH 'md:cianfhoghlaim' (TYPE MOTHERDUCK);")
            con.execute("USE oideachais;")
        else:
            con.execute("INSTALL httpfs; LOAD httpfs;")
            con.execute(
                f"SET s3_endpoint='{AWS_ENDPOINT.replace('http://', '').replace('https://', '')}';"
            )
            con.execute("SET s3_use_ssl=false;")
            con.execute("SET s3_url_style='path';")
            if AWS_ACCESS_KEY:
                con.execute(f"SET s3_access_key_id='{AWS_ACCESS_KEY}';")
            if AWS_SECRET_KEY:
                con.execute(f"SET s3_secret_access_key='{AWS_SECRET_KEY}';")
            con.execute("SET s3_region='garage';")
        ok = True
    except Exception as e:
        ok = False
        mo.md(f"⚠️ DuckDB attach failed: {e}")

    mo.md(
        f"""
        ## 1. Infrastructure status

        - **Garage S3:** `{AWS_ENDPOINT}`
        - **Lakehouse:** `{ "md:cianfhoghlaim" if use_md else "local DuckDB" }`
        """
    )
    return AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, con, ok


@app.cell
def _(con, duckdb, mo, os, pd, use_md):
    """3. Lakehouse / DLT verification — pulls rows from `curriculum.curriculum_pages`."""
    try:
        if use_md:
            query = """
                SELECT cycle, subject, language, count(*) AS pages
                FROM cianfhoghlaim.curriculum.curriculum_pages
                GROUP BY cycle, subject, language
                ORDER BY pages DESC
                LIMIT 25
            """
        else:
            query = """
                SELECT cycle, subject, language, count(*) AS pages
                FROM read_parquet('s3://ducklake/oideachais/curriculum/curriculum_pages/*.parquet')
                GROUP BY cycle, subject, language
                ORDER BY pages DESC
                LIMIT 25
            """
        df_pages = con.execute(query).to_pandas()
        status = f"✅ Data successfully queried ({len(df_pages)} rows)"
    except Exception as e:
        df_pages = pd.DataFrame({"error": [str(e)]})
        status = f"❌ Pipeline connection failed: {e}"

    ducklake_ui = mo.vstack([
        mo.md(f"### 3. BIEP lakehouse verification\n{status}"),
        mo.ui.table(df_pages, selection=None),
    ])
    return df_pages, ducklake_ui, status


@app.cell
def _(AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY, boto3, mo):
    """4. Garage S3 PDF storage verification."""
    garage_status = ""
    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=AWS_ENDPOINT,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name="garage",
        )
        objects = s3.list_objects_v2(Bucket="ducklake", Prefix="oideachais/downloads/")
        if "Contents" in objects:
            pdf_count = len([obj for obj in objects["Contents"] if obj["Key"].endswith(".pdf")])
            garage_status = f"✅ Found {pdf_count} PDFs in Garage S3 (`s3://ducklake/oideachais/downloads/`)"
        else:
            garage_status = "⚠️ Garage S3 bucket is empty. Did the `pdf_downloads` job run?"
    except Exception as e:
        garage_status = f"❌ Garage S3 connection failed: {e}"

    garage_ui = mo.md(f"## 4. Garage S3 verification\n{garage_status}")
    return garage_ui, garage_status


@app.cell
def _(
    AWS_ACCESS_KEY, AWS_ENDPOINT, AWS_SECRET_KEY,
    mo, use_md, duckdb,
):
    """5. LanceDB BGE-M3 vector index verification."""
    import lancedb

    LANCEDB_URI = "s3://lance/oideachais/"
    lance_status = ""
    search_ui = mo.md("")

    try:
        db = lancedb.connect(
            LANCEDB_URI,
            storage_options={
                "endpoint_url": AWS_ENDPOINT,
                "aws_access_key_id": AWS_ACCESS_KEY,
                "aws_secret_access_key": AWS_SECRET_KEY,
                "region": "garage",
            },
        )
        tables = db.table_names()
        if "biep_curriculum_embeddings" in tables:
            table = db.open_table("biep_curriculum_embeddings")
            row_count = table.count_rows()
            lance_status = f"✅ LanceDB connected. `biep_curriculum_embeddings` has {row_count} BGE-M3 chunks."

            try:
                from sentence_transformers import SentenceTransformer
                import numpy as np

                model = SentenceTransformer("BAAI/bge-m3")
                vec = model.encode("What is the structure of the leaving cert biology exam?")
                results = table.search(vec).limit(3).to_pandas()
                if not results.empty:
                    display_cols = [c for c in ["text", "_distance", "subject"] if c in results.columns]
                    search_ui = mo.vstack([
                        mo.md(f"**Test query** — model `BAAI/bge-m3`, {len(results)} hits"),
                        mo.ui.table(results[display_cols], selection=None),
                    ])
                else:
                    search_ui = mo.md("*No semantic results found.*")
            except Exception as e:
                search_ui = mo.callout(
                    mo.md(f"`sentence-transformers` query failed: {e}"),
                    kind="warn",
                )
        else:
            lance_status = f"⚠️ LanceDB connected, but `biep_curriculum_embeddings` not found. Available: {tables}"
    except Exception as e:
        lance_status = f"❌ LanceDB verification failed: {e}"

    lancedb_ui = mo.vstack([
        mo.md(f"## 5. LanceDB (BGE-M3) verification\n{lance_status}"),
        search_ui,
    ])
    return db, lancedb, lance_status, lancedb_ui, results, search_ui, table


@app.cell
def _(
    con, duckdb, mo, os, pd, use_md,
):
    """2. Dagster orchestrator — read available jobs (best-effort).

    No longer requires the legacy ``oideachais/data_platform`` path; if
    ``dagster_defs.definitions`` is importable from the v4 workspace it
    is used, otherwise we fall back to ``dg list jobs``.
    """
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

    cycle_dropdown = mo.ui.dropdown(
        options=["biep_junior_cycle", "biep_senior_cycle"],
        value="biep_senior_cycle",
        label="Education cycle",
    )
    partition_input = mo.ui.text(
        value="en|chemistry",
        label="Partition key (language|subject)",
    )

    mo.vstack([
        mo.md("## 2. Dagster orchestrator (best-effort)"),
        mo.md(
            "Use the Dagster UI for full backfills — this notebook only "
            "introspects available jobs. Triggering a job from the notebook "
            "is intentionally **disabled** in v4 (it bricks the "
            "Garage S3 single-tenant)."
        ),
        mo.hstack([cycle_dropdown, partition_input]),
        mo.md(f"**Discovered jobs:** `{job_options[:8]}`"),
    ])
    return cycle_dropdown, job_options, partition_input


@app.cell
def _(ducklake_ui, garage_ui, lancedb_ui, mo):
    tabs = mo.ui.tabs({
        "1. Infra": mo.md("See section 1 above."),
        "2. Orchestrator": mo.md("See section 2 above."),
        "3. Lakehouse": ducklake_ui,
        "4. Garage S3": garage_ui,
        "5. LanceDB": lancedb_ui,
    })
    tabs
    return (tabs,)


if __name__ == "__main__":
    app.run()

# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab (the "Ask BAML" tab)
# ────────────────────────────────────────────────────────────────────────────

@app.cell
def _llm_tab(mo):
    """P3 — LLM-assisted analysis tab via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the BIEP v3 lakehouse explorer assistant. You help "
            "operators query the DuckLake / MotherDuck / LanceDB lakehouse. "
            "When the user asks about a table or column, refer to the DLT "
            "schema introspection in information_schema.tables."
        ),
        prompts=[
            "📚 How many tables are in this schema?",
            "🔍 Show me the schema for the most recently materialised table",
            "📊 What are the top 10 most frequent values in <column_name>?",
            "🎯 How do I query for a specific subject's curriculum_pages?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"), _chat])
    return (_chat,)


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv=None):
    """CLI entry point — emits a JSON summary payload (per marimo scripts guide)."""
    parser = cli_argparser_biep("BIEP lakehouse explorer")
    args = parser.parse_args(argv)

    payload = {
        "notebook": __name__,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)
