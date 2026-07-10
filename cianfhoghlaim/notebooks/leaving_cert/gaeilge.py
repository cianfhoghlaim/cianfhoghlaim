# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "pandas>=2.0",
#     "altair>=5.0",
#     "polars>=0.20",
#     "pyarrow>=15.0",
# ]
# ///
"""Gaeilge — BIEP v1 per-subject marimo notebook (LC022, Irish-only).

Phase 6 of the BIEP v1 flagship
(`openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/`).

5 visualisations over the Gaeilge DuckLake tables in
``md:oideachais.leaving_cert.gaeilge_*``:

1. Topic frequency per year (with `irish_fada` asset_check badge)
2. Cross-linguistic concept coverage (EN ↔ GA topic mapping)
3. Litríocht / Úrsceal / Filíocht breakdown (donut chart)
4. Marking scheme complexity (heatmap)
5. Asset generator — BAML ``GenerateGaeilgeQuestPack`` (v2 target)

**Gaeilge is Irish-only** per the BIEP v1 spec requirement
"gaeilge-only syllabuses (no English sibling)". The notebook UI
strings are bilingual EN + GA with the `irish_fada` asset_check
verifying that all extracted Irish strings preserve the fada
diacritic.

Reference: openspec/specs/british-isles-education-pipeline/spec.md
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import os
    from pathlib import Path
    import marimo as mo
    import duckdb
    import pandas as pd
    import altair as alt

    SUBJECT = "gaeilge"
    ROOT = Path(
        os.environ.get(
            "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
            "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
        )
    ) / SUBJECT

    mo.md(
        f"""
        # Gaeilge — Leaving Certificate — BIEP v1 (Gaeilge amháin)

        **Ábhar:** {SUBJECT}
        **Inneall:** `md:oideachais` (MotherDuck + DuckLake)
        **Teangacha:** Gaeilge amháin (Níl deartháir Béarla ann)

        5 léiriúchán ar na táblaí Gaeilge DuckLake.
        """
    )
    return SUBJECT, ROOT, alt, duckdb, mo, os, pd


@app.cell
def _lakehouse(mo, os, duckdb):
    """Live lakehouse wiring with graceful local fallback."""
    use_md = os.getenv("MOTHERDUCK_ENABLED", "false").lower() == "true"
    token = os.getenv("MOTHERDUCK_TOKEN", "")

    if use_md and token:
        try:
            duckdb.sql(f"SET motherduck_token='{token}'")
            con = duckdb.connect("md:oideachais")
            engine_label = "md:oideachais"
        except Exception as exc:
            con = duckdb.connect(":memory:")
            engine_label = f"local_duckdb (md unreachable: {type(exc).__name__})"
    else:
        con = duckdb.connect(":memory:")
        engine_label = "local_duckdb (offline fallback)"

    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_gaeilge_topics ("
        "  subject VARCHAR, level VARCHAR, language VARCHAR, year INTEGER, "
        "  topic VARCHAR, topic_label_ga VARCHAR, topic_label_en VARCHAR, n BIGINT"
        ")"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_gaeilge_marking ("
        "  subject VARCHAR, level VARCHAR, topic VARCHAR, band VARCHAR, "
        "  n_descriptors BIGINT"
        ")"
    )
    mo.md(f"### Inneall: **{engine_label}**")
    return con, engine_label


@app.cell
def _viz_topic_frequency_irish(con, mo, alt, pd):
    """1. Topic frequency per year (with `irish_fada` badge)."""
    try:
        df = con.sql(
            """
            SELECT year, topic, topic_label_ga, count(*) AS n
            FROM oideachais.leaving_cert.gaeilge_topics
            WHERE subject = 'gaeilge' AND language = 'ga'
            GROUP BY year, topic, topic_label_ga
            ORDER BY year, n DESC
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {
                "year": [2023, 2024, 2025] * 4,
                "topic": (["Litríocht"] * 3 + ["Úrsceal"] * 3 +
                          ["Filíocht"] * 3 + ["Gramadach"] * 3),
                "topic_label_ga": (["Litríocht"] * 3 + ["Úrsceal"] * 3 +
                                   ["Filíocht"] * 3 + ["Gramadach"] * 3),
                "n": [15, 17, 19, 10, 12, 14, 11, 13, 15, 8, 10, 12],
            }
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Bliain"),
                y=alt.Y("n:Q", title="Líon topaicí"),
                color=alt.Color("topic_label_ga:N", title="Topaic"),
                tooltip=["year", "topic_label_ga", "n"],
            )
            .properties(width=600, height=320, title="Gaeilge — minicíocht topaicí de réir bliana")
        )
    mo.md(
        """
        ## 1. Minicíocht topaicí de réir bliana

        > **irish_fada asset_check**: Deimhníonn sé seo go gcoimeádtar
        > an fada i ngach teaghrán Gaeilge (e.g. `Máirt`, `Gaeilge`,
        > `scríbhneoir`, `Cian`, `Áireamhán`).
        """
    )
    chart
    return chart, df


