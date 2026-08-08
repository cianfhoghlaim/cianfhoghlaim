# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# [tool.uv]
# package = "biep-v3-aistear-dashboard"
# ///

"""BIEP v3 Ireland Aistear (Early Childhood, ages 0-6) dashboard — 14 cohorts.

Per the 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1 change +
the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change.

This is the **operator console** for the Ireland Aistear BIEP v3
pipeline. Uses the canonical `build_biep_v3_dashboard()` helper with
the Ireland jurisdiction + the M-Aistear milestone.

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — every marimo v14 idiom.
- ibis (per `.agents/skills/ibis/SKILL.md`) — ibis-first contract.
- BIEP v3 4-stage Ireland rollout (Aistear → Primary → JC → LC).

TABLES:
- cianfhoghlaim.ireland.aistear.<theme>_<age_band>_<lang_medium>_chunks  (14 Apps)
- cianfhoghlaim.education.ireland.aistear._audit.aistear_audit  (14 audit rows)

Reference: openspec/changes/2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1/
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(
    width="full",
    layout_file="26_aistear_dashboard.grid.json",
)


# R2/R3 + P1-P5: The single composable call.
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
    """The Aistear intro cell — E1 + E4."""
    _ctx = setup_biep_registry_header()
    mo.callout(
        mo.md(
            """
            🎯 **M-Aistear acceptance gate** (per `2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1`):

            - `aistear_documents_ingested >= 14`
            - `aistear_extractions_ragas >= 0.70`
            - `aistear_lance_chunks >= 5_000`

            Run `mise run biep:v3:m-aistear` to materialise the 14 cohorts.
            """
        ),
        kind="warn",
    )
    mo.md(
        f"""
        # 🇮🇪 BIEP v3 — Ireland Aistear (Early Childhood, ages 0-6) Dashboard

        **14 cohorts** across 4 NCCA themes × 4 age bands × 3 language
        mediums (IRISH_MEDIUM / ENGLISH_MEDIUM / BILINGUAL):

        | Theme | Age Bands | Lang Mediums |
        |---|---|---|
        | WELL_BEING (Biú Folláine) | INFANTS / TODDLERS / PRE_SCHOOL | 3 lang mediums |
        | IDENTITY_BELONGING (Céannacht agus Muintearas) | INFANTS / TODDLERS / PRE_SCHOOL / EARLY_PRIMARY_BRIDGE | 3 lang mediums |
        | COMMUNICATING (Cumarsáid) | INFANTS / PRE_SCHOOL / EARLY_PRIMARY_BRIDGE | 3 lang mediums |
        | EXPLORING_THINKING (Taiscéalaíocht agus Smaointeoireacht) | INFANTS / PRE_SCHOOL / EARLY_PRIMARY_BRIDGE | 3 lang mediums |

        **Entrypoint**: `mise run biep:v3:m-aistear` (the canonical 5-phase pattern).

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell(column=1)
def _dashboard(mo):
    """The single composable call — the entire 7-tab operator console."""
    tabs = build_biep_v3_dashboard(
        jurisdiction="ireland",
        milestone="M-Aistear",
        deferred=False,
    )
    tabs
    return (tabs,)


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits the asset-check JSON payload."""
    import subprocess

    parser = cli_argparser_biep("26_aistear_dashboard")
    args = parser.parse_args(argv)

    asset_check_map = {
        ("m0", "documents_ingested"): "lakehouse_smoke_test_check,baml_codegen_check,registry_seed_check,lance_namespace_check",
        ("m-aistear", "documents_ingested"): "aistear_documents_ingested_check",
        ("m-aistear", "extractions_ragas"): "aistear_extractions_ragas_check",
        ("m-aistear", "lance_chunks"): "aistear_lance_chunks_check",
    }

    checks = asset_check_map.get((args.milestone, args.asset_check))
    if checks is None:
        payload = {
            "notebook": "26_aistear_dashboard",
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
            "notebook": "26_aistear_dashboard",
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
            "notebook": "26_aistear_dashboard",
            "milestone": args.milestone,
            "asset_check": args.asset_check,
            "status": "error",
            "error": str(exc),
        }
        print(cli_payload_to_output(payload, args.output))
        return 4


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)