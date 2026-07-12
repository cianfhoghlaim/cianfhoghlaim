"""
Cross-subject topic overlap — FalkorDB query for shared topics across
2+ LC subjects. Visualised as a Venn-style heatmap.

Example: "Data analysis" appears in chemistry (stoichiometry), maths
(statistics), geography (data interpretation), computer_science
(data structures), gaeilge (literary analysis of data presentation).

Lakehouse tables consumed:
  - oideachais.leaving_cert.<subject>_topics  (the per-subject topic tables)
  - oideachais.lc.<subject>.<level>_<language>  (LanceDB; for similarity joins)
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# ///

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _lakehouse():
    """Live lakehouse wiring — fan-out across the 5 per-subject topic tables."""
    import duckdb
    subjects = ["chemistry", "computer_science", "gaeilge", "geography", "mathematics"]
    try:
        con = duckdb.connect("md:oideachais")
        union_sql = " UNION ALL ".join(
            f"SELECT '{s}' AS subject, topic FROM oideachais.leaving_cert.{s}_topics"
            for s in subjects
        )
        topic_subject_df = con.sql(f"SELECT * FROM ({union_sql})").df()
    except Exception:
        con = duckdb.connect(":memory:")
        topic_subject_df = con.sql(
            "SELECT * FROM (VALUES ('no-data', 'no-data')) AS t(subject, topic) WHERE FALSE"
        ).df()
    return con, topic_subject_df, subjects


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
    import os
    import marimo as mo
    from pathlib import Path
    ROOT = Path(os.environ.get(
        "CIANFHOGHLAIM_LEAVING_CERT_ROOT",
        "/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/leaving_certificate",
    ))
    mo.md("""
    # Cross-subject Topic Overlap

    FalkorDB query: for each Topic node, how many LC subjects cover
    it? Render as a Venn-style heatmap (1 = belongs to subject).

    Stars: shared topics across 2+ subjects are candidates for
    cross-subject curriculum alignment.
    """)
    return mo, ROOT


@app.cell
def _viz(topic_subject_df, subjects):
    """Live altair heatmap — pivot of (topic × subject)."""
    import altair as alt
    if topic_subject_df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("lakehouse unavailable"))
    else:
        chart = (
            alt.Chart(topic_subject_df.assign(covered=1))
            .mark_rect()
            .encode(
                x="subject:O",
                y="topic:O",
                color=alt.Color(
                    "covered:O",
                    scale=alt.Scale(range=["#f0f0f0", "#2c7fb8"]),
                ),
                tooltip=["topic", "subject"],
            )
            .properties(
                width=400,
                height=300,
                title="Topic coverage across 5 LC subjects (live)",
            )
        )
    return (chart,)


if __name__ == "__main__":
    app.run()
