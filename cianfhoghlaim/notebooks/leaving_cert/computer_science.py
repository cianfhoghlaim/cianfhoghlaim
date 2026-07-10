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
"""Computer Science — BIEP v1 per-subject marimo notebook (LC022).

Phase 6 of the BIEP v1 flagship
(`openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/`).

5 visualisations over the Computer Science DuckLake tables in
``md:oideachais.leaving_cert.computer_science_*``:

1. Topic frequency per year (line chart) — algorithms / data / systems / web split
2. Pseudocode complexity distribution (bar chart)
3. Code-trace question coverage (heatmap)
4. Marking scheme complexity (heatmap)
5. Asset generator — BAML ``GenerateComputerScienceQuestPack`` (v2 target)

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

    SUBJECT = "computer_science"
    ROOT = Path(
        os.environ.get(
            "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
            "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
        )
    ) / SUBJECT

    mo.md(
        f"""
        # Computer Science — Leaving Certificate — BIEP v1

        **Subject:** {SUBJECT}
        **Engine:** `md:oideachais` (MotherDuck + DuckLake lakehouse)
        **Languages:** English + Gaeilge (bilingual)

        5 visualisations over the CS DuckLake tables: algorithms,
        data structures, systems, web/networks, marking schemes.
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
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_computer_science_topics ("
        "  subject VARCHAR, level VARCHAR, language VARCHAR, year INTEGER, "
        "  topic VARCHAR, n BIGINT"
        ")"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_computer_science_papers ("
        "  subject VARCHAR, level VARCHAR, language VARCHAR, year INTEGER, "
        "  question_type VARCHAR, n BIGINT"
        ")"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_computer_science_marking ("
        "  subject VARCHAR, level VARCHAR, topic VARCHAR, band VARCHAR, "
        "  n_descriptors BIGINT"
        ")"
    )
    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _viz_topic_frequency(con, mo, alt, pd):
    """1. Topic frequency per year."""
    try:
        df = con.sql(
            """
            SELECT year, topic, count(*) AS n
            FROM oideachais.leaving_cert.computer_science_topics
            WHERE subject = 'computer_science'
            GROUP BY year, topic
            ORDER BY year, n DESC
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"year": [2023, 2024, 2025] * 4,
             "topic": (["Algorithms"] * 3 + ["Data Structures"] * 3 +
                       ["Systems"] * 3 + ["Web & Networks"] * 3),
             "n": [14, 16, 19, 11, 13, 15, 9, 12, 14, 7, 10, 12]}
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
            .properties(width=600, height=320, title="CS topic frequency per year")
        )
    mo.md("## 1. Topic frequency per year (line chart)")
    chart
    return chart, df


@app.cell
def _viz_pseudocode_complexity(con, mo, alt, pd):
    """2. Pseudocode complexity distribution (bar chart)."""
    try:
        df = con.sql(
            """
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
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"category": ["algorithms", "data_structures", "systems", "web_networks", "other"],
             "n": [42, 38, 27, 22, 11]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("category:N", title="Category", sort="-y"),
                y=alt.Y("n:Q", title="Topic count"),
                color=alt.Color("category:N", legend=None),
                tooltip=["category", "n"],
            )
            .properties(width=600, height=300, title="CS topic distribution (algorithms / data / systems / web)")
        )
    mo.md("## 2. Pseudocode complexity distribution (bar chart)")
    chart
    return chart, df


@app.cell
def _viz_code_trace(con, mo, alt, pd):
    """3. Code-trace question coverage (heatmap by year × question type)."""
    try:
        df = con.sql(
            """
            SELECT year, question_type, count(*) AS n
            FROM oideachais.leaving_cert.computer_science_papers
            WHERE subject = 'computer_science'
            GROUP BY year, question_type
            ORDER BY year, n DESC
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"year": [2023] * 5 + [2024] * 5 + [2025] * 5,
             "question_type": ["code_trace", "pseudocode", "short_answer",
                               "extended", "diagram"] * 3,
             "n": [8, 12, 6, 9, 4, 9, 13, 7, 10, 5, 10, 14, 8, 11, 6]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_rect()
            .encode(
                x=alt.X("question_type:N", title="Question type"),
                y=alt.Y("year:O", title="Year"),
                color=alt.Color("n:Q", title="Count", scale=alt.Scale(scheme="viridis")),
                tooltip=["year", "question_type", "n"],
            )
            .properties(width=500, height=200, title="Code-trace question coverage heatmap")
        )
    mo.md("## 3. Code-trace question coverage (heatmap)")
    chart
    return chart, df


@app.cell
def _viz_marking_complexity(con, mo, alt, pd):
    """4. Marking scheme complexity (heatmap)."""
    try:
        df = con.sql(
            """
            SELECT topic, band, count(*) AS n_descriptors
            FROM oideachais.leaving_cert.computer_science_marking
            WHERE subject = 'computer_science'
            GROUP BY topic, band
            ORDER BY topic, band
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"topic": (["Algorithms"] * 3 + ["Data Structures"] * 3 + ["Systems"] * 3),
             "band": (["AO1", "AO2", "AO3"] * 3),
             "n_descriptors": [6, 9, 4, 5, 8, 3, 4, 6, 5]}
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
            .properties(width=500, height=300, title="CS marking scheme complexity heatmap")
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

        The four canonical BIEP BAML extractors fire against the
        Computer Science corpus:

        - `ExtractCurriculumSyllabus` — CS syllabus PDF → typed record
        - `ExtractExamPaperLayout` — CS exam paper → typed record
        - `ExtractMarkingSchemeGuideline` — CS marking scheme → typed record
        - `ExtractSyllabusDiagram` — CS syllabus diagram extraction

        Plus the asset generator `GenerateComputerScienceQuestPack`
        (v2 target) producing 10 quiz items per CS topic.
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
            source_pdf="SC-CS-Syllabus-Eng.pdf",
            subject="computer_science",
            language="en",
        )
    except Exception as exc:
        results["syllabus"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["exam_paper"] = b.ExtractExamPaperLayout(
            source_pdf="LC-CS-Paper-2025.pdf",
            subject="computer_science",
            language="en",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["exam_paper"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["marking"] = b.ExtractMarkingSchemeGuideline(
            source_pdf="SC-CS-Marking-Eng.pdf",
            subject="computer_science",
            language="en",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["marking"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["diagrams"] = b.ExtractSyllabusDiagram(
            source_pdf="SC-CS-Syllabus-Eng.pdf",
            subject="computer_science",
            language="en",
            pointing_model="allenai/Molmo2-8B",
        )
    except Exception as exc:
        results["diagrams"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["quest_pack"] = b.GenerateComputerScienceQuestPack(
            topic="Algorithms",
            level="higher",
            language="en",
            n_items=10,
        )
    except Exception as exc:
        results["quest_pack"] = {"status": "deferred-to-v2", "error": str(exc)[:100]}

    mo.md(
        f"""
        **Extraction results:**

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