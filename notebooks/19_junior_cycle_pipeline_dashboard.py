from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""BIEP v3 Junior Cycle pipeline dashboard — 8 NCCA Junior Cycle subjects at full scope.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-3.1): the 8 NCCA Junior Cycle subjects (Mathematics, English,
Gaeilge, Science, Geography, History, CSPE, SPHE) get their own dashboard.

This is the **operator console** for the Ireland BIEP v3 Junior Cycle
pipeline. The 8-cell operator console is hoisted into
`notebooks/_shared/biiep_v3_dashboard_v2.py:build_biep_v3_dashboard()`,
wrapped in `mo.ui.tabs` (P1), and includes:
- RAGAS gauge widget (P5)
- `mo.ui.chat` streaming (per the marimo_baml helper)
- 4 stage factory wiring (per the 4_stage_factory.py)

Cross-references:
- `baml_src/british_isles/_shared/junior_cycle_template.baml` (the 8 JC subjects)
- `agents/adk/jc_subject_agent.py` (the JC ADK agent)
- `cocoindex_flows/biep_parity/4_stage_factory.py` (the JC CocoIndex Apps)
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full", app_title="BIEP v3 — Junior Cycle")


@app.cell
def _():
    from notebooks._shared.biiep_v3_dashboard_v2 import build_biep_v3_dashboard
    tabs = build_biep_v3_dashboard(
        jurisdiction="ireland_jc",
        milestone="M3",
    )
    tabs
    return (tabs,)


@app.cell
def _(tabs):
    import marimo as mo
    # The Junior Cycle dashboard exposes 8 NCCA JC subjects at full scope
    mo.md(
        f"""
        # Junior Cycle (Ireland, ages 12-15)

        ## 8 NCCA JC Subjects at Full Scope

        1. **Mathematics** (`JC-MATH`)
        2. **English** (`JC-ENGL`)
        3. **Gaeilge** (`JC-GAEL`)
        4. **Science** (`JC-SCI`)
        5. **Geography** (`JC-GEOG`)
        6. **History** (`JC-HIST`)
        7. **CSPE** (Civic, Social, Political Education) (`JC-CSPE`)
        8. **SPHE** (Social, Personal, Health Education) (`JC-SPHE`)

        ## 4 Cell Operator Console

        {tabs}

        ## Cross-References

        - BAML template: `baml_src/british_isles/_shared/junior_cycle_template.baml`
        - ADK agent: `agents/adk/jc_subject_agent.py`
        - CocoIndex factory: `cocoindex_flows/biep_parity/4_stage_factory.py`
        - Dashboard helper: `notebooks/_shared/biiep_v3_dashboard_v2.py`
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    """The BAML chat for the JC stage (per Mega-3d Phase 2 wire-up).

    Routes through the canonical `make_baml_chat_for_stage` runtime
    helper from `notebooks/_shared/marimo_integration_runtime.py`.
    The stage = "jc" selects the JC_FUNCTIONS list from
    `notebooks/_shared/marimo_baml.py`.
    """
    from notebooks._shared.marimo_integration_runtime import (
        make_baml_chat_for_stage,
    )
    chat = make_baml_chat_for_stage(stage="jc", subject=None)
    if chat is None:
        return mo.md("BAML chat unavailable (baml-py not installed).")
    return chat


if __name__ == "__main__":
    app.run()