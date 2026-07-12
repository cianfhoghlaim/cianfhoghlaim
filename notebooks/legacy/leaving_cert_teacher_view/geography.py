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
# Marimo notebook for Geography teacher dashboard.
#
# Geography is the diagram-heaviest subject (maps, climate graphs) — the
# BAML `ExtractSyllabusDiagram` function (per-subject CocoIndex v1 App
# oideachais-cocoindex-v1) extracts bbox + caption pairs which land in
# `oideachais.leaving_cert.geography_diagrams`.

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
        # Geography — Leaving Cert Teacher Dashboard

        An Tíreolaíocht — the Geography subject uses the WoW map zones
        layout (hex-based claims with decay indicators). The 6 British Isles
        subnations are the 6 zones. The 4 Irish provinces are the home base.

        Geography exercises the **diagram-heavy** path of the British-Isles
        Education pipeline: 1 JPG scanned exam page → docling-serve fallback
        → `oideachais.leaving_cert.geography_diagrams` table populated via
        the `molmo2-8b` pointing model.
        """
    )
    return


@app.cell
def _():
    import duckdb
    try:
        con = duckdb.connect("md:oideachais")
        topics_df = con.sql(
            """
            SELECT topic, level, count(*) AS n
            FROM oideachais.leaving_cert.geography_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Core 1: Physical Geography', 'HL', 20),
                ('Core 2: Regional Geography', 'HL', 20),
                ('Elective 1', 'HL', 15),
                ('Elective 2', 'HL', 15),
                ('Elective 3', 'HL', 15),
                ('Elective 4', 'HL', 15)
            ) AS t(topic, level, n)
            """
        ).df()
    return con, topics_df


@app.cell
def _(topics_df):
    import altair as alt
    chart = (
        alt.Chart(topics_df)
        .mark_bar()
        .encode(
            y=alt.Y("topic:N", sort="-x"),
            x=alt.X("n:Q", title="Weight (% of total exam marks)"),
            color="level:N",
            tooltip=["topic", "level", "n"],
        )
        .properties(
            width=500,
            height=300,
            title="Geography — Topic Distribution (HL)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
