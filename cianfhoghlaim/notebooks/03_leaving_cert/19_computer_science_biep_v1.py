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
"""Computer Science — BIEP v1 per-subject marimo notebook.

5 visualisations over the Computer Science DuckLake tables in
`md:oideachais.leaving_cert.computer_science_*`:

1. Topic frequency per year (algorithms / data / systems / web split)
2. Pseudocode complexity
3. Code-trace question coverage
4. Marking scheme complexity
5. Quiz generator placeholder (BAML `GenerateComputerScienceQuestPack` — v2)

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
        # Computer Science — BIEP v1 Dashboard

        5 visualisations over Leaving Certificate Computer Science.
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
    # 1. Topic frequency per year (algorithms / data / systems / web split).
    topic_freq = mo.sql(
        f"""
        SELECT year, topic, count(*) AS n
        FROM oideachais.leaving_cert.computer_science_topics
        WHERE subject = 'computer_science'
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
    # 2. Pseudocode complexity.
    pseudocode = mo.sql(
        f"""
        SELECT
          CASE
            WHEN topic ILIKE '%algorithm%' THEN 'algorithms'
            WHEN topic ILIKE '%data%' THEN 'data_structures'
            WHEN topic ILIKE '%system%' THEN 'systems'
            WHEN topic ILIKE '%web%' OR topic ILIKE '%network%' THEN 'web_networks'
            ELSE 'other'
          END AS category,
          count(*) AS n
        FROM oideachais.leaving_cert.computer_science_topics
        WHERE subject = 'computer_science'
        GROUP BY category
        ORDER BY n DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(pseudocode)
    return (pseudocode,)


@app.cell
def _(con, mo):
    # 3. Code-trace question coverage.
    code_trace = mo.sql(
        f"""
        SELECT question_type, count(*) AS n
        FROM oideachais.leaving_cert.computer_science_papers,
             unnest(sections) AS sec,
             unnest(sec.questions) AS q
        WHERE subject = 'computer_science'
        GROUP BY question_type
        ORDER BY n DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(code_trace)
    return (code_trace,)


@app.cell
def _(con, mo):
    # 4. Marking scheme complexity.
    marking_complexity = mo.sql(
        f"""
        SELECT topic, band, count(*) AS n_descriptors
        FROM oideachais.leaving_cert.computer_science_marking
        WHERE subject = 'computer_science'
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

        `b.GenerateComputerScienceQuestPack` will produce 10 quiz items
        per Computer Science topic in v2.
        """
    )
    return


if __name__ == "__main__":
    app.run()
