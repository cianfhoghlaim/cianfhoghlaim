"""marimo notebook: adk2_aistear_deep_research_dashboard — operator console for the ADK 2 Pillar-3 Aistear deep-research pipeline.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Mirrors notebooks/26_aistear_dashboard.py but wraps `agents.workflows.aistear_deep_research`.

Pipeline (FLAT, no recursion — L4a pattern from the ADK 2 codelab):
    START → decompose → research_topic (parallel_worker × 4 Aistear themes)
                                       │  │  │  │
                                       └──┴──┴──┴──┘
                                                   ▼
                                             synthesize

The 4 canonical Aistear themes:
- Well-being (Biú Folláine)
- Identity-Belonging (Céannacht agus Muintearas)
- Communicating (Cumarsáid)
- Exploring-Thinking (Taiscéalaíocht agus Smaointeoireacht)

Reference surfaces:
- agents/workflows/aistear_deep_research.py
- agents/meaisinfhoghlaim/educational/teachers/agents.py (downstream consumer)
- orchestration/defs/2_materials/aistear/ (the 14 BAML-extracted apps)

Run with:
    uv run marimo edit notebooks/_shared/tertiary/walkthroughs/adk2_aistear_deep_research_dashboard.py
    uv run python notebooks/_shared/tertiary/walkthroughs/adk2_aistear_deep_research_dashboard.py --cli
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
        # ADK 2 Pillar-3 — Aistear Deep Research Dashboard

        Operator console for the **Aistear** ADK 2 Pillar-3 deep-research pipeline.

        The 4 NCCA Aistear themes (Well-being, Identity-Belonging, Communicating,
        Exploring-Thinking) are decomposed by `decompose_node` and fanned out to
        4 parallel `research_topic_node(parallel_worker=True)` workers, then
        synthesised back into one final answer.

        ## Pipeline graph

        ```
        START → decompose ─→ research_topic (×4 themes, parallel)
                                  └──┴──┴──┴──┘
                                            ▼
                                       synthesize
        ```

        ## Reference surfaces

        - `agents/workflows/aistear_deep_research.py`
        - `orchestration/defs/2_materials/aistear/` (the 14 BAML apps)
        - `notebooks/_shared/marimo_patterns.py` (`run_dagster_asset_check`, `llm_chat_with_prompts`)
        """
    )
    return


@app.cell
def _phase_status() -> None:
    import marimo as mo
    from datetime import datetime

    mo.md(
        f"""
        ## Phase status

        Walkthrough `adk2_aistear_deep_research_dashboard` — fetched at {datetime.utcnow().isoformat()}.
        """
    )
    return


@app.cell
def _workflow_import() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from agents.workflows import aistear_deep_research  # type: ignore

    workflow = aistear_deep_research
    return (workflow,)


@app.cell
def _render_workflow(workflow) -> None:
    import marimo as mo

    mo.md(
        f"""
        ### Imported Pillar-3 workflow

        - **Name**: `{workflow.name}`
        - **Edges**: {len(workflow.edges)} chains
        - **Parallel workers**: 4 (one per Aistear theme)

        ```python
        from google.adk.workflow import Workflow
        # edges are tuples of (from, to_1, to_2, ...)
        ```

        Run interactively:

        ```python
        from agents.workflows.aistear_deep_research import run_aistear_deep_research
        result = await run_aistear_deep_research(
            query="How do the 4 Aistear themes support early-childhood wellbeing?"
        )
        ```
        """
    )
    return


@app.cell
def _run_button() -> None:
    import marimo as mo

    run_btn = mo.ui.run_button(label="Run Pillar-3 Aistear deep research")
    return (run_btn,)


@app.cell
def _run(run_btn, workflow) -> None:
    import marimo as mo

    out = None
    if run_btn.value:
        try:
            import asyncio
            from agents.workflows.aistear_deep_research import run_aistear_deep_research

            out = asyncio.run(
                run_aistear_deep_research(
                    query="How do the 4 Aistear themes support early-childhood wellbeing?"
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