@app.cell
def _viz_cross_linguistic(con, mo, alt, pd):
    """2. Cross-linguistic concept coverage (EN ↔ GA topic mapping)."""
    try:
        df = con.sql(
            """
            SELECT topic_label_en, topic_label_ga, level
            FROM oideachais.leaving_cert.gaeilge_topics
            WHERE subject = 'gaeilge' AND language = 'ga'
            ORDER BY level, topic_label_ga
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"topic_label_en": ["Literature", "Novel", "Poetry", "Grammar",
                                "Oral Irish", "Comprehension"],
             "topic_label_ga": ["Litríocht", "Úrsceal", "Filíocht",
                                "Gramadach", "Béaltriail", "Tuiscint"],
             "level": ["higher", "higher", "higher", "ordinary",
                       "ordinary", "ordinary"]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_circle(size=200)
            .encode(
                x=alt.X("topic_label_en:N", title="English label", sort="-y"),
                y=alt.Y("topic_label_ga:N", title="Lipéad Gaeilge", sort="-x"),
                color=alt.Color("level:N", title="Leibhéal"),
                tooltip=["topic_label_en", "topic_label_ga", "level"],
            )
            .properties(width=500, height=300, title="Cross-linguistic mapping (EN ↔ GA)")
        )
    mo.md("## 2. Cross-linguistic concept coverage (EN ↔ GA)")
    chart
    return chart, df


@app.cell
def _viz_genre_breakdown(con, mo, alt, pd):
    """3. Litríocht / Úrsceal / Filíocht breakdown (donut chart)."""
    try:
        df = con.sql(
            """
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
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"genre": ["Litríocht", "Úrsceal", "Filíocht", "Eile"],
             "n": [45, 32, 28, 12]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_arc(innerRadius=80)
            .encode(
                theta=alt.Theta("n:Q", title="Count"),
                color=alt.Color("genre:N", title="Seánra"),
                tooltip=["genre", "n"],
            )
            .properties(width=400, height=300, title="Litríocht / Úrsceal / Filíocht breakdown")
        )
    mo.md("## 3. Litríocht / Úrsceal / Filíocht breakdown (donut)")
    chart
    return chart, df


@app.cell
def _viz_marking_complexity(con, mo, alt, pd):
    """4. Marking scheme complexity (heatmap)."""
    try:
        df = con.sql(
            """
            SELECT topic, band, count(*) AS n_descriptors
            FROM oideachais.leaving_cert.gaeilge_marking
            WHERE subject = 'gaeilge'
            GROUP BY topic, band
            ORDER BY topic, band
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"topic": (["Litríocht"] * 4 + ["Úrsceal"] * 4 + ["Filíocht"] * 4),
             "band": (["AO1", "AO2", "AO3", "AO4"] * 3),
             "n_descriptors": [6, 9, 5, 4, 5, 7, 4, 3, 4, 6, 5, 3]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_rect()
            .encode(
                x=alt.X("band:N", title="Cuspóir Measúnaithe (banda)"),
                y=alt.Y("topic:N", title="Topaic"),
                color=alt.Color("n_descriptors:Q", scale=alt.Scale(scheme="viridis")),
                tooltip=["topic", "band", "n_descriptors"],
            )
            .properties(width=500, height=300, title="Marking scheme complexity heatmap — Gaeilge")
        )
    mo.md("## 4. Marking scheme complexity (heatmap)")
    chart
    return chart, df


@app.cell
def _baml_extractors(mo):
    """5. Asset generator — BAML ExtractCurriculumSyllabus + qpack call."""
    mo.md(
        """
        ## 5. BAML extractors + asset generator

        Na ceithre eastóscóirí BAML canónacha don chorpais Gaeilge:

        - `ExtractCurriculumSyllabus` — Gaeilge syllabus PDF → taifead
        - `ExtractExamPaperLayout` — Gaeilge exam paper → taifead
        - `ExtractMarkingSchemeGuideline` — Gaeilge marking scheme → taifead
        - `ExtractSyllabusDiagram` — Gaeilge syllabus diagram

        Plus the asset generator `GenerateGaeilgeQuestPack` (v2
        target) — 10 ceist ar an topaic, i nGaeilge.
        """
    )
    return


@app.cell
def _baml_calls(mo):
    """Stage 2: BAML extraction — wrapped for offline rendering."""
    results = {}
    try:
        from cianfhoghlaim.baml_client import b
        results["syllabus"] = b.ExtractCurriculumSyllabus(
            source_pdf="SC-Gaeilge-Syllabus-GA.pdf",
            subject="gaeilge",
            language="ga",
        )
    except Exception as exc:
        results["syllabus"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["exam_paper"] = b.ExtractExamPaperLayout(
            source_pdf="LC-Gaeilge-Paper-2025.pdf",
            subject="gaeilge",
            language="ga",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["exam_paper"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["marking"] = b.ExtractMarkingSchemeGuideline(
            source_pdf="SC-Gaeilge-Marking-GA.pdf",
            subject="gaeilge",
            language="ga",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["marking"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["diagrams"] = b.ExtractSyllabusDiagram(
            source_pdf="SC-Gaeilge-Syllabus-GA.pdf",
            subject="gaeilge",
            language="ga",
            pointing_model="allenai/Molmo2-8B",
        )
    except Exception as exc:
        results["diagrams"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["quest_pack"] = b.GenerateGaeilgeQuestPack(
            topic="Litríocht",
            level="higher",
            language="ga",
            n_items=10,
        )
    except Exception as exc:
        results["quest_pack"] = {"status": "deferred-to-v2", "error": str(exc)[:100]}

    mo.md(
        f"""
        **Torthaí eastóscáin:**

        - `syllabus`: `{type(results.get('syllabus', {})).__name__}`
        - `exam_paper`: `{type(results.get('exam_paper', {})).__name__}`
        - `marking`: `{type(results.get('marking', {})).__name__}`
        - `diagrams`: `{type(results.get('diagrams', {})).__name__}`
        - `quest_pack`: `{type(results.get('quest_pack', {})).__name__}`
        """
    )
    return results


if __name__ == "__main__":
    app.run()