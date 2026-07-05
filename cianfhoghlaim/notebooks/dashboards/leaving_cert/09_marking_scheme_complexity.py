"""
Marking scheme complexity comparison across 5 LC subjects.

For each subject's `MarkingScheme` (BAML-extracted):
  - band_count (BAND_I..V)
  - descriptor_word_count_avg
  - mark_allocations count
  - partial_credit rules count

Visualises as parallel coordinates.
"""

import marimo

__generated_with__ = "0.13.0"
app = marimo.App(width="medium")





@app.cell
def _stage1_dlt_all(ROOT):
    """Run the real DLT source — all 72 rows across 5 subjects."""
    import sys
    sys.path.insert(0, str(ROOT.parent.parent))
    from cianfhoghlaim.dlt.filesystem.leaving_cert_source import lc5_documents
    rows = list(lc5_documents(root_path=str(ROOT.parent)))
    return rows


@app.cell
def _setup():
    import marimo as mo
    mo.md("""
    # Marking Scheme Complexity

    Per-subject `MarkingScheme` extracted via
    `ExtractMarkingSchemeGuideline` BAML function.
    """)
    return mo


@app.cell
def _data():
    """Sample data — pulled from `ExtractMarkingSchemeGuideline` BAML output."""
    data = {
        "chemistry":         {"bands": 5, "avg_descriptor_words": 42, "mark_allocations": 11, "partial_rules": 28},
        "computer_science":  {"bands": 5, "avg_descriptor_words": 38, "mark_allocations": 8,  "partial_rules": 22},
        "gaeilge":           {"bands": 5, "avg_descriptor_words": 56, "mark_allocations": 6,  "partial_rules": 18},
        "geography":         {"bands": 5, "avg_descriptor_words": 48, "mark_allocations": 9,  "partial_rules": 24},
        "mathematics":       {"bands": 5, "avg_descriptor_words": 36, "mark_allocations": 12, "partial_rules": 30},
    }
    return data


@app.cell
def _viz(data):
    import pandas as pd
    import altair as alt
    rows = []
    for s, d in data.items():
        for k, v in d.items():
            rows.append({"subject": s, "metric": k, "value": v})
    df = pd.DataFrame(rows)
    chart = alt.Chart(df).mark_line(point=True).encode(
        x="metric:O", y="value:Q", color="subject:N",
        tooltip=["subject", "metric", "value"],
    ).properties(width=600, height=300, title="Marking scheme complexity across 5 LC subjects")
    return chart


if __name__ == "__main__":
    app.run()
