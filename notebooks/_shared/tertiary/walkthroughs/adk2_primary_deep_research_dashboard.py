"""marimo notebook: adk2_primary_deep_research_dashboard — operator console for the ADK 2 Pillar-3 Primary deep-research pipeline.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors notebooks/27_primary_dashboard.py but wraps `agents.workflows.primary_deep_research`.

Pipeline (FLAT — L4a pattern):
    START → decompose → research_topic (parallel_worker × 6 Primary curriculum areas)
                                       │  │  │  │  │  │
                                       └──┴──┴──┴──┴──┴──┘
                                                   ▼
                                             synthesize

The 6 Primary curriculum areas:
- Mathematics (Matamaitic)
- English (Béarla)
- Irish (Gaeilge)
- Science (Eolaíocht)
- History (Stair)
- Geography (Tíreolaíocht)

Reference surfaces:
- agents/workflows/primary_deep_research.py
- agents/meaisinfhoghlaim/educational/teachers/agents.py
- orchestration/defs/2_materials/primary/

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/adk2_primary_deep_research_dashboard.py
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
        # ADK 2 Pillar-3 — Primary Deep Research Dashboard

        Operator console for the **Primary curriculum** ADK 2 Pillar-3 deep-research pipeline.

        The 6 NCCA Primary curriculum areas are decomposed by `decompose_node` and
        fanned out to 6 parallel `research_topic_node(parallel_worker=True)` workers,
        then synthesised back into one final answer.

        ## Pipeline graph

        ```
        START → decompose ─→ research_topic (×6 areas, parallel)
                                  └──┴──┴──┴──┴──┴──┘
                                            ▼
                                       synthesize
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
    from agents.workflows import primary_deep_research  # type: ignore

    workflow = primary_deep_research
    return (workflow,)


@app.cell
def _render_workflow(workflow) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported Pillar-3 workflow

        - **Name**: `{workflow.name}`
        - **Edges**: {len(workflow.edges)} chains
        - **Parallel workers**: 6 (one per Primary curriculum area)
        """
    )
    return


@app.cell
def _run_button() -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Run Pillar-3 Primary deep research")
    return (run_btn,)


@app.cell
def _run(run_btn, workflow) -> None:
    import marimo as mo

    out = None
    if run_btn.value:
        try:
            import asyncio
            from agents.workflows.primary_deep_research import run_primary_deep_research

            out = asyncio.run(
                run_primary_deep_research(
                    query="How do the 6 Primary curriculum areas link together across stages?"
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
