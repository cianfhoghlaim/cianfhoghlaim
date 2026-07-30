# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
# ]
# [tool.uv]
# package = "biep-v3-ireland-dashboard"
# ///

"""BIEP v3 Ireland pipeline dashboard — Ireland LC (12 cohorts) + JC (88 cohorts) = 100 total.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the Ireland BIEP v3 pipelines. It
exposes the canonical 8-cell surface:

1. **`_intro()`** — BIEP v3 milestone summary + scheduling policy
2. **`_ibis_conn()`** — ibis-first connection (per the BIEP v3 spec)
3. **`_commands()`** — canonical `mise run` + `dagster` + `openspec` commands
4. **`_cohort_matrix()`** — 100-row Ireland cohort matrix (12 LC + 88 JC)
5. **`_drill_down()`** — per-cohort DuckLake rows + LanceDB chunks + RAGAS score
6. **`_schedule()`** — yearly + monthly + weekly + nightly + event-driven cron table
7. **`_asset_check_status()`** — live `dagster asset check` result
8. **`_dive_link()`** — link to the canonical MotherDuck Dives

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- marimo (per `.agents/skills/marimo/SKILL.md`).
- BIEP v3 systematic download — 5-milestone plan + 4-cadence scheduling.

TABLES:
- cianfhoghlaim.education.ireland.leaving_cycle.<subject>.<level>_<lang>  (12 rows: 6 subjects × 2 langs)
- cianfhoghlaim.education.ireland.junior_cycle.<subject>.<year>_<lang>  (36 rows: 18 subjects × 2 langs)
- cianfhoghlaim.education.ireland.junior_cycle.short_courses.<code>  (16 rows)
- cianfhoghlaim.education.ireland.junior_cycle.cbas.<cba_id>  (36 rows)

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
    mo.md(biep_v3_overview("ireland"))
    return (mo, biiep_v3_overview)


# -----------------------------------------------------------------------------
# Cell 2: ibis-first connection (per the BIEP v3 spec)
# -----------------------------------------------------------------------------

@app.cell
def _ibis_conn(mo):
    """The ibis-first connection (per the BIEP v3 spec)."""
    from notebooks._shared.db import connect_md
    conn = connect_md()
    mo.md("✓ ibis-first wired — `md:cianfhoghlaim`")
    return (conn,)


# -----------------------------------------------------------------------------
# Cell 3: Commands (canonical operator commands for the Ireland BIEP pipelines)
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
# Cell 4: Cohort matrix (100 rows: 12 LC + 88 JC)
# -----------------------------------------------------------------------------

@app.cell
def _cohort_matrix(conn, mo):
    """The 100-row Ireland cohort matrix (12 LC + 88 JC)."""
    df = conn.sql(
        """
        SELECT 'lc' AS stage, subject_slug, qualification_level, language, COUNT(*) AS row_count
        FROM cianfhoghlaim.education.ireland.leaving_cycle
        GROUP BY subject_slug, qualification_level, language
        UNION ALL BY NAME
        SELECT 'jc_spec', subject_slug, qualification_level, language, COUNT(*)
        FROM cianfhoghlaim.education.ireland.junior_cycle
        GROUP BY subject_slug, qualification_level, language
        UNION ALL BY NAME
        SELECT 'jc_short_course', short_course_code, 'untiered', language, COUNT(*)
        FROM cianfhoghlaim.education.ireland.junior_cycle.short_courses
        GROUP BY short_course_code, language
        UNION ALL BY NAME
        SELECT 'jc_cba', subject_slug, qualification_level, 'en', COUNT(*)
        FROM cianfhoghlaim.education.ireland.junior_cycle.cbas
        GROUP BY subject_slug, qualification_level
        ORDER BY stage, subject_slug, language
        """
    ).execute()
    mo.ui.table(df, label="100 Ireland cohorts (12 LC + 88 JC)")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 5: Drill down — per-cohort DuckLake rows + LanceDB chunks + RAGAS score
# -----------------------------------------------------------------------------

@app.cell
def _drill_down(mo, conn):
    """Drill down on a single cohort to see DuckLake rows + LanceDB chunks + RAGAS score."""
    cohort_kind_dropdown = mo.ui.dropdown(
        options=["lc", "jc_spec", "jc_short_course", "jc_cba"],
        value="lc",
        label="Cohort kind",
    )
    return (cohort_kind_dropdown,)


@app.cell
def _drill_subject(mo, conn, cohort_kind_dropdown):
    """Drill down on a single subject within the selected cohort kind."""
    if cohort_kind_dropdown.value == "lc":
        subjects = [
            "mathematics", "chemistry", "geography", "english", "gaeilge", "computer_science",
        ]
    elif cohort_kind_dropdown.value == "jc_spec":
        subjects = [
            "english", "gaeilge", "mathematics", "irish_history", "geography", "science",
            "business_studies", "french", "german", "spanish", "italian", "home_economics",
            "music", "art", "technology", "engineering", "graphics", "wood_technology",
        ]
    elif cohort_kind_dropdown.value == "jc_short_course":
        subjects = [
            "coding", "chinese", "japanese", "russian", "polish", "lithuanian",
            "portuguese", "arabic", "hebrew", "philosophy", "film_studies",
            "financial_literacy", "media_literacy", "personal_professional_development",
            "digital_media", "athletic_studies",
        ]
    else:  # jc_cba
        subjects = [
            "english_1", "english_2", "gaeilge_1", "gaeilge_2", "mathematics_1",
            "mathematics_2", "irish_history_1", "irish_history_2", "geography_1",
            "geography_2", "science_1", "science_2", "business_studies_1",
            "business_studies_2", "french_1", "french_2", "german_1", "german_2",
            "spanish_1", "spanish_2", "italian_1", "italian_2", "home_economics_1",
            "home_economics_2", "music_1", "music_2", "art_1", "art_2", "technology_1",
            "technology_2", "engineering_1", "engineering_2", "graphics_1",
            "graphics_2", "wood_technology_1", "wood_technology_2",
        ]
    subject_dropdown = mo.ui.dropdown(
        options=subjects,
        value=subjects[0],
        label="Subject / cohort_id",
    )
    return (subject_dropdown,)


@app.cell
def _drill_show(mo, conn, cohort_kind_dropdown, subject_dropdown):
    """Show the per-cohort DuckLake row count + RAGAS score."""
    from notebooks._shared.db import compute_ragas_distribution
    if cohort_kind_dropdown.value == "lc":
        ragas_kind = "lc_spec"
    elif cohort_kind_dropdown.value == "jc_spec":
        ragas_kind = "jc_spec"
    elif cohort_kind_dropdown.value == "jc_short_course":
        ragas_kind = "jc_short_course"
    else:
        ragas_kind = "jc_cba"
    ragas = compute_ragas_distribution(ragas_kind)
    mo.md(
        f"## Per-cohort drill-down: `{cohort_kind_dropdown.value} / {subject_dropdown.value}`\n\n"
        f"- **Cohort kind**: `{ragas_kind}`\n"
        f"- **Avg RAGAS score**: `{ragas['avg_ragas_score']:.3f}`\n"
        f"- **Min / max RAGAS**: `{ragas['min_ragas_score']:.3f}` / `{ragas['max_ragas_score']:.3f}`\n"
        f"- **Cohorts (kind)**: `{ragas['cohort_count']}`\n"
        f"- **Passing cohorts (RAGAS >= 0.70)**: `{ragas['passing_cohorts']}`\n"
        f"- **Status**: `{ragas['status']}`\n\n"
        f"### Canonical snake_case S3 path (for this cohort)\n\n"
        f"```\n"
        f"{_format_snake_case_path(cohort_kind_dropdown.value, subject_dropdown.value)}\n"
        f"```\n"
    )
    return (ragas,)


@app.cell
def _():
    """Helper: format the canonical snake_case S3 path for a cohort."""
    def _format_snake_case_path(cohort_kind: str, subject: str) -> str:
        from notebooks._shared.db import format_snake_case_cohort_path
        if cohort_kind == "lc":
            return format_snake_case_cohort_path(
                jurisdiction="ireland",
                stage="leaving_cycle",
                subject_slug=subject,
                board="na",
                qualification_level="higher",
                language="en",
                year=2024,
                sha256_8="a1b2c3d4",
            )
        elif cohort_kind == "jc_spec":
            return format_snake_case_cohort_path(
                jurisdiction="ireland",
                stage="junior_cycle",
                subject_slug=subject,
                board="na",
                qualification_level="ordinary",
                language="en",
                year=2024,
                sha256_8="a1b2c3d4",
            )
        elif cohort_kind == "jc_short_course":
            return format_snake_case_cohort_path(
                jurisdiction="ireland",
                stage="junior_cycle.short_courses",
                subject_slug=subject,
                board="na",
                qualification_level="untiered",
                language="en",
                year=2024,
                sha256_8="a1b2c3d4",
            )
        else:  # jc_cba
            return format_snake_case_cohort_path(
                jurisdiction="ireland",
                stage="junior_cycle.cbas",
                subject_slug=subject,
                board="na",
                qualification_level="untiered",
                language="en",
                year=2024,
                sha256_8="a1b2c3d4",
            )
    return (_format_snake_case_path,)


# -----------------------------------------------------------------------------
# Cell 6: Schedule (the BIEP v3 4-cadence scheduling policy)
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
        + "### ChangeDetection.io sensors (event-driven)\n\n"
        + "- `ncca_registry_sensor` (NCCA, Ireland) — triggers `england_a_level_extractions` etc. when a new LC spec is published\n"
        + "- `sqa_registry_sensor` (SQA, Scotland) — reserved for the SCT/WLS/NI follow-up change\n"
        + "- `wjec_registry_sensor` (WJEC, Wales) — reserved\n"
        + "- `ccea_registry_sensor` (CCEA, Northern Ireland) — reserved\n"
        + "- `jcq_registry_sensor` (AQA + OCR + Edexcel) — triggers `england_a_level_extractions` etc. when a new A-Level/GCSE spec is published\n"
        + "- `jcq_registry_sensor` (JCQ, England) — already wired (per the 2026-08-07 hardening change)\n"
        + "- `isle_of_man_registry_sensor`, `jersey_registry_sensor`, `guernsey_registry_sensor` — reserved for the Crown Dependencies follow-up change\n"
    )
    return (BIEP_V3_CRON_SCHEDULE,)


# -----------------------------------------------------------------------------
# Cell 7: Asset check status (live `dagster asset check` result)
# -----------------------------------------------------------------------------

@app.cell
def _asset_check_button(mo):
    """Run-button to invoke the live `dagster asset check` for the Ireland BIEP v3 assets."""
    import subprocess
    import json

    def _run_asset_check(per_milestone: str = "m1") -> str:
        """Run the canonical `dagster asset check` and return the result as a markdown string."""
        asset_check_map = {
            "m0": "lakehouse_smoke_test_check,baml_codegen_check,registry_seed_check,lance_namespace_check",
            "m1": "ireland_lc_documents_ingested_check,ireland_lc_extractions_ragas_check,ireland_lc_lance_chunks_check",
            "m2": "ireland_jc_documents_ingested_check,ireland_jc_extractions_ragas_check,ireland_jc_lance_chunks_check",
        }
        checks = asset_check_map.get(per_milestone, asset_check_map["m1"])
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
        options=["m0", "m1", "m2"],
        value="m1",
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
            f"for the `{milestone_dropdown.value.upper()}` milestone.\n\n"
            f"The check runs `uv run dagster asset check --select <checks> -m orchestration.definitions` "
            f"and displays the exit code + stdout + stderr.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 8: Dive link (canonical MotherDuck Dives for Ireland)
# -----------------------------------------------------------------------------

@app.cell
def _dive_link(mo):
    """Link to the canonical MotherDuck Dives for Ireland."""
    mo.md(
        "## Canonical MotherDuck Dives for Ireland\n\n"
        "- **`ireland_lc_syllabus_topics`** — read the 12 per-cohort DuckLake tables; "
        "surfaces topic frequency per subject per language with RAGAS score histogram\n"
        "  (DAG: `motherduck/dives/ireland_lc_syllabus_topics.py`)\n"
        "- **`ireland_jc_curriculum_topics`** — read the 88 per-cohort DuckLake tables "
        "(36 specs + 16 short courses + 36 CBAs); surfaces topic + learning-outcome frequency per cohort kind\n"
        "  (DAG: `motherduck/dives/ireland_jc_curriculum_topics.py`)\n\n"
        "### Flights (yearly, runs `mise run biep:v3:m<N>` + writes status)\n\n"
        "- **`ireland_lc_daily_sync_flight`** — runs M1, replicates to LanceDB, writes "
        "`cianfhoghlaim.education.ireland._audit.daily_sync_status`\n"
        "  (DAG: `motherduck/flights/ireland_lc_daily_sync_flight.py`)\n"
        "- **`ireland_jc_daily_sync_flight`** — runs M2, same flow as the LC flight\n"
        "  (DAG: `motherduck/flights/ireland_jc_daily_sync_flight.py`)\n"
    )
    return


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()
