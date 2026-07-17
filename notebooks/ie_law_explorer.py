# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "duckdb>=1.0",
#   "ibis-framework[duckdb]>=9.0",
#   "altair>=5.0",
#   "polars>=0.20",
#   "pyarrow>=15.0",
# ]
# ///
"""
Pick-8 Ireland/law Explorer — unified marimo notebook across the 5
Pick-8 operational-law sources:

  1. **piab**         — Personal Injuries Assessment Board (PIABPage)
  2. **courts**       — Courts Service (CourtForm + CourtFee)
  3. **judgements**   — Judgements.ie (Judgement)
  4. **court_rules**  — Court Rules library (CourtRule)
  5. **legal_aid**    — Legal Aid Board (LegalAidPage + LegalAidForm)

Cells:
  1. Lakehouse connection + engine label (MotherDuck or local fallback)
  2. Source row-count table (per source x per DuckLake table)
  3. Search box — semantic-like ILIKE search over title / summary
  4. Statute-citation cross-reference (the canonical join key)
  5. Per-source drill-down picker + joined result table

Reference: openspec/changes/archive/2026-07-07-finalize-v4-landing/
           absorbed/2026-07-06-ireland-legal-pipeline/proposal.md
           (Pick-8 scoped reimplementation)
"""
from __future__ import annotations

import marimo

__generated_with = "0.13.0"
app = marimo.App(width="medium", app_title="Pick-8 Ireland/law Explorer")


@app.cell
def _intro_cell():
    import marimo as mo

    mo.md(
        """
        # Pick-8 Ireland/law Explorer

        Unified dashboard across the 5 operational-law sources
        in the Ireland/law quadrant:

        1. **piab** — Personal Injuries Assessment Board (PIAB)
        2. **courts** — Courts Service (forms + fees)
        3. **judgements** — Judgements.ie (~30,000 published decisions)
        4. **court_rules** — Rules of Court (PDF library)
        5. **legal_aid** — Legal Aid Board (Ireland)

        All 5 sources are read from `cianfhoghlaim.law.ie.*` DuckLake
        tables (MotherDuck `md:oideachais` or local DuckDB fallback).
        """
    )
    return (mo,)


@app.cell
def _connect_cell(mo):
    import sys
    from pathlib import Path

    # Make the in-repo `nb_utils` importable. The notebook lives at
    # `cianfhoghlaim/notebooks/ie_law_explorer.py`; nb_utils is a
    # sibling at `cianfhoghlaim/notebooks/nb_utils.py`.
    _here = Path(__file__).resolve().parent if "__file__" in dir() else Path.cwd()
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))

    try:
        from nb_utils import connect_biep_lakehouse

        con, engine_label = connect_biep_lakehouse(local_fallback=True)
        con_status = f"Connected to `{engine_label}`"
    except Exception as exc:
        # Hard fallback to in-memory DuckDB so the notebook still renders.
        import duckdb

        con = duckdb.connect(":memory:")
        engine_label = "unavailable"
        con_status = f"In-memory DuckDB (connect_biep_lakehouse failed: {exc})"

    mo.md(f"**Lakehouse:** {con_status}")
    return con, engine_label


@app.cell
def _row_count_cell(mo, con, engine_label):
    import polars as pl

    # The 7 Pick-8 IE/law DuckLake tables (L2-mirrored BAML extractions).
    # Coalesce to 0 rows when the table is missing (local fallback path).
    tables: list[tuple[str, str]] = [
        ("piab",         "cianfhoghlaim.law.ie.piab_pages"),
        ("piab",         "cianfhoghlaim.law.ie.piab_forms"),
        ("courts",       "cianfhoghlaim.law.ie.courts_forms"),
        ("courts",       "cianfhoghlaim.law.ie.court_fees"),
        ("judgements",   "cianfhoghlaim.law.ie.judgements"),
        ("court_rules",  "cianfhoghlaim.law.ie.court_rules"),
        ("legal_aid",    "cianfhoghlaim.law.ie.legal_aid_pages"),
        ("legal_aid",    "cianfhoghlaim.law.ie.legal_aid_forms"),
    ]

    rows: list[dict] = []
    for source, table in tables:
        try:
            n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        except Exception:
            n = 0
        rows.append({"source": source, "table": table, "row_count": n})

    df = pl.DataFrame(rows)
    mo.ui.table(df, label=f"Row counts ({engine_label})")
    return (df,)


