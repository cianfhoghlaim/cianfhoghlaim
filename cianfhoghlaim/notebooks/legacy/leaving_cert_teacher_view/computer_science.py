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
# Marimo notebook for Computer Science teacher dashboard.
#
# Sparse subject — only 2 OL exam papers per language; validates the
# British-Isles Education pipeline on small-corpus subjects.
# Queries live `oideachais.leaving_cert.computer_science_*` DuckLake tables.

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
        # Computer Science — Leaving Cert Teacher Dashboard

        The Computer Science subject uses the BitCraft Recipe Tree +
        Clair Obscur skill tree. The 4 NCCA CS topics (Algorithms + Data
        + Systems + Networks) are arranged as the 4 branches.

        This is a **sparse corpus** (2 OL papers each language, plus the
        specification PDF) — the British-Isles pipeline exercises its
        low-corpus path here.
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
            FROM oideachais.leaving_cert.computer_science_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Algorithms', 'OL', 30),
                ('Data Structures', 'OL', 30),
                ('Computer Systems', 'OL', 20),
                ('Networks', 'OL', 20)
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
            title="Computer Science — Topic Distribution (OL)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
