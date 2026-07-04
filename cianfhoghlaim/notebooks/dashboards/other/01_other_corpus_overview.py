"""
Gemini Other Corpus Overview — 12 PDFs.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    from pathlib import Path
    CORPUS = "other"
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/other")
    pdfs = sorted(ROOT.glob("*.pdf")) if ROOT.exists() else []
    mo.md(f"""
    # Gemini Other Corpus Overview

    **Path:** `leabharlann/gemini_deep_research/other/`
    **Total PDFs:** {len(pdfs)}
    **Approx size:** 4.1 MB
    """)
    return mo, pdfs


@app.cell
def _stage2_classify():
    from pathlib import Path
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/other")
    pdfs = list(ROOT.glob("*.pdf"))
    cats = {}
    for p in pdfs:
        n = p.name.lower()
        c = "OTHER"
        cats[c] = cats.get(c, 0) + 1
    return cats


if __name__ == "__main__":
    app.run()
