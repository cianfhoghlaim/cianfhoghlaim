from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""BIEP v3 England GCSE pipeline dashboard — 9 subjects × 3 awarding bodies.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-3.3): the 9 GCSE subjects (per the canonical
GCSESubjectSlug enum) get their own dashboard.

This is the **operator console** for the England BIEP v3 GCSE
pipeline. The 8-cell operator console is hoisted into
`notebooks/_shared/biiep_v3_dashboard_v2.py:build_biep_v3_dashboard()`,
wrapped in `mo.ui.tabs` (P1), and includes:
- RAGAS gauge widget (P5)
- `mo.ui.chat` streaming (per the marimo_baml helper)
- 4 stage factory wiring (per the 4_stage_factory.py)

Cross-references:
- `baml_src/british_isles/_shared/gcse_extraction_template.baml`
- `agents/adk/gcse_subject_agent.py`
- `cocoindex/biep_parity/4_stage_factory.py`
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full", app_title="BIEP v3 — GCSE")


@app.cell
def _():
    from notebooks._shared.biiep_v3_dashboard_v2 import build_biep_v3_dashboard
    tabs = build_biep_v3_dashboard(
        jurisdiction="england_gcse",
        milestone="M4",
    )
    tabs
    return (tabs,)


@app.cell
def _(tabs):
    import marimo as mo
    mo.md(
        f"""
        # GCSE (England, ages 14-16)

        ## 9 GCSE Subjects × 3 Awarding Bodies

        **Subjects**: Mathematics, English Language, English Literature,
        Biology, Chemistry, Physics, History, Geography, Religious Studies

        **Awarding Bodies**: AQA, OCR, Edexcel

        ## 4 Cell Operator Console

        {tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()