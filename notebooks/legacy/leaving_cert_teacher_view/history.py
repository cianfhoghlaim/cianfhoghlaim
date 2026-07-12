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
# Marimo notebook for History teacher dashboard.
#
# History emphasises the temporal axis — the Graphiti bi-temporal model
# (event_time = syllabus revision year, ingest_time = PDF ingestion
# timestamp) is the canonical contract for `leaving_cert_history_*` tables.

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
        # History — Leaving Cert Teacher Dashboard

        The History subject uses the WoW raid-frames grid layout for the
        historical figures. The Morrígan's war-mask is the primary icon.

        For the British-Isles Education pipeline, History is the temporal
        keystone — Graphiti episodes in `oideachais.leaving_cert.history_*`
        carry both `event_time` (LO revision year) and `ingest_time`
        (pipeline ingestion timestamp), enabling curriculum evolution
        queries against the live lakehouse.
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
            FROM oideachais.leaving_cert.history_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Early Modern Ireland (1494-1803)', 'HL', 25),
                ('Modern Ireland (1801-1993)', 'HL', 25),
                ('European Renaissance', 'HL', 15),
                ('Industrial Revolution', 'HL', 15),
                ('20th Century Europe', 'HL', 20)
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
            title="History — Topic Distribution (HL)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
