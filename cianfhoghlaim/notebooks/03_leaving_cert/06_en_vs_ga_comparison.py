"""
Cross-subject EN vs GA comparison — same Learning Outcome in EN vs GA.

For each subject's syllabus + the canonical LO list, pull the EN
text and the GA text; visualise the translation fidelity as a
divergence chart. This is the canonical read against the
`oideachais.leaving_cert.<subject>_cross_linguistic` table populated
by the `ExtractCrossLinguisticConcept` BAML function.

Lakehouse tables consumed:
  - oideachais.leaving_cert.<subject>_cross_linguistic
  - oideachais.leaving_cert.<subject>_topics
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
    """Live lakehouse wiring — fanned-out read across per-subject cross_linguistic.

    For each subject we union its `_cross_linguistic` table into a single
    long-format view (subject, lo_id, translation_fidelity). Falls back
    to an empty frame when the lakehouse is unreachable so the chart
    code remains exercised offline.
    """
    import duckdb
    subjects = ["chemistry", "computer_science", "gaeilge", "geography", "mathematics"]
    try:
        con = duckdb.connect("md:oideachais")
        union_sql = " UNION ALL ".join(
            f"""
            SELECT '{s}' AS subject, lo_id, translation_fidelity
            FROM oideachais.leaving_cert.{s}_cross_linguistic
            """
            for s in subjects
        )
        df = con.sql(f"SELECT * FROM ({union_sql})").df()
    except Exception:
        con = duckdb.connect(":memory:")
        df = con.sql(
            "SELECT * FROM (VALUES ('no-data', 'no-data', 0.0)) "
            "AS t(subject, lo_id, translation_fidelity) WHERE FALSE"
        ).df()
    return con, df, subjects


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
    mo.md(f"""
    # EN ↔ GA Cross-Linguistic Comparison

    Compares the same Learning Outcome (LO) in English vs Irish
    across all 5 LC subjects. Routes through BAML
    `ExtractCrossLinguisticConcept` per subject, populating
    `oideachais.leaving_cert.<subject>_cross_linguistic`.
    """)
    return mo, ROOT


@app.cell
def _viz(df):
    """Live altair — fidelity per LO across all 5 subjects."""
    import altair as alt
    if df.empty:
        chart = alt.Chart().mark_text().encode(text=alt.value("lakehouse unavailable"))
    else:
        chart = (
            alt.Chart(df)
            .mark_circle(size=80)
            .encode(
                x="lo_id:O",
                y=alt.Y("translation_fidelity:Q", scale=alt.Scale(domain=[0.5, 1.0])),
                color="subject:N",
                tooltip=["subject", "lo_id", "translation_fidelity"],
            )
            .properties(
                width=700,
                height=300,
                title="Translation fidelity per LO across 5 subjects (live cross_linguistic)",
            )
        )
    return (chart,)


@app.cell
def _chemistry():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCrossLinguisticConcept(
            subject="chemistry",
            source_pdf="SCSEC09_Chemistry_syllabus_Eng.pdf",
            ga_source_pdf="SCSEC09_Chemistry_syllabus_Gaeilge.pdf",
        )
    except Exception as exc:
        return {"error": str(exc)}


@app.cell
def _gaeilge():
    try:
        from cianfhoghlaim.baml_client import b
        return b.ExtractCrossLinguisticConcept(
            subject="gaeilge",
            source_pdf="Siollabais-Nuashonraithe-na-hArdteistimeireachta_1.pdf",
        )
    except Exception as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    app.run()
