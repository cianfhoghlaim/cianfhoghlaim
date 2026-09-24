"""marimo notebook: adk2_jc_deep_research_dashboard — operator console for the ADK 2 Pillar-3 JC deep-research pipeline (L4b RECURSIVE pattern).

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors notebooks/19_junior_cycle_pipeline_dashboard.py but wraps `agents.workflows.jc_deep_research`.

Pipeline (RECURSIVE — L4b pattern):
    START → decompose → research_topic (parallel_worker × 18 JC subjects)
                                       │  │  │  │ │ │
                                       └──┴──┴──┴──┴┴┴──┘
                                                   ▼
                                       synthesise (recurses for CBA breakdown)

The 18 JC core subjects include English, Irish, Mathematics, Science, History,
Geography, French, German, Spanish, Italian, Business, Home Economics, Music,
Art, Technology, Engineering, Wood Tech, Graphics.

Reference surfaces:
- agents/workflows/jc_deep_research.py
- agents/meaisinfhoghlaim/educational/students_jc/agents.py
- orchestration/defs/2_materials/jc/

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/adk2_jc_deep_research_dashboard.py
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
        # ADK 2 Pillar-3 — Junior Cycle Deep Research Dashboard (L4b recursive)

        Operator console for the **JC** ADK 2 Pillar-3 deep-research pipeline.

        Unlike Aistear + Primary (FLAT, L4a), JC uses the **L4b recursive pattern**
        — each subject decomposes into its 2 CBAs, then the CBAs each decompose
        into their Achievement Level descriptors (4 per CBA).

        ## Pipeline graph

        ```
        START → decompose ─→ research_topic (×18 JC subjects, parallel)
                                  └──┴──┴──┴──┴──┴──┴──┴──┘
                                              ▼
                                  synthesise (RECURSES for CBA breakdown)
                                              ▼
                                  CBA Achievement Levels (4 × 2 per subject)
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
    from agents.workflows import jc_deep_research  # type: ignore

    workflow = jc_deep_research
    return (workflow,)


@app.cell
def _render_workflow(workflow) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported Pillar-3 workflow (L4b recursive)

        - **Name**: `{workflow.name}`
        - **Edges**: {len(workflow.edges)} chains
        - **Parallel workers**: 18 (one per JC core subject)
        - **Recursion depth**: 2 (subject → CBA → Achievement Level)
        """
    )
    return


@app.cell
def _run_button() -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Run Pillar-3 JC deep research")
    return (run_btn,)


@app.cell
def _run(run_btn, workflow) -> None:
    import marimo as mo

    out = None
    if run_btn.value:
        try:
            import asyncio
            from agents.workflows.jc_deep_research import run_jc_deep_research

            out = asyncio.run(
                run_jc_deep_research(
                    query="How do JC CBAs integrate with subject-level learning outcomes?"
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
