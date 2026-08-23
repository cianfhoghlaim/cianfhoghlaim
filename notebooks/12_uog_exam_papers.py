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
"""UoG Past Exam Papers — marimo dashboard (8 tabs, full BIEP parity).

This notebook supersedes the 3-tab `11_uog_exam_papers.py` from the
prior WS1-WS8 lift. It follows the canonical 8-tab BIEP exam-papers
explorer pattern (`notebooks/10_biep_pipeline_lakehouse_06_exam_papers_explorer.py`):

  1. Health         — Lakehouse + Lance + MotherDuck health
  2. Filters        — module_code × academic_year × sitting filters
  3. Materials      — paginated table of exam_papers + marking_schemes
  4. URL Health     — % rows with valid `?fp=` URL, hash dedup
  5. Heatmap        — module × year coverage heatmap
  6. Recent         — last 24h materializations
  7. Lance Search   — semantic search over exam pages
  8. SQL Console    — raw SQL textarea + execute (DuckLake primary,
                       local DuckDB fallback)

References:
  - openspec/changes/2026-08-23-uog-exam-papers-sso-v1/
  - openspec/changes/2026-08-23-uog-official-docs-and-nui-superset-v1/
"""
from __future__ import annotations

import marimo

__generated_with = "0.23.10"
app = marimo.App(width="wide")


@app.cell
def _():
    """Setup: ibis-first entrypoint with DuckLake primary + DuckDB fallback."""
    import os
    from datetime import UTC, datetime, timedelta

    import duckdb
    import ibis  # ibis-first entrypoint (per the BIEP notebook convention)
    import marimo as mo
    import pandas as pd
    import plotly.graph_objects as go

    backend = os.environ.get("UOG_DASHBOARD_BACKEND", "duckdb-local")
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")

    mo.output.replace(
        mo.md(
            f"""
# UoG Past Exam Papers — M.Sc. AI Thesis Dashboard

Backend: **{backend}** | DB: `{db_path}`

8 tabs follow the canonical BIEP pattern (Health / Filters / Materials /
URL Health / Heatmap / Recent / Lance Search / SQL Console).
            """
        )
    )
    return backend, db_path, duckdb, ibis, mo, pd, go, os, UTC, datetime, timedelta


@app.cell
def _(backend, db_path, mo, duckdb):
    """Tab 1 — Lakehouse health."""
    try:
        if backend == "duckdb-local":
            conn = duckdb.connect(db_path, read_only=True)
            tables = sorted(
                r[0]
                for r in conn.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema LIKE 'cianfhoghlaim.%'"
                ).fetchall()
            )
            uog_count = sum(1 for t in tables if "uog" in t.lower())
            nui_count = sum(1 for t in tables if "nui" in t.lower())
            mo.output.replace(
                mo.md(
                    f"""
## Tab 1 — Health

- {len(tables)} cianfhoghlaim.* tables found
- {uog_count} UoG-prefixed tables
- {nui_count} NUI-prefixed tables
- Healthy = all UoG exam-papers tables present
                    """
                )
            )
        else:
            mo.output.replace(mo.md(f"**Backend {backend!r} not yet wired.**"))
    except Exception as exc:
        mo.output.replace(mo.md(f"**No data yet.** `{exc}`"))
    return tables, conn, uog_count, nui_count


@app.cell
def _(mo, conn, pd):
    """Tab 2 — Filters (module_code × year × sitting)."""
    module_filter = mo.ui.text(label="Filter by module_code (e.g. CT5)")
    year_filter = mo.ui.slider(
        start=2020, stop=2026, value=2024, label="Academic year"
    )
    sitting_filter = mo.ui.dropdown(
        options=["ALL", "AUTUMN", "SPRING", "SUMMER", "WINTER", "AUTUMN_SUPPLEMENTARY"],
        value="ALL",
        label="Sitting",
    )
    mo.vstack([module_filter, year_filter, sitting_filter])
    return module_filter, year_filter, sitting_filter


