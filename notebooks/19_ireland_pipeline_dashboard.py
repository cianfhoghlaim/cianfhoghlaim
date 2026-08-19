from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""BIEP v3 Ireland pipeline dashboard — Ireland LC (12 cohorts) + JC (88 cohorts) = 100 total.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change +
the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change
(which added the 6 marimo v14 features: tabbed operator console +
LLM-assisted analysis + RAGAS gauge widget + dual-mode CLI).

This is the **operator console** for the Ireland BIEP v3 pipelines. The
8-cell operator console is hoisted into
`notebooks/_shared/area_shims/biiep_v3_dashboard.py:build_biep_v3_dashboard()`,
wrapped in `mo.ui.tabs` (P1), and includes:
- RAGAS gauge widget (P5) — per-cohort visual RAGAS score
- LLM-assisted analysis tab (P3) — wired to the canonical litellm proxy
- 3-column multi-pane grid layout (P4)
- Dual-mode CLI per https://docs.marimo.io/guides/scripts/ (P6)

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — every marimo v14 idiom.
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query goes through
  `notebooks._shared.db.py:connect_md()` (ibis-first).
- BIEP v3 systematic download — the 5-milestone plan + 4-cadence scheduling.

TABLES:
- cianfhoghlaim.education.ireland.leaving_cycle.<subject>.<level>_<lang>  (12 rows: 6 subjects × 2 langs)
- cianfhoghlaim.education.ireland.junior_cycle.<subject>.<year>_<lang>  (36 rows: 18 subjects × 2 langs)
- cianfhoghlaim.education.ireland.junior_cycle.short_courses.<code>  (16 rows)
- cianfhoghlaim.education.ireland.junior_cycle.cbas.<cba_id>  (36 rows)

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
# P4 — 3-column multi-pane grid layout. The layout file is saved next
# to the notebook (the marimo runtime resolves the path relative to
# the notebook file at edit time).
app = marimo.App(
    width="full",
    layout_file="19_ireland_pipeline_dashboard.grid.json",
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


# ────────────────────────────────────────────────────────────────────────────
# Cell 1: Setup + R1 — `setup_biep_registry_header()`
# ────────────────────────────────────────────────────────────────────────────

@app.cell(column=0, hide_code=True)
def _intro(mo):
    """The Ireland BIEP v3 intro cell — E1 (section header) + E4 (milestone callout).

    2026-08-08 fix (per issue #152): the marimo `app.run()` script-runner
    invokes cell functions in a sandboxed namespace that does NOT see
    the module-scope imports. Re-import the function locally so the
    name is in the cell's local scope (works for the `marimo edit`
    UI; the CLI mode (`python notebooks/19_*.py --output=json`) takes
    a different path and doesn't hit the marimo runtime at all).
    """
    from notebooks._shared.marimo_patterns import setup_biep_registry_header
    _ctx = setup_biep_registry_header()
    mo.callout(
        mo.md(
            f"""
            🎯 **M1 acceptance gate** (per `2026-08-13-biep-v3-systematic-download-ireland-england-v1`):

            - `ireland_lc_documents_ingested >= 12`
            - `ireland_lc_extractions_ragas >= 0.70`
            - `ireland_lc_lance_chunks >= 12_000`

            The 3 asset checks MUST all pass before M2 (Ireland JC) can begin.
            Run `mise run biep:v3:ireland:gate --milestone=m1` for CI consumption.
            """
        ),
        kind="warn",
    )
    mo.md(
        f"""
        # 🇮🇪 BIEP v3 — Ireland Pipeline Dashboard

        **100 cohorts** across 12 Leaving Cycle (LC) + 88 Junior Cycle
        (JC) = 36 specs + 16 short courses + 36 CBAs.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled in `deployment-choice.yaml`)

        ## Run modes

        - **Marimo mode**: `marimo edit notebooks/19_ireland_pipeline_dashboard.py`
        - **CLI mode**: `python notebooks/19_ireland_pipeline_dashboard.py --milestone m1 --asset-check documents_ingested`

        Per https://docs.marimo.io/guides/scripts/ — the CLI mode
        emits a JSON payload to stdout (for `mise run biep:v3:gate`
        consumption).

        📚 **References**:
        - `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/`
        - `openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/`
        - `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md`
        - `openspec/specs/british-isles-education-pipeline-v3/spec.md`
        - `openspec/specs/centralized-model-registry/spec.md`
        - `notebooks/_shared/db.py:connect_md()`
        - `notebooks/_shared/area_shims/biiep_v3_dashboard.py:build_biep_v3_dashboard()`
        - `.agents/skills/marimo/SKILL.md`
        - `.agents/skills/ibis/SKILL.md`
        - https://docs.marimo.io/guides/scripts/
        """
    )
    return (_ctx, mo)


# ────────────────────────────────────────────────────────────────────────────
# Cell 2: The single `build_biep_v3_dashboard()` call (R2/R3/P1-P5)
# ────────────────────────────────────────────────────────────────────────────

@app.cell(column=1)
def _dashboard(mo):
    """The single composable call — the entire 7-tab operator console.

    R2/R3 + P1 + P3 + P5 — the 8-cell surface collapses into a single
    function call. Change `jurisdiction` to point at your jurisdiction.
    """
    tabs = build_biep_v3_dashboard(
        jurisdiction="ireland",
        milestone="M1",
        deferred=False,
    )
    tabs
    return (tabs,)


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits the asset-check JSON payload.

    Per https://docs.marimo.io/guides/scripts/ — when run with CLI args,
    this script emits JSON to stdout (the marimo runtime is skipped).
    The CI gate `mise run biep:v3:ireland:gate --milestone=m1` pipes this
    JSON for assertion.

    Usage:
        python notebooks/19_ireland_pipeline_dashboard.py --milestone m1 --asset-check documents_ingested --output json
    """
    import subprocess

    parser = cli_argparser_biep("19_ireland_pipeline_dashboard")
    args = parser.parse_args(argv)

    # The canonical asset check map (per the BIEP v3 spec)
    asset_check_map = {
        ("m0", "documents_ingested"): "lakehouse_smoke_test_check,baml_codegen_check,registry_seed_check,lance_namespace_check",
        ("m1", "documents_ingested"): "ireland_lc_documents_ingested_check",
        ("m1", "extractions_ragas"): "ireland_lc_extractions_ragas_check",
        ("m1", "lance_chunks"): "ireland_lc_lance_chunks_check",
        ("m2", "documents_ingested"): "ireland_jc_documents_ingested_check",
        ("m2", "extractions_ragas"): "ireland_jc_extractions_ragas_check",
        ("m2", "lance_chunks"): "ireland_jc_lance_chunks_check",
    }

    checks = asset_check_map.get((args.milestone, args.asset_check))
    if checks is None:
        payload = {
            "notebook": "19_ireland_pipeline_dashboard",
            "jurisdiction": args.jurisdiction,
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
            "notebook": "19_ireland_pipeline_dashboard",
            "jurisdiction": args.jurisdiction,
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
            "notebook": "19_ireland_pipeline_dashboard",
            "jurisdiction": args.jurisdiction,
            "milestone": args.milestone,
            "asset_check": args.asset_check,
            "checks": checks,
            "status": "error",
            "exit_code": -1,
            "error": str(exc),
        }
        print(cli_payload_to_output(payload, args.output))
        return 4


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)