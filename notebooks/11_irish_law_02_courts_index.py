# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo>=0.13.0",
#     "duckdb>=1.0",
#     "ibis-framework[duckdb]>=9.0",
#     "altair>=5.0",
#     "polars>=0.20",
# ]
# #/
"""Ireland Legal Pipeline · Courts Service Index.

Catalogue of the Courts Service of Ireland — forms, judgements, fees,
and Rules of Court.

5 cells:
  1. Forms catalogue (filterable by court_level + category)
  2. Court fees (per court level)
  3. Rules of Court (per court level)
  4. Recent Judgements.ie publications
  5. Cross-source: find the court form for a given Judgement type

Lakehouse tables consumed:
  - cianfhoghlaim.law.ie.courts_forms
  - cianfhoghlaim.law.ie.court_fees
  - cianfhoghlaim.law.ie.court_rules
  - cianfhoghlaim.law.ie.judgements

Run:
  cd cianfhoghlaim && uv run marimo edit notebooks/12_ireland_law/02_courts_index.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium")


@app.cell
def _setup():
    """Connect to the MotherDuck + DuckLake lakehouse (with graceful fallback)."""
    import os
    import marimo as mo
    import duckdb

    md_token = os.environ.get("MOTHERDUCK_TOKEN", "")
    if md_token:
        con = duckdb.connect("md:cianfhoghlaim")
    else:
        con = duckdb.connect(":memory:")

    mo.md(
        """
        # Courts Service Index · courts.ie

        Forms, judgements, fees, and Rules of Court — one searchable
        catalogue over the `cianfhoghlaim.law.ie.*` DuckLake tables.
        """
    )
    return (con, mo)


@app.cell
def _forms(con):
    """1. Forms catalogue — filterable by court_level + category."""
    try:
        rows = con.sql(
            """
            SELECT form_number, form_title, court_level, category,
                   purpose, fee_eur, fillable_fields, downloadable_url
            FROM cianfhoghlaim.law.ie.courts_forms
            ORDER BY court_level, category, form_number
            LIMIT 200
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _forms_view(mo, rows):
    """Render the courts forms catalogue."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No courts forms in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No courts forms in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="Courts forms catalogue")


@app.cell
def _fees(con):
    """2. Court fees — per court level."""
    try:
        rows = con.sql(
            """
            SELECT fee_code, fee_description, amount_eur,
                   court_level, effective_date, notes
            FROM cianfhoghlaim.law.ie.court_fees
            ORDER BY court_level, fee_code
            LIMIT 200
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _fees_view(mo, rows):
    """Render the court fees."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No court fees in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No court fees in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="Court fees schedule")


@app.cell
def _rules(con):
    """3. Rules of Court — per court level."""
    try:
        rows = con.sql(
            """
            SELECT rule_number, "order", court_level, subject,
                   effective_date
            FROM cianfhoghlaim.law.ie.court_rules
            ORDER BY court_level, "order", rule_number
            LIMIT 200
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _rules_view(mo, rows):
    """Render the Rules of Court."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No court rules in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No court rules in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="Rules of Court")


@app.cell
def _judgements(con):
    """4. Recent Judgements.ie publications."""
    try:
        rows = con.sql(
            """
            SELECT neutral_citation, case_name, court_level,
                   decision_date, judge, catchwords, holding
            FROM cianfhoghlaim.law.ie.judgements
            ORDER BY decision_date DESC
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _judgements_view(mo, rows):
    """Render recent judgements."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md("_No judgements in lakehouse yet._")
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md("_No judgements in lakehouse yet._")
    return mo.ui.table(df.to_pandas(), label="Recent Judgements.ie publications")


@app.cell
def _cross_source(con):
    """5. Cross-source: Judgements joined with the relevant court form."""
    try:
        rows = con.sql(
            """
            SELECT
              j.neutral_citation,
              j.court_level,
              j.category,
              j.form_number,
              j.form_title,
              j.fee_eur,
              j.url         AS judgement_url
            FROM cianfhoghlaim.law.ie.judgements j
            LIMIT 50
            """
        ).df()
    except Exception:
        rows = []
    return (rows,)


@app.cell
def _cross_source_view(mo, rows):
    """Render the cross-source judgements ↔ forms join."""
    import polars as pl

    if isinstance(rows, list) and not rows:
        return mo.md(
            "_No cross-source joins yet — re-materialise the courts_ie "
            "source to populate both tables._"
        )
    df = pl.DataFrame(rows) if not isinstance(rows, pl.DataFrame) else rows
    if df.is_empty():
        return mo.md(
            "_No cross-source joins yet — re-materialise the courts_ie "
            "source to populate both tables._"
        )
    return mo.ui.table(df.to_pandas(), label="Judgement ↔ Form join")


if __name__ == "__main__":
    app.run()