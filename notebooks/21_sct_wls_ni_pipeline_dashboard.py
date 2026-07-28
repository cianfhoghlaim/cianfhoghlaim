# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-sct-wls-ni-dashboard"
# ///

"""BIEP v3 Scotland + Wales + Northern Ireland pipeline dashboard — 380 cohorts (deferred).

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the SCT + WLS + NI BIEP v3 pipelines.
The 380 cohorts (Scotland 150 + Wales 160 + Northern Ireland 70) are
**deferred to a follow-up change** (`2026-08-13-biep-v3-sct-wls-ni-v1`).
The current notebook renders the BIEP v3 8-cell surface in **preview mode**:
the cohort matrix queries the registry for placeholder rows; the asset
check status is informational.

8-cell structure:
1. **`_intro()`** — BIEP v3 milestone summary + deferred status
2. **`_ibis_conn()`** — ibis-first connection (per the BIEP v3 spec)
3. **`_commands()`** — canonical `mise run` + `dagster` + `openspec` commands
4. **`_cohort_matrix()`** — 380-row cohort matrix (3 jurisdictions × per-jurisdiction cohorts)
5. **`_drill_down()`** — per-jurisdiction drilldown
6. **`_schedule()`** — yearly + monthly + weekly + nightly + event-driven cron table
7. **`_asset_check_status()`** — live `dagster asset check` result
8. **`_dive_link()`** — link to the canonical MotherDuck Dives (reserved)

Reference: openspec/changes/2026-08-13-biep-v3-sct-wls-ni-v1/ (deferred change)
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
        biiep_v3_overview("scotland+wales+ni")
        + "\n\n## Status\n\n"
        + "**DEFERRED**: The 380 cohorts (Scotland 150 + Wales 160 + Northern Ireland 70) "
        + "are deferred to a follow-up change "
        + "(`2026-08-13-biep-v3-sct-wls-ni-v1`).\n\n"
        + "The current notebook renders the BIEP v3 8-cell surface in **preview mode** — "
        + "the cohort matrix queries the registry for placeholder rows; the asset check "
        + "status is informational.\n"
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
        "⚠️ The SCT/WLS/NI pipelines are deferred. The queries below return "
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
        "## Canonical BIEP v3 operator commands (deferred for SCT/WLS/NI)\n\n"
        "The SCT/WLS/NI pipelines are deferred to a follow-up change. The commands "
        "below show the Ireland + England commands that are **active** today; the "
        "SCT/WLS/NI-specific commands will be added in `2026-08-13-biep-v3-sct-wls-ni-v1`.\n\n"
        "```bash\n"
        + "\n".join(BIEP_V3_OPERATOR_COMMANDS)
        + "\n```\n"
    )
    return (BIEP_V3_OPERATOR_COMMANDS,)


# -----------------------------------------------------------------------------
# Cell 4: Cohort matrix (380 rows: 150 SCT + 160 WLS + 70 NI)
# -----------------------------------------------------------------------------

@app.cell
def _cohort_matrix(conn, mo):
    """The 380-row SCT + WLS + NI cohort matrix (3 jurisdictions × per-jurisdiction cohorts)."""
    df = conn.sql(
        """
        SELECT jurisdiction, subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education._registry.subjects
        WHERE jurisdiction IN ('scotland', 'wales', 'northern_ireland')
          AND status = 'ACTIVE'
        GROUP BY jurisdiction, subject_slug, qualification_level, language
        ORDER BY jurisdiction, qualification_level, subject_slug, language
        """
    ).execute()
    mo.ui.table(df, label="380 SCT/WLS/NI cohorts (3 jurisdictions)")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 5: Drill down
# -----------------------------------------------------------------------------

@app.cell
def _drill_jurisdiction(mo):
    """Drill down on a single jurisdiction."""
    jurisdiction_dropdown = mo.ui.dropdown(
        options=["scotland", "wales", "northern_ireland"],
        value="scotland",
        label="Jurisdiction",
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
        "## BIEP v3 scheduling policy (deferred for SCT/WLS/NI)\n\n"
        "| Document class | Cadence | Cron |\n"
        "|:--|:--|:--|\n"
        + "\n".join(
            f"| {s['document_class']} | {s['cadence']} | `{s['cron']}` |"
            for s in BIEP_V3_CRON_SCHEDULE
        )
        + "\n\n"
        + "### ChangeDetection.io sensors (SCT/WLS/NI-specific)\n\n"
        + "- `sqa_registry_sensor` (SQA, Scotland) — wired but not yet backed by assets\n"
        + "- `wjec_registry_sensor` (WJEC, Wales) — wired but not yet backed by assets\n"
        + "- `ccea_registry_sensor` (CCEA, Northern Ireland) — wired but not yet backed by assets\n"
    )
    return (BIEP_V3_CRON_SCHEDULE,)


# -----------------------------------------------------------------------------
# Cell 7: Asset check status
# -----------------------------------------------------------------------------

@app.cell
def _asset_check_button(mo):
    """Run-button to invoke the live `dagster asset check` for the SCT/WLS/NI BIEP v3 assets."""
    import subprocess

    def _run_asset_check() -> str:
        """Run the canonical `dagster asset check` and return the result as a markdown string."""
        # The SCT/WLS/NI assets don't exist yet — this is a placeholder
        checks = "sct_wls_ni_documents_ingested_check"  # reserved name
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
                f"### Asset check result for SCT/WLS/NI (deferred)\n\n"
                f"**Checks**: `{checks}`\n\n"
                f"**Exit code**: `{result.returncode}`\n\n"
                f"```\n{result.stdout[-1000:]}\n```\n\n"
                f"```\n{result.stderr[-500:]}\n```\n"
            )
        except Exception as exc:  # noqa: BLE001
            return f"**Error running `dagster asset check`**: `{exc}`\n\nRun `mise install` first to ensure the `dagster` CLI is in PATH.\n"

    run_button = mo.ui.run_button(label="Run `dagster asset check` (SCT/WLS/NI)")
    return (_run_asset_check, run_button)


@app.cell
def _asset_check_status(mo, _run_asset_check, run_button):
    """Display the live `dagster asset check` result for the SCT/WLS/NI assets."""
    if run_button.value:
        result_md = _run_asset_check()
        mo.md(result_md)
    else:
        mo.md(
            "Click **Run `dagster asset check` (SCT/WLS/NI)** to invoke the live asset check.\n\n"
            "⚠️ The SCT/WLS/NI assets don't exist yet. The check will return exit code 1.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 8: Dive link
# -----------------------------------------------------------------------------

@app.cell
def _dive_link(mo):
    """Link to the canonical MotherDuck Dives for SCT/WLS/NI (reserved)."""
    mo.md(
        "## Canonical MotherDuck Dives for SCT/WLS/NI (reserved)\n\n"
        "- **`sct_topics`** — reserved (Scotland 150 cohorts)\n"
        "  (DAG: TBD — to be added in `2026-08-13-biep-v3-sct-wls-ni-v1`)\n"
        "- **`wls_topics`** — reserved (Wales 160 cohorts)\n"
        "  (DAG: TBD)\n"
        "- **`ni_topics`** — reserved (Northern Ireland 70 cohorts)\n"
        "  (DAG: TBD)\n"
    )
    return


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
