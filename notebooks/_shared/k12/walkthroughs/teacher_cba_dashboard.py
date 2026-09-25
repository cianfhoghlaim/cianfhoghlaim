"""marimo notebook: teacher_cba_dashboard — JC CBA timeline + Achievement Level dashboard for the K-12 teacher.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pulls from the BAML-extracted `cba_task_extraction` schema (per `baml_src/british_isles/ireland/k12/cba_task_extraction.baml`).

Reference surfaces:
- baml_src/british_isles/ireland/k12/cba_task_extraction.baml
- dlt_sources/british_isles/ireland/teacher_workload/
- agents/meaisinfhoghlaim/educational/teachers/agents.py (cba_planner sub-agent)

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/teacher_cba_dashboard.py
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
        # K-12 Teacher — CBA Timeline Dashboard

        Each JC core subject has **2 CBAs** (Classroom-Based Assessments). Each CBA
        has **4 Achievement Levels** (Yet to meet expectations → Exceptional).

        The `cba_task_extraction.baml` schema extracts:
        - subject (English, Irish, Mathematics, …)
        - cba_number (1 or 2)
        - title, brief, format
        - achievement_level_descriptors (4 levels)
        - week_target, assessment_window

        ## Reference surfaces

        - `baml_src/british_isles/ireland/k12/cba_task_extraction.baml`
        - `dlt_sources/british_isles/ireland/junior_cycle/`
        - `agents/meaisinfhoghlaim/educational/teachers/agents.py:cba_planner`
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
def _baml_schema_ref() -> None:
    import marimo as mo

    mo.md(
        """
        ### CBA Achievement Level descriptors (per NCCA)

        | Level | Descriptor | Mark range |
        |---|---|---|
        | 1 | Yet to meet expectations | 0-39% |
        | 2 | In line with expectations | 40-54% |
        | 3 | Above expectations | 55-74% |
        | 4 | Exceptional | 75-100% |
        """
    )
    return


@app.cell
def _render_form() -> None:
    import marimo as mo

    subject = mo.ui.dropdown(
        options=["English", "Irish", "Mathematics", "Science", "History", "Geography", "French", "Spanish", "German", "Italian", "Business", "Music", "Art", "Home Economics", "Technology", "Wood Tech", "Engineering", "Graphics"],
        value="Mathematics",
        label="JC subject",
    )
    return (subject,)


@app.cell
def _render_form(subject) -> None:
    subject
    return


if __name__ == "__main__":
    app.run()
