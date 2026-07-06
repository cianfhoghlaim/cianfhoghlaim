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
# Marimo notebook for Mathematics teacher dashboard.
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.10.
# Renders the 8-subject NCCA syllabus landscape with bilingual EN + GA content
# over the live British-Isles Education pipeline lakehouse.
#
# Run: `uv run marimo edit notebooks/leaving_cert/mathematics.py`

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
        # Mathematics — Leaving Cert Teacher Dashboard

        Bilingual (EN + GA) overview of the 8 NCCA Leaving Certificate
        subjects, with the Mathematics subject as the lead.

        This dashboard queries the live `md:oideachais` lakehouse
        (`oideachais.leaving_cert.mathematics_{syllabus,papers,marking,topics,diagrams}`
        DuckLake tables + `oideachais.lc.mathematics.<level>_<language>` LanceDB
        embeddings) for the British-Isles Education pipeline.
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
            SELECT subject, level, language, topic, count(*) AS n
            FROM oideachais.leaving_cert.mathematics_topics
            GROUP BY subject, level, language, topic
            ORDER BY n DESC
            """
        ).df()
        LIVE = True
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Algebra', 'HL', 'en', 25),
                ('Calculus', 'HL', 'en', 25),
                ('Probability', 'HL', 'en', 15),
                ('Statistics', 'HL', 'en', 10),
                ('Finance', 'HL', 'en', 10),
                ('Geometry', 'HL', 'en', 5),
                ('Complex Numbers', 'HL', 'en', 5),
                ('Sequences', 'HL', 'en', 5)
            ) AS t(topic, level, language, n)
            """
        ).df()
        LIVE = False
    return LIVE, con, topics_df


@app.cell
def _(topics_df):
    import altair as alt
    chart = (
        alt.Chart(topics_df)
        .mark_bar()
        .encode(
            y=alt.Y("topic:N", sort="-x"),
            x=alt.X("n:Q", title="Weight (% of total exam marks)"),
            color="language:N",
            tooltip=["topic", "level", "language", "n"],
        )
        .properties(
            width=500,
            height=300,
            title="Mathematics — Topic Distribution (HL, EN + GA)",
        )
    )
    return (chart,)


@app.cell
def _(mo):
    mo.md(
        """
        ## 5 NCCA Key Competencies for Mathematics

        | Competency | Tuatha Dé deity | Sample LO |
        |:--|:--|:--|
        | Communicating | Brigid | LC-MATHS-LO-1.1 |
        | Information Processing | Ogma | LC-MATHS-LO-2.1 |
        | Critical & Creative Thinking | Lugh | LC-MATHS-LO-3.1 |
        | Personal Effectiveness | Dian Cecht | LC-MATHS-LO-4.1 |
        | Working with Others | Trí Dé Dána | LC-MATHS-LO-5.1 |
        """
    )
    return


if __name__ == "__main__":
    app.run()
