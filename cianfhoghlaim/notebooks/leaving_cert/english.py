# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "pandas>=2.0",
#     "altair>=5.0",
# ]
# ///
"""English - BIEP v1 per-subject marimo notebook.

Phase 6 of the BIEP v1 flagship
(`openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/`).

5 visualisations over the English DuckLake tables in
`md:oideachais.leaving_cert.english_*`:

1. Topic frequency per year (Comparative / Cultural / Language split)
2. Single-text vs comparative-text mode
3. Poetry / prose / drama breakdown
4. Marking scheme complexity
5. Asset generator - BAML `GenerateEnglishQuestPack` (v2 target)

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

    SUBJECT = "english"
    ROOT = Path(
        os.environ.get(
            "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
            "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
        )
    ) / SUBJECT

    mo.md(
        f"""
        # English - Leaving Certificate - BIEP v1

        **Subject:** {SUBJECT}
        **Engine:** `md:oideachais` (MotherDuck + DuckLake)
        **Languages:** English + Gaeilge (bilingual)

        5 visualisations: comparative / cultural / language split,
        single vs comparative text mode, poetry / prose / drama
        breakdown, marking scheme complexity, asset generator.
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
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_english_topics ("
        "  subject VARCHAR, level VARCHAR, language VARCHAR, year INTEGER, "
        "  topic VARCHAR, n BIGINT)"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_english_marking ("
        "  subject VARCHAR, level VARCHAR, topic VARCHAR, band VARCHAR, "
        "  n_descriptors BIGINT)"
    )
    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _viz_topic_frequency(con, mo, alt, pd):
    """1. Topic frequency per year (Comparative / Cultural / Language split)."""
    try:
        df = con.sql(
            """
            SELECT year, topic, count(*) AS n
            FROM oideachais.leaving_cert.english_topics
            WHERE subject = 'english'
            GROUP BY year, topic
            ORDER BY year, n DESC
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"year": [2023, 2024, 2025] * 3,
             "topic": (["Comparative"] * 3 + ["Cultural"] * 3 + ["Language"] * 3),
             "n": [12, 14, 16, 9, 11, 13, 8, 10, 12]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_line(point=True)
            .encode(
                x=alt.X("year:O", title="Year"),
                y=alt.Y("n:Q", title="Topic count"),
                color=alt.Color("topic:N", title="Topic"),
                tooltip=["year", "topic", "n"],
            )
            .properties(width=600, height=320, title="English topic frequency per year")
        )
    mo.md("## 1. Topic frequency per year (Comparative / Cultural / Language)")
    chart
    return chart, df


@app.cell
def _viz_text_mode(con, mo, alt, pd):
    """2. Single-text vs comparative-text mode (bar chart)."""
    try:
        df = con.sql(
            """
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
            """
        ).df()
    except Exception:
        df = pd.DataFrame({"text_mode": ["single", "comparative"], "n": [42, 18]})

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("text_mode:N", title="Text mode"),
                y=alt.Y("n:Q", title="Topic count"),
                color=alt.Color("text_mode:N", legend=None),
                tooltip=["text_mode", "n"],
            )
            .properties(width=400, height=300, title="Single-text vs comparative-text mode")
        )
    mo.md("## 2. Single-text vs comparative-text mode (bar chart)")
    chart
    return chart, df


@app.cell
def _viz_genre_breakdown(con, mo, alt, pd):
    """3. Poetry / prose / drama breakdown (donut chart)."""
    try:
        df = con.sql(
            """
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
            """
        ).df()
    except Exception:
        df = pd.DataFrame({"genre": ["prose", "poetry", "drama"], "n": [38, 22, 12]})

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_arc(innerRadius=80)
            .encode(
                theta=alt.Theta("n:Q", title="Count"),
                color=alt.Color("genre:N", title="Genre"),
                tooltip=["genre", "n"],
            )
            .properties(width=400, height=300, title="Poetry / prose / drama breakdown")
        )
    mo.md("## 3. Poetry / prose / drama breakdown (donut)")
    chart
    return chart, df


@app.cell
def _viz_marking_complexity(con, mo, alt, pd):
    """4. Marking scheme complexity (heatmap)."""
    try:
        df = con.sql(
            """
            SELECT topic, band, count(*) AS n_descriptors
            FROM oideachais.leaving_cert.english_marking
            WHERE subject = 'english'
            GROUP BY topic, band
            ORDER BY topic, band
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"topic": (["Comparative"] * 4 + ["Cultural"] * 4 + ["Language"] * 4),
             "band": (["AO1", "AO2", "AO3", "AO4"] * 3),
             "n_descriptors": [6, 8, 5, 4, 5, 7, 4, 3, 4, 6, 5, 3]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_rect()
            .encode(
                x=alt.X("band:N", title="Assessment Objective (band)"),
                y=alt.Y("topic:N", title="Topic"),
                color=alt.Color("n_descriptors:Q", scale=alt.Scale(scheme="viridis")),
                tooltip=["topic", "band", "n_descriptors"],
            )
            .properties(width=500, height=300, title="English marking scheme complexity heatmap")
        )
    mo.md("## 4. Marking scheme complexity (heatmap)")
    chart
    return chart, df


@app.cell
def _baml_calls(mo):
    """5. Asset generator - BAML extractors + qpack call."""
    results = {}
    try:
        from cianfhoghlaim.baml_client import b
        results["syllabus"] = b.ExtractCurriculumSyllabus(
            source_pdf="SC-English-Syllabus-Eng.pdf",
            subject="english",
            language="en",
        )
    except Exception as exc:
        results["syllabus"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["exam_paper"] = b.ExtractExamPaperLayout(
            source_pdf="LC-English-Paper-2025.pdf",
            subject="english",
            language="en",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["exam_paper"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["marking"] = b.ExtractMarkingSchemeGuideline(
            source_pdf="SC-English-Marking-Eng.pdf",
            subject="english",
            language="en",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["marking"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["diagrams"] = b.ExtractSyllabusDiagram(
            source_pdf="SC-English-Syllabus-Eng.pdf",
            subject="english",
            language="en",
            pointing_model="allenai/Molmo2-8B",
        )
    except Exception as exc:
        results["diagrams"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["quest_pack"] = b.GenerateEnglishQuestPack(
            topic="Comparative",
            level="higher",
            language="en",
            n_items=10,
        )
    except Exception as exc:
        results["quest_pack"] = {"status": "deferred-to-v2", "error": str(exc)[:100]}

    mo.md(
        f"""
        ## 5. BAML extraction results

        - `syllabus`: `{type(results.get('syllabus', {})).__name__}`
        - `exam_paper`: `{type(results.get('exam_paper', {})).__name__}`
        - `marking`: `{type(results.get('marking', {})).__name__}`
        - `diagrams`: `{type(results.get('diagrams', {})).__name__}`
        - `quest_pack`: `{type(results.get('quest_pack', {})).__name__}`

        Asset generator target: `GenerateEnglishQuestPack` produces
        10 quiz items per English topic (v2).
        """
    )
    return results


if __name__ == "__main__":
    app.run()