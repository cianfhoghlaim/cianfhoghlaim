"""marimo notebook: adk2_tertiary_deep_research_dashboard — operator console for the ADK 2 Pillar-3 Tertiary deep-research pipeline.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Wraps `agents.workflows.tertiary_deep_research`.

Pipeline (L4a flat + L4b recursion for matriculation):
    START → decompose → research_topic (parallel_worker × 4 NUI institutions + QQI + Apprenticeships)
                                       │  │  │  │  │  │
                                       └──┴──┴──┴──┴──┴──┘
                                                   ▼
                                       synthesise (recurses for matriculation → CAO points → QQI ladder)

The 4 NUI institutions:
- UCD (Ollscoil Chathair Bhaile Átha Cliath)
- UCG / UoG (Ollscoil na Gaillimhe)
- UCC (Ollscoil Chorcaí)
- NUIM (Ollscoil Mhá Nuad)

Plus QQI FET + Apprenticeships.

Reference surfaces:
- agents/workflows/tertiary_deep_research.py
- agents/meaisinfhoghlaim/educational/students_union/agents.py
- orchestration/defs/2_materials/tertiary/

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/adk2_tertiary_deep_research_dashboard.py
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
        # ADK 2 Pillar-3 — Tertiary Deep Research Dashboard

        Operator console for the **Tertiary (post-LC)** ADK 2 Pillar-3 deep-research pipeline.

        The 4 NUI institutions + QQI + Apprenticeships are decomposed by `decompose_node`
        and fanned out to 6 parallel `research_topic_node(parallel_worker=True)` workers,
        then synthesised back into one final answer that recursively walks the
        matriculation → CAO points → QQI ladder chain.

        ## Pipeline graph

        ```
        START → decompose ─→ research_topic (×4 NUI + QQI + Apprenticeship, parallel)
                                  └──┴──┴──┴──┴──┴──┘
                                              ▼
                                  synthesise (RECURSES for matriculation ladder)
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
    from agents.workflows import tertiary_deep_research  # type: ignore

    workflow = tertiary_deep_research
    return (workflow,)


@app.cell
def _render_workflow(workflow) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported Pillar-3 workflow (L4a + L4b hybrid)

        - **Name**: `{workflow.name}`
        - **Edges**: {len(workflow.edges)} chains
        - **Parallel workers**: 6 (4 NUI + QQI + Apprenticeship)
        - **Recursion depth**: 2 (institution → matriculation → CAO/QQI ladder)
        """
    )
    return


@app.cell
def _run_button() -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Run Pillar-3 Tertiary deep research")
    return (run_btn,)


@app.cell
def _run(run_btn, workflow) -> None:
    import marimo as mo

    out = None
    if run_btn.value:
        try:
            import asyncio
            from agents.workflows.tertiary_deep_research import run_tertiary_deep_research

            out = asyncio.run(
                run_tertiary_deep_research(
                    query="How does UCG / UoG matriculate QQI FET Level 5 applicants for Arts programmes?"
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
