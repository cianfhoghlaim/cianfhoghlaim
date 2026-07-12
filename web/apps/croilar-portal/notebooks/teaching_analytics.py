"""Cianfhoghlaim Teaching + CV Analytics.

Run with: marimo run notebooks/cianfhoghlaim/teaching_analytics.py
WASM export: marimo export wasm notebooks/cianfhoghlaim/teaching_analytics.py -o public/wasm/cianfhoghlaim-teaching/
"""

import marimo

__generated_with = "0.17.2"
app = marimo.App(width="full")


@app.cell(hide_code=True)
def header():
    import marimo as mo

    return mo.md("# Cianfhoghlaim — Teaching & CV Analytics")


@app.cell
def imports():
    import altair as alt
    import duckdb
    import marimo as mo

    alt.data_transformers.enable("vegafusion")

    data_path = "data/croilar.duckdb"
    conn = duckdb.connect(data_path, read_only=True)

    return mo, duckdb, alt, data_path, conn


@app.cell
def cv_overview(mo, conn):
    try:
        entries = conn.execute(
            "SELECT category, COUNT(*) AS count FROM cv_data.cv_raw GROUP BY category"
        ).fetchdf()
        if entries.empty:
            return mo.md("⚠️ No CV data yet — run the DLT CV pipeline.")
        return mo.ui.table(entries)
    except Exception:
        return mo.md("⚠️ Database not available.")


@app.cell
def publications_timeline(mo, conn):
    try:
        pubs = conn.execute(
            "SELECT filename, category FROM cv_data.cv_raw WHERE category IN ('achievement', 'publication') ORDER BY filename LIMIT 10"
        ).fetchdf()
        if pubs.empty:
            return mo.md("No publications found.")
        return mo.ui.table(pubs)
    except Exception:
        return mo.md("No publication data.")


@app.cell
def teaching_summary(mo, conn):
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM teaching_data.cv_raw"
        ).fetchone()[0]

        return mo.md(f"""
        ## Teaching Record

        - **Teaching documents loaded**: {count}
        - **Pipeline**: `teaching_croilar` DLT pipeline
        - **Extraction**: `teaching_extraction.baml` via LiteLLM
        - **Search index**: LanceDB `croilar_teaching`
        """)
    except Exception:
        return mo.md("No teaching data available.")
