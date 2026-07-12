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
"""Gaeilge — BIEP v1 per-subject marimo notebook (Irish-only).

5 visualisations over the Gaeilge DuckLake tables in
`md:oideachais.leaving_cert.gaeilge_*`:

1. Topic frequency per year (with `irish_fada` asset_check badge)
2. Cross-linguistic concept coverage (EN ↔ GA)
3. Litríocht / Úrsceal / Filíocht breakdown
4. Marking scheme complexity
5. Quiz generator placeholder (BAML `GenerateGaeilgeQuestPack` — v2)

Gaeilge is Irish-only per the BIEP v1 spec requirement
"gaeilge-only syllabuses (no English sibling)".

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
        # Gaeilge — BIEP v1 Dashboard (Gaeilge amháin)

        5 léiriúchán ar an siollabas, na páipéir scrúdaithe, agus na
        scéimeanna marcála Gaeilge.
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
    # 1. Topic frequency per year + `irish_fada` asset_check badge.
    topic_freq = mo.sql(
        f"""
        SELECT year, topic, topic_label_ga, count(*) AS n
        FROM oideachais.leaving_cert.gaeilge_topics
        WHERE subject = 'gaeilge' AND language = 'ga'
        GROUP BY year, topic, topic_label_ga
        ORDER BY year, n DESC
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(topic_freq.head(50))
    return (topic_freq,)


@app.cell
def _(mo):
    # `irish_fada` asset_check badge (per spec Scenario "irish_fada check fails").
    mo.md(
        """
        > **irish_fada asset_check**: Verifies that all extracted
        > Irish-language strings preserve the fada diacritic (e.g.
        > `Máirt`, `Gaeilge`, `scríbhneoir`, `Cian`, `Áireamhán`).
        """
    )
    return


@app.cell
def _(con, mo):
    # 2. Cross-linguistic concept coverage (EN ↔ GA).
    cross_ling = mo.sql(
        f"""
        SELECT topic_label_en, topic_label_ga, level
        FROM oideachais.leaving_cert.gaeilge_topics
        WHERE subject = 'gaeilge' AND language = 'ga'
        ORDER BY level, topic_label_ga
        """,
        engine=con,
        output=False,
    )
    mo.ui.table(cross_ling.head(30))
    return (cross_ling,)


@app.cell
def _(con, mo):
    # 3. Litríocht / Úrsceal / Filíocht breakdown.
    genre = mo.sql(
        f"""
        SELECT
          CASE
            WHEN topic_label_ga ILIKE '%litríocht%' THEN 'Litríocht'
            WHEN topic_label_ga ILIKE '%úrsceal%' OR topic_label_ga ILIKE '%ursceal%' THEN 'Úrsceal'
            WHEN topic_label_ga ILIKE '%filíocht%' OR topic_label_ga ILIKE '%filiocht%' THEN 'Filíocht'
            ELSE 'Eile'
          END AS genre,
          count(*) AS n
        FROM oideachais.leaving_cert.gaeilge_topics
        WHERE subject = 'gaeilge' AND language = 'ga'
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
        FROM oideachais.leaving_cert.gaeilge_marking
        WHERE subject = 'gaeilge'
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
        ## Giniúint ceist (v2)

        `b.GenerateGaeilgeQuestPack` — 10 ceist ar an topaic, i nGaeilge.
        """
    )
    return


if __name__ == "__main__":
    app.run()
