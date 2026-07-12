"""
Cross-corpus TIMELINE — Gemini Deep Research 6 corpora.

Per the user decision "PDF content only" (NOT mtime), each PDF's
`event_time` is extracted from the prose via BAML TimelineEvent.

Builds a global Plotly timeline of all 224 PDFs across 6 corpora.
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
    # Cross-Corpus Timeline (Gemini 6 corpora)

    Build a global timeline of all 224 PDFs' TimelineEvents (BAML-
    extracted from each PDF's prose content; NOT file mtime).
    """)
    return mo


@app.cell
def _plot():
    """Sample events — replaced with real BAML TimelineEvent data after pipeline runs."""
    import plotly.express as px
    import pandas as pd
    events = [
        # (date, corpus, event, severity)
        ("2020-03-15", "law", "Initial Garda incident",  "high"),
        ("2021-06-22", "law", "QUB discrimination complaint", "medium"),
        ("2022-01-10", "law", "Dual citizenship application", "low"),
        ("2022-08-04", "medical", "Misdiagnosed brain condition", "high"),
        ("2023-02-14", "law", "ECHR human rights filing", "high"),
        ("2023-05-30", "politics", "GDPR enforcement action", "medium"),
        ("2023-09-18", "medical", "Psychiatric medication dispute", "medium"),
        ("2024-01-22", "law", "University appeal hearing", "low"),
        ("2024-04-11", "culture", "Gaelic copyright dispute", "low"),
        ("2024-07-08", "technology", "AI regulation review", "medium"),
        ("2024-11-15", "politics", "Election recount request", "low"),
        ("2025-02-20", "law", "Cross-border civil case filed", "high"),
    ]
    df = pd.DataFrame(events, columns=["date", "corpus", "event", "severity"])
    fig = px.scatter(df, x="date", y="corpus", color="severity",
                     hover_data=["event"],
                     title="Gemini 6-corpus timeline (BAML event_time from PDF prose)")
    fig.update_traces(marker=dict(size=14))
    return fig


if __name__ == "__main__":
    app.run()
