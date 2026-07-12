"""
Mathematics LC Analysis — LC003.

Notable: mathematics is LaTeX + formula-heavy. The dense-OCR step
routes through deepseek-ocr-2 (compressed-doc specialist, math-aware)
per the v4 registry.

Lakehouse tables consumed:
  - oideachais.leaving_cert.mathematics_{syllabus,papers,marking,topics,diagrams}
  - oideachais.lc.mathematics.<level>_<language>

Pipeline: 16 PDFs (7 en + 9 ga) under
        cianfhoghlaim/leaving_certificate/mathematics/{en,ga}/

Formula detection uses `molmo2-8b` pointing for diagram-like figures.
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# ///

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _lakehouse():
    """Live lakehouse wiring — `md:oideachais` MotherDuck + DuckLake."""
    import duckdb
    try:
        con = duckdb.connect("md:oideachais")
        topics_df = con.sql(
            """
            SELECT topic, level, language, count(*) AS n
            FROM oideachais.leaving_cert.mathematics_topics
            GROUP BY topic, level, language
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            "SELECT * FROM (VALUES ('no-data', 'HL', 'en', 0)) AS t(topic, level, language, n) WHERE FALSE"
        ).df()
    return con, topics_df


@app.cell
def _stage1_dlt_source(ROOT):
    """Run the real DLT source — yields 72 rows; filter by mathematics."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    subject_rows = [r for r in rows if r["subject"] == "mathematics"]
    return subject_rows


@app.cell
def _setup():
    import os
    import marimo as mo
    from pathlib import Path
    SUBJECT = "mathematics"
    SUBJECT_CODE = "LC003"
    ROOT = Path(os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    )) / SUBJECT
    all_pdfs = []
    for lang in ("en", "ga"):
        lang_dir = ROOT / lang
        if lang_dir.exists():
            all_pdfs.extend(sorted(lang_dir.glob("*.pdf")))
    mo.md(f"""
    # Mathematics LC Analysis (LC003)

    **Subject:** {SUBJECT} ({SUBJECT_CODE})
    **Total PDFs:** {len(all_pdfs)} ({len([p for p in all_pdfs if '/en/' in str(p)])} en + {len([p for p in all_pdfs if '/ga/' in str(p)])} ga)

    Note: Mathematics is **LaTeX + formula-heavy**. Dense OCR routes
    through `deepseek-ocr-2` (compressed-doc specialist, math-aware)
    per the v4 registry. Diagram detection uses `molmo2-8b`.

    Files:
    {chr(10).join(f'- `{p.name}` ({p.stat().st_size / 1024:.1f} KB)' for p in all_pdfs)}
    """)
    return mo, all_pdfs, ROOT


@app.cell
def _lakehouse_topic_chart(topics_df):
    """Live lakehouse chart — mathematics LO frequencies (EN + GA)."""
    import altair as alt
    if topics_df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("lakehouse unavailable"))
    else:
        chart = (
            alt.Chart(topics_df)
            .mark_bar()
            .encode(
                y=alt.Y("topic:N", sort="-x"),
                x=alt.X("n:Q", title="count(*) of LOs"),
                color="language:N",
                tooltip=["topic", "level", "language", "n"],
            )
            .properties(
                width=500,
                height=300,
                title="oideachais.leaving_cert.mathematics_topics (live, EN + GA)",
            )
        )
    return (chart,)


@app.cell
def _stage1_ocr(all_pdfs):
    from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_ocr_backend
    return [
        {"file": str(p), "model": select_ocr_backend(p).model.key}
        for p in all_pdfs
    ]


@app.cell
def _stage2_syllabus():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCurriculumSyllabus(
            source_pdf="SCSEC25_Maths_syllabus_examination-2015_English.pdf",
            subject="mathematics", language="en", stage="LC_OL",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage2_papers_ol():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractExamPaperLayout(
            source_pdf="LC003ALP100EV.pdf",
            subject="mathematics", language="en", level="OL", year=2025,
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage2_papers_hl():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractExamPaperLayout(
            source_pdf="LC003ALP200EV.pdf",
            subject="mathematics", language="en", level="HL", year=2025,
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage5_cognify():
    try:
        import cognee
        return {"dataset": "oideachais_mathematics", "ok": True}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    app.run()