@app.cell
def _search_cell(mo, con, df):
    # Build a single searchable virtual view by UNION ALL-ing the
    # 8 tables. Each row has (source, table, title, summary, url).
    # We project the common fields (title, url, summary) so the
    # search box can ILIKE across all 5 sources in one shot.
    _union_parts: list[str] = []
    for _, row in df.iter_rows(named=True):
        tbl = row["table"]
        _union_parts.append(
            f"SELECT '{row['source']}' AS source, '{tbl}' AS origin_table, "
            f"COALESCE(title, form_title, case_name, neutral_citation, headline, '') AS title, "
            f"COALESCE(url, source_url, '') AS url, "
            f"COALESCE(summary, holding, purpose, '') AS snippet "
            f"FROM {tbl}"
        )
    _union_sql = " UNION ALL ".join(_union_parts) if _union_parts else "SELECT 1 WHERE FALSE"

    search_input = mo.ui.text(
        value="",
        placeholder="Search across all 5 sources (title / summary / snippet)...",
        full_width=True,
    )
    mo.vstack([
        mo.md("### Cross-source search"),
        search_input,
    ])
    return search_input, _union_sql


@app.cell
def _search_results_cell(mo, con, _union_sql, search_input):
    import polars as pl

    _q = (search_input.value or "").strip()
    if not _q:
        result = pl.DataFrame(
            {"source": [], "origin_table": [], "title": [], "url": [], "snippet": []}
        )
    else:
        try:
            _rows = con.execute(
                f"SELECT * FROM ({_union_sql}) WHERE "
                f"  LOWER(title)   LIKE LOWER('%{_q}%') OR "
                f"  LOWER(snippet) LIKE LOWER('%{_q}%') "
                f"LIMIT 100"
            ).fetchall()
            _cols = [d[0] for d in con.description]
            result = pl.DataFrame(_rows, schema=_cols, orient="row")
        except Exception as exc:
            result = pl.DataFrame(
                {"error": [f"search failed: {exc}"]}
            )
    mo.ui.table(result, label=f"Search results for `{_q}`")
    return (result,)


@app.cell
def _statute_linkage_cell(mo, con, engine_label):
    import polars as pl

    mo.md(
        """
        ### Statute-citation cross-reference

        The canonical join key: the `statutes_cited` /
        `related_statutes` / `statutory_basis` arrays extracted by the
        6 BAML functions in `cianfhoghlaim/baml/education/law/*.baml` are
        joined to the canonical
        `cianfhoghlaim.education.ie.irish_statute_book.acts` table.
        """
    )

    # The cross-source statute linkage view is the L2 asset
    # `ie_law_statute_linkage` (defined in
    # cianfhoghlaim/orchestration/defs/2_materials/ie_law/assets.py).
    # It writes to cianfhoghlaim.law.ie.ie_law_statute_links.
    _linkage_table = "cianfhoghlaim.law.ie.ie_law_statute_links"
    try:
        _n = con.execute(f"SELECT COUNT(*) FROM {_linkage_table}").fetchone()[0]
        _top_statutes = con.execute(
            f"SELECT matched_act_id, COUNT(*) AS n "
            f"FROM {_linkage_table} "
            f"WHERE matched_act_id IS NOT NULL "
            f"GROUP BY matched_act_id ORDER BY n DESC LIMIT 20"
        ).fetchall()
        _statute_df = pl.DataFrame(_top_statutes, schema=["act_id", "citation_count"], orient="row")
    except Exception:
        _n = 0
        _statute_df = pl.DataFrame({"act_id": [], "citation_count": []})

    mo.vstack([
        mo.md(f"**Total statute links:** `{_n}` ({engine_label})"),
        mo.ui.table(_statute_df, label="Top 20 cited acts across all 5 sources"),
    ])
    return


@app.cell
def _per_source_picker(mo, con, df):
    sources = sorted({row["source"] for row in df.iter_rows(named=True)})
    source_picker = mo.ui.dropdown(
        options=sources,
        value=sources[0] if sources else "piab",
        label="Drill into source",
    )
    mo.vstack([source_picker])
    return (source_picker,)


@app.cell
def _drilldown_cell(mo, con, source_picker, df):
    import polars as pl

    _src = source_picker.value
    _tables = [
        row["table"]
        for row in df.iter_rows(named=True)
        if row["source"] == _src
    ]
    if not _tables:
        return

    table_picker = mo.ui.dropdown(
        options=_tables,
        value=_tables[0],
        label="DuckLake table",
    )

    # Try a 50-row sample of the picked table.
    try:
        _tbl = table_picker.value
        _rows = con.execute(f"SELECT * FROM {_tbl} LIMIT 50").fetchall()
        _cols = [d[0] for d in con.description]
        sample = pl.DataFrame(_rows, schema=_cols, orient="row")
    except Exception as exc:
        sample = pl.DataFrame({"error": [f"sample failed: {exc}"]})

    mo.vstack([
        table_picker,
        mo.ui.table(sample, label=f"Sample from `{_src}`"),
    ])
    return (table_picker,)


if __name__ == "__main__":
    app.run()
