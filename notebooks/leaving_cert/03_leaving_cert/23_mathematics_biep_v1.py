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
"""Mathematics — BIEP v1 per-subject marimo notebook.

5 visualisations over the Mathematics DuckLake tables in
`md:oideachais.leaving_cert.mathematics_*`:

1. Topic frequency per year (line chart)
2. Exam paper difficulty trend (bar chart)
3. Cross-linguistic topic mapping (Gaeilge ↔ Mathematics key terms)
4. Marking scheme complexity (heatmap)
5. Quiz generator: 10 quiz items per topic via the BAML
   `GenerateMathsQuestPack` schema (deferred to v2; placeholder
   structure for now)

KCG patterns used:
- `mo.sql(engine=md:oideachais)` for federated SQL
- ibis-first analytics (per `oideachais-marimo-dashboards` spec)
- PEP 723 inline deps
- Reads PDF paths from `os.environ["CIANFHOGHLAIM_LEAVING_CERT_ROOT"]`
- Never hardcodes secrets

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
        # Mathematics — BIEP v1 Dashboard

        5 visualisations over the Leaving Certificate Mathematics
        syllabus, exam papers, and marking schemes.
        """
    )
    return


@app.cell
def _():
    import os
    from cianfhoghlaim.notebooks.nb_utils import (
        BIEP_LANGUAGES,
        BIEP_LEVELS,
        connect_biep_lakehouse,
    )
    lc_root = os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "~/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    )
    con, engine = connect_biep_lakehouse(use_md=False, local_fallback=True)
    return BIEP_LANGUAGES, BIEP_LEVELS, con, engine, lc_root


@app.cell
def _(con, mo):
    # 1. Topic frequency per year — line chart.
    topic_freq = mo.sql(
        f"""
        SELECT year, topic, count(*) AS n
        FROM oideachais.leaving_cert.mathematics_topics
        WHERE subject = 'mathematics'
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
    # 2. Exam paper difficulty trend — bar chart (BAML-derived).
    diff_trend = mo.sql(
        f"""
        SELECT year, AVG(marks) AS avg_marks, COUNT(*) AS n_papers
        FROM oideachais.leaving_cert.mathematics_papers
        WHERE subject = 'mathematics'
        GROUP BY year
        ORDER BY year
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(diff_trend)
    return (diff_trend,)


@app.cell
def _(con, mo):
    # 3. Cross-linguistic topic mapping (Mathematics key terms, EN only —
    #    Mathematics is taught in English in Ireland; bilingual display
    #    is the contrast with Gaeilge).
    cross_ling = mo.sql(
        f"""
        SELECT topic_label_en, topic_label_ga, level
        FROM oideachais.leaving_cert.mathematics_topics
        WHERE subject = 'mathematics' AND language = 'en'
        ORDER BY level, topic_label_en
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(cross_ling.head(20))
    return (cross_ling,)


@app.cell
def _(con, mo):
    # 4. Marking scheme complexity — heatmap-ready table (descriptor count
    #    per topic per band).
    marking_complexity = mo.sql(
        f"""
        SELECT topic, band, count(*) AS n_descriptors
        FROM oideachais.leaving_cert.mathematics_marking
        WHERE subject = 'mathematics'
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
    # 5. Quiz generator placeholder — 10 quiz items per topic.
    #    v2 will call b.GenerateMathsQuestPack from
    #    baml/education/subjects/qpack_mathematics.baml.
    mo.md(
        """
        ## Quiz generator (deferred to v2)

        The `b.GenerateMathsQuestPack` BAML function lives in
        `baml/education/subjects/qpack_mathematics.baml` and will
        produce 10 quiz items per Mathematics topic.
        """
    )
    return


if __name__ == "__main__":
    app.run()
