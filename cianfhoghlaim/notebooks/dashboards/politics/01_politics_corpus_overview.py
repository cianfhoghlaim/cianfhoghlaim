"""
Gemini Politics Corpus Overview — 47 PDFs.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    from pathlib import Path
    CORPUS = "politics"
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/politics")
    pdfs = sorted(ROOT.glob("*.pdf")) if ROOT.exists() else []
    mo.md(f"""
    # Gemini Politics Corpus Overview

    **Path:** `leabharlann/gemini_deep_research/politics/`
    **Total PDFs:** {len(pdfs)}
    **Approx size:** 18 MB
    """)
    return mo, pdfs


@app.cell
def _stage2_classify():
    from pathlib import Path
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/politics")
    pdfs = list(ROOT.glob("*.pdf"))
    cats = {}
    for p in pdfs:
        n = p.name.lower()
        if "election" in n:
            c = "ELECTIONS"
        elif "policy" in n:
            c = "POLICY"
        elif "judicial" in n or "court" in n:
            c = "JUDICIAL"
        elif "international" in n:
            c = "INTERNATIONAL_RELATIONS"
        else:
            c = "GOVERNANCE"
        cats[c] = cats.get(c, 0) + 1
    return cats


@app.cell
def _viz(stage2_classify):
    import pandas as pd
    import altair as alt
    df = pd.DataFrame([{"category": k, "count": v} for k, v in stage2_classify.items()]).sort_values("count", ascending=False)
    chart = alt.Chart(df).mark_bar().encode(
        x="count:Q", y="category:N", color="category:N",
    ).properties(width=500, height=250, title="Politics corpus: cases by topic")
    return chart


if __name__ == "__main__":
    app.run()
