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
"""Geography — BIEP v1 per-subject marimo notebook.

Phase 6 of the BIEP v1 flagship
(`openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/`).

5 visualisations over the Geography DuckLake tables in
``md:oideachais.leaving_cert.geography_*``:

1. Topic frequency per year (Physical / Regional / Economic split)
2. Fieldwork requirement coverage
3. Cross-subject competency mapping (LanceDB
   `oideachais.lc.cross_subject.competencies` via lance_scan)
4. Marking scheme complexity (heatmap)
5. Asset generator — BAML ``GenerateGeogQuestPack`` (canonical qpack signature)

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

    SUBJECT = "geography"
    ROOT = Path(
        os.environ.get(
            "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
            "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
        )
    ) / SUBJECT

    mo.md(
        f"""
        # Geography — Leaving Certificate — BIEP v1

        **Subject:** {SUBJECT}
        **Engine:** `md:oideachais` (MotherDuck + DuckLake)
        **Languages:** English + Gaeilge (bilingual)

        5 visualisations: physical / regional / economic topic split,
        fieldwork coverage, cross-subject competency mapping (LanceDB),
        marking scheme complexity, asset generator.
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
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_geography_topics ("
        "  subject VARCHAR, level VARCHAR, language VARCHAR, year INTEGER, "
        "  topic VARCHAR, n BIGINT"
        ")"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_geography_syllabus ("
        "  subject VARCHAR, level VARCHAR, language VARCHAR, module_topics JSON"
        ")"
    )
    con.execute(
        "CREATE TABLE IF NOT EXISTS oideachais_leaving_cert_geography_marking ("
        "  subject VARCHAR, level VARCHAR, topic VARCHAR, band VARCHAR, "
        "  n_descriptors BIGINT"
        ")"
    )
    mo.md(f"### Engine: **{engine_label}**")
    return con, engine_label


@app.cell
def _viz_topic_frequency(con, mo, alt, pd):
    """1. Topic frequency per year (Physical / Regional / Economic split)."""
    try:
        df = con.sql(
            """
            SELECT year, topic, count(*) AS n
            FROM oideachais.leaving_cert.geography_topics
            WHERE subject = 'geography'
            GROUP BY year, topic
            ORDER BY year, n DESC
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {
                "year": [2023, 2024, 2025] * 3,
                "topic": (["Physical Geography"] * 3 +
                          ["Regional Geography"] * 3 +
                          ["Economic Geography"] * 3),
                "n": [13, 15, 17, 9, 11, 13, 8, 10, 12],
            }
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
            .properties(width=600, height=320, title="Geography topic frequency per year")
        )
    mo.md("## 1. Topic frequency per year (Physical / Regional / Economic)")
    chart
    return chart, df


@app.cell
def _viz_fieldwork(con, mo, alt, pd):
    """2. Fieldwork requirement coverage (bar chart by estimated hours)."""
    try:
        df = con.sql(
            """
            SELECT
                json_extract_string(m, '$.name_en') AS module_name,
                json_extract_string(m, '$.type') AS type,
                CAST(json_extract_string(m, '$.estimated_hours') AS INTEGER) AS estimated_hours
            FROM oideachais.leaving_cert.geography_syllabus s,
                 json_each(s.module_topics) AS m
            WHERE s.subject = 'geography'
              AND (json_extract_string(m, '$.name_en') ILIKE '%fieldwork%'
                   OR json_extract_string(m, '$.name_en') ILIKE '%field work%')
            ORDER BY estimated_hours DESC
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"module_name": ["River Fieldwork", "Coastal Fieldwork",
                             "Urban Fieldwork", "Glacial Fieldwork",
                             "Climate Fieldwork"],
             "type": ["physical", "physical", "regional", "physical", "physical"],
             "estimated_hours": [12, 10, 8, 9, 7]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_bar()
            .encode(
                x=alt.X("module_name:N", title="Fieldwork module", sort="-y"),
                y=alt.Y("estimated_hours:Q", title="Estimated hours"),
                color=alt.Color("type:N", title="Type"),
                tooltip=["module_name", "type", "estimated_hours"],
            )
            .properties(width=600, height=300, title="Geography fieldwork requirement coverage")
        )
    mo.md("## 2. Fieldwork requirement coverage (bar chart)")
    chart
    return chart, df


@app.cell
def _viz_cross_subject(con, mo, alt, pd):
    """3. Cross-subject competency mapping (LanceDB via lance_scan)."""
    try:
        df = con.sql(
            """
            SELECT competency, level, language, count(*) AS n
            FROM lance_scan('oideachais.lc.cross_subject.competencies')
            WHERE subject = 'geography'
            GROUP BY competency, level, language
            ORDER BY competency, level
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"competency": ["Climate Analysis", "Population Studies",
                            "Urban Planning", "Economic Indicators",
                            "Sustainability"],
             "level": ["higher", "higher", "ordinary", "higher", "ordinary"],
             "language": ["en", "en", "en", "ga", "en"],
             "n": [12, 10, 8, 6, 9]}
        )

    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("no data"))
    else:
        chart = (
            alt.Chart(df)
            .mark_circle(size=250)
            .encode(
                x=alt.X("competency:N", title="Cross-subject competency"),
                y=alt.Y("level:N", title="Level"),
                color=alt.Color("language:N", title="Language"),
                size=alt.Size("n:Q", title="Coverage count"),
                tooltip=["competency", "level", "language", "n"],
            )
            .properties(width=600, height=250, title="Cross-subject competency mapping (LanceDB)")
        )
    mo.md("## 3. Cross-subject competency mapping (LanceDB `oideachais.lc.cross_subject.competencies`)")
    chart
    return chart, df


@app.cell
def _viz_marking_complexity(con, mo, alt, pd):
    """4. Marking scheme complexity (heatmap)."""
    try:
        df = con.sql(
            """
            SELECT topic, band, count(*) AS n_descriptors
            FROM oideachais.leaving_cert.geography_marking
            WHERE subject = 'geography'
            GROUP BY topic, band
            ORDER BY topic, band
            """
        ).df()
    except Exception:
        df = pd.DataFrame(
            {"topic": (["Physical Geography"] * 4 +
                       ["Regional Geography"] * 4 +
                       ["Economic Geography"] * 4),
             "band": (["AO1", "AO2", "AO3", "AO4"] * 3),
             "n_descriptors": [5, 8, 6, 3, 4, 6, 5, 2, 4, 7, 5, 3]}
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
            .properties(width=500, height=300, title="Geography marking scheme complexity heatmap")
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
        Geography corpus:

        - `ExtractCurriculumSyllabus` — Geography syllabus PDF → typed record
        - `ExtractExamPaperLayout` — Geography exam paper → typed record
        - `ExtractMarkingSchemeGuideline` — Geography marking scheme → typed record
        - `ExtractSyllabusDiagram` — Geography syllabus diagram extraction

        Plus the asset generator `GenerateGeogQuestPack` using the
        canonical `(syllabus, past_papers, marking_schemes, level)`
        qpack signature.
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
            source_pdf="SC-Geography-Syllabus-Eng.pdf",
            subject="geography",
            language="en",
        )
    except Exception as exc:
        results["syllabus"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["exam_paper"] = b.ExtractExamPaperLayout(
            source_pdf="LC-Geography-Paper-2025.pdf",
            subject="geography",
            language="en",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["exam_paper"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["marking"] = b.ExtractMarkingSchemeGuideline(
            source_pdf="SC-Geography-Marking-Eng.pdf",
            subject="geography",
            language="en",
            level="higher",
            year=2025,
        )
    except Exception as exc:
        results["marking"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client import b
        results["diagrams"] = b.ExtractSyllabusDiagram(
            source_pdf="SC-Geography-Syllabus-Eng.pdf",
            subject="geography",
            language="en",
            pointing_model="allenai/Molmo2-8B",
        )
    except Exception as exc:
        results["diagrams"] = {"status": "offline", "error": str(exc)[:100]}

    try:
        from cianfhoghlaim.baml_client.baml_client import types
        from cianfhoghlaim.baml_client.baml_client.sync_client import b

        syllabus = types.LeavingCertSyllabus(
            subject="Geography",
            year=2025,
            level="Higher",
            topics=[
                types.SyllabusTopic(
                    topicId="LC-GEOG-PHYSICAL",
                    name="Physical Geography",
                    description="Physical geography processes and landform development for Leaving Certificate Geography.",
                    learningOutcomes=["LC-GEOG-LO-2.3: Explain physical processes with evidence and diagrams."],
                    weightPct=25,
                )
            ],
        )
        results["quest_pack"] = b.GenerateGeogQuestPack(
            syllabus=syllabus,
            past_papers=[],
            marking_schemes=[],
            level="higher",
        )
    except Exception as exc:
        results["quest_pack"] = {"status": "error", "error": str(exc)[:100]}

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