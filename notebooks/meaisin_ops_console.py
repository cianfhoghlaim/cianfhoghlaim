# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///

"""Meaisin Ops Console — the canonical 12-agent fleet operator dashboard.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change — this single grouped marimo dashboard consolidates:
- 60_meaisin_ireland_ops.py
- 61_meaisin_england_ops.py
- 62_meaisin_extraction_progress.py
- 63_meaisin_eval_dashboard.py
- 64_meaisin_bilingual_curriculum.py

Into a single 6-tab grouped marimo notebook following the canonical
marimo v14 patterns (P1-P6 + R1-R4).

## The 6 tabs

1. Overview - 12-agent fleet summary + 4 surfaces
2. Ireland - Ireland LC + JC cohort ops (164 expected)
3. England - England A-Level + GCSE cohort ops (276 expected)
4. Extraction Progress - Per-cohort extraction drill-down
5. RAGAS Eval - Per-cohort RAGAS score + regression alerts
6. Bilingual Coverage - EN/GA bilingual coverage audit

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) - every marimo v14 idiom.
- ibis (per `.agents/skills/ibis/SKILL.md`) - ibis-first contract.
- centralized-registry (per `.agents/skills/centralized-registry/SKILL.md`).

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
from notebooks._shared.area_shims.meaisin import MEAISIN_OVERVIEW_TABS


@app.cell(hide_code=True)
def _intro(mo):
    """R1 - `setup_biep_registry_header()` + the meaisin console intro."""
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 🤖 Meaisin Ops Console

        The **canonical 12-agent fleet operator dashboard**. Consolidates
        the 5 legacy meaisin ops dashboards into a single 6-tab grouped
        marimo notebook.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    """The 6-tab operator console (P1 - mo.ui.tabs)."""
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in MEAISIN_OVERVIEW_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    """P3 - LLM-assisted analysis tab via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Meaisin 12-agent fleet operator console assistant. "
            "You have access to the 12 agents across 4 surfaces (openclaw + "
            "openchamber + hermes + ocr-router). When the user asks about "
            "an agent or surface, refer to the meaisin agent registry."
        ),
        prompts=[
            "🤖 List all 12 agents and their domains",
            "📊 What's the current extraction completion % for Ireland LC Mathematics?",
            "🔍 Find cohorts where the RAGAS score has regressed by >0.05",
            "🌐 Show me the bilingual coverage for the Gaeilge LC curriculum",
            "📋 Generate a per-jurisdiction missing-subject audit",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Meaisin Ops Console (via litellm)"), _chat])


def _cli_main(argv=None):
    """CLI entry point - emits a meaisin agent fleet summary payload."""
    parser = cli_argparser_biep("meaisin_ops_console")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "meaisin_ops_console",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "agents": [
            "root", "curriculum", "translation", "corpus",
            "research", "education_research", "bunchloch_research",
            "geospatial", "statistics", "curriculum_comparison",
            "agui_curriculum", "mcp_curriculum",
        ],
        "note": (
            "Run `mise run agents:smoke` for the agent fleet smoke test, "
            "or `mise run agents:audit` for the registry audit."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)