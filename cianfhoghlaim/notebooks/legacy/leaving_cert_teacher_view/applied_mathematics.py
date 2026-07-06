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
# Marimo notebook for Applied Mathematics teacher dashboard.
#
# Live lakehouse queries:
#   - oideachais.leaving_cert.applied_mathematics_{syllabus,papers,marking,topics,diagrams}
#   - oideachais.lc.applied_mathematics.<level>_<language>

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
        # Applied Mathematics — Leaving Cert Teacher Dashboard

        The Applied Mathematics subject uses the Clair Obscur Belle Époque
        material library + the BitCraft Recipe Tree (the algorithm-design-pattern
        visualisation). The 4 modules (Mechanics + Statistics) are arranged
        hierarchically.

        BGE-M3 multilingual embeddings (1024-dim) live in
        `oideachais.lc.applied_mathematics.<level>_<language>` — the
        British-Isles Education pipeline indexes LOs across EN + GA.
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
            FROM oideachais.leaving_cert.applied_mathematics_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Mechanics', 'HL', 40),
                ('Statistics', 'HL', 25),
                ('Probability', 'HL', 20),
                ('Numerical Methods', 'HL', 15)
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
            color=alt.Color("topic:N", scale=alt.Scale(scheme="purples")),
            tooltip=["topic", "level", "n"],
        )
        .properties(
            width=400,
            height=400,
            title="Applied Mathematics — Topic Distribution (HL)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
