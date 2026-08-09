# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# [tool.uv]
# package = "biep-v3-crown-dashboard"
# ///

"""BIEP v3 Crown Dependencies pipeline dashboard — 360 cohorts (deferred).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change +
the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change.

This is the **operator console** for the Crown Dependencies BIEP v3
pipelines (Jersey + Guernsey + Isle of Man). The 360 cohorts (Jersey
120 + Guernsey 120 + Isle of Man 120) are **deferred** to a follow-up
change. The current notebook renders the BIEP v3 8-cell surface in
**preview mode**.

Uses the canonical `build_biep_v3_dashboard()` helper with the Crown
jurisdiction + `deferred=True`.

Reference: openspec/changes/2026-08-13-biep-v3-crown-dependencies-v1/ (deferred change)
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(
    width="full",
    layout_file="22_crown_dependencies_dashboard.grid.json",
)


# R2/R3 + P1-P5: The single composable call (preview mode).
from notebooks._shared.area_shims.biiep_v3_dashboard import (
    build_biep_v3_dashboard,
)
from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    setup_biep_registry_header,
)


@app.cell(column=0, hide_code=True)
def _intro(mo):
    """The Crown Dependencies intro cell — E1 + E4 + DEFERRED banner."""
    _ctx = setup_biep_registry_header()
    mo.callout(
        mo.md(
            """
            ⚠️ **DEFERRED**: The 360 cohorts (Jersey 120 + Guernsey 120 + Isle of Man 120)
            are deferred to the follow-up change `2026-08-13-biep-v3-crown-dependencies-v1`.

            The current notebook renders the BIEP v3 8-cell surface in **preview mode**.
            """
        ),
        kind="warn",
    )
    mo.md(
        f"""
        # 🇯🇪🇬🇬🇮🇲 BIEP v3 — Crown Dependencies Pipeline Dashboard (Deferred)

        **360 cohorts** (Jersey 120 + Guernsey 120 + Isle of Man 120) across IoQ / GCSE / A-Level.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell(column=1)
def _dashboard(mo):
    """The single composable call — the entire 7-tab operator console (preview mode)."""
    tabs = build_biep_v3_dashboard(
        jurisdiction="crown",
        milestone=None,
        deferred=True,
    )
    tabs
    return (tabs,)


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits an informational payload (DAGSTER assets are deferred)."""
    parser = cli_argparser_biep("22_crown_dependencies_dashboard")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "22_crown_dependencies_dashboard",
        "jurisdiction": "crown",
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "deferred",
        "exit_code": 0,
        "note": (
            "The Crown assets don't exist yet. The check will return exit code 1. "
            "Tracked by the follow-up change `2026-08-13-biep-v3-crown-dependencies-v1`."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)