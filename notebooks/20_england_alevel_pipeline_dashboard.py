# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.14.10", "ibis-framework[duckdb]>=9.0", "duckdb>=1.0",
#   "pandas>=2.2", "altair>=5.0", "pyarrow>=15", "anywidget>=0.9",
#   "traitlets>=5.14", "python-dotenv>=1.0",
# ]
# [tool.uv]
# package = "biep-v3-england-alevel-dashboard"
# ///

"""BIEP v3 England A-Level pipeline dashboard — 15 subjects × 3 awarding bodies.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-3.2): the 15 A-Level subjects (per the canonical
ALevelSubjectSlug enum) get their own dashboard.

This is the **operator console** for the England BIEP v3 A-Level
pipeline. The 8-cell operator console is hoisted into
`notebooks/_shared/biiep_v3_dashboard_v2.py:build_biep_v3_dashboard()`,
wrapped in `mo.ui.tabs` (P1), and includes:
- RAGAS gauge widget (P5)
- `mo.ui.chat` streaming (per the marimo_baml helper)
- 4 stage factory wiring (per the 4_stage_factory.py)

Cross-references:
- `baml_src/british_isles/_shared/alevel_extraction_template.baml`
- `agents/adk/alevel_subject_agent.py`
- `cocoindex/biep_parity/4_stage_factory.py`
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full", app_title="BIEP v3 — A-Level")


@app.cell
def _():
    from notebooks._shared.biiep_v3_dashboard_v2 import build_biep_v3_dashboard
    tabs = build_biep_v3_dashboard(
        jurisdiction="england_alevel",
        milestone="M4",
    )
    tabs
    return (tabs,)


@app.cell
def _(tabs):
    import marimo as mo
    mo.md(
        f"""
        # A-Level (England, ages 16-18)

        ## 15 A-Level Subjects × 3 Awarding Bodies

        **Subjects**: Mathematics, Further Mathematics, English Literature,
        English Language, Biology, Chemistry, Physics, Psychology,
        History, Geography, Economics, Business, History of Art,
        Politics, Sociology

        **Awarding Bodies**: AQA, OCR, Edexcel

        ## 4 Cell Operator Console

        {tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()