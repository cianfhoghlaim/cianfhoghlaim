"""
Computer_Science LC Analysis — LC219.

Sparse subject — only 2 OL exam papers per language (LC219ALP038EV +
LC219ALP040EV) plus the specification PDF. Used to validate the
British-Isles Education pipeline on small-corpus subjects.

Lakehouse tables consumed:
  - oideachais.leaving_cert.computer_science_{syllabus,papers,marking,topics,diagrams}
  - oideachais.lc.computer_science.<level>_<language>

Pipeline stages: see 01_chemistry_analysis.py header.
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
            FROM oideachais.leaving_cert.computer_science_topics
            GROUP BY topic, level, language
            ORDER BY n DESC
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            "SELECT * FROM (VALUES ('no-data', 'OL', 'en', 0)) AS t(topic, level, language, n) WHERE FALSE"
        ).df()
    return con, topics_df


@app.cell
def _stage1_dlt_source(ROOT):
    """Run the real DLT source — yields 72 rows; filter by computer_science."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    subject_rows = [r for r in rows if r["subject"] == "computer_science"]
    return subject_rows


@app.cell
def _setup():
    import os
    import marimo as mo
    from pathlib import Path
    SUBJECT = "computer_science"
    SUBJECT_CODE = "LC219"
    ROOT = Path(os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    )) / SUBJECT
    pdfs_en = sorted(list((ROOT / "en").glob("*.pdf"))) if (ROOT / "en").exists() else []
    pdfs_ga = sorted(list((ROOT / "ga").glob("*.pdf"))) if (ROOT / "ga").exists() else []
    all_pdfs = pdfs_en + pdfs_ga
    mo.md(f"""
    # Computer Science LC Analysis (LC219)

    **Subject:** {SUBJECT} ({SUBJECT_CODE})
    **Total PDFs:** {len(all_pdfs)} ({len(pdfs_en)} en + {len(pdfs_ga)} ga)
    Note: This is a **sparse subject** (only 2 exam papers per language),
    so the pipeline validates the small-corpus path.

    Files discovered:
    {chr(10).join(f'- `{f.name}` ({f.stat().st_size / 1024:.1f} KB)' for f in all_pdfs)}
    """)
    return mo, all_pdfs, ROOT


@app.cell
def _lakehouse_topic_chart(topics_df):
    """Live lakehouse chart — replaces hardcoded sample lists."""
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
                title="oideachais.leaving_cert.computer_science_topics (live)",
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
            source_pdf="LC-Computer-Science-specification-updated.pdf",
            subject="computer_science", language="en", stage="LC_OL",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage2_papers():
    try:
        from cianfhoghlaim.baml_client import b
        return [
            b.ExtractExamPaperLayout(
                source_pdf=p, subject="computer_science",
                language="en", level="OL", year=2025,
            )
            for p in ["LC219ALP038EV.pdf", "LC219ALP040EV.pdf"]
        ]
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage5_cognify():
    try:
        import cognee
        return {"dataset": "oideachais_computer_science", "ok": True}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    app.run()
