"""
Computer_Science LC Analysis — LC219.

Sparse subject — only 2 exam papers (LC219ALP038EV + LC219ALP040EV)
plus the specification PDF. Used to validate the pipeline on
small-corpus subjects.

Pipeline stages: see 01_chemistry_analysis.py header.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    from pathlib import Path
    SUBJECT = "computer_science"
    SUBJECT_CODE = "LC219"
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate/computer_science")
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
    return mo, all_pdfs


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
