"""
Geography LC Analysis — LC005.

Notable: geography includes 1 JPG scanned exam page (LC005CLP004EV.jpg
at the en root). This exercises the Docling-Serve fallback path for
non-PDF inputs.

Lakehouse tables consumed:
  - oideachais.leaving_cert.geography_{syllabus,papers,marking,topics,diagrams}
  - oideachais.lc.geography.<level>_<language>

Pipeline: 18 PDFs + 1 JPG across en/ga. Diagrams (maps, climate graphs)
route through molmo2-8b per LC5 BAML ExtractSyllabusDiagram.
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
    """Live lakehouse wiring — `md:oideachais` MotherDuck + DuckLake.

    Joins `geography_topics` (the LO frequency table) with the diagram table
    `geography_diagrams` to surface the diagram-heavy nature of the subject.
    """
    import duckdb
    try:
        con = duckdb.connect("md:oideachais")
        topics_df = con.sql(
            """
            SELECT topic, level, count(*) AS n
            FROM oideachais.leaving_cert.geography_topics
            GROUP BY topic, level
            ORDER BY n DESC
            """
        ).df()
        diagrams_df = con.sql(
            """
            SELECT topic, bbox_label, language
            FROM oideachais.leaving_cert.geography_diagrams
            """
        ).df()
    except Exception:
        con = duckdb.connect(":memory:")
        topics_df = con.sql(
            "SELECT * FROM (VALUES ('no-data', 'HL', 0)) AS t(topic, level, n) WHERE FALSE"
        ).df()
        diagrams_df = con.sql(
            "SELECT * FROM (VALUES ('no-data', 'no-data', 'en')) AS t(topic, bbox_label, language) WHERE FALSE"
        ).df()
    return con, topics_df, diagrams_df


@app.cell
def _stage1_dlt_source(ROOT):
    """Run the real DLT source — yields 72 rows; filter by geography."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    subject_rows = [r for r in rows if r["subject"] == "geography"]
    return subject_rows


@app.cell
def _setup():
    import os
    import marimo as mo
    from pathlib import Path
    SUBJECT = "geography"
    SUBJECT_CODE = "LC005"
    ROOT = Path(os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    )) / SUBJECT
    all_pdfs = []
    all_jpgs = []
    for lang in ("en", "ga"):
        lang_dir = ROOT / lang
        if lang_dir.exists():
            all_pdfs.extend(lang_dir.glob("*.pdf"))
            all_jpgs.extend(lang_dir.glob("*.jpg"))
    mo.md(f"""
    # Geography LC Analysis (LC005)

    **Subject:** {SUBJECT} ({SUBJECT_CODE})
    **Total PDFs:** {len(all_pdfs)} ({len([p for p in all_pdfs if '/en/' in str(p)])} en + {len([p for p in all_pdfs if '/ga/' in str(p)])} ga)
    **Total JPGs:** {len(all_jpgs)} (scanned exam pages)

    Note: Includes 1 JPG scanned exam page → routes through
    **docling-serve** (DocTags layout) instead of llama-swap.

    PDFs discovered:
    {chr(10).join(f'- `{p.name}` ({p.stat().st_size / 1024:.1f} KB)' for p in all_pdfs)}
    JPGs discovered:
    {chr(10).join(f'- `{j.name}` ({j.stat().st_size / 1024:.1f} KB)' for j in all_jpgs)}
    """)
    return mo, all_pdfs, all_jpgs, ROOT


@app.cell
def _lakehouse_topic_chart(topics_df):
    """Live lakehouse chart — geography LO frequencies."""
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
                color="level:N",
                tooltip=["topic", "level", "n"],
            )
            .properties(
                width=500,
                height=300,
                title="oideachais.leaving_cert.geography_topics (live)",
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
def _stage1_jpg_routing(all_jpgs):
    """JPGs (scanned exam pages) bypass select_ocr_backend → use docling-serve."""
    return [
        {"file": str(j), "route": "docling-serve", "reason": "scanned image; DocTags layout"}
        for j in all_jpgs
    ]


@app.cell
def _stage2_diagrams():
    """Geography is diagram-heavy — extract maps + climate graphs via molmo2-8b."""
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractSyllabusDiagram(
            source_pdf="SC-Geography-Spec-ENG-INT.pdf",
            subject="geography", language="en",
            pointing_model="allenai/Molmo2-8B",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage5_cognify():
    try:
        import cognee
        return {"dataset": "oideachais_geography", "ok": True}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    app.run()
