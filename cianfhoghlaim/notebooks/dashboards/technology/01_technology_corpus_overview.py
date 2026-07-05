"""
Gemini Technology Corpus Overview — 24 PDFs.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")





@app.cell
def _stage1_dlt_gemini(ROOT):
    """Run the real DLT source — 224 rows; filter by corpus."""
    import sys
    sys.path.insert(0, str(ROOT.parent))
    from cianfhoghlaim.dlt.filesystem.gemini_corpus_source import gemini_documents
    rows = list(gemini_documents(root_path=str(ROOT.parent)))
    return rows


@app.cell
def _setup():
    import marimo as mo
    from pathlib import Path
    CORPUS = "technology"
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/technology")
    pdfs = sorted(ROOT.glob("*.pdf")) if ROOT.exists() else []
    mo.md(f"""
    # Gemini Technology Corpus Overview

    **Path:** `leabharlann/gemini_deep_research/technology/`
    **Total PDFs:** {len(pdfs)}
    **Approx size:** 8.2 MB
    """)
    return mo, pdfs


@app.cell
def _stage2_classify():
    from pathlib import Path
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/technology")
    pdfs = list(ROOT.glob("*.pdf"))
    cats = {}
    for p in pdfs:
        n = p.name.lower()
        if "ai" in n or "llm" in n or "ml" in n:
            c = "AI_ML"
        elif "privacy" in n:
            c = "DATA_PRIVACY"
        elif "security" in n or "cyber" in n:
            c = "CYBERSECURITY"
        elif "standard" in n:
            c = "STANDARDS"
        elif "regulation" in n:
            c = "REGULATION"
        else:
            c = "SOFTWARE"
        cats[c] = cats.get(c, 0) + 1
    return cats


@app.cell
def _viz(stage2_classify):
    import pandas as pd
    import altair as alt
    df = pd.DataFrame([{"category": k, "count": v} for k, v in stage2_classify.items()]).sort_values("count", ascending=False)
    chart = alt.Chart(df).mark_bar().encode(
        x="count:Q", y="category:N", color="category:N",
    ).properties(width=500, height=250, title="Technology corpus: docs by topic")
    return chart


if __name__ == "__main__":
    app.run()
