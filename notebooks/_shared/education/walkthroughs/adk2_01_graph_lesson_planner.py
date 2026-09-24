"""marimo notebook: ADK 2 Pillar 1 — Workflow(edges=...) graph for lesson_planner_agent.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.

Mirrors the L1_graph_basics + L2a_parallel_join pattern from
docs/google_examples/adk2-tutorial.

Run with:
    uv run marimo edit notebooks/_shared/education/walkthroughs/adk2_01_graph_lesson_planner.py
"""
from __future__ import annotations

import marimo

__generated_with = "0.14.0"
app = marimo.App(width="full")


@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # ADK 2 · Pillar 1 — Workflow(edges=...) graph for lesson_planner_agent

        Replaces the 1.x LlmAgent + FunctionTool pattern with the ADK 2
        `Workflow(edges=...)` graph primitive. Per the L1_graph_basics
        walkthrough: a plain Python function and an LLM agent are BOTH
        just nodes in the same `edges` list.

        ## Reference surfaces
        - `agents/workflows/teacher_daily_workflow.py` — the actual graph
        - `agents/meaisinfhoghlaim/_shared/schemas.py` — the Pydantic I/O types
        - `agents/meaisinfhoghlaim/educational/teachers/_root.py` — the Pillar-2 collaborative root
        - `agents/meaisinfhoghlaim/educational/teachers/lesson_planner_agent.py` — the agent node
        - `docs/google_examples/adk2-tutorial/L1_graph_basics/workflow.py` — the canonical L1 reference
        - `openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/specs/adk2-pillars-orchestration/spec.md`

        See `scripts/preflight_education.py` to confirm the agent stack is ready,
        and `scripts/walk_education.py` to walk all 5 chapters end-to-end.
        """
    )
    return


@app.cell
def _graph_diagram():
    import marimo as mo
    mo.md(
        """
        ## The graph

        ```
        START ─► plan_today (function, 0 LLM)
                  │
                  ▼
              lesson_planner (agent)
                  │
                  ▼
            assessment_scorer (agent)
                  │
                  ▼
              sen_pastoral (agent)
        ```

        Per the L2a pattern: a function node prepares the day (zero LLM
        calls), then agents reason in sequence. The whole graph runs
        in ONE go; to fan out in parallel, see the Pillar 3 deep-research
        notebooks (adk2_03_dynamic_aistear_research.py et al.).
        """
    )
    return


@app.cell
def _synthesis():
    import marimo as mo
    mo.md(
        """
        ## Synthesis

        The 3 Pillar-1 graphs (teacher_daily + student_secondary +
        tertiary_personal) replace the 1.x keyword-routed agent dispatch
        with explicit, testable, composable structure. They're the
        visible graphs; the Pillar-2 root orchestrators
        (teacher_root + student_root + students_union_root) are the
        invisible team that gets fanned out across the relevant subset of
        specialists; the Pillar-3 deep-research pipelines are the
        dynamic workflows that grow at runtime.
        """
    )
    return


if __name__ == "__main__":
    app.run()
