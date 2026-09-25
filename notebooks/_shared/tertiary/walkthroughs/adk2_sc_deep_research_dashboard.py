"""marimo notebook: adk2_sc_deep_research_dashboard — operator console for the ADK 2 Pillar-3 Senior Cycle deep-research pipeline (L4b RECURSIVE + exam-paper aware).

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors notebooks/22_crown_dependencies_dashboard.py but wraps `agents.workflows.sc_deep_research`.

Pipeline (RECURSIVE — L4b pattern):
    START → decompose → research_topic (parallel_worker × 50+ LC subjects)
                                       │  │  │  │ │ │
                                       └──┴──┴──┴──┴┴┴──┘
                                                   ▼
                                       synthesise (recurses for past-paper → marking-scheme → chief-examiner)

Reference surfaces:
- agents/workflows/sc_deep_research.py
- agents/meaisinfhoghlaim/educational/students_jc/agents.py (shared with JC)
- orchestration/defs/2_materials/sc/

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/adk2_sc_deep_research_dashboard.py
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
        # ADK 2 Pillar-3 — Senior Cycle Deep Research Dashboard (L4b recursive, exam-paper aware)

        Operator console for the **Senior Cycle (Leaving Cert)** ADK 2 Pillar-3 deep-research pipeline.

        Like JC, SC uses the **L4b recursive pattern** — but the recursion walks
        through **past paper → marking scheme → Chief Examiner report → rubric descriptors**
        for each of the 50+ LC subjects.

        ## Pipeline graph

        ```
        START → decompose ─→ research_topic (×50+ LC subjects, parallel)
                                  └──┴──┴──┴──┴──┴──┴──┴──┘
                                              ▼
                                  synthesise (RECURSES for paper → marking → examiner)
                                              ▼
                                  Rubric descriptors (4 levels per question)
        ```
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo
    from datetime import datetime

    mo.md(
        f"""
        ## Phase status — fetched at {datetime.utcnow().isoformat()}
        """
    )
    return


@app.cell
def _workflow_import() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from agents.workflows import sc_deep_research  # type: ignore

    workflow = sc_deep_research
    return (workflow,)


@app.cell
def _render_workflow(workflow) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported Pillar-3 workflow (L4b recursive)

        - **Name**: `{workflow.name}`
        - **Edges**: {len(workflow.edges)} chains
        - **Parallel workers**: 50+ (one per LC subject family)
        - **Recursion depth**: 3 (subject → paper → marking → examiner)
        """
    )
    return


@app.cell
def _run_button() -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Run Pillar-3 SC deep research")
    return (run_btn,)


@app.cell
def _run(run_btn, workflow) -> None:
    import marimo as mo

    out = None
    if run_btn.value:
        try:
            import asyncio
            from agents.workflows.sc_deep_research import run_sc_deep_research

            out = asyncio.run(
                run_sc_deep_research(
                    query="How does the LC Maths marking scheme reward structured proofs vs worked answers?"
                )
            )
        except Exception as exc:
            out = {"error": str(exc)}
    return (out,)


@app.cell
def _render_out(out) -> None:
    import marimo as mo

    if out is None:
        mo.md("_Click **Run** to execute the pipeline._")
    else:
        mo.md(f"```json\n{out}\n```")
    return


if __name__ == "__main__":
    app.run()
