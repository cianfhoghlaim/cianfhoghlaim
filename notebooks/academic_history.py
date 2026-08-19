from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Academic History - the canonical M.Sc. AI 25/26 academic history dashboard.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change - this single grouped marimo dashboard consolidates:
- 17_academic_history_01_uog_maths_corpus_overview.py
- 17_academic_history_02_module_syllabus_assessment_map.py
- 17_academic_history_03_statistics_methods_lab.py
- 17_academic_history_04_numerical_analysis_lab.py
- 17_academic_history_05_nonlinear_systems_lab.py
- 17_academic_history_06_formulas_theorems_worked_solutions.py
- 17_academic_history_07_assignments_exams_answers.py
- 17_academic_history_08_academic_history_chat.py

Into a single 8-tab grouped marimo notebook.

Reference: openspec/changes/2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="full")


from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    llm_chat_with_prompts,
    setup_biep_registry_header,
    tabbed_biep_operator_console,
)
from notebooks._shared.area_shims.academic_history import ACADEMIC_HISTORY_TABS


@app.cell(hide_code=True)
def _intro(mo):
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 🎓 Academic History (M.Sc. AI 25/26)

        The **canonical UoG M.Sc. AI academic history dashboard**.
        Consolidates the 8 legacy academic history sub-notebooks into a
        single 8-tab grouped marimo notebook.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in ACADEMIC_HISTORY_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Academic History assistant. You have access to the "
            "M.Sc. AI 25/26 corpus (250 documents, 12 modules, 1000+ formulas "
            "+ theorems, 250+ past assignments + exam papers)."
        ),
        prompts=[
            "📚 List all 12 M.Sc. AI modules with ECTS weightings",
            "📊 Find statistics methods for survival analysis",
            "🔢 Show me Newton-Raphson method for root finding",
            "〰️ Explain logistic map bifurcation diagram",
            "🔣 What's the spectral theorem for symmetric matrices?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Academic History (via litellm)"), _chat])


def _cli_main(argv=None):
    parser = cli_argparser_biep("academic_history")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "academic_history",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "modules": 12,
        "semesters": 2,
        "note": (
            "Run via `marimo edit notebooks/academic_history.py` for the "
            "interactive console with 8 tabs."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)