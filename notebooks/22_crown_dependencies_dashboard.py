# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-crown-dashboard"
# ///

"""BIEP v3 Crown Dependencies pipeline dashboard — 360 cohorts (deferred).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the Crown Dependencies BIEP v3
pipelines (Jersey + Guernsey + Isle of Man). The 360 cohorts
(Jersey 120 + Guernsey 120 + Isle of Man 120) are **deferred to a
follow-up change** (`2026-08-13-biep-v3-crown-dependencies-v1`).

The current notebook renders the BIEP v3 8-cell surface in **preview mode**.

8-cell structure:
1. **`_intro()`** — BIEP v3 milestone summary + deferred status
2. **`_ibis_conn()`** — ibis-first connection
3. **`_commands()`** — canonical `mise run` + `dagster` + `openspec` commands
4. **`_cohort_matrix()`** — 360-row cohort matrix
5. **`_drill_down()`** — per-jurisdiction drilldown
6. **`_schedule()`** — yearly + monthly + weekly + nightly + event-driven cron table
7. **`_asset_check_status()`** — live `dagster asset check` result
8. **`_dive_link()`** — link to the canonical MotherDuck Dives (reserved)

Reference: openspec/changes/2026-08-13-biep-v3-crown-dependencies-v1/ (deferred change)
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
    mo.md(
        biiep_v3_overview("crown")
        + "\n\n## Status\n\n"
        + "**DEFERRED**: The 360 cohorts (Jersey 120 + Guernsey 120 + Isle of Man 120) "
        + "are deferred to a follow-up change "
        + "(`2026-08-13-biep-v3-crown-dependencies-v1`).\n\n"
        + "The current notebook renders the BIEP v3 8-cell surface in **preview mode**.\n"
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
    mo.md(
        "✓ ibis-first wired — `md:cianfhoghlaim`\n\n"
        "⚠️ The Crown Dependencies pipelines are deferred. The queries below return "
        "registry placeholder rows; the asset checks return informational only."
    )
    return (conn,)


# -----------------------------------------------------------------------------
# Cell 3: Commands
# -----------------------------------------------------------------------------

@app.cell
def _commands(mo):
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_OPERATOR_COMMANDS
    mo.md(
        "## Canonical BIEP v3 operator commands (deferred for Crown)\n\n"
        "The Crown Dependencies pipelines are deferred to a follow-up change. The "
        "commands below show the Ireland + England commands that are **active** today.\n\n"
        "```bash\n"
        + "\n".join(BIEP_V3_OPERATOR_COMMANDS)
        + "\n```\n"
    )
    return (BIEP_V3_OPERATOR_COMMANDS,)


# -----------------------------------------------------------------------------
# Cell 4: Cohort matrix (360 rows: 120 Jersey + 120 Guernsey + 120 IoM)
# -----------------------------------------------------------------------------

@app.cell
def _cohort_matrix(conn, mo):
    """The 360-row Crown Dependencies cohort matrix."""
    df = conn.sql(
        """
        SELECT jurisdiction, subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction IN ('jersey', 'guernsey', 'isle_of_man')
          AND status = 'ACTIVE'
        GROUP BY jurisdiction, subject_slug, qualification_level, language
        ORDER BY jurisdiction, qualification_level, subject_slug, language
        """
    ).execute()
    mo.ui.table(df, label="360 Crown cohorts (Jersey + Guernsey + Isle of Man)")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 5: Drill down
# -----------------------------------------------------------------------------

@app.cell
def _drill_jurisdiction(mo):
    """Drill down on a single Crown Dependency."""
    jurisdiction_dropdown = mo.ui.dropdown(
        options=["jersey", "guernsey", "isle_of_man"],
        value="jersey",
        label="Crown Dependency",
    )
    return (jurisdiction_dropdown,)


@app.cell
def _drill_show(mo, conn, jurisdiction_dropdown):
    """Show the per-jurisdiction cohort count."""
    df = conn.sql(
        """
        SELECT subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction = ?
          AND status = 'ACTIVE'
        GROUP BY subject_slug, qualification_level, language
        ORDER BY subject_slug, qualification_level, language
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
        "## BIEP v3 scheduling policy (deferred for Crown Dependencies)\n\n"
        "| Document class | Cadence | Cron |\n"
        "|:--|:--|:--|\n"
        + "\n".join(
            f"| {s['document_class']} | {s['cadence']} | `{s['cron']}` |"
            for s in BIEP_V3_CRON_SCHEDULE
        )
        + "\n\n"
        + "### ChangeDetection.io sensors (Crown-specific)\n\n"
        + "- `jersey_registry_sensor` (Jersey) — wired but not yet backed by assets\n"
        + "- `guernsey_registry_sensor` (Guernsey) — wired but not yet backed by assets\n"
        + "- `isle_of_man_registry_sensor` (Isle of Man) — wired but not yet backed by assets\n"
    )
    return (BIEP_V3_CRON_SCHEDULE,)


# -----------------------------------------------------------------------------
# Cell 7: Asset check status
# -----------------------------------------------------------------------------

@app.cell
def _asset_check_button(mo):
    """Run-button to invoke the live `dagster asset check` for the Crown BIEP v3 assets."""
    import subprocess

    def _run_asset_check() -> str:
        """Run the canonical `dagster asset check` and return the result as a markdown string."""
        # The Crown assets don't exist yet — this is a placeholder
        checks = "crown_dependencies_documents_ingested_check"  # reserved name
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
                f"### Asset check result for Crown (deferred)\n\n"
                f"**Checks**: `{checks}`\n\n"
                f"**Exit code**: `{result.returncode}`\n\n"
                f"```\n{result.stdout[-1000:]}\n```\n\n"
                f"```\n{result.stderr[-500:]}\n```\n"
            )
        except Exception as exc:  # noqa: BLE001
            return f"**Error running `dagster asset check`**: `{exc}`\n\nRun `mise install` first to ensure the `dagster` CLI is in PATH.\n"

    run_button = mo.ui.run_button(label="Run `dagster asset check` (Crown)")
    return (_run_asset_check, run_button)


@app.cell
def _asset_check_status(mo, _run_asset_check, run_button):
    """Display the live `dagster asset check` result for the Crown assets."""
    if run_button.value:
        result_md = _run_asset_check()
        mo.md(result_md)
    else:
        mo.md(
            "Click **Run `dagster asset check` (Crown)** to invoke the live asset check.\n\n"
            "⚠️ The Crown assets don't exist yet. The check will return exit code 1.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 8: Dive link
# -----------------------------------------------------------------------------

@app.cell
def _dive_link(mo):
    """Link to the canonical MotherDuck Dives for Crown Dependencies (reserved)."""
    mo.md(
        "## Canonical MotherDuck Dives for Crown Dependencies (reserved)\n\n"
        "- **`jersey_topics`** — reserved (Jersey 120 cohorts)\n"
        "  (DAG: TBD — to be added in `2026-08-13-biep-v3-crown-dependencies-v1`)\n"
        "- **`guernsey_topics`** — reserved (Guernsey 120 cohorts)\n"
        "  (DAG: TBD)\n"
        "- **`isle_of_man_topics`** — reserved (Isle of Man 120 cohorts)\n"
        "  (DAG: TBD)\n"
    )
    return


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
