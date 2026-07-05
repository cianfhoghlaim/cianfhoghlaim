"""
Cross-subject topic overlap — FalkorDB query for shared topics across
2+ LC subjects. Visualised as a Venn-style heatmap.

Example: "Data analysis" appears in chemistry (stoichiometry), maths
(statistics), geography (data interpretation), computer_science
(data structures), gaeilge (literary analysis of data presentation).
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
    # Cross-subject Topic Overlap

    FalkorDB query: for each Topic node, how many LC subjects cover
    it? Render as a Venn-style heatmap (1 = belongs to subject).

    Stars: shared topics across 2+ subjects are candidates for
    cross-subject curriculum alignment.
    """)
    return mo


@app.cell
def _query():
    """FalkorDB query — in production: GRAPH.QUERY on the lc5_knowledge_graph."""
    sample_topics = [
        ("topic:data_analysis",   ["computer_science", "mathematics", "geography"]),
        ("topic:atomic_structure",["chemistry"]),
        ("topic:stoichiometry",   ["chemistry", "mathematics"]),
        ("topic:graph_theory",    ["mathematics", "computer_science"]),
        ("topic:climate_data",    ["geography", "mathematics"]),
        ("topic:probability",     ["mathematics", "computer_science", "geography"]),
        ("topic:literary_analysis",["gaeilge", "english"]),
        ("topic:molecular_bonds", ["chemistry"]),
        ("topic:flowcharts",      ["computer_science", "mathematics"]),
        ("topic:geographic_data", ["geography", "computer_science"]),
    ]
    return sample_topics


@app.cell
def _viz(sample_topics):
    import pandas as pd
    import altair as alt
    subjects = ["chemistry", "computer_science", "gaeilge", "geography", "mathematics"]
    rows = []
    for topic, subs in sample_topics:
        for s in subjects:
            rows.append({"topic": topic, "subject": s, "covered": int(s in subs)})
    df = pd.DataFrame(rows)
    chart = alt.Chart(df).mark_rect().encode(
        x="subject:O", y="topic:O", color=alt.Color("covered:O", scale=alt.Scale(range=["#f0f0f0", "#2c7fb8"])),
        tooltip=["topic", "subject", "covered"],
    ).properties(width=400, height=300, title="Topic coverage across 5 LC subjects (1 = covered)")
    return chart


if __name__ == "__main__":
    app.run()
