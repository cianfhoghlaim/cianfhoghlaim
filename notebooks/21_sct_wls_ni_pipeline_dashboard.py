from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""BIEP v3 Scotland + Wales + Northern Ireland pipeline dashboard — 380 cohorts (deferred).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change +
the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change.

This is the **operator console** for the SCT + WLS + NI BIEP v3
pipelines. The 380 cohorts (Scotland 150 + Wales 160 + Northern
Ireland 70) are **deferred** to a follow-up change. The current
notebook renders the BIEP v3 8-cell surface in **preview mode**:
the cohort matrix queries the registry for placeholder rows; the
asset check status is informational.

Uses the canonical `build_biep_v3_dashboard()` helper with the
SCT/WLS/NI jurisdiction + `deferred=True`.

Reference: openspec/changes/2026-08-13-biep-v3-sct-wls-ni-v1/ (deferred change)
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(
    width="full",
    layout_file="21_sct_wls_ni_pipeline_dashboard.grid.json",
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
    """The SCT/WLS/NI intro cell — E1 + E4 + DEFERRED banner."""
    _ctx = setup_biep_registry_header()
    mo.callout(
        mo.md(
            """
            ⚠️ **DEFERRED**: The 380 cohorts (Scotland 150 + Wales 160 + Northern Ireland 70)
            are deferred to the follow-up change `2026-08-13-biep-v3-sct-wls-ni-v1`.

            The current notebook renders the BIEP v3 8-cell surface in **preview mode**:
            the cohort matrix queries the registry for placeholder rows; the asset check
            status is informational.
            """
        ),
        kind="warn",
    )
    mo.md(
        f"""
        # 🏴󠁧󠁢󠁳󠁣󠁴󠁿🏴󠁧󠁢󠁷󠁬󠁳󠁿🇬🇧 BIEP v3 — SCT + WLS + NI Pipeline Dashboard (Deferred)

        **380 cohorts** (Scotland 150 + Wales 160 + Northern Ireland 70) across
        SQA / WJEC / CCEA.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell(column=1)
def _dashboard(mo):
    """The single composable call — the entire 7-tab operator console (preview mode)."""
    tabs = build_biep_v3_dashboard(
        jurisdiction="scotland+wales+ni",
        milestone=None,
        deferred=True,
    )
    tabs
    return (tabs,)


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits an informational payload (DAGSTER assets are deferred)."""
    parser = cli_argparser_biep("21_sct_wls_ni_pipeline_dashboard")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "21_sct_wls_ni_pipeline_dashboard",
        "jurisdiction": "scotland+wales+ni",
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "deferred",
        "exit_code": 0,
        "note": (
            "The SCT/WLS/NI assets don't exist yet. The check will return exit code 1. "
            "Tracked by the follow-up change `2026-08-13-biep-v3-sct-wls-ni-v1`."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)