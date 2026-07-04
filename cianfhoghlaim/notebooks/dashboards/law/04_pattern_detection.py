"""
Cross-corpus pattern detection — Cognee cognify over the 6 Gemini corpora.

Finds recurring patterns across the 224 PDFs:
  - "dual citizenship + discrimination" appears in law + politics
  - "QUB malpractice + Garda data" appears in law + medical
  - "ECHR + cross-border" appears in law + politics
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Cross-Corpus Pattern Detection

    After Cognee cognify over all 6 Gemini corpora, run pattern-detection
    queries against the resulting knowledge graph.

    Recurring patterns (heuristic, sample data shown):
    - "dual citizenship + discrimination" → law + politics
    - "QUB malpractice" → law + medical
    - "ECHR + cross-border" → law + politics
    - "Gaelic copyright" → law + culture
    - "AI regulation" → politics + technology
    """)
    return mo


@app.cell
def _cognee_patterns():
    """Sample data — replaced with real FalkorDB query after pipeline runs."""
    return [
        ("dual citizenship + discrimination", ["law", "politics"]),
        ("QUB malpractice", ["law", "medical"]),
        ("ECHR + cross-border", ["law", "politics"]),
        ("Gaelic copyright", ["law", "culture"]),
        ("AI regulation", ["politics", "technology"]),
        ("psychiatric medication", ["law", "medical"]),
        ("student rights dispute", ["law", "education"]),
        ("tenancy discrimination", ["law", "culture"]),
    ]


@app.cell
def _viz(cognee_patterns):
    import pandas as pd
    import altair as alt
    # All corpora x pattern matrix
    corpora = ["law", "medical", "politics", "culture", "technology", "other"]
    rows = []
    for pattern, sources in cognee_patterns:
        for c in corpora:
            rows.append({"pattern": pattern, "corpus": c, "matches": int(c in sources)})
    df = pd.DataFrame(rows)
    chart = alt.Chart(df).mark_rect().encode(
        x="corpus:O", y="pattern:O", color=alt.Color("matches:O", scale=alt.Scale(range=["#f0f0f0", "#2c7fb8"])),
    ).properties(width=300, height=200, title="Recurring patterns across 6 Gemini corpora")
    return chart


if __name__ == "__main__":
    app.run()
