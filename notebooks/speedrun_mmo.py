from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""Speedrun MMO - the canonical Túatha educational MMO operator dashboard.

Per the 2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1
change - this single grouped marimo dashboard consolidates:
- 16_speedrun_mmo_00_celtic_nft.py
- 16_speedrun_mmo_01_mission_control.py
- 16_speedrun_mmo_01_language_staking.py
- 16_speedrun_mmo_02_cianfhoghlaim_mmo_progress.py
- 16_speedrun_mmo_02_token_shop.py
- 16_speedrun_mmo_03_quest_randomness.py
- 16_speedrun_mmo_04_item_exchange.py
- 16_speedrun_mmo_05..08_*.py

Into a single 7-tab grouped marimo notebook.

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
from notebooks._shared.area_shims.speedrun_mmo import SPEEDRUN_MMO_TABS


@app.cell(hide_code=True)
def _intro(mo):
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 🎮 Speedrun MMO (Túatha)

        The **canonical Túatha educational MMO operator dashboard**.
        Consolidates the 8 legacy speedrun MMO sub-notebooks into a
        single 7-tab grouped marimo notebook.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in SPEEDRUN_MMO_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Speedrun MMO assistant. You have access to the "
            "Túatha Celtic NFT collection (216 unique NFTs), the 100+ "
            "missions across 6 seasons, and the language staking pools "
            "(Irish / Welsh / Scottish Gaelic / Breton)."
        ),
        prompts=[
            "🎨 Show me my Celtic NFT collection",
            "🎯 What missions are available in Season 3?",
            "💰 What's the current staking APY for Irish tokens?",
            "📊 Show my MMO progress (level, XP, achievements)",
            "🛒 What items can I buy in the token shop?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Speedrun MMO (via litellm)"), _chat])


def _cli_main(argv=None):
    parser = cli_argparser_biep("speedrun_mmo")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "speedrun_mmo",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "seasons": 6,
        "missions": "100+",
        "note": (
            "Run via `marimo edit notebooks/speedrun_mmo.py` for the "
            "interactive console with 7 tabs."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)