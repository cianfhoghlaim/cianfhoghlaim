"""marimo notebook: teacher_pd_dashboard — K-12 teacher Professional Development dashboard.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pulls from the `teacher_pd` DLT source at `dlt_sources/british_isles/ireland/teacher_pd/`.

Reference surfaces:
- dlt_sources/british_isles/ireland/teacher_pd/
- agents/meaisinfhoghlaim/educational/teachers/agents.py:lesson_planner (PD-aware)

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/teacher_pd_dashboard.py
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
        # K-12 Teacher — Professional Development Dashboard

        PD opportunities from Oide, PDST, NIPT, INTO, TUI, ASTI.

        ## DLT sources

        - `dlt_sources/british_isles/ireland/teacher_pd/`
        - `dlt_sources/british_isles/ireland/oide/`
        - `dlt_sources/british_isles/ireland/pdst/`
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

    provider = mo.ui.dropdown(
        options=["Oide", "PDST", "NIPT", "INTO", "TUI", "ASTI", "NCCA", "Scoilnet"],
        value="Oide",
        label="Provider",
    )
    return (provider,)


@app.cell
def _render(provider) -> None:
    provider
    return


if __name__ == "__main__":
    app.run()
