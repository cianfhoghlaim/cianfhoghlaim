# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///

"""Sync Health - the canonical 11-sync-layer health dashboard.

Per the 2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1
change - this single grouped marimo dashboard consolidates:
- 14_dev_env_tools_05..10_*.py (6 sub-notebooks)
- 15_observability_01..03_*.py (3 sub-notebooks)
- 25_dagster_sync_dashboard.py
- 26_baml_sync_dashboard.py
- 27_stacks_sync_dashboard.py
- 28_dlt_sync_dashboard.py
- 29_agents_sync_dashboard.py
- 30_notebooks_sync_dashboard.py

Into a single 11-tab grouped marimo notebook.

## The 11 sync layers

1. Overview - 11-layer status grid
2. Paths - Drift detection on repo paths
3. CCC - CocoIndex code semantic search
4. Cognee - Knowledge graph sync (11 clusters)
5. Skills - .agents/skills/ validation
6. MCP - 14 MCP servers health
7. Dagster - ~833 Dagster assets sync
8. BAML - 838 BAML classes + 7 clusters
9. Stacks - 89 Docker Compose stacks
10. Agents - 12-agent fleet sync
11. Notebooks - 60+ marimo notebooks sync

Reference: openspec/changes/2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1/
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
from notebooks._shared.area_shims.sync_health import (
    SYNC_HEALTH_TABS,
    build_sync_status_grid,
)


@app.cell(hide_code=True)
def _intro(mo):
    """The 11-layer status grid (the canonical "Overview" tab)."""
    _ctx = setup_biep_registry_header()
    _grid = build_sync_status_grid()
    mo.vstack([
        mo.md(
            f"""
            # 🔄 Sync Health Dashboard

            The **canonical 11-sync-layer health dashboard**. Consolidates
            the 10 legacy sync sub-notebooks into a single 11-tab grouped
            marimo notebook.

            **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
            **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
            """
        ),
        mo.md(_grid),
    ])
    return (_ctx, mo)


@app.cell
def _overview_tabs(mo):
    """The 10 per-layer tabs (plus the Overview from _intro)."""
    _tab_dict = {
        name: mo.md(content_fn())
        for name, content_fn in SYNC_HEALTH_TABS
    }
    tabs = tabbed_biep_operator_console(_tab_dict)
    tabs
    return (tabs,)


@app.cell
def _llm_tab(mo):
    """P3 - LLM-assisted sync health Q&A via mo.ui.chat + mo.ai.llm.openai()."""
    _chat = llm_chat_with_prompts(
        system_message=(
            "You are the Sync Health assistant. You have access to the "
            "11 sync layer statuses from `stedding/sync-reports/all-<date>.md`. "
            "When the user asks about a sync layer, refer to the most "
            "recent sync report."
        ),
        prompts=[
            "💡 Which sync layers are currently failing?",
            "💡 Show me the most recent 5 sync reports",
            "💡 Which MCP servers are unhealthy?",
            "💡 How many models are enabled in deployment-choice.yaml?",
            "💡 What's the status of the BAML schema sync?",
        ],
    )
    mo.vstack([mo.md("## 🤖 Ask the Sync Health (via litellm)"), _chat])


def _cli_main(argv=None):
    """CLI entry point - emits a sync health summary payload."""
    parser = cli_argparser_biep("sync_health")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "sync_health",
        "tab": "all",
        "status": "ok",
        "exit_code": 0,
        "sync_layers": [
            "paths", "ccc", "cognee", "skills", "mcp",
            "dagster", "baml", "stacks", "agents",
            "notebooks", "drift-docs",
        ],
        "note": (
            "Run `mise run sync:all` to refresh the sync reports, "
            "then re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)