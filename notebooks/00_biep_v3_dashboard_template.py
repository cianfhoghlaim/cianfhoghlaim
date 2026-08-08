# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13",
#   "ibis-framework[duckdb]>=9.0",
#   "pandas>=2.2",
#   "altair>=5.0",
#   "pyarrow>=15",
#   "anywidget>=0.9",
#   "traitlets>=5.14",
# ]
# ///

"""BIEP v3 Dashboard Template — the canonical 8-cell template for any new BIEP jurisdiction dashboard.

This template is the SINGLE FUNCTION CALL pattern that any new BIEP v3
jurisdiction dashboard should start from. The 8-cell BIEP v3 operator
console is wrapped in a `mo.ui.tabs` widget via
`build_biep_v3_dashboard()` from
`notebooks/_shared/area_shims/biiep_v3_dashboard.py`.

To create a new BIEP v3 dashboard for a new jurisdiction, copy this
file and change ONLY the `build_biep_v3_dashboard(jurisdiction=...)`
call:

```python
tabs = build_biep_v3_dashboard(jurisdiction="new_jurisdiction", milestone="M5")
```

That's it. The full 7-tab operator console is rendered (Overview /
Cohorts / Drill / Schedule / Asset Checks / Dives / Activity).

## The 8 pillars of improvement (applied via the helper modules)

R1 — `setup_biep_registry_header()` — collapses the 14-line
    `try/except ImportError` header.
R2 — `build_biep_v3_dashboard()` — collapses the open-coded 8 cells.
R3 — `mo.ui.tabs` wrapping (per P1).
R4 — Dual-mode CLI per https://docs.marimo.io/guides/scripts/.
P1 — Tabbed operator console.
P2 — Live progress + form gating.
P3 — LLM-assisted analysis tab.
P4 — 3-column multi-pane grid layout.
P5 — RAGAS gauge widget (anywidget).
P6 — Dual-mode CLI.

## KCG patterns used
- marimo (per `.agents/skills/marimo/SKILL.md`) — every marimo v14
  idiom demonstrated.
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query goes through
  `notebooks/_shared/db.py:connect_md()` (ibis-first).
- BIEP v3 systematic download — the 5-milestone plan + 4-cadence
  scheduling per the BIEP v3 spec.

Reference: openspec/changes/2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1/
"""
import marimo

from notebooks._shared.area_shims.biiep_v3_dashboard import (
    build_biep_v3_dashboard,
)
from notebooks._shared.marimo_patterns import (
    cli_argparser_biep,
    cli_main_if_argv,
    cli_payload_to_output,
    setup_biep_registry_header,
)


__generated_with = "0.14.10"
app = marimo.App(width="full")


# ────────────────────────────────────────────────────────────────────────────
# Cell 1: Setup + R1 — `setup_biep_registry_header()`
# ────────────────────────────────────────────────────────────────────────────

@app.cell(hide_code=True)
def _intro(mo):
    """The canonical BIEP v3 dashboard intro cell."""
    _ctx = setup_biep_registry_header()
    mo.md(
        f"""
        # 📋 BIEP v3 Dashboard Template

        This is the **canonical 8-cell template** for any new BIEP v3
        jurisdiction dashboard. To create a new dashboard, copy this
        file and change the `build_biep_v3_dashboard(jurisdiction=...)`
        call.

        **Registry**: `{_ctx['registry_summary']}` ({_ctx['dlt_source_count']} DLT + {_ctx['coco_app_count']} CocoIndex + {_ctx['baml_class_count']} BAML)
        **Default LLM**: `{_ctx['default_llm']}` ({_ctx['enabled_models']} enabled in `deployment-choice.yaml`)

        ## Run modes

        - **Marimo mode**: `marimo edit notebooks/<your_dashboard>.py`
        - **CLI mode**: `python notebooks/<your_dashboard>.py --milestone m1 --asset-check documents_ingested`

        Per https://docs.marimo.io/guides/scripts/ — the CLI mode
        emits a JSON payload to stdout (for `mise run biep:v3:gate`
        consumption).
        """
    )
    return (_ctx, mo)


# ────────────────────────────────────────────────────────────────────────────
# Cell 2: The single `build_biep_v3_dashboard()` call (R2/R3/P1-P5)
# ────────────────────────────────────────────────────────────────────────────

@app.cell
def _dashboard(mo):
    """The single composable call — the entire 7-tab operator console.

    Change `jurisdiction` to point at your jurisdiction. Set
    `milestone` to your BIEP v3 milestone (M0-M4). Set `deferred=True`
    if the jurisdiction is deferred (SCT/WLS/NI + Crown).
    """
    tabs = build_biep_v3_dashboard(
        jurisdiction="ireland",  # ← CHANGE THIS to your jurisdiction
        milestone="M1",         # ← CHANGE THIS to your milestone
        deferred=False,          # ← SET TO True if deferred
    )
    tabs
    return (tabs,)


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv: list[str] | None = None) -> int:
    """CLI entry point — emits a JSON payload describing the dashboard.

    Per https://docs.marimo.io/guides/scripts/ — when run with CLI args,
    this script emits JSON to stdout (the marimo runtime is skipped).
    The CI gate `mise run biep:v3:gate` pipes this JSON for assertion.
    """
    import json
    parser = cli_argparser_biep("00_biep_v3_dashboard_template")
    args = parser.parse_args(argv)

    payload = {
        "notebook": "00_biep_v3_dashboard_template",
        "jurisdiction": args.jurisdiction,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "cohort_kind": args.cohort_kind,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "This is the canonical BIEP v3 dashboard template. "
            "Copy this file and change `build_biep_v3_dashboard(jurisdiction=...)` "
            "to point at your jurisdiction."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)