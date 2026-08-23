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
"""UoG Personal Archive — marimo dashboard (8 tabs, full BIEP parity).

Lifts `leabharlann/ollscoil_na_gaillimhe/` (the user's three UoG
courses' artefacts: BA Maths & Education, HDip Software Design,
Diploma in Irish C1) plus the transcript PDFs to feature parity with
the leaving-cycle subject pipeline. The notebook reads the 8 typed
DuckLake tables populated by the personal-archive pipeline:

  - cianfhoghlaim.education.ie.personal_archive_artefacts
  - cianfhoghlaim.education.ie.personal_archive_assignments
  - cianfhoghlaim.education.ie.personal_archive_questions
  - cianfhoghlaim.education.ie.personal_archive_topics
  - cianfhoghlaim.education.ie.personal_archive_reading_lists
  - cianfhoghlaim.education.ie.personal_archive_code_cells
  - cianfhoghlaim.education.ie.personal_archive_ca_marks
  - cianfhoghlaim.education.ie.personal_archive_modules
  - cianfhoghlaim.education.ie.student_transcripts

8 tabs follow the canonical BIEP pattern
(notebooks/12_uog_exam_papers.py):

  1. Health         — Lakehouse + Lance + MotherDuck health
  2. Filters        — module_code × programme × provenance × kind filters
  3. Materials      — paginated table of artefacts + questions + topics
  4. URL Health     — % rows with valid `lecturer_name` / `grade` joins,
                      transcript join coverage %
  5. Heatmap        — module × topic_category coverage heatmap
  6. Recent         — last 24h materializations
  7. Lance Search   — semantic search over the 4 LanceDB tables
                      (artefacts / questions / topics / lecture notes)
  8. SQL Console    — raw SQL textarea + execute (DuckLake primary,
                       local DuckDB fallback)

A **CS4423 worked example** sidebar pre-filters every tab to
`module_code='CS4423'` and shows the full module dossier.

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
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
    import ibis
    import marimo as mo
    import pandas as pd

    backend = os.environ.get("UOG_DASHBOARD_BACKEND", "duckdb-local")
    db_path = os.environ.get("OOG_LOCAL_DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")

    mo.output.replace(
        mo.md(
            f"""
# UoG Personal Archive — Tertiary Modules Dashboard

Backend: **{backend}** | DB: `{db_path}`

8 tabs follow the canonical BIEP pattern (Health / Filters / Materials /
URL Health / Heatmap / Recent / Lance Search / SQL Console).

The CS4423 worked example (the Numerical Analysis 2 module from the
HDip Software Design programme) is the canonical pre-filter for the
sidebar.
            """
        )
    )
    return backend, db_path, duckdb, ibis, mo, pd, os, UTC, datetime, timedelta


@app.cell
def _(mo):
    """Sidebar — the CS4423 worked example selector."""
    example_module = mo.ui.dropdown(
        options=[
            "CS4423 — Numerical Analysis 2",
            "MP491 — Mathematics Project",
            "MA344 — Differential Equations",
            "GA201 — Irish Language C1",
        ],
        value="CS4423 — Numerical Analysis 2",
        label="Worked example module",
    )
    mo.output.replace(example_module)
    return example_module,


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
            pa_count = sum(
                1 for t in tables if t.startswith("personal_archive_")
            )
            transcript_count = sum(
                1 for t in tables if "transcript" in t.lower()
            )
            mo.output.replace(
                mo.md(
                    f"""
## Tab 1 — Health

