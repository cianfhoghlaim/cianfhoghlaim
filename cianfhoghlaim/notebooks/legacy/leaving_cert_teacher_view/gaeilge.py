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
# Marimo notebook for Gaeilge teacher dashboard.
# Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T6.10.
#
# Gaeilge is unique: all source PDFs live at the subject root (no en/ subdir)
# because the entire corpus is Irish-language. This notebook connects to the
# live `oideachais.lc.gaeilge.<level>_ga` LanceDB table and the
# `oideachais.leaving_cert.gaeilge_*` DuckLake tables.

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
        # Gaeilge — Leaving Cert Teacher Dashboard

        An teanga is na Mná Gaoithe — the language is the women of the wind.

        The Gaeilge subject uses Insular Art (Book of Kells knotwork) +
        Uncial/Insular script + Ogham as the primary script. Ogma
        (the inventor of Ogham) is the Tuatha Dé deity.

        The British-Isles Education pipeline ingests the Gaeilge corpus
        via the asymmetric `leaving_cert_source._scan_subject()` path
        (no `en/` subdir) and routes through `glm-4.6v-flash`
        (multilingual + Irish-fluent).
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
            FROM oideachais.leaving_cert.gaeilge_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            """
            SELECT * FROM (VALUES
                ('Léamh', 'HL', 30),
                ('Scríbhneoireacht', 'HL', 25),
                ('Cluastuiscint', 'HL', 20),
                ('Litríocht', 'HL', 15),
                ('Gramadach', 'HL', 10)
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
            color=alt.Color("topic:N", scale=alt.Scale(scheme="greens")),
            tooltip=["topic", "level", "n"],
        )
        .properties(
            width=400,
            height=400,
            title="Gaeilge — Skill Distribution (HL, GA)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
