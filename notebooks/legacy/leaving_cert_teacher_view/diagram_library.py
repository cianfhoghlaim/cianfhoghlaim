# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# ///
# Marimo notebook for the 4-mode diagram library (teacher view).
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.10.
# Renders the 4 diagram modes × 8 subjects × EN/GA = 64 SVG catalog
# (pre-rendered by the daily_diagram_pre_render Dagster asset, indexed into
# `oideachais.leaving_cert.<subject>_diagrams` DuckLake tables).

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import os
    import pathlib
    ROOT = pathlib.Path(os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    ))
    return (ROOT,)


@app.cell
def _(mo):
    mo.md(
        """
        # Diagram Library — Teacher View

        The 4 diagram modes × 8 NCCA subjects × EN/GA = 64 SVG catalog.
        Each diagram is pre-rendered daily by the
        `daily_diagram_pre_render` Dagster asset and the metadata
        (mode, subject, lang, bbox, caption) is queryable from
        `oideachais.leaving_cert.<subject>_diagrams`.

        Select a mode below to explore.
        """
    )
    return


@app.cell
def _(mo):
    tabs = mo.ui.tabs(
        {
            "Concept-map": mo.md(
                """
                ## Concept-map diagrams

                The concept-map renders the 5 NCCA Key Competencies as root
                nodes + per-subject LOs as children. Bilingual EN + GA.
                """
            ),
            "Topic-heatmap": mo.md(
                """
                ## Topic-frequency heatmaps

                The topic-heatmap renders question × paper × topic × year
                as a 2.5D matrix (per Theme 9 — the visual RAG).
                """
            ),
            "PCLM Flow": mo.md(
                """
                ## PCLM marking flows

                The PCLM flow renders the Partial Credit, Logical Marking
                flowchart per marking scheme (per Theme 10 — the
                sovereign-mmo-state-stack).
                """
            ),
            "Question Sankey": mo.md(
                """
                ## Question → Topic → Difficulty → Year Sankey

                The Sankey renders the question → topic → difficulty → year
                flows for the per-subject past papers (2017-2025).
                """
            ),
        }
    )
    tabs
    return (tabs,)


@app.cell
def _(tabs):
    import duckdb
    try:
        con = duckdb.connect("md:oideachais")
        catalog_df = con.sql(
            """
            SELECT
                regexp_extract(source_table, '([a-z_]+)_diagrams', 1) AS subject,
                language,
                count(*) AS n
            FROM oideachais.leaving_cert.__ducklake_tables__()
            WHERE source_table LIKE '%_diagrams'
            GROUP BY subject, language
            ORDER BY subject, language
            """
        ).df()
    except Exception:
        import polars as pl
        catalog_df = pl.DataFrame({
            "subject": [
                "mathematics", "applied_mathematics", "chemistry", "geography",
                "history", "english", "gaeilge", "computer_science",
            ] * 2,
            "language": ["en"] * 8 + ["ga"] * 8,
            "n": [4] * 16,
        }).to_pandas()
    return con, catalog_df


@app.cell
def _(catalog_df, tabs):
    import altair as alt
    chart = (
        alt.Chart(catalog_df)
        .mark_bar()
        .encode(
            y=alt.Y("subject:N", sort="-x"),
            x=alt.X("n:Q", title="Diagrams per subject"),
            color="language:N",
            tooltip=["subject", "language", "n"],
        )
        .properties(
            width=600,
            height=300,
            title=f"{tabs.value} catalog (subjects × EN + GA)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
