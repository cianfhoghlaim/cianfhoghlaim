# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-8-jurisdiction-overview"
# ///

"""BIEP v3 8-jurisdiction overview — all 1,560 cohorts side-by-side (Ireland + England active; 5 deferred).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the cross-jurisdiction BIEP v3
pipelines. It exposes the canonical 8-cell surface and surfaces the
cohort matrix across all 8 British Isles jurisdictions.

8-cell structure:
1. **`_intro()`** — BIEP v3 milestone summary + 8-jurisdiction breakdown
2. **`_ibis_conn()`** — ibis-first connection
3. **`_commands()`** — canonical `mise run` + `dagster` + `openspec` commands
4. **`_cohort_matrix()`** — 8-jurisdiction cohort matrix (1,560 rows)
5. **`_drill_down()`** — per-jurisdiction drilldown
6. **`_schedule()`** — yearly + monthly + weekly + nightly + event-driven cron table
7. **`_asset_check_status()`** — live `dagster asset check` result
8. **`_dive_link()`** — link to the canonical MotherDuck Dives (per-jurisdiction)

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""

import marimo


# Centralized registries (per the `centralized-model-registry` capability).
# When the 4 artifacts are available, surface them in the dashboard
# header so operators know what models / pipelines / datasets / stacks
# are enabled in this deployment.
try:
    from meaisinfhoghlaim.models import MODEL_REGISTRY, model_for  # noqa: E402
    from notebooks._shared.schema import (  # noqa: E402
        list_dlt_sources, list_cocoindex_apps, list_baml_classes,
        read_deployment_choice,
    )
    _DEFAULT_LLM = model_for("text_llm", "default")
    _REGISTRY_SUMMARY = MODEL_REGISTRY.summary()
    _DLT_SOURCE_COUNT = len(list_dlt_sources())
    _COCO_APP_COUNT = len(list_cocoindex_apps())
    _BAML_CLASS_COUNT = len(list_baml_classes())
    _ENABLED_MODELS = sum(
        1 for v in read_deployment_choice().get("enabled_models", {}).values() if v
    )
except ImportError:
    # Fallback for minimal container builds where the registry is unavailable
    _DEFAULT_LLM = "minimax-m3"  # canonical M3 alias (the legacy hardcoded value)
    _REGISTRY_SUMMARY = {"total": 0, "by_family": {}, "available": 0, "deprecated": 0}
    _DLT_SOURCE_COUNT = _COCO_APP_COUNT = _BAML_CLASS_COUNT = 0
    _ENABLED_MODELS = 0

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


# -----------------------------------------------------------------------------
# Cell 1: Intro
# -----------------------------------------------------------------------------

@app.cell
def _intro():
    import marimo as mo
    from notebooks._shared.area_shims.leaving_cert import biiep_v3_overview
    mo.md(
        biiep_v3_overview("all")
        + "\n\n## 8-jurisdiction breakdown\n\n"
        + "| Jurisdiction | Stage | Active milestones | Cohorts (active + deferred) |\n"
        + "|:--|:--|:--|--:|\n"
        + "| 🇮🇪 Ireland | LC + JC | M1 + M2 | 100 active (12 LC + 88 JC) |\n"
        + "| 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England | A-Level + GCSE | M3 + M4 | 276 active (147 A-Level + 129 GCSE) |\n"
        + "| 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland | SQA | deferred to SCT/WLS/NI | 150 reserved |\n"
        + "| 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales | WJEC | deferred to SCT/WLS/NI | 160 reserved |\n"
        + "| 🇬🇧 Northern Ireland | CCEA | deferred to SCT/WLS/NI | 70 reserved |\n"
        + "| 🇯🇪 Jersey | IoQ | deferred to Crown | 120 reserved |\n"
        + "| 🇬🇬 Guernsey | IoQ | deferred to Crown | 120 reserved |\n"
        + "| 🇮🇲 Isle of Man | IoM | deferred to Crown | 120 reserved |\n"
        + "| **Total** | | **M0 + M1 + M2 + M3 + M4** | **376 active + 740 reserved = 1,116** |\n"
    )
    return (mo, biiep_v3_overview)


# -----------------------------------------------------------------------------
# Cell 2: ibis-first connection
# -----------------------------------------------------------------------------

@app.cell
def _ibis_conn(mo):
    """The ibis-first connection (per the BIEP v3 spec)."""
    from notebooks._shared.db import connect_md
    conn = connect_md()
    mo.md("✓ ibis-first wired — `md:cianfhoghlaim`")
    return (conn,)


# -----------------------------------------------------------------------------
# Cell 3: Commands
# -----------------------------------------------------------------------------

@app.cell
def _commands(mo):
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_OPERATOR_COMMANDS
    mo.md(
        "## Canonical BIEP v3 operator commands\n\n"
        "```bash\n"
        + "\n".join(BIEP_V3_OPERATOR_COMMANDS)
        + "\n```\n"
    )
    return (BIEP_V3_OPERATOR_COMMANDS,)


# -----------------------------------------------------------------------------
# Cell 4: Cohort matrix (8-jurisdiction)
# -----------------------------------------------------------------------------

@app.cell
def _cohort_matrix(conn, mo):
    """The 8-jurisdiction cohort matrix."""
    df = conn.sql(
        """
        SELECT
            jurisdiction,
            educational_stage AS stage,
            exam_board AS board,
            COUNT(*) AS subject_count,
            COUNT(DISTINCT subject_slug) AS distinct_subjects
        FROM cianfhoghlaim.education._registry.subjects
        WHERE status = 'ACTIVE'
        GROUP BY jurisdiction, educational_stage, exam_board
        ORDER BY jurisdiction, educational_stage, exam_board
        """
    ).execute()
    mo.ui.table(df, label="8-jurisdiction cohort matrix")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 5: Drill down — per-jurisdiction cohort details
# -----------------------------------------------------------------------------

@app.cell
def _drill_jurisdiction(mo):
    """Drill down on a single jurisdiction."""
    jurisdiction_dropdown = mo.ui.dropdown(
        options=[
            "ireland", "england", "scotland", "wales", "northern_ireland",
            "jersey", "guernsey", "isle_of_man",
        ],
        value="ireland",
        label="Jurisdiction",
    )
    return (jurisdiction_dropdown,)


@app.cell
def _drill_show(mo, conn, jurisdiction_dropdown):
    """Show the per-jurisdiction cohort details."""
    df = conn.sql(
        """
        SELECT subject_slug, educational_stage, exam_board, language, qualification_level
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction = ?
          AND status = 'ACTIVE'
        ORDER BY educational_stage, exam_board, subject_slug, language
        """,
        params=(jurisdiction_dropdown.value,),
    ).execute()
    mo.ui.table(df, label=f"{jurisdiction_dropdown.value.title()} cohorts")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 6: Schedule
# -----------------------------------------------------------------------------

@app.cell
def _schedule(mo):
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_CRON_SCHEDULE
    mo.md(
        "## BIEP v3 scheduling policy (all 8 jurisdictions)\n\n"
        "| Document class | Cadence | Cron |\n"
        "|:--|:--|:--|\n"
        + "\n".join(
            f"| {s['document_class']} | {s['cadence']} | `{s['cron']}` |"
            for s in BIEP_V3_CRON_SCHEDULE
        )
        + "\n\n"
        + "### Per-jurisdiction cron schedules (active)\n\n"
        + "| Jurisdiction | Cron | M0 + M1+M2 + M3+M4 |\n"
        + "|:--|:--|:--|\n"
        + "| Ireland LC | `0 0 1 9 *` (yearly) | M0 + M1 |\n"
        + "| Ireland JC | `0 0 1 9 *` (yearly) | M0 + M2 |\n"
        + "| England A-Level | `0 0 1 9 *` (yearly) | M0 + M3 |\n"
        + "| England GCSE | `0 0 1 9 *` (yearly) | M0 + M4 |\n"
        + "| gov.ie circulars | `0 0 1 * *` (monthly) | (not jurisdiction-scoped) |\n"
        + "| M0 foundation | `0 6 * * 1` (weekly) | (all jurisdictions) |\n"
        + "| RAGAS + audit | `0 0 * * *` (nightly) | (all jurisdictions) |\n"
    )
    return (BIEP_V3_CRON_SCHEDULE,)


# -----------------------------------------------------------------------------
# Cell 7: Asset check status
# -----------------------------------------------------------------------------

@app.cell
def _asset_check_button(mo):
    """Run-button to invoke the live `dagster asset check` for the BIEP v3 M0 foundation assets."""
    import subprocess

    def _run_asset_check() -> str:
        """Run the canonical `dagster asset check` and return the result as a markdown string."""
        checks = (
            "lakehouse_smoke_test_check,baml_codegen_check,"
            "registry_seed_check,lance_namespace_check"
        )
        try:
            result = subprocess.run(
                [
                    "uv", "run", "dagster", "asset", "check",
                    "--select", checks,
                    "-m", "orchestration.definitions",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            return (
                f"### Asset check result for M0 foundation\n\n"
                f"**Checks**: `{checks}`\n\n"
                f"**Exit code**: `{result.returncode}`\n\n"
                f"```\n{result.stdout[-1000:]}\n```\n\n"
                f"```\n{result.stderr[-500:]}\n```\n"
            )
        except Exception as exc:  # noqa: BLE001
            return f"**Error running `dagster asset check`**: `{exc}`\n\nRun `mise install` first to ensure the `dagster` CLI is in PATH.\n"

    run_button = mo.ui.run_button(label="Run `dagster asset check` (M0 foundation)")
    return (_run_asset_check, run_button)


@app.cell
def _asset_check_status(mo, _run_asset_check, run_button):
    """Display the live `dagster asset check` result for the M0 foundation assets."""
    if run_button.value:
        result_md = _run_asset_check()
        mo.md(result_md)
    else:
        mo.md(
            "Click **Run `dagster asset check` (M0 foundation)** to invoke the live asset check.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 8: Dive link
# -----------------------------------------------------------------------------

@app.cell
def _dive_link(mo):
    """Link to the canonical MotherDuck Dives for all 8 jurisdictions."""
    mo.md(
        "## Canonical MotherDuck Dives (per-jurisdiction)\n\n"
        "- **`ireland_lc_syllabus_topics`** — Ireland LC (12 cohorts)\n"
        "- **`ireland_jc_curriculum_topics`** — Ireland JC (88 cohorts)\n"
        "- **`england_a_level_topics`** — England A-Level (147 cohorts)\n"
        "- **`england_a_level_complexity`** — England A-Level mark allocation\n"
        "- **`england_gcse_topics`** — England GCSE (129 cohorts)\n"
        "- **`england_gcse_complexity`** — England GCSE mark allocation\n"
        "- **`sct_topics`** — reserved (Scotland, 150 cohorts)\n"
        "- **`wls_topics`** — reserved (Wales, 160 cohorts)\n"
        "- **`ni_topics`** — reserved (Northern Ireland, 70 cohorts)\n"
        "- **`jersey_topics`** — reserved (Jersey, 120 cohorts)\n"
        "- **`guernsey_topics`** — reserved (Guernsey, 120 cohorts)\n"
        "- **`isle_of_man_topics`** — reserved (Isle of Man, 120 cohorts)\n\n"
        "### Flights (yearly, runs `mise run biep:v3:m<N>` + writes status)\n\n"
        "- **`ireland_lc_daily_sync_flight`** — M1\n"
        "- **`ireland_jc_daily_sync_flight`** — M2\n"
        "- **`england_a_level_daily_sync_flight`** — M3\n"
        "- **`england_gcse_daily_sync_flight`** — M4\n"
    )
    return


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
