# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-england-dashboard"
# ///

"""BIEP v3 England pipeline dashboard — England A-Level (147 cohorts) + GCSE (129 cohorts) = 276 total.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the England BIEP v3 pipelines. It
exposes the canonical 8-cell surface:

1. **`_intro()`** — BIEP v3 milestone summary + scheduling policy
2. **`_ibis_conn()`** — ibis-first connection (per the BIEP v3 spec)
3. **`_commands()`** — canonical `mise run` + `dagster` + `openspec` commands
4. **`_cohort_matrix()`** — 276-row England cohort matrix (147 A-Level + 129 GCSE)
5. **`_drill_down()`** — per-board × per-subject cohort drilldown
6. **`_schedule()`** — yearly + monthly + weekly + nightly + event-driven cron table
7. **`_asset_check_status()`** — live `dagster asset check` result
8. **`_dive_link()`** — link to the canonical MotherDuck Dives

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- marimo (per `.agents/skills/marimo/SKILL.md`).
- BIEP v3 systematic download — 5-milestone plan + 4-cadence scheduling.

TABLES:
- cianfhoghlaim.education.england.a_level.<board>.<subject>.voted_canonical  (147 rows: 49 × 3)
- cianfhoghlaim.education.england.gcse.<board>.<subject>.voted_canonical  (129 rows: 43 × 3)

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""

import marimo

__generated_with_marimo__ = "0.13.0"
app = marimo.App(width="full")


# -----------------------------------------------------------------------------
# Cell 1: Intro
# -----------------------------------------------------------------------------

@app.cell
def _intro():
    import marimo as mo
    from notebooks._shared.area_shims.leaving_cert import biiep_v3_overview
    mo.md(biep_v3_overview("england"))
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
# Cell 4: Cohort matrix (276 rows: 147 A-Level + 129 GCSE)
# -----------------------------------------------------------------------------

@app.cell
def _cohort_matrix(conn, mo):
    """The 276-row England cohort matrix (147 A-Level + 129 GCSE)."""
    df = conn.sql(
        """
        SELECT exam_board, subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education.england.a_level
        GROUP BY exam_board, subject_slug, qualification_level, language
        UNION ALL BY NAME
        SELECT exam_board, subject_slug, qualification_level, language, COUNT(*)
        FROM cianfhoghlaim.education.england.gcse
        GROUP BY exam_board, subject_slug, qualification_level, language
        ORDER BY qualification_level, exam_board, subject_slug, language
        """
    ).execute()
    mo.ui.table(df, label="276 England cohorts (147 A-Level + 129 GCSE)")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 5: Drill down — per-board × per-subject cohort drilldown
# -----------------------------------------------------------------------------

@app.cell
def _drill_level(mo):
    """Drill down on a single qualification level."""
    level_dropdown = mo.ui.dropdown(
        options=["a_level", "gcse"],
        value="a_level",
        label="Qualification level",
    )
    return (level_dropdown,)


@app.cell
def _drill_board(mo, level_dropdown):
    """Drill down on a single awarding board."""
    if level_dropdown.value == "a_level":
        label = "A-Level awarding board (49 subjects × 3 = 147 cohorts)"
    else:
        label = "GCSE awarding board (43 subjects × 3 = 129 cohorts)"
    board_dropdown = mo.ui.dropdown(
        options=["aqa", "ocr", "edexcel"],
        value="aqa",
        label=label,
    )
    return (board_dropdown,)


@app.cell
def _drill_show(mo, level_dropdown, board_dropdown):
    """Show the per-board × per-level RAGAS score + chunk count + sample subject drilldown."""
    from notebooks._shared.db import compute_ragas_distribution
    if level_dropdown.value == "a_level":
        ragas_kind = "a_level"
    else:
        ragas_kind = "gcse"
    ragas = compute_ragas_distribution(ragas_kind)
    mo.md(
        f"## Per-board drill-down: `{level_dropdown.value} / {board_dropdown.value}`\n\n"
        f"- **Qualification level**: `{level_dropdown.value}`\n"
        f"- **Awarding board**: `{board_dropdown.value}`\n"
        f"- **Cohort kind**: `{ragas_kind}`\n"
        f"- **Avg RAGAS score**: `{ragas['avg_ragas_score']:.3f}`\n"
        f"- **Min / max RAGAS**: `{ragas['min_ragas_score']:.3f}` / `{ragas['max_ragas_score']:.3f}`\n"
        f"- **Cohorts (kind)**: `{ragas['cohort_count']}`\n"
        f"- **Passing cohorts (RAGAS >= 0.70)**: `{ragas['passing_cohorts']}`\n"
        f"- **Status**: `{ragas['status']}`\n"
    )
    return (ragas,)


# -----------------------------------------------------------------------------
# Cell 6: Schedule
# -----------------------------------------------------------------------------

@app.cell
def _schedule(mo):
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_CRON_SCHEDULE
    mo.md(
        "## BIEP v3 scheduling policy\n\n"
        "| Document class | Cadence | Cron |\n"
        "|:--|:--|:--|\n"
        + "\n".join(
            f"| {s['document_class']} | {s['cadence']} | `{s['cron']}` |"
            for s in BIEP_V3_CRON_SCHEDULE
        )
        + "\n\n"
        + "### ChangeDetection.io sensors (England-specific)\n\n"
        + "- `bonneagar/stacks/changedetection/monitors/aqa_monitor.yaml` — AQA GCSE + A-Level specs\n"
        + "- `bonneagar/stacks/changedetection/monitors/ocr_monitor.yaml` — OCR GCSE + A-Level specs\n"
        + "- `bonneagar/stacks/changedetection/monitors/edexcel_monitor.yaml` — Edexcel GCSE + A-Level specs\n"
        + "- `orchestration/sensors/jcq_registry_sensor.py` — polls the registry every 5 minutes; "
        + "triggers the 4-path ensemble when a new spec is published\n"
    )
    return (BIEP_V3_CRON_SCHEDULE,)


# -----------------------------------------------------------------------------
# Cell 7: Asset check status
# -----------------------------------------------------------------------------

@app.cell
def _asset_check_button(mo):
    """Run-button to invoke the live `dagster asset check` for the England BIEP v3 assets."""
    import subprocess

    def _run_asset_check(per_milestone: str = "m3") -> str:
        """Run the canonical `dagster asset check` and return the result as a markdown string."""
        asset_check_map = {
            "m3": "england_a_level_documents_ingested_check,england_a_level_extractions_ragas_check,england_a_level_lance_chunks_check",
            "m4": "england_gcse_documents_ingested_check,england_gcse_extractions_ragas_check,england_gcse_lance_chunks_check",
        }
        checks = asset_check_map.get(per_milestone, asset_check_map["m3"])
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
                f"### Asset check result for `{per_milestone.upper()}`\n\n"
                f"**Checks**: `{checks}`\n\n"
                f"**Exit code**: `{result.returncode}`\n\n"
                f"```\n{result.stdout[-1000:]}\n```\n\n"
                f"```\n{result.stderr[-500:]}\n```\n"
            )
        except Exception as exc:  # noqa: BLE001
            return f"**Error running `dagster asset check`**: `{exc}`\n\nRun `mise install` first to ensure the `dagster` CLI is in PATH.\n"

    milestone_dropdown = mo.ui.dropdown(
        options=["m3", "m4"],
        value="m3",
        label="Milestone",
    )
    run_button = mo.ui.run_button(label="Run `dagster asset check`")
    return (_run_asset_check, milestone_dropdown, run_button)


@app.cell
def _asset_check_status(mo, _run_asset_check, milestone_dropdown, run_button):
    """Display the live `dagster asset check` result for the selected milestone."""
    if run_button.value:
        result_md = _run_asset_check(milestone_dropdown.value)
        mo.md(result_md)
    else:
        mo.md(
            f"Click **Run `dagster asset check`** to invoke the live asset check "
            f"for the `{milestone_dropdown.value.upper()}` milestone.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 8: Dive link
# -----------------------------------------------------------------------------

@app.cell
def _dive_link(mo):
    """Link to the canonical MotherDuck Dives for England."""
    mo.md(
        "## Canonical MotherDuck Dives for England\n\n"
        "- **`england_a_level_topics`** — read the 147 per-cohort DuckLake tables; "
        "surfaces topic + learning-outcome frequency per board per subject with RAGAS score histogram\n"
        "  (DAG: `motherduck/dives/england_a_level_topics.py`)\n"
        "- **`england_a_level_complexity`** — mark-allocation + assessment-objective "
        "distribution per board per subject\n"
        "  (DAG: `motherduck/dives/england_a_level_complexity.py`)\n"
        "- **`england_gcse_topics`** — same as A-Level but for GCSE (43 subjects × 3 = 129 cohorts)\n"
        "  (DAG: `motherduck/dives/england_gcse_topics.py`)\n"
        "- **`england_gcse_complexity`** — same as A-Level complexity but for GCSE\n"
        "  (DAG: `motherduck/dives/england_gcse_complexity.py`)\n\n"
        "### Flights (yearly, runs `mise run biep:v3:m<N>` + writes status)\n\n"
        "- **`england_a_level_daily_sync_flight`** — runs M3, replicates to LanceDB, writes "
        "`cianfhoghlaim.education.england._audit.daily_sync_status`\n"
        "  (DAG: `motherduck/flights/england_a_level_daily_sync_flight.py`)\n"
        "- **`england_gcse_daily_sync_flight`** — runs M4, same flow as the A-Level flight\n"
        "  (DAG: `motherduck/flights/england_gcse_daily_sync_flight.py`)\n"
    )
    return


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
