"""marimo notebook: student_jc_dashboard — K-12 student (Junior Cycle, ages 12-15) dashboard.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Wraps `student_secondary_workflow` (Pillar 1, ADK 2): homework_tracker → cba_planner → study_plan → exam_timetable.

Reference surfaces:
- agents/workflows/student_secondary_workflow.py
- dlt_sources/british_isles/ireland/junior_cycle/
- baml_src/british_isles/ireland/k12/jc_subject_extraction.baml

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/student_jc_dashboard.py
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
        # K-12 Student — Junior Cycle Dashboard (Ages 12-15)

        The 18 JC core subjects + 16 short courses. Each subject has 2 CBAs.

        ## Pipeline graph (Pillar 1, ADK 2)

        ```
        START → homework_tracker → cba_planner → study_plan → exam_timetable
        ```
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
def _workflow_import() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from agents.workflows import student_secondary_workflow  # type: ignore

    return (student_secondary_workflow,)


@app.cell
def _render(student_secondary_workflow) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported Pillar-1 workflow

        - **Name**: `{student_secondary_workflow.name}`
        - **Edges**: {len(student_secondary_workflow.edges)} chains
        - **Sequence**: homework_tracker → cba_planner → study_plan → exam_timetable
        """
    )
    return


if __name__ == "__main__":
    app.run()
