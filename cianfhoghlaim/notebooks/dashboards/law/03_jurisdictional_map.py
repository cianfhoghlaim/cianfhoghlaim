"""
Jurisdictional map — visualises case distribution by jurisdiction across
the 6 Gemini corpora on a choropleth (Ireland / NI / UK / EU / ECHR / US / International).
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")





@app.cell
def _stage1_dlt_gemini_all(ROOT):
    """Run the real DLT source — 224 rows across 6 corpora."""
    import sys
    sys.path.insert(0, str(ROOT.parent))
    from cianfhoghlaim.dlt.filesystem.gemini_corpus_source import gemini_documents
    rows = list(gemini_documents(root_path=str(ROOT.parent)))
    return rows


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Jurisdictional Map

    Choropleth of the 224 Gemini PDFs grouped by inferred jurisdiction
    (heuristic from filename: `echr` → EU, `qub` → NI, `uk_` / `ucl_` →
    UK, etc.).
    """)
    return mo


@app.cell
def _jurisdiction_distribution():
    from pathlib import Path
    ROOT = Path("/Users/cianmacandeisigh/dev/kings_college_galway/leabharlann/gemini_deep_research")
    corpora = ("law", "medical", "politics", "culture", "technology", "other")
    jurisdictions = {}
    for corpus in corpora:
        d = ROOT / corpus
        if not d.exists():
            continue
        for p in d.glob("*.pdf"):
            n = p.name.lower()
            if "echr" in n:
                j = "EUROPEAN_UNION"
            elif "belfast" in n or "qub" in n or "ni_" in n:
                j = "NORTHERN_IRELAND"
            elif "ucl" in n or "uk_" in n:
                j = "UNITED_KINGDOM"
            elif "dual" in n or "cross_border" in n:
                j = "CROSS_BORDER"
            else:
                j = "IRELAND"
            jurisdictions[j] = jurisdictions.get(j, 0) + 1
    return jurisdictions


@app.cell
def _viz(jurisdiction_distribution):
    import pandas as pd
    import plotly.express as px
    # Map jurisdictions to ISO 3166-1 alpha-3 codes for the choropleth
    country_map = {
        "IRELAND": "IRL",
        "NORTHERN_IRELAND": "GBR",  # NI is part of UK
        "UNITED_KINGDOM": "GBR",
        "EUROPEAN_UNION": "DEU",   # proxy
        "CROSS_BORDER": "IRL",    # primary jurisdiction
    }
    rows = [{"iso": country_map.get(j, "IRL"), "jurisdiction": j, "count": c}
            for j, c in jurisdiction_distribution.items()]
    df = pd.DataFrame(rows)
    fig = px.choropleth(df, locations="iso", color="count",
                        hover_name="jurisdiction",
                        title="Gemini 6-corpus: jurisdictional distribution")
    return fig


if __name__ == "__main__":
    app.run()
