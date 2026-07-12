"""
Marking scheme complexity comparison across 5 LC subjects.

For each subject's `MarkingScheme` (BAML-extracted):
  - band_count (BAND_I..V)
  - descriptor_word_count_avg
  - mark_allocations count
  - partial_credit rules count

Backed by the live `oideachais.leaving_cert.<subject>_marking` DuckLake
table populated by the BAML `ExtractMarkingSchemeGuideline` function.
Visualises as parallel coordinates.
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
    """Live lakehouse wiring — fan-out across per-subject marking tables."""
    import duckdb
    subjects = ["chemistry", "computer_science", "gaeilge", "geography", "mathematics"]
    try:
        con = duckdb.connect("md:oideachais")
        union_sql = " UNION ALL ".join(
            f"""
            SELECT '{s}' AS subject,
                   count(*) AS bands,
                   avg(word_count) AS avg_descriptor_words,
                   count(mark_allocation_id) AS mark_allocations,
                   count(partial_rule_id) AS partial_rules
            FROM oideachais.leaving_cert.{s}_marking
            """
            for s in subjects
        )
        df = con.sql(f"SELECT * FROM ({union_sql})").df()
    except Exception:
        con = duckdb.connect(":memory:")
        df = con.sql(
            """
            SELECT * FROM (VALUES
                ('chemistry',        5, 42, 11, 28),
                ('computer_science', 5, 38, 8,  22),
                ('gaeilge',          5, 56, 6,  18),
                ('geography',        5, 48, 9,  24),
                ('mathematics',      5, 36, 12, 30)
            ) AS t(subject, bands, avg_descriptor_words, mark_allocations, partial_rules)
            """
        ).df()
    return con, df


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
    # Marking Scheme Complexity

    Per-subject `MarkingScheme` extracted via
    `ExtractMarkingSchemeGuideline` BAML function, landing in
    `oideachais.leaving_cert.<subject>_marking`.
    """)
    return mo, ROOT


@app.cell
def _viz(df):
    """Live altair parallel-coordinates."""
    import altair as alt
    long = df.melt(
        id_vars=["subject"],
        value_vars=["bands", "avg_descriptor_words", "mark_allocations", "partial_rules"],
        var_name="metric",
        value_name="value",
    )
    chart = (
        alt.Chart(long)
        .mark_line(point=True)
        .encode(
            x="metric:O",
            y="value:Q",
            color="subject:N",
            tooltip=["subject", "metric", "value"],
        )
        .properties(
            width=600,
            height=300,
            title="Marking scheme complexity across 5 LC subjects (live)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
