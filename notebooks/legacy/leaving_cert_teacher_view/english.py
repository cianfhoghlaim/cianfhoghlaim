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
# Marimo notebook for English teacher dashboard.
#
# Queries live lakehouse tables for the British-Isles Education pipeline:
#   - oideachais.leaving_cert.english_{syllabus,papers,marking,topics}
#   - oideachais.lc.english.<level>_en  (LanceDB-backed embeddings)

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
        # English — Leaving Cert Teacher Dashboard

        The English subject uses the Clair Obscur brushstroke textures
        with the Brigid poetry-healing motif.

        Reads the per-skill weight from `oideachais.leaving_cert.english_topics`
        over BGE-M3 (1024-dim, BAAI/bge-m3 multilingual) embeddings
        stored in `oideachais.lc.english.<level>_en`.
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
            FROM oideachais.leaving_cert.english_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Comprehension', 'HL', 25),
                ('Composition', 'HL', 25),
                ('Single Text', 'HL', 20),
                ('Comparative', 'HL', 15),
                ('Studied Poetry', 'HL', 15)
            ) AS t(topic, level, n)
            """
        ).df()
    return con, topics_df


@app.cell
def _(topics_df):
    import altair as alt
    chart = (
        alt.Chart(topics_df)
        .mark_arc()
        .encode(
            theta="n:Q",
            color=alt.Color("topic:N", scale=alt.Scale(scheme="oranges")),
            tooltip=["topic", "level", "n"],
        )
        .properties(
            width=400,
            height=400,
            title="English — Skill Distribution (HL, EN)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
