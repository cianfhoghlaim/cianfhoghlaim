"""marimo notebook: student_sc_dashboard — K-12 student (Senior Cycle, ages 15-18) dashboard.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Wraps `student_secondary_workflow` (shared with JC) + `sc_deep_research` (Pillar 3, ADK 2 L4b recursive).

Reference surfaces:
- agents/workflows/student_secondary_workflow.py
- agents/workflows/sc_deep_research.py
- dlt_sources/british_isles/ireland/senior_cycle/

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/student_sc_dashboard.py
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
        # K-12 Student — Senior Cycle Dashboard (Ages 15-18)

        The 50+ LC subjects across 7 families. Exam papers, marking schemes, Chief
        Examiner reports.

        ## Pipeline graph (Pillar 1 + 3, ADK 2)

        ```
        START → homework_tracker → cba_planner → study_plan → exam_timetable
                                                          │
                                                          ▼
                                                  sc_deep_research (L4b)
                                                  subject → paper → marking → examiner
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
def _form() -> None:
    import marimo as mo

    subject = mo.ui.dropdown(
        options=["Mathematics", "English", "Irish", "Chemistry", "Physics", "Biology", "History", "Geography", "French", "German", "Spanish", "Italian", "Business", "Economics", "Accounting", "Art", "Music", "Construction Studies", "Design", "Engineering", "Technology", "Graphics", "Home Economics", "Agricultural Science", "Applied Mathematics", "Religious Education", "Classical Studies", "Politics", "Sociology"],
        value="Mathematics",
        label="LC subject",
    )
    return (subject,)


@app.cell
def _render(subject) -> None:
    subject
    return


if __name__ == "__main__":
    app.run()
