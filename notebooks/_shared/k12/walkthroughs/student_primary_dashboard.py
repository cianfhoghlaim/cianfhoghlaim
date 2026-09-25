"""marimo notebook: student_primary_dashboard — K-12 student (Primary, ages 4-12) dashboard.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pulls from the Primary DLT source at `dlt_sources/british_isles/ireland/primary/`.

Reference surfaces:
- dlt_sources/british_isles/ireland/primary/
- baml_src/british_isles/ireland/k12/primary_curriculum_extraction.baml

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/student_primary_dashboard.py
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
        # K-12 Student — Primary Dashboard (Ages 4-12)

        The 12 NCCA Primary curriculum areas × 4 stages (Junior Infants → 6th Class).

        ## Stages

        | Stage | Stage (GA) | Age |
        |---|---|---|
        | JUNIOR_INFANTS | Naíonáin Shóisearacha | 4-5 |
        | SENIOR_INFANTS | Naíonáin Shinsearacha | 5-6 |
        | FIRST_TO_SECOND | Rang 1-2 | 6-8 |
        | THIRD_TO_FOURTH | Rang 3-4 | 8-10 |
        | FIFTH_TO_SIXTH | Rang 5-6 | 10-12 |
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
def _render() -> None:
    import marimo as mo

    mo.md(
        """
        ### Reference surfaces

        - `dlt_sources/british_isles/ireland/primary/`
        - `baml_src/british_isles/ireland/k12/primary_curriculum_extraction.baml`
        - `agents/meaisinfhoghlaim/educational/teachers/agents.py:lesson_planner` (consumes)
        """
    )
    return


if __name__ == "__main__":
    app.run()
