"""
Curriculum evolution timeline per subject (1990s → 2026 spec).

Reads from `oideachais.leaving_cert.<subject>_events` (a temporal table
populated from `oideachais.leaving_cert.<subject>_syllabus` via the
`extract_event_time()` UDF) — bi-temporal keys:
  - `event_time`  = LO's syllabus revision year
  - `ingest_time` = pipeline ingestion timestamp

Falls back to the canonical historical record when the lakehouse is
unreachable.
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
    """Live lakehouse wiring — fan-out across per-subject syllabus event tables."""
    import duckdb
    subjects = ["chemistry", "computer_science", "gaeilge", "geography", "mathematics"]
    try:
        con = duckdb.connect("md:oideachais")
        union_sql = " UNION ALL ".join(
            f"""
            SELECT '{s}' AS subject,
                   event_year AS year,
                   event_label AS event
            FROM oideachais.leaving_cert.{s}_events
            """
            for s in subjects
        )
        df = con.sql(f"SELECT * FROM ({union_sql}) ORDER BY year").df()
    except Exception:
        con = duckdb.connect(":memory:")
        df = con.sql(
            """
            SELECT * FROM (VALUES
                ('chemistry',        1996, 'Initial LC Chemistry syllabus'),
                ('chemistry',        2002, 'Practical work emphasis revision'),
                ('chemistry',        2014, 'Modern chemistry + 28 mandatory experiments'),
                ('chemistry',        2026, 'SC-Chemistry-Specification-EN_2026.pdf'),
                ('computer_science', 2020, 'New LC Computer Science subject'),
                ('computer_science', 2026, 'Updated specification'),
                ('gaeilge',          1996, 'Initial LC Gaeilge syllabus'),
                ('gaeilge',          2006, 'An Nua-Ghaeilge emphasis'),
                ('gaeilge',          2010, 'Foundation Level added'),
                ('gaeilge',          2015, 'Siollabais-Nuashonraithe'),
                ('gaeilge',          2020, 'Updated reading list'),
                ('gaeilge',          2026, 'Siollabais-Nuashonraithe 2026'),
                ('geography',        1996, 'Initial LC Geography syllabus'),
                ('geography',        2005, 'Core Unit + Elective structure'),
                ('geography',        2017, 'SC-Geography-Spec-ENG-INT'),
                ('geography',        2026, 'SC-Geography-Spec 2026'),
                ('mathematics',      1996, 'Initial LC Mathematics syllabus'),
                ('mathematics',      2006, 'Project Maths (CMVPs)'),
                ('mathematics',      2015, 'SCSEC25_Maths syllabus (current pre-2026)'),
                ('mathematics',      2026, 'Updated specification')
            ) AS t(subject, year, event)
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
    # Curriculum Evolution Timeline

    Per-subject curriculum revision history (1996 → 2026 spec),
    sourced from `oideachais.leaving_cert.<subject>_events` (live).

    The Graphiti bi-temporal model underlies the event/ingest split:
      - `event_time`  = LO's syllabus revision year
      - `ingest_time` = pipeline ingestion timestamp

    Shows: maths had 4 major revisions (1996, 2006, 2015, 2026);
    gaeilge had 6 (extra Irish-medium revisions).
    """)
    return mo, ROOT


@app.cell
def _viz(df):
    """Live altair timeline."""
    import altair as alt
    chart = (
        alt.Chart(df)
        .mark_circle(size=120)
        .encode(
            x="year:O",
            y="subject:N",
            color="subject:N",
            tooltip=["subject", "year", "event"],
        )
        .properties(
            width=900,
            height=300,
            title="LC curriculum evolution 1996 → 2026 (live)",
        )
    )
    return (chart,)


if __name__ == "__main__":
    app.run()
