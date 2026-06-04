"""Marimo notebook — Croílár CV Dashboard.

Interactive exploration of Cian de Búrca's CV data pipeline.
Requires: marimo, altair, ibis, duckdb
"""

import marimo

__generated_with = "0.18.0"
app = marimo.App(width="full", app_title="Croílár CV Dashboard")


@app.cell
def __():
    import marimo as mo
    import duckdb
    import altair as alt
    import polars as pl
    from pathlib import Path
    return mo, duckdb, alt, pl, Path


@app.cell
def __(Path, mo):
    duckdb_path = Path("./croilar.duckdb")
    mo.md(f"""
    # 🧬 Croílár CV Dashboard

    Connected to DuckDB at `{duckdb_path}`.
    Pipeline status and CV analytics for the croilar data engineering subproject.
    """)
    return duckdb_path,


@app.cell
def __(duckdb, duckdb_path, mo, pl):
    try:
        conn = duckdb.connect(str(duckdb_path), read_only=True)
        raw_count = conn.execute(
            "SELECT COUNT(*) FROM cv_data.cv_raw"
        ).fetchone()[0]
        conn.close()
    except Exception as e:
        raw_count = 0

    mo.statistic(
        label="CV Documents Ingested",
        value=raw_count,
        caption="cv_data.cv_raw table",
        direction="increase",
    )
    return conn, raw_count


@app.cell
def __(duckdb, duckdb_path, mo, pl):
    try:
        conn = duckdb.connect(str(duckdb_path), read_only=True)
        status = conn.execute("""
            SELECT category, COUNT(*) as count
            FROM cv_data.cv_raw
            GROUP BY category
            ORDER BY count DESC
        """).pl()
        conn.close()
    except Exception:
        status = pl.DataFrame({"category": [], "count": []})

    if status.height > 0:
        mo.ui.table(
            status,
            label="Documents by Category",
        )
    else:
        mo.md("> _No CV data ingested yet. Run `cv_pdf_ingestion` in Dagster._")
    return status,


@app.cell
def __(alt, mo, status):
    if status.height > 0:
        chart = alt.Chart(status).mark_bar().encode(
            x=alt.X("category:N", title="Category"),
            y=alt.Y("count:Q", title="Documents"),
            color=alt.Color("category:N", legend=None),
        ).properties(title="CV Documents by Category", width=600, height=300)
        mo.ui.altair_chart(chart)
    return chart,


@app.cell
def __(mo):
    mo.md("""
    ## Pipeline Assets

    | Asset | Group | Status |
    |:--|:--|:--|
    | `cv_pdf_ingestion` | cv_pipeline | Ready to run |
    | `cv_extraction` | cv_pipeline | Depends on cv_pdf_ingestion |
    | `cv_search_index` | cv_pipeline | Depends on cv_extraction |
    | `placement_ingestion` | teaching_pipeline | Ready to run |
    | `teaching_extraction` | teaching_pipeline | Depends on placement_ingestion |
    | `teaching_search` | teaching_pipeline | Depends on teaching_extraction |
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Schedules

    - **Daily Music Ingestion** — 03:00 UTC — spotify_ingestion, soundcloud_ingestion, youtube_ingestion, track_metadata_embedded
    - **Weekly CV Refresh** — 04:00 Sunday — cv_pdf_ingestion, cv_extraction, cv_search_index
    - **Monthly Identity Check** — 05:00, 1st of month — id_document_verification
    """)
    return


@app.cell
def __(mo):
    mo.md("""
    ## Search Index

    The CV search index is built by the CocoIndex `CVEmbedding` flow:
    - Model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dims)
    - Vector DB: LanceDB (`croilar_cv` collection)
    - Language detection: en / ga (Irish markers heuristic)
    - Index file: `croilar/cv/search_index.json`
    """)
    return


if __name__ == "__main__":
    app.run()
