"""marimo notebook: student_aistear_dashboard — K-12 student (Aistear, ages 0-6) dashboard.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pulls from the Aistear DLT source at `dlt_sources/british_isles/ireland/aistear/`.

Reference surfaces:
- dlt_sources/british_isles/ireland/aistear/
- baml_src/british_isles/ireland/k12/aistear_framework_extraction.baml
- agents/meaisinfhoghlaim/educational/students_jc/agents.py (Aistear-aware)

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/student_aistear_dashboard.py
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
        # K-12 Student — Aistear Dashboard (Ages 0-6)

        The 4 Aistear themes × 4 age bands (Infants / Toddlers / Pre-school / Early Primary Bridge)
        × 3 language mediums (Irish / English / Bilingual).

        ## Reference surfaces

        - `dlt_sources/british_isles/ireland/aistear/`
        - `baml_src/british_isles/ireland/k12/aistear_framework_extraction.baml`
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
def _theme_grid() -> None:
    import marimo as mo

    mo.md(
        """
        ### The 4 Aistear themes

        | Theme | Theme (GA) | Age bands |
        |---|---|---|
        | WELL_BEING | Biú Folláine | Infants / Toddlers / Pre-school |
        | IDENTITY_BELONGING | Céannacht agus Muintearas | Infants / Toddlers / Pre-school / Early Primary Bridge |
        | COMMUNICATING | Cumarsáid | Infants / Pre-school / Early Primary Bridge |
        | EXPLORING_THINKING | Taiscéalaíocht agus Smaointeoireacht | Infants / Pre-school / Early Primary Bridge |
        """
    )
    return


@app.cell
def _run_button() -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Refresh from DuckLake")
    return (run_btn,)


@app.cell
def _render(run_btn) -> None:
    run_btn
    return


if __name__ == "__main__":
    app.run()