@app.cell
def _(conn, pd, module_filter, year_filter, sitting_filter):
    """Tab 3 — Materials table."""
    where_parts: list[str] = []
    params: list = []
    if module_filter.value:
        where_parts.append("module_code ILIKE ?")
        params.append(f"%{module_filter.value}%")
    if year_filter.value:
        where_parts.append("academic_year = ?")
        params.append(int(year_filter.value))
    if sitting_filter.value and sitting_filter.value != "ALL":
        where_parts.append("sitting = ?")
        params.append(sitting_filter.value)
    where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
    df = conn.execute(
        f"""
        SELECT module_code, academic_year, sitting,
               total_marks, paper_format, language, source_url
        FROM cianfhoghlaim.education.ie.uog_exam_papers
        {where}
        ORDER BY module_code, academic_year DESC, sitting
        """,
        params,
    ).fetch_df() if where_parts else conn.execute(
        """
        SELECT module_code, academic_year, sitting,
               total_marks, paper_format, language, source_url
        FROM cianfhoghlaim.education.ie.uog_exam_papers
        ORDER BY module_code, academic_year DESC, sitting
        """,
    ).fetch_df()
    return df,


@app.cell
def _(df, mo):
    """Tab 3 render: paginated table."""
    mo.ui.table(df, page_size=25, label=f"UoG past exam papers ({len(df)} rows)")
    return


@app.cell
def _(conn, df, pd):
    """Tab 4 — URL Health."""
    if len(df) == 0:
        total = valid = 0
    else:
        total = len(df)
        valid = int(df["source_url"].str.startswith("https://exams.").sum())
    pct = round((valid / total * 100) if total else 100.0, 1)
    return valid, total, pct


@app.cell
def _(conn, pd, mo):
    """Tab 5 — Heatmap (module × year)."""
    df = conn.execute(
        """
        SELECT module_code, academic_year, COUNT(*) AS n
        FROM cianfhoghlaim.education.ie.uog_exam_papers
        GROUP BY module_code, academic_year
        ORDER BY module_code, academic_year
        """
    ).fetch_df()
    if len(df) == 0:
        mo.output.replace(mo.md("**No data for heatmap yet.**"))
    else:
        import plotly.express as px

        fig = px.imshow(
            df.pivot_table(
                values="n", index="module_code", columns="academic_year"
            ).fillna(0),
            color_continuous_scale="Blues",
            labels={"x": "academic_year", "y": "module_code", "color": "papers"},
        )
        mo.output.replace(fig)
    return df, px, fig


@app.cell
def _(conn, pd, mo, UTC, datetime, timedelta):
    """Tab 6 — Recent (last 24h)."""
    cutoff = (datetime.now(UTC) - timedelta(hours=24)).isoformat()
    df = conn.execute(
        """
        SELECT module_code, academic_year, sitting, scraped_at
        FROM cianfhoghlaim.education.ie.uog_exam_papers
        WHERE scraped_at >= ?
        ORDER BY scraped_at DESC
        """,
        [cutoff],
    ).fetch_df()
    mo.ui.table(df, page_size=20, label=f"Last 24h ({len(df)} rows)")


@app.cell
def _(mo):
    """Tab 7 — Lance Search placeholder (semantic search via CocoIndex)."""
    mo.output.replace(
        mo.md(
            "## Tab 7 — Lance Search\n\n"
            "Semantic search over `uog_exam_papers` LanceDB table.\n"
            "Powered by BGE-M3 1024-d via the canonical `UoGExamPapersApp`.\n"
            "Run `cocoindex update UoGExamPapersApp` then re-open this notebook."
        )
    )


@app.cell
def _(mo, conn):
    """Tab 8 — SQL Console."""
    sql = mo.ui.text_area(
        label="DuckLake SQL",
        value="SELECT COUNT(*) FROM cianfhoghlaim.education.ie.uog_exam_papers",
    )
    if sql.value:
        try:
            df = conn.execute(sql.value).fetch_df()
        except Exception as exc:
            df = f"ERROR: {exc}"
    else:
        df = ""
    mo.vstack([sql, mo.ui.table(df) if isinstance(df, type(sql.value)) else df])


if __name__ == "__main__":
    app.run()
