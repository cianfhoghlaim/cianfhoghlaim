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
"""Chemistry — BIEP v1 per-subject marimo notebook.

5 visualisations over the Chemistry DuckLake tables in
`md:oideachais.leaving_cert.chemistry_*`:

1. Topic frequency per year (line chart)
2. Diagram extraction coverage (count of diagrams per PDF per topic)
3. Experiment ↔ Learning Outcome alignment
4. Marking scheme complexity
5. Quiz generator placeholder (BAML `GenerateChemistryQuestPack` — v2)

KCG patterns used:
- `mo.sql(engine=md:oideachais)` for federated SQL
- ibis-first analytics
- PEP 723 inline deps

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
        # Chemistry — BIEP v1 Dashboard

        5 visualisations over Leaving Certificate Chemistry.
        """
    )
    return


@app.cell
def _():
    import os
    from cianfhoghlaim.notebooks.nb_utils import connect_biep_lakehouse
    con, engine = connect_biep_lakehouse(use_md=False, local_fallback=True)
    return con, engine


@app.cell
def _(con, mo):
    # 1. Topic frequency per year.
    topic_freq = mo.sql(
        f"""
        SELECT year, topic, count(*) AS n
        FROM oideachais.leaving_cert.chemistry_topics
        WHERE subject = 'chemistry'
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
    # 2. Diagram extraction coverage (count of diagrams per PDF per topic).
    diagrams = mo.sql(
        f"""
        SELECT source_pdf, topic, count(*) AS n_diagrams
        FROM oideachais.leaving_cert.chemistry_diagrams
        WHERE subject = 'chemistry'
        GROUP BY source_pdf, topic
        ORDER BY n_diagrams DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(diagrams.head(30))
    return (diagrams,)


@app.cell
def _(con, mo):
    # 3. Experiment ↔ Learning Outcome alignment.
    experiment_alignment = mo.sql(
        f"""
        SELECT m.module_id, m.name_en, m.estimated_hours,
               count(*) AS n_learning_outcomes
        FROM oideachais.leaving_cert.chemistry_syllabus s,
             unnest(s.module_topics) AS m
        WHERE s.subject = 'chemistry'
        GROUP BY m.module_id, m.name_en, m.estimated_hours
        ORDER BY n_learning_outcomes DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(experiment_alignment)
    return (experiment_alignment,)


@app.cell
def _(con, mo):
    # 4. Marking scheme complexity.
    marking_complexity = mo.sql(
        f"""
        SELECT topic, band, count(*) AS n_descriptors
        FROM oideachais.leaving_cert.chemistry_marking
        WHERE subject = 'chemistry'
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

        `b.GenerateChemistryQuestPack` will produce 10 quiz items per
        Chemistry topic in v2.
        """
    )
    return


if __name__ == "__main__":
    app.run()
