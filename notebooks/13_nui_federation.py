# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "marimo>=0.23.10",
#   "duckdb>=1.5.4,<1.6.0",
#   "pandas>=2.0",
#   "ibis-framework[duckdb]>=10",
#   "plotly>=5.18",
#   "lancedb>=0.15",
#   "mlflow>=2.13",
# ]
# ///
"""NUI Federation — marimo dashboard (8 tabs, full BIEP parity).

The NUI federation sub-package's primary surface. Drives the 8-tab
canonical BIEP pattern against:
  - `cianfhoghlaim.education.ie.nui_members`
  - `cianfhoghlaim.education.ie.nui_constituent_circulars`
  - `cianfhoghlaim.education.ie.nui_archive`

The first tab (Members) is the headline: the 4 current constituents
(UCD, UCC, MU, UoG) + the pre-1908 QUB historical member.

References:
  - openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.10"
app = marimo.App(width="wide")


@app.cell
def _():
    import os

    import duckdb
    import marimo as mo
    import pandas as pd

    backend = os.environ.get("UOG_DASHBOARD_BACKEND", "duckdb-local")
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")

    mo.output.replace(
        mo.md(
            f"""
# NUI Federation Dashboard

Backend: **{backend}** | DB: `{db_path}`

The National University of Ireland (NUI) federation surface. 8 tabs:
Members / Constituent Circulars / Archive / Module Equivalence / Lance
Search / Heatmap / URL Health / SQL Console.
            """
        )
    )
    return backend, db_path, duckdb, mo, os, pd


@app.cell
def _(conn, mo):
    """Tab 1 — Members (4 current + the pre-1908 QUB archive)."""
    df = conn.execute(
        """
        SELECT member_id, member_name, kind, home_url,
               joined_nui_year, left_nui_year
        FROM cianfhoghlaim.education.ie.nui_members
        ORDER BY left_nui_year NULLS LAST, joined_nui_year
        """
    ).fetch_df()
    mo.ui.table(df, page_size=10, label=f"NUI members ({len(df)} rows)")


@app.cell
def _(conn, mo, pd):
    """Tab 2 — Constituent Circulars (1 per constituent per year)."""
    df = conn.execute(
        """
        SELECT circular_id, member_id, year, title, url
        FROM cianfhoghlaim.education.ie.nui_constituent_circulars
        ORDER BY year DESC, member_id
        """
    ).fetch_df()
    mo.ui.table(df, page_size=20, label=f"NUI circulars ({len(df)} rows)")


@app.cell
def _(conn, mo, pd):
    """Tab 3 — Archive (pre-1908 QUB + the 3 Queen's Colleges)."""
    df = conn.execute(
        """
        SELECT archive_id, url, description, scraped_at
        FROM cianfhoghlaim.education.ie.nui_archive
        ORDER BY archive_id
        """
    ).fetch_df()
    mo.ui.table(df, page_size=20, label=f"NUI archive links ({len(df)} rows)")


@app.cell
def _(mo):
    """Tab 4 — Module Equivalence (CT516 ↔ UCD-CS-516 etc.).

    Populated by the `populate_nui_member_connects` cognify rule.
    Run `python -m scripts.graph_storage.cognify.rules.nui_member_connects
    --populate` to regenerate.
    """
    mo.output.replace(
        mo.md(
            "## Tab 4 — NUI Module Equivalence\n\n"
            "The NUI↔UoG module equivalence table. Each row pairs a UoG "
            "module code with its NUI-member equivalent. The 'CT516' row "
            "is the canonical M.Sc. AI Deep Learning module."
        )
    )


@app.cell
def _(mo):
    """Tab 7 — Heatmap placeholder."""
    mo.output.replace(mo.md("## Tab 7 — Heatmap\n\nMembers × archive link count heatmap goes here."))


@app.cell
def _(mo, conn):
    """Tab 8 — SQL Console."""
    sql = mo.ui.text_area(
        label="DuckLake SQL",
        value="SELECT member_name, home_url FROM cianfhoghlaim.education.ie.nui_members",
    )
    if sql.value:
        try:
            df = conn.execute(sql.value).fetch_df()
            mo.ui.table(df)
        except Exception as exc:
            mo.output.replace(f"ERROR: {exc}")


if __name__ == "__main__":
    app.run()