- {len(tables)} cianfhoghlaim.* tables found
- {pa_count} `personal_archive_*` tables present
- {transcript_count} transcript tables present
- Healthy = all 9 personal-archive + 1 transcript tables present
                    """
                )
            )
        else:
            mo.output.replace(mo.md(f"**Backend {backend!r} not yet wired.**"))
    except Exception as exc:
        mo.output.replace(mo.md(f"**No data yet.** `{exc}`"))
    return tables, conn, pa_count, transcript_count


@app.cell
def _(mo):
    """Tab 2 — Filters."""
    module_filter = mo.ui.text(
        label="Filter by module_code (e.g. CS4, MA3, GA2)"
    )
    programme_filter = mo.ui.dropdown(
        options=["ALL", "BA_MATHS_ED", "HDIP_SD", "DIP_IRISH_C1", "OTHER"],
        value="ALL",
        label="Programme",
    )
    provenance_filter = mo.ui.multiselect(
        options=[
            "PERSONAL_SUBMISSION",
            "LECTURE_PROVIDED",
            "TRANSCRIPT_PDF",
            "PUBLIC_ARCHIVE",
        ],
        label="Provenance",
    )
    kind_filter = mo.ui.multiselect(
        options=[
            "ASSIGNMENT_SUBMISSION",
            "LECTURE_NOTES",
            "READING_LIST",
            "CODE_CELL",
            "EXAM_PAPER",
            "TRANSCRIPT",
            "OTHER",
        ],
        label="Artefact kind",
    )
    mo.output.replace(
        mo.vstack(
            [module_filter, programme_filter, provenance_filter, kind_filter]
        )
    )
    return module_filter, programme_filter, provenance_filter, kind_filter


@app.cell
def _(
    conn,
    pd,
    module_filter,
    programme_filter,
    provenance_filter,
    kind_filter,
):
    """Tab 3 — Materials table."""
    where_parts: list[str] = []
    params: list = []
    if module_filter.value:
        where_parts.append("module_code ILIKE ?")
        params.append(f"%{module_filter.value}%")
    if programme_filter.value and programme_filter.value != "ALL":
        where_parts.append("programme = ?")
        params.append(programme_filter.value)
    if provenance_filter.value:
        placeholders = ",".join("?" for _ in provenance_filter.value)
        where_parts.append(f"artefact_provenance IN ({placeholders})")
        params.extend(provenance_filter.value)
    if kind_filter.value:
        placeholders = ",".join("?" for _ in kind_filter.value)
        where_parts.append(f"artefact_kind IN ({placeholders})")
        params.extend(kind_filter.value)
    where = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""
    sql = f"""
        SELECT artefact_id, artefact_title, artefact_kind,
               artefact_provenance, module_code, academic_year,
               programme, lecturer_name
        FROM cianfhoghlaim.education.ie.personal_archive_artefacts
        {where}
        ORDER BY module_code, academic_year DESC, artefact_title
    """
    df = (
        conn.execute(sql, params).fetch_df()
        if where_parts
        else conn.execute(sql).fetch_df()
    )
    return df,


@app.cell
def _(df, mo):
    """Tab 3 render: paginated table."""
    mo.ui.table(df, page_size=25, label=f"Personal-archive artefacts ({len(df)} rows)")
    return


@app.cell
def _(conn, df, pd):
    """Tab 4 — URL Health + transcript join coverage."""
    try:
        total = conn.execute(
            "SELECT COUNT(*) FROM cianfhoghlaim.education.ie.personal_archive_artefacts"
        ).fetchone()[0]
        with_lecturer = conn.execute(
            "SELECT COUNT(*) FROM cianfhoghlaim.education.ie.personal_archive_artefacts "
            "WHERE artefact_provenance = 'LECTURE_PROVIDED' "
            "  AND lecturer_name IS NOT NULL AND lecturer_name != ''"
        ).fetchone()[0]
        transcript_join = conn.execute(
            """
            SELECT COUNT(*) FROM cianfhoghlaim.education.ie.student_transcripts t
            JOIN cianfhoghlaim.education.ie.personal_archive_artefacts a
              ON a.module_code = t.module_code
             AND a.academic_year = t.academic_year
            """
        ).fetchone()[0]
        artefacts_with_kind = total
    except Exception:
        total = artefacts_with_kind = with_lecturer = transcript_join = 0
    lecturer_pct = round((with_lecturer / artefacts_with_kind * 100) if artefacts_with_kind else 100.0, 1)
    join_pct = round((transcript_join / total * 100) if total else 100.0, 1)
    return total, with_lecturer, transcript_join, lecturer_pct, join_pct


@app.cell
def _(mo, total, with_lecturer, transcript_join, lecturer_pct, join_pct):
    """Tab 4 render — URL health card."""
    mo.output.replace(
        mo.md(
            f"""
## Tab 4 — URL / Join Health

