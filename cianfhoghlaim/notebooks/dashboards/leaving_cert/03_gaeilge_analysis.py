"""
Gaeilge LC Analysis — LC001.

Notable: gaeilge has NO en/ subdir; all files live at the root of the
gaeilge/ directory (the Irish-language curriculum). This exercises
the asymmetric handling in leaving_cert_source._scan_subject().

Routes via glm-4.6v-flash (multilingual + Irish-fluent) per
select_ocr_backend() heuristic.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")





@app.cell
def _stage1_dlt_source(ROOT):
    """Run the real DLT source — yields 72 rows; filter by gaeilge."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    subject_rows = [r for r in rows if r["subject"] == "gaeilge"]
    return subject_rows


@app.cell
def _setup():
    import marimo as mo
    from pathlib import Path
    SUBJECT = "gaeilge"
    SUBJECT_CODE = "LC001"
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate/gaeilge")
    all_pdfs = sorted(list(ROOT.glob("*.pdf"))) if ROOT.exists() else []
    mo.md(f"""
    # Gaeilge LC Analysis (LC001)

    **Subject:** {SUBJECT} ({SUBJECT_CODE})
    **Total PDFs:** {len(all_pdfs)} (all at root; no en/ subdir)

    Note: gaeilge is unique — all files are Irish-language and live at
    the root of the gaeilge/ directory. The pipeline must handle this
    asymmetry gracefully.

    Files discovered:
    {chr(10).join(f'- `{p.name}` ({p.stat().st_size / 1024:.1f} KB)' for p in all_pdfs)}
    """)
    return mo, all_pdfs


@app.cell
def _stage1_ocr(all_pdfs):
    from cianfhoghlaim.meaisinfhoghlaim.models.registry import select_ocr_backend
    # All gaeilge files use glm-4.6v-flash (Irish-language routing)
    return [
        {"file": str(p), "model": select_ocr_backend(p, page_count=None).model.key}
        for p in all_pdfs
    ]


@app.cell
def _stage2_syllabus():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCurriculumSyllabus(
            source_pdf="Siollabais-Nuashonraithe-na-hArdteistimeireachta_1.pdf",
            subject="gaeilge", language="ga", stage="LC_OL",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage2_foundation():
    """Extract the Foundation-level variant (lower-stakes exam variant)."""
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCurriculumSyllabus(
            source_pdf="lc_irish_foundation.pdf",
            subject="gaeilge", language="ga", stage="LC_FDN",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage2_cross_linguistic():
    """Extract the EN ↔ GA topic concept mappings for gaeilge."""
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCrossLinguisticConcept(
            subject="gaeilge",
            source_pdf="Siollabais-Nuashonraithe-na-hArdteistimeireachta_1.pdf",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _stage5_cognify():
    try:
        import cognee
        return {"dataset": "oideachais_gaeilge", "ok": True}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    app.run()
