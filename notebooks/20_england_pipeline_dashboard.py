# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# [tool.uv]
# package = "biep-v3-england-dashboard"
# ///

"""BIEP v3 England pipeline dashboard — England A-Level (147 cohorts) + GCSE (129 cohorts) = 276 total.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change +
the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change.

This is the **operator console** for the England BIEP v3 pipelines. The
8-cell operator console is hoisted into
`notebooks/_shared/area_shims/biiep_v3_dashboard.py:build_biep_v3_dashboard()`,
wrapped in `mo.ui.tabs` (P1), and includes:
- RAGAS gauge widget (P5)
- LLM-assisted analysis tab (P3)
- 3-column multi-pane grid layout (P4)
- Dual-mode CLI per https://docs.marimo.io/guides/scripts/ (P6)

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — every marimo v14 idiom.
- ibis (per `.agents/skills/ibis/SKILL.md`) — ibis-first contract.
- BIEP v3 systematic download — the 5-milestone plan + 4-cadence scheduling.

TABLES:
- cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical  (147 rows: 49 × 3)
- cianfhoghlaim.education.england.gcse.<board>.<subject>.voted_canonical  (129 rows: 43 × 3)

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(
    width="full",
    layout_file="20_england_pipeline_dashboard.grid.json",
)


# R2/R3 + P1-P5: The single composable call that replaces the open-coded
# 8-cell surface. The full 7-tab operator console is rendered via
# `build_biep_v3_dashboard()` (P1 = `mo.ui.tabs` wrapping).
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
    """The England BIEP v3 intro cell — E1 (section header) + E4 (milestone callout).

    2026-08-08 fix (per issue #152): the marimo `app.run()` script-runner
    invokes cell functions in a sandboxed namespace that does NOT see
    the module-scope imports. Re-import the function locally so the
    name is in the cell's local scope (works for the `marimo edit`
    UI; the CLI mode takes a different path).
    """
    from notebooks._shared.marimo_patterns import setup_biep_registry_header
    _ctx = setup_biep_registry_header()
    mo.callout(
        mo.md(
            """
            🎯 **M3 + M4 acceptance gates** (per `2026-08-13-biep-v3-systematic-download-ireland-england-v1`):

            - `england_a_level_documents_ingested >= 147 + england_a_level_extractions_ragas >= 0.70 + england_a_level_lance_chunks >= 147_000`
            - `england_gcse_documents_ingested >= 129 + england_gcse_extractions_ragas >= 0.70 + england_gcse_lance_chunks >= 129_000`

            Run `mise run biep:v3:england:gate --milestone=m3` for CI consumption.
            """
        ),
        kind="warn",
    )
    mo.md(
        f"""
        # 🏴󠁧󠁢󠁥󠁮󠁧󠁿 BIEP v3 — England Pipeline Dashboard

        **276 cohorts** across 147 A-Level (49 × 3 boards) + 129 GCSE
        (43 × 3 boards: AQA + OCR + Edexcel).

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)

        ## Run modes

        - **Marimo mode**: `marimo edit notebooks/20_england_pipeline_dashboard.py`
        - **CLI mode**: `python notebooks/20_england_pipeline_dashboard.py --milestone m3 --asset-check documents_ingested`

        📚 **References**:
        - `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/`
        - `openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/`
        - `notebooks/_shared/area_shims/biiep_v3_dashboard.py:build_biep_v3_dashboard()`
        - `.agents/skills/marimo/SKILL.md`
        """
    )
    return (_ctx, mo)


@app.cell(column=1)
def _dashboard(mo):
    """The single composable call — the entire 7-tab operator console."""
    tabs = build_biep_v3_dashboard(
        jurisdiction="england",
        milestone="M3",
        deferred=False,
    )
    tabs
    return (tabs,)


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits the asset-check JSON payload."""
    import subprocess

    parser = cli_argparser_biep("20_england_pipeline_dashboard")
    args = parser.parse_args(argv)

    asset_check_map = {
        ("m3", "documents_ingested"): "england_a_level_documents_ingested_check",
        ("m3", "extractions_ragas"): "england_a_level_extractions_ragas_check",
        ("m3", "lance_chunks"): "england_a_level_lance_chunks_check",
        ("m4", "documents_ingested"): "england_gcse_documents_ingested_check",
        ("m4", "extractions_ragas"): "england_gcse_extractions_ragas_check",
        ("m4", "lance_chunks"): "england_gcse_lance_chunks_check",
    }

    checks = asset_check_map.get((args.milestone, args.asset_check))
    if checks is None:
        payload = {
            "notebook": "20_england_pipeline_dashboard",
            "milestone": args.milestone,
            "asset_check": args.asset_check,
            "status": "unknown_milestone_or_asset_check",
            "exit_code": 2,
        }
        print(cli_payload_to_output(payload, args.output))
        return 2

    try:
        result = subprocess.run(
            [
                "uv", "run", "dagster", "asset", "check",
                "--select", checks,
                "-m", "orchestration.definitions",
            ],
            capture_output=True, text=True, timeout=120,
        )
        payload = {
            "notebook": "20_england_pipeline_dashboard",
            "milestone": args.milestone,
            "asset_check": args.asset_check,
            "checks": checks,
            "exit_code": result.returncode,
            "status": "passed" if result.returncode == 0 else "failed",
            "stdout_tail": result.stdout[-1000:],
            "stderr_tail": result.stderr[-500:],
        }
        print(cli_payload_to_output(payload, args.output))
        return 0 if result.returncode == 0 else 1
    except Exception as exc:  # noqa: BLE001
        payload = {
            "notebook": "20_england_pipeline_dashboard",
            "milestone": args.milestone,
            "asset_check": args.asset_check,
            "status": "error",
            "error": str(exc),
        }
        print(cli_payload_to_output(payload, args.output))
        return 4


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)