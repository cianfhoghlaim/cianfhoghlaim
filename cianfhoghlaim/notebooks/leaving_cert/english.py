# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb",
#     "ibis-framework",
#     "polars",
#     "altair",
#     "pyarrow",
# ]
# ///
"""English — BIEP v1 per-subject marimo notebook.

5 visualisations over the English DuckLake tables in
`md:oideachais.leaving_cert.english_*`:

1. Topic frequency per year (Comparative / Cultural / Language split)
2. Single-text vs comparative-text mode
3. Poetry / prose / drama breakdown
4. Marking scheme complexity
5. Quiz generator placeholder (BAML `GenerateEnglishQuestPack` — v2)

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
openspec/specs/british-isles-education-pipeline/spec.md
"""
import marimo

__version__ = "0.1.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # English — BIEP v1 Dashboard

        5 visualisations over Leaving Certificate English.
        """
    )
    return


@app.cell
def _():
    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse
    con, engine = connect_biep_lakehouse(use_md=False, local_fallback=True)
    return con, engine


@app.cell
def _(con, mo):
    # 1. Topic frequency per year (Comparative / Cultural / Language split).
    topic_freq = mo.sql(
        f"""
        SELECT year, topic, count(*) AS n
        FROM oideachais.leaving_cert.english_topics
        WHERE subject = 'english'
        GROUP BY year, topic
        ORDER BY year, n DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(topic_freq.head(50))
    return (topic_freq,)


@app.cell
def _(con, mo):
    # 2. Single-text vs comparative-text mode.
    mode = mo.sql(
        f"""
        SELECT
          CASE
            WHEN topic ILIKE '%comparative%' THEN 'comparative'
            ELSE 'single'
          END AS text_mode,
          count(*) AS n
        FROM oideachais.leaving_cert.english_topics
        WHERE subject = 'english'
        GROUP BY text_mode
        ORDER BY n DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(mode)
    return (mode,)


@app.cell
def _(con, mo):
    # 3. Poetry / prose / drama breakdown.
    genre = mo.sql(
        f"""
        SELECT
          CASE
            WHEN topic ILIKE '%poetry%' OR topic ILIKE '%poem%' THEN 'poetry'
            WHEN topic ILIKE '%drama%' OR topic ILIKE '%play%' THEN 'drama'
            ELSE 'prose'
          END AS genre,
          count(*) AS n
        FROM oideachais.leaving_cert.english_topics
        WHERE subject = 'english'
        GROUP BY genre
        ORDER BY n DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(genre)
    return (genre,)


@app.cell
def _(con, mo):
    # 4. Marking scheme complexity.
    marking_complexity = mo.sql(
        f"""
        SELECT topic, band, count(*) AS n_descriptors
        FROM oideachais.leaving_cert.english_marking
        WHERE subject = 'english'
        GROUP BY topic, band
        ORDER BY topic, band
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(marking_complexity)
    return (marking_complexity,)


@app.cell
def _(mo):
    # 5. Quiz generator placeholder.
    mo.md(
        """
        ## Quiz generator (deferred to v2)

        `b.GenerateEnglishQuestPack` will produce 10 quiz items per
        English topic in v2.
        """
    )
    return


if __name__ == "__main__":
    app.run()
