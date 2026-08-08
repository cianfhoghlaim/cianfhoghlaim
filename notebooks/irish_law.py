# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///

"""Irish Law - the canonical Irish law operator dashboard.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change - this single grouped marimo dashboard consolidates:
- 11_irish_law_01_personal_injury_journey.py
- 11_irish_law_02_courts_index.py
- 11_irish_law_03_wrc_decision_search.py
- 11_irish_law_04_citizensinfo_rights.py
- 11_irish_law_05_gov_ie_law_corpus.py
- 11_irish_law_06_unified_cross_source_query.py

Into a single 6-tab grouped marimo notebook.

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
from notebooks._shared.area_shims.irish_law import IRISH_LAW_TABS


@app.cell(hide_code=True)
def _intro(mo):
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # ⚖️ Irish Law

        The **canonical Irish law operator dashboard**. Consolidates the
        6 legacy Irish law sub-notebooks into a single 6-tab grouped
        marimo notebook.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in IRISH_LAW_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Irish Law assistant. You have access to 5 sources: "
            "personal injury cases, court decisions (District / Circuit / "
            "High / Supreme), WRC decisions, Citizens Info rights, and the "
            "Gov.ie law corpus."
        ),
        prompts=[
            "🩹 What's the PIAB process for personal injury claims?",
            "⚖️ Find recent Supreme Court decisions on employment law",
            "📋 Search WRC for unfair dismissal decisions",
            "🏛️ What are my rights as a tenant under Irish law?",
            "📜 Find the Statute of Limitations for contract claims",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Irish Law (via litellm)"), _chat])


def _cli_main(argv=None):
    parser = cli_argparser_biep("irish_law")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "irish_law",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "sources": ["PIAB", "Courts", "WRC", "Citizens Info", "Gov.ie"],
        "note": (
            "Run via `marimo edit notebooks/irish_law.py` for the "
            "interactive console with 6 tabs."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)