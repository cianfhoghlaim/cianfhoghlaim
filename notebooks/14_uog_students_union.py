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
"""UoG Students' Union — marimo dashboard (8 tabs, full BIEP parity).

Drives the canonical 8-tab BIEP pattern against the
`cianfhoghlaim.education.ie.uog_students_union_documents` and
`cianfhoghlaim.education.ie.class_rep_handbooks` DuckLake tables.

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
# UoG Students' Union Dashboard

Backend: **{backend}** | DB: `{db_path}`

The UoG Students' Union (Students' Union) public-corpus surface.
8 tabs: Policies / Welfare / Elections / Referenda / Class-Rep
Handbooks / Lance Search / Heatmap / SQL Console.
            """
        )
    )
    return backend, db_path, duckdb, mo, os, pd


@app.cell
def _(conn, mo, pd):
    """Tab 1 — All SU documents."""
    df = conn.execute(
        """
        SELECT document_id, resource_kind, title, summary, effective_year,
               elected_officer, officer_role, is_constitution, source_url
        FROM cianfhoghlaim.education.ie.uog_students_union_documents
        ORDER BY is_constitution DESC, resource_kind, title
        """
    ).fetch_df()
    mo.ui.table(df, page_size=20, label=f"SU documents ({len(df)} rows)")


@app.cell
def _(conn, mo, pd):
    """Tab 2 — Welfare guides."""
    df = conn.execute(
        """
        SELECT document_id, title, body, summary, effective_year
        FROM cianfhoghlaim.education.ie.uog_students_union_documents
        WHERE resource_kind = 'WELFARE_GUIDE'
        ORDER BY effective_year DESC
        """
    ).fetch_df()
    mo.ui.table(df, page_size=10, label=f"Welfare guides ({len(df)} rows)")


@app.cell
def _(conn, mo, pd):
    """Tab 3 — Elections."""
    df = conn.execute(
        """
        SELECT document_id, title, elected_officer, officer_role, effective_year
        FROM cianfhoghlaim.education.ie.uog_students_union_documents
        WHERE resource_kind = 'ELECTION_MANIFESTO'
        ORDER BY effective_year DESC
        """
    ).fetch_df()
    mo.ui.table(df, page_size=20, label=f"Election manifestos ({len(df)} rows)")


@app.cell
def _(conn, mo, pd):
    """Tab 4 — Referenda."""
    df = conn.execute(
        """
        SELECT document_id, title, body, effective_year
        FROM cianfhoghlaim.education.ie.uog_students_union_documents
        WHERE resource_kind = 'REFERENDUM'
        ORDER BY effective_year DESC
        """
    ).fetch_df()
    mo.ui.table(df, page_size=10, label=f"Referenda ({len(df)} rows)")


@app.cell
def _(conn, mo, pd):
    """Tab 5 — Class-Rep Handbooks (per college)."""
    df = conn.execute(
        """
        SELECT college_slug, academic_year, title, url
        FROM cianfhoghlaim.education.ie.class_rep_handbooks
        ORDER BY college_slug
        """
    ).fetch_df()
    mo.ui.table(df, page_size=10, label=f"Class-Rep handbooks ({len(df)} rows)")


@app.cell
def _(mo):
    """Tab 6 — Lance Search placeholder."""
    mo.output.replace(
        mo.md(
            "## Tab 6 — Lance Search\n\n"
            "Semantic search over `uog_students_union_documents` LanceDB "
            "table. Run `cocoindex update UoGStudentsUnionApp` first."
        )
    )


@app.cell
def _(mo):
    """Tab 7 — Heatmap placeholder."""
    mo.output.replace(
        mo.md(
            "## Tab 7 — Heatmap\n\n"
            "SU service coverage heatmap goes here. Populated by the "
            "`populate_uog_su_covers_service` cognify rule."
        )
    )


@app.cell
def _(mo, conn):
    """Tab 8 — SQL Console."""
    sql = mo.ui.text_area(
        label="DuckLake SQL",
        value=(
            "SELECT resource_kind, COUNT(*) FROM "
            "cianfhoghlaim.education.ie.uog_students_union_documents "
            "GROUP BY resource_kind"
        ),
    )
    if sql.value:
        try:
            df = conn.execute(sql.value).fetch_df()
            mo.ui.table(df)
        except Exception as exc:
            mo.output.replace(f"ERROR: {exc}")


if __name__ == "__main__":
    app.run()
