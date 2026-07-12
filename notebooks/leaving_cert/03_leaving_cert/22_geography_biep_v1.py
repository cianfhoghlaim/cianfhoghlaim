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
"""Geography — BIEP v1 per-subject marimo notebook.

5 visualisations over the Geography DuckLake tables in
`md:oideachais.leaving_cert.geography_*`:

1. Topic frequency per year (Physical / Regional / Economic split)
2. Fieldwork requirement coverage
3. Cross-subject competency mapping (uses the LanceDB
   `oideachais.lc.cross_subject.competencies` table)
4. Marking scheme complexity
5. Quiz generator placeholder (BAML `GenerateGeographyQuestPack` — v2)

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
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
        # Geography — BIEP v1 Dashboard

        5 visualisations over Leaving Certificate Geography.
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
    # 1. Topic frequency per year (Physical / Regional / Economic split).
    topic_freq = mo.sql(
        f"""
        SELECT year, topic, count(*) AS n
        FROM oideachais.leaving_cert.geography_topics
        WHERE subject = 'geography'
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
    # 2. Fieldwork requirement coverage.
    fieldwork = mo.sql(
        f"""
        SELECT module_id, name_en, estimated_hours, type
        FROM oideachais.leaving_cert.geography_syllabus s,
             unnest(s.module_topics) AS m
        WHERE s.subject = 'geography'
          AND (m.name_en ILIKE '%fieldwork%' OR m.name_en ILIKE '%field work%')
        ORDER BY module_id
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(fieldwork)
    return (fieldwork,)


@app.cell
def _(con, mo):
    # 3. Cross-subject competency mapping.
    cross_subject = mo.sql(
        f"""
        SELECT competency, level, language, count(*) AS n
        FROM lance_scan('oideachais.lc.cross_subject.competencies')
        WHERE subject = 'geography'
        GROUP BY competency, level, language
        ORDER BY competency, level
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(cross_subject)
    return (cross_subject,)


@app.cell
def _(con, mo):
    # 4. Marking scheme complexity.
    marking_complexity = mo.sql(
        f"""
        SELECT topic, band, count(*) AS n_descriptors
        FROM oideachais.leaving_cert.geography_marking
        WHERE subject = 'geography'
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

        `b.GenerateGeographyQuestPack` will produce 10 quiz items per
        Geography topic in v2.
        """
    )
    return


if __name__ == "__main__":
    app.run()
