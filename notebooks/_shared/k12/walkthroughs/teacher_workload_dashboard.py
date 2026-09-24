"""marimo notebook: teacher_workload_dashboard — K-12 teacher's weekly workload overview.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Reads from `dlt_sources/british_isles/ireland/teacher_workload/` (DuckLake table).

Reference surfaces:
- dlt_sources/british_isles/ireland/teacher_workload/
- agents/meaisinfhoghlaim/educational/teachers/_root.py

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/teacher_workload_dashboard.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro() -> None:
    import marimo as mo

    mo.md(
        """
        # K-12 Teacher — Workload Dashboard

        Weekly workload view across all classes a teacher takes. Pulls from the
        `teacher_workload` DuckLake table (DLT source at
        `dlt_sources/british_isles/ireland/teacher_workload/`).

        ## Dimensions

        - class_roster × week_number → period_count, prep_hours, marking_hours, cba_count
        - SEN_flag × week_number → flagged_students_count
        - parent_liaison_count × week_number
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo
    from datetime import datetime

    mo.md(f"## Phase status — fetched at {datetime.utcnow().isoformat()}")
    return


@app.cell
def _duckdb_query() -> None:
    import duckdb

    con = duckdb.connect("md:cianfhoghlaim")
    rows = con.execute(
        """
        SELECT class_roster, week_number,
               SUM(period_count) AS periods,
               SUM(prep_hours + marking_hours) AS total_hours
        FROM cianfhoghlaim.education.ireland.teacher_workload._audit.teacher_workload_audit
        GROUP BY 1, 2
        ORDER BY 2 DESC
        LIMIT 50
        """
    ).fetchall()
    return (rows,)


@app.cell
def _render(rows) -> None:
    import marimo as mo
    import pandas as pd

    df = pd.DataFrame(rows, columns=["class_roster", "week", "periods", "hours"])
    mo.ui.table(df)
    return


if __name__ == "__main__":
    app.run()
