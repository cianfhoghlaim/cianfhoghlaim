"""marimo notebook: ADK 2 — 06 schemas.

Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
Pattern mirrors notebooks/_shared/education/walkthroughs/adk2_01_graph_lesson_planner.py.

Run with:
    uv run marimo edit notebooks/_shared/education/walkthroughs/adk2_06_schemas.py
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
        # ADK 2 · 06 schemas

        Per openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/.
        Mirrors docs/google_examples/adk2-tutorial + docs/google_examples/agent-valley-archive.

        See:
        - openspec/changes/2026-09-23-upgrade-to-adk2-pillars-1-2-3-v1/specs/adk2-pillars-orchestration/spec.md
        - agents/workflows/ + agents/meaisinfhoghlaim/_shared/
        - scripts/preflight_education.py + scripts/walk_education.py
        """
    )
    return


@app.cell
def _detail():
    import marimo as mo
    mo.md(
        """
        ## Walkthrough
        This notebook walks through the corresponding code, the
        educational context, and the relevant docs/google_examples
        reference. See adk2_01_graph_lesson_planner.py for the full
        template.
        """
    )
    return


if __name__ == "__main__":
    app.run()
