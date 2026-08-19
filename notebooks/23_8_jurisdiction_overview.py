from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES  # canonical PEP 723 template (per the 2026-11-25-mega-3c-marimo-and-integration-v1 change)

"""BIEP v3 8-jurisdiction overview — all 1,116 cohorts side-by-side (Ireland + England active; 5 deferred).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change +
the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change.

This is the **operator console** for the cross-jurisdiction BIEP v3
pipelines. It exposes the canonical 8-cell surface and surfaces the
cohort matrix across all 8 British Isles jurisdictions.

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — `mo.ui.tabs` wrapping
  + LLM-assisted analysis + dual-mode CLI per
  https://docs.marimo.io/guides/scripts/.
- ibis (per `.agents/skills/ibis/SKILL.md`) — ibis-first contract.

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""

import marimo

__generated_with = "0.14.10"
app = marimo.App(
    width="full",
    layout_file="23_8_jurisdiction_overview.grid.json",
)


# R1 + R3 + P3 + P5: Hoist the centralized-registry header + the LLM
# tab + the RAGAS gauge widget.
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
    """The 8-jurisdiction overview intro cell.

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
            🎯 **Cross-jurisdiction overview** — 8 British Isles jurisdictions + 2 scanner domains:

            | Jurisdiction | Stage | Active milestones | Cohorts (active + deferred) |
            |:--|:--|:--|--:|
            | 🇮🇪 Ireland | LC + JC | M1 + M2 | 100 active (12 LC + 88 JC) |
            | 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | A-Level + GCSE | M3 + M4 | 276 active (147 A-Level + 129 GCSE) |
            | 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | SQA | deferred to SCT/WLS/NI | 150 reserved |
            | 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales | WJEC | deferred to SCT/WLS/NI | 160 reserved |
            | 🇬🇧 Northern Ireland | CCEA | deferred to SCT/WLS/NI | 70 reserved |
            | 🇯🇪 Jersey | IoQ | deferred to Crown | 120 reserved |
            | 🇬🇬 Guernsey | IoQ | deferred to Crown | 120 reserved |
            | 🇮🇲 Isle of Man | IoM | deferred to Crown | 120 reserved |
            | **Total** | | **M0 + M1 + M2 + M3 + M4** | **376 active + 740 reserved = 1,116** |
            """
        ),
        kind="info",
    )
    mo.md(
        f"""
        # 🌍 BIEP v3 — 8-Jurisdiction Overview Dashboard

        The **cross-jurisdiction operator console** for the BIEP v3
        pipelines. The 8-cell surface is hoisted into
        `notebooks/_shared/area_shims/biiep_v3_dashboard.py:build_biep_v3_dashboard()`
        wrapped in `mo.ui.tabs` (P1).

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled)
        """
    )
    return (_ctx, mo)


@app.cell(column=1)
def _dashboard(mo):
    """The single composable call — the entire 8-jurisdiction operator console."""
    tabs = build_biep_v3_dashboard(
        jurisdiction="all",
        milestone=None,
        deferred=False,
    )
    tabs
    return (tabs,)


def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits a cross-jurisdiction summary payload."""
    import subprocess

    parser = cli_argparser_biep("23_8_jurisdiction_overview")
    args = parser.parse_args(argv)

    # The M0 foundation check covers all 8 jurisdictions
    checks = "lakehouse_smoke_test_check,baml_codegen_check,registry_seed_check,lance_namespace_check"

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
            "notebook": "23_8_jurisdiction_overview",
            "jurisdiction": "all",
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
            "notebook": "23_8_jurisdiction_overview",
            "milestone": args.milestone,
            "asset_check": args.asset_check,
            "status": "error",
            "error": str(exc),
        }
        print(cli_payload_to_output(payload, args.output))
        return 4


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)