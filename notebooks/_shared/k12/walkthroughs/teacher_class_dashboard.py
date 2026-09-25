"""marimo notebook: teacher_class_dashboard — per-class dashboard for the K-12 teacher.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pulls from `class_roster` + `teacher_workload` DuckLake tables.

Reference surfaces:
- dlt_sources/british_isles/ireland/class_roster/
- dlt_sources/british_isles/ireland/teacher_workload/

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/teacher_class_dashboard.py
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
        # K-12 Teacher — Per-Class Dashboard

        Per-class roster + SEN flags + CBA timeline + parent liaison log.

        ## Pipeline

        1. Pick a class
        2. View roster (with parent consent + SEN flags)
        3. View CBA timeline
        4. View workload for the week
        5. View parent communication log
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
def _tabs() -> None:
    import marimo as mo

    tabs = mo.ui.tabs(
        {
            "Roster": mo.md("_Per-class roster with parent consent + SEN flags._"),
            "CBA timeline": mo.md("_CBAs scheduled for this class._"),
            "Workload": mo.md_("_Workload hours for this class._"),
            "Parent comms": mo.md("_Parent communication log + consent status._"),
        }
    )
    return (tabs,)


@app.cell
def _render(tabs) -> None:
    tabs
    return


if __name__ == "__main__":
    app.run()
