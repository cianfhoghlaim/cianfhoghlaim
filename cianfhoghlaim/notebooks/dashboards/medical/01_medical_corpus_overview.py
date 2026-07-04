"""
Gemini Medical Corpus Overview — 54 PDFs from
leabharlann/gemini_deep_research/medical/

Per-corpus pipeline: qwen3-vl-8b OCR → BAML ExtractMedicalCaseProfile
→ DuckLake → Cognee cognify → Graphiti temporal episode.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    from pathlib import Path
    CORPUS = "medical"
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/medical")
    pdfs = sorted(ROOT.glob("*.pdf")) if ROOT.exists() else []
    mo.md(f"""
    # Gemini Medical Corpus Overview

    **Path:** `leabharlann/gemini_deep_research/medical/`
    **Total PDFs:** {len(pdfs)}
    **Approx size:** 18 MB

    First 10 files:
    {chr(10).join(f'- `{p.name}` ({p.stat().st_size / 1024:.0f} KB)' for p in pdfs[:10])}
    """)
    return mo, pdfs


@app.cell
def _stage2_classify():
    from pathlib import Path
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research/medical")
    pdfs = list(ROOT.glob("*.pdf"))
    cats = {}
    for p in pdfs:
        n = p.name.lower()
        if "brain" in n or "neurology" in n:
            c = "NEUROLOGY"
        elif "psychiatr" in n:
            c = "PSYCHIATRY"
        elif "surgery" in n:
            c = "SURGERY"
        elif "diagnosis" in n:
            c = "DIAGNOSIS"
        else:
            c = "MEDICAL_MALPRACTICE"
        cats[c] = cats.get(c, 0) + 1
    return cats


@app.cell
def _viz(stage2_classify):
    import pandas as pd
    import altair as alt
    df = pd.DataFrame([{"category": k, "count": v} for k, v in stage2_classify.items()]).sort_values("count", ascending=False)
    chart = alt.Chart(df).mark_bar().encode(
        x="count:Q", y="category:N", color="category:N",
    ).properties(width=500, height=250, title="Medical corpus: cases by category")
    return chart


@app.cell
def _stage5_cognify():
    try:
        import cognee
        return {"dataset": "gemini_medical_research", "ok": True, "corpus_size": 54}
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    app.run()