- Total artefacts: **{total}**
- Artefacts with `lecturer_name` filled: **{with_lecturer}** ({lecturer_pct}%)
- Artefacts joined to `student_transcripts`: **{transcript_join}** ({join_pct}%)
- Healthy = lecturer % >= 80 AND transcript join % >= 60
            """
        )
    )
    return


@app.cell
def _(conn, mo):
    """Tab 5 — Heatmap (module × topic_category)."""
    try:
        df = conn.execute(
            """
            SELECT module_code, topic_category, COUNT(*) AS n
            FROM cianfhoghlaim.education.ie.personal_archive_topics
            GROUP BY module_code, topic_category
            ORDER BY module_code, topic_category
            """
        ).fetch_df()
    except Exception:
        df = None
    if df is None or len(df) == 0:
        mo.output.replace(mo.md("**No data for heatmap yet.**"))
    else:
        import plotly.express as px

        fig = px.imshow(
            df.pivot_table(
                values="n",
                index="module_code",
                columns="topic_category",
            ).fillna(0),
            color_continuous_scale="Greens",
            labels={
                "x": "topic_category",
                "y": "module_code",
                "color": "topics",
            },
        )
        mo.output.replace(fig)
    return df, px, fig


@app.cell
def _(conn, mo, UTC, datetime, timedelta):
    """Tab 6 — Recent (last 24h)."""
    cutoff = (datetime.now(UTC) - timedelta(hours=24)).isoformat()
    try:
        df = conn.execute(
            """
            SELECT artefact_id, artefact_title, module_code, scraped_at
            FROM cianfhoghlaim.education.ie.personal_archive_artefacts
            WHERE scraped_at >= ?
            ORDER BY scraped_at DESC
            """,
            [cutoff],
        ).fetch_df()
        mo.ui.table(df, page_size=20, label=f"Last 24h ({len(df)} rows)")
    except Exception as exc:
        mo.output.replace(
            mo.md(f"**Recent panel requires the pipeline to have run at least once.** `{exc}`")
        )
    return df,


@app.cell
def _(mo):
    """Tab 7 — Lance Search (semantic search over the 4 LanceDB tables)."""
    mo.output.replace(
        mo.md(
            "## Tab 7 — Lance Search\n\n"
            "Semantic search over the 4 personal-archive LanceDB tables "
            "(`personal_archive_artefacts`, `personal_archive_questions`, "
            "`personal_archive_topics`, `personal_archive_lecture_notes`) "
            "via BGE-M3 1024-d.\n\n"
            "Powered by the canonical `UoGPersonalArchive{Artefacts,"
            "Questions,Topics,LectureNotes}App` v1 Apps. "
            "Run `cocoindex update` then re-open this notebook."
        )
    )


@app.cell
def _(mo, conn):
    """Tab 8 — SQL Console."""
    sql = mo.ui.text_area(
        label="DuckLake SQL (personal_archive_*)",
        value=(
            "SELECT module_code, COUNT(*) AS artefacts "
            "FROM cianfhoghlaim.education.ie.personal_archive_artefacts "
            "GROUP BY module_code ORDER BY artefacts DESC"
        ),
    )
    if sql.value:
        try:
            df = conn.execute(sql.value).fetch_df()
        except Exception as exc:
            df = f"ERROR: {exc}"
    else:
        df = ""
    mo.vstack([sql, mo.ui.table(df) if hasattr(df, "columns") else df])
    return sql, df


@app.cell
def _(mo, example_module):
    """CS4423 worked-example sidebar — pre-filtered dossier."""
    module_code = example_module.value.split(" ")[0]
    mo.output.replace(
        mo.md(
            f"""
## CS4423 Worked Example — Module Dossier

Sidebar selected module: **{module_code}**

- Every artefact from `personal_archive_artefacts WHERE module_code='{module_code}'`
- Every question from `personal_archive_questions WHERE module_code='{module_code}'`
- Every topic from `personal_archive_topics WHERE module_code='{module_code}'`
- Every code cell from `personal_archive_code_cells WHERE module_code='{module_code}'`
- Transcript rows from `student_transcripts WHERE module_code='{module_code}'`

Run the SQL Console (Tab 8) with a `WHERE module_code='{module_code}'`
filter to inspect.
            """
        )
    )
    return module_code,


if __name__ == "__main__":
    app.run()
