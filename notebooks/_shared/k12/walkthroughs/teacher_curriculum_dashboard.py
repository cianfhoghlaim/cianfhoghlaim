"""marimo notebook: teacher_curriculum_dashboard — K-12 teacher's curriculum operator console.

Per openspec/changes/2026-09-23-k12-teacher-student-pipeline-v1/.
Wraps `agents.meaisinfhoghlaim.educational.teachers.agents` (10 ADK 2 agents, 5 teacher + 5 student).

The 5 teacher sub-agents:
- lesson_planner (curriculum-aligned lesson generator)
- assessment_scorer (CBA + state-exam rubric scorer)
- sen_pastoral (Special Educational Needs + wellbeing liaison)
- cba_planner (Classroom-Based Assessment timeline generator)
- parent_liaison (parent communication + consent tracking)

Reference surfaces:
- agents/meaisinfhoghlaim/educational/teachers/agents.py
- agents/meaisinfhoghlaim/educational/teachers/_root.py (teacher_root orchestrator)
- dlt_sources/british_isles/ireland/teacher_workload/

Run with:
    uv run marimo edit notebooks/_shared/k12/walkthroughs/teacher_curriculum_dashboard.py
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
        # K-12 Teacher — Curriculum Dashboard

        Operator console for the **teacher_root** orchestrator and its 5 sub-agents:

        1. **lesson_planner** — pulls NCCA curriculum strands + outcomes, generates
           a 5-stage (Aistear → LC) lesson plan with EN/GA bilingual notes.
        2. **assessment_scorer** — applies rubric descriptors to JC CBAs and LC exam answers.
        3. **sen_pastoral** — flags SEN + wellbeing concerns (Children First 2015).
        4. **cba_planner** — generates CBA timelines with 2 CBAs × 4 Achievement Levels.
        5. **parent_liaison** — tracks parent consent + communication logs.

        ## Pipeline graph (Pillar 1, ADK 2)

        ```
        START → lesson_planner → assessment_scorer → sen_pastoral
                (curriculum)     (rubric)            (wellbeing)
                                                            │
                                                            ▼
                                                    parent_liaison
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
def _teacher_root_import() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from agents.meaisinfhoghlaim.educational.teachers._root import teacher_root  # type: ignore

    return (teacher_root,)


@app.cell
def _render_root(teacher_root) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported teacher_root orchestrator

        - **Name**: `{teacher_root.name}`
        - **Sub-agents**: 5 (lesson_planner, assessment_scorer, sen_pastoral, cba_planner, parent_liaison)
        - **Memory**: InMemoryMemoryService (Phase 1) → Vertex AI Memory Bank (Phase 2)
        """
    )
    return


@app.cell
def _tabs() -> None:
    import marimo as mo

    tabs = mo.ui.tabs(
        {
            "Lesson planner": mo.md("_Generates a curriculum-aligned lesson plan._"),
            "Assessment scorer": mo.md("_Scores JC CBA / LC exam rubric._"),
            "SEN pastoral": mo.md("_Flags SEN + wellbeing concerns._"),
            "CBA planner": mo.md("_Generates CBA timeline._"),
            "Parent liaison": mo.md("_Tracks parent consent + comms._"),
        }
    )
    return (tabs,)


@app.cell
def _render_tabs(tabs) -> None:
    tabs
    return


if __name__ == "__main__":
    app.run()
