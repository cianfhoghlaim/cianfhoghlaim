"""marimo notebook: student_wellbeing_dashboard — K-12 student wellbeing + SEN liaison dashboard.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Pulls from the `sen_pastoral` agent + Children First 2015 designated-liaison-person rules.

Reference surfaces:
- agents/meaisinfhoghlaim/educational/teachers/agents.py:sen_pastoral
- Children First Act 2015 (designated liaison person for SEN records)
- GDPR Art. 9 (special category data — health, SEN status)

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/student_wellbeing_dashboard.py
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
        # K-12 Student — Wellbeing + SEN Dashboard

        Wellbeing flags + SEN concerns + designated liaison person routing.

        ## Compliance

        - **Children First Act 2015**: every SEN concern routes to the
          designated liaison person in the school.
        - **GDPR Art. 9**: SEN + health data is *special category personal data* —
          all read/write access is logged in `user:visit_count`.

        ## Reference surfaces

        - `agents/meaisinfhoghlaim/educational/teachers/agents.py:sen_pastoral`
        - `agents/meaisinfhoghlaim/educational/_archive/memory.py:burn` (GDPR delete)
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
def _consent_notice() -> None:
    import marimo as mo

    mo.callout(
        mo.md(
            """
            **Compliance notice**: This dashboard reads `user:stage` + `user:visit_count`
            from session state only — never writes without parent consent on file.
            Use `burn()` (per `agents/meaisinfhoghlaim/educational/_archive/memory.py`)
            to GDPR-delete records.
            """
        ),
        kind="warn",
    )
    return


if __name__ == "__main__":
    app.run()
