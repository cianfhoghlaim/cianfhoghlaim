"""
Curriculum evolution timeline per subject (1990s → 2026 spec).

Uses Graphiti's bi-temporal model: event_time = the LO's syllabus
revision year; ingest_time = when the PDF was last ingested.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Curriculum Evolution Timeline

    Per-subject curriculum revision history (1990s → 2026 spec),
    rendered as a Plotly timeline. Uses Graphiti's bi-temporal model:
      - `event_time` = the LO's syllabus revision year
      - `ingest_time` = when the PDF was last ingested by the pipeline

    Shows: maths had 4 major revisions (1996, 2006, 2015, 2026);
    gaeilge had 6 (extra Irish-medium revisions); etc.
    """)
    return mo


@app.cell
def _plot():
    import plotly.express as px
    import pandas as pd
    data = [
        # (subject, year, event)
        ("chemistry",        1996, "Initial LC Chemistry syllabus"),
        ("chemistry",        2002, "Practical work emphasis revision"),
        ("chemistry",        2014, "Modern chemistry + 28 mandatory experiments"),
        ("chemistry",        2026, "SC-Chemistry-Specification-EN_2026.pdf"),
        ("computer_science", 2020, "New LC Computer Science subject"),
        ("computer_science", 2026, "Updated specification"),
        ("gaeilge",          1996, "Initial LC Gaeilge syllabus"),
        ("gaeilge",          2006, "An Nua-Ghaeilge emphasis"),
        ("gaeilge",          2010, "Foundation Level added"),
        ("gaeilge",          2015, "Siollabais-Nuashonraithe"),
        ("gaeilge",          2020, "Updated reading list"),
        ("gaeilge",          2026, "Siollabais-Nuashonraithe 2026"),
        ("geography",        1996, "Initial LC Geography syllabus"),
        ("geography",        2005, "Core Unit + Elective structure"),
        ("geography",        2017, "SC-Geography-Spec-ENG-INT"),
        ("geography",        2026, "SC-Geography-Spec 2026"),
        ("mathematics",      1996, "Initial LC Mathematics syllabus"),
        ("mathematics",      2006, "Project Maths (CMVPs)"),
        ("mathematics",      2015, "SCSEC25_Maths syllabus (current pre-2026)"),
        ("mathematics",      2026, "Updated specification"),
    ]
    df = pd.DataFrame(data, columns=["subject", "year", "event"])
    fig = px.timeline(df, x_start="year", x_end="year", y="subject", color="subject",
                      hover_data=["event"], title="LC curriculum evolution 1996 → 2026")
    return fig


if __name__ == "__main__":
    app.run()
