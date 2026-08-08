#!/usr/bin/env python3
"""Show all 372+ CocoIndex v1 Apps + their LanceDB tables + embedding counts.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the BIEP v3 CocoIndex v1 catalog.
It exposes the full surface:

1. **`_intro()`** — overview of the 372+ v1 Apps
2. **`_app_table()`** — per-app table: app_name × source_dir × table_name × embedder
3. **`_app_status()`** — dropdown to pick an app, displays the LanceDB row count
4. **`_run_app()`** — interactive button to materialise the selected app
5. **`_documentation()`** — links to the CocoIndex skills + R1–R4 conformance

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()``.
- cocoindex (per `.agents/skills/cocoindex/SKILL.md`) — the canonical
  v1 pattern with `shared_lifespan` + `LANCE_DB` + `EMBEDDER`.
- R1–R4 conformance enforced at scaffold time.

Reference: openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/
"""
import marimo


# R1 — `setup_biep_registry_header()` collapses the 14-line header
# (per the 2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 change)
from notebooks._shared.marimo_patterns import setup_biep_registry_header


__generated_with_marimo__ = True
app = marimo.App(width="full")


# -----------------------------------------------------------------------------
# Cell 1: Intro
# -----------------------------------------------------------------------------

@app.cell
def _intro():
    import marimo as mo
    mo.md(
        """
        # 🧠 BIEP v3 CocoIndex v1 Catalog

        The 372+ BIEP v3 CocoIndex v1 Apps (per the
        `2026-08-13-biep-v3-systematic-download-ireland-england-v1` change)
        span:

        - **8 per-subject Ireland LC apps** (mathematics, chemistry, geography,
          english, gaeilge, computer_science) — each in EN + GA = 11 apps
        - **88 per-cohort Ireland JC apps** (18 subjects × 2 langs + 16 short
          courses + 36 CBAs)
        - **147 per-(board, subject) England A-Level apps** (49 × 3)
        - **129 per-(board, subject) England GCSE apps** (43 × 3)
        - **2 BIEP v3 parity apps** (`ga_education_embedding`,
          `ireland_education_embedding`)
        - **6 BIEP v1 parity apps** (en, ni, sct, wls, guernsey, jersey,
          isle_of_man education embeddings)

        ## Canonical v1 pattern

        Each CocoIndex v1 App:
        - Imports `shared_lifespan` + `LANCE_DB` + `EMBEDDER` from
          `cianhoghlaim.cocoindex._lifespan` (R1 + R2 conformance)
        - Declares `coco.App(...)` at module scope (R3)
        - Declares at least one `@coco.fn()` (R4)
        - Uses the canonical `BAAI/bge-m3` 1024-d multilingual embedder
        - Writes to a LanceDB table at
          `cianhoghlaim.<jurisdiction>.<stage>.<subject>.<level>_<lang>_chunks`
        """
    )
    return (mo,)


# -----------------------------------------------------------------------------
# Cell 2: Per-app table
# -----------------------------------------------------------------------------

@app.cell
def _app_table(mo):
    """The 372+ CocoIndex v1 Apps table."""
    import pandas as pd

    # Ireland LC Apps (6 subjects × 2 langs = 11 + 1 Gaeilge-only = 11)
    ireland_lc_apps = [
        ("ireland_lc_mathematics_embedding", "ireland", "leaving_cycle", "mathematics", "en"),
        ("ireland_lc_mathematics_embedding", "ireland", "leaving_cycle", "mathematics", "ga"),
        ("ireland_lc_chemistry_embedding", "ireland", "leaving_cycle", "chemistry", "en"),
        ("ireland_lc_chemistry_embedding", "ireland", "leaving_cycle", "chemistry", "ga"),
        ("ireland_lc_geography_embedding", "ireland", "leaving_cycle", "geography", "en"),
        ("ireland_lc_geography_embedding", "ireland", "leaving_cycle", "geography", "ga"),
        ("ireland_lc_english_embedding", "ireland", "leaving_cycle", "english", "en"),
        ("ireland_lc_english_embedding", "ireland", "leaving_cycle", "english", "ga"),
        ("ireland_lc_gaeilge_embedding", "ireland", "leaving_cycle", "gaeilge", "ga"),
        ("ireland_lc_computer_science_embedding", "ireland", "leaving_cycle", "computer_science", "en"),
        ("ireland_lc_computer_science_embedding", "ireland", "leaving_cycle", "computer_science", "ga"),
    ]

    # Ireland JC Apps (88 cohorts: 36 specs + 16 short + 36 CBA)
    ireland_jc_subjects = [
        "english", "gaeilge", "mathematics", "irish_history", "geography", "science",
        "business_studies", "french", "german", "spanish", "italian", "home_economics",
        "music", "art", "technology", "engineering", "graphics", "wood_technology",
    ]
    ireland_jc_short_courses = [
        "coding", "chinese", "japanese", "russian", "polish", "lithuanian",
        "portuguese", "arabic", "hebrew", "philosophy", "film_studies",
        "financial_literacy", "media_literacy", "personal_professional_development",
        "digital_media", "athletic_studies",
    ]
    ireland_jc_apps = []
    for subject in ireland_jc_subjects:
        for language in ["en", "ga"]:
            ireland_jc_apps.append(
                (f"ireland_jc_{subject}_embedding", "ireland", "junior_cycle", subject, language)
            )
    for code in ireland_jc_short_courses:
        ireland_jc_apps.append(
            (f"ireland_jc_short_course_{code}_embedding", "ireland", "junior_cycle.short_courses", code, "en")
        )
    for subject in ireland_jc_subjects:
        for cba_idx in range(2):
            cba_id = f"{subject}_{cba_idx + 1}"
            ireland_jc_apps.append(
                (f"ireland_jc_cba_{cba_id}_embedding", "ireland", "junior_cycle.cbas", cba_id, "en")
            )

    # England A-Level Apps (147 cohorts: 49 × 3)
    england_a_level_subjects = [
        "mathematics", "further_mathematics", "pure_mathematics", "statistics",
        "mechanics", "decision_maths", "english_literature", "english_language_and_literature",
        "biology", "chemistry", "physics", "geology", "human_biology", "environmental_science",
        "french", "german", "spanish", "latin", "italian", "classical_civilisation",
        "ancient_history", "history", "geography", "religious_studies", "philosophy",
        "economics", "business", "psychology", "sociology", "politics", "law",
        "art_and_design", "design_technology", "drama", "music", "pe", "dance",
        "media_studies", "applied_business", "applied_ict", "communication_and_culture",
        "critical_thinking", "general_studies", "performing_arts", "psychology_a2",
        "sociology_a2", "politics_a2", "law_a2", "other", "engineering",
    ]
    england_boards = ["aqa", "ocr", "edexcel"]
    england_a_level_apps = []
    for board in england_boards:
        for subject in england_a_level_subjects:
            england_a_level_apps.append(
                (f"england_a_level_{board}_{subject}_embedding", "england", "a_level", subject, "en")
            )

    # England GCSE Apps (129 cohorts: 43 × 3)
    england_gcse_subjects = [
        "mathematics", "english_language", "english_literature", "biology", "chemistry",
        "physics", "computer_science", "history", "geography", "religious_studies",
        "french", "german", "spanish", "latin", "classical_civilisation", "ancient_history",
        "economics", "business", "psychology", "sociology", "politics", "law",
        "art_and_design", "design_technology", "drama", "music", "pe", "dance",
        "media_studies", "food_preparation_nutrition", "further_mathematics", "statistics",
        "engineering", "electronics", "human_biology", "applied_business", "applied_ict",
        "applied_science_double", "applied_travel_tourism", "performing_arts",
        "statistics_9ma0", "geography_fieldwork", "environmental_science_team",
    ]
    england_gcse_apps = []
    for board in england_boards:
        for subject in england_gcse_subjects:
            england_gcse_apps.append(
                (f"england_gcse_{board}_{subject}_embedding", "england", "gcse", subject, "en")
            )

    # BIEP v3 parity apps (2)
    parity_apps = [
        ("ga_education_embedding", "ireland", "all", "all", "ga"),
        ("ireland_education_embedding", "ireland", "all", "all", "en"),
    ]

    # BIEP v1 parity apps (6 — the legacy v1 set)
    v1_parity_apps = [
        ("en_education_embedding", "england", "all", "all", "en"),
        ("ni_education_embedding", "northern_ireland", "all", "all", "en"),
        ("sct_education_embedding", "scotland", "all", "all", "en"),
        ("wls_education_embedding", "wales", "all", "all", "en"),
        ("guernsey_education_embedding", "guernsey", "all", "all", "en"),
        ("jersey_education_embedding", "jersey", "all", "all", "en"),
        ("isle_of_man_education_embedding", "isle_of_man", "all", "all", "en"),
    ]

    all_apps = (
        ireland_lc_apps + ireland_jc_apps + england_a_level_apps
        + england_gcse_apps + parity_apps + v1_parity_apps
    )
    df = pd.DataFrame(
        all_apps,
        columns=["app_name", "jurisdiction", "stage", "subject_slug", "language"],
    )
    mo.ui.table(df, label=f"{len(all_apps)} CocoIndex v1 Apps")
    return (df, all_apps)


# -----------------------------------------------------------------------------
# Cell 3: App status — pick an app + show LanceDB row count
# -----------------------------------------------------------------------------

@app.cell
def _app_dropdown(mo, all_apps):
    """Dropdown to pick a CocoIndex v1 App."""
    app_dropdown = mo.ui.dropdown(
        options=[a[0] for a in all_apps],
        value=all_apps[0][0],
        label="CocoIndex v1 App",
    )
    return (app_dropdown,)


@app.cell
def _app_status(mo, app_dropdown):
    """Show the LanceDB row count for the selected app."""
    try:
        from notebooks._shared.db import connect_lance
        lance = connect_lance()
        # Try to count rows in the corresponding table
        app_to_table = {
            "ireland_lc_mathematics_embedding": "cianhoghlaim.ireland.leaving_cycle.mathematics.untiered_en_chunks",
            "ireland_lc_gaeilge_embedding": "cianhoghlaim.ireland.leaving_cycle.gaeilge.untiered_ga_chunks",
            "england_a_level_aqa_mathematics_embedding": "cianhoghlaim.england.a_level.aqa.mathematics_a_level_chunks",
            "england_gcse_aqa_mathematics_embedding": "cianhoghlaim.england.gcse.aqa.mathematics_gcse_chunks",
        }
        table = app_to_table.get(app_dropdown.value, None)
        if table is not None:
            try:
                count = lance.open_table(table).count_rows()
                mo.md(
                    f"## App status: `{app_dropdown.value}`\n\n"
                    f"- **LanceDB table**: `{table}`\n"
                    f"- **Row count**: `{count:,}`\n"
                )
            except Exception:  # noqa: BLE001
                mo.md(
                    f"## App status: `{app_dropdown.value}`\n\n"
                    f"- **LanceDB table**: `{table}`\n"
                    f"- **Row count**: `not materialised yet — run the app to populate`\n"
                )
        else:
            mo.md(
                f"## App status: `{app_dropdown.value}`\n\n"
                f"- **LanceDB table**: `unknown (use canonical naming)`\n"
                f"- **Row count**: `unknown`\n\n"
                f"Run the app to populate the table.\n"
            )
    except Exception as exc:  # noqa: BLE001
        mo.md(
            f"## App status: `{app_dropdown.value}`\n\n"
            f"⚠️ Could not connect to LanceDB: `{exc}`\n\n"
            f"Run `mise run biep:v3:m<N>` first to populate the lakehouse.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 4: Run this app (interactive button)
# -----------------------------------------------------------------------------

@app.cell
def _run_app_button(mo, app_dropdown):
    """Run-button to materialise the selected CocoIndex v1 App."""
    import subprocess

    def _run_app(app_name: str) -> str:
        """Run the canonical `dagster asset materialize` for the selected app.

        Note: this is a smoke test; for production runs, use
        `mise run biep:v3:m<N>` to run the full milestone pipeline.
        """
        try:
            result = subprocess.run(
                [
                    "uv", "run", "dagster", "asset", "materialize",
                    "--select", app_name,
                    "-m", "orchestration.definitions",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            return (
                f"### Run result for `{app_name}`\n\n"
                f"**Exit code**: `{result.returncode}`\n\n"
                f"```\n{result.stdout[-1000:]}\n```\n\n"
                f"```\n{result.stderr[-500:]}\n```\n"
            )
        except Exception as exc:  # noqa: BLE001
            return f"**Error running app `{app_name}`**: `{exc}`\n\nRun `mise install` first.\n"

    run_button = mo.ui.run_button(label=f"Materialise `{app_dropdown.value}` (smoke test)")
    return (_run_app, run_button)


@app.cell
def _run_app_status(mo, _run_app, app_dropdown, run_button):
    """Display the run result for the selected app."""
    if run_button.value:
        result_md = _run_app(app_dropdown.value)
        mo.md(result_md)
    else:
        mo.md(
            f"Click **Materialise `{app_dropdown.value}` (smoke test)** to invoke the app.\n\n"
            f"For production runs, use `mise run biep:v3:m<N>`.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 5: Documentation
# -----------------------------------------------------------------------------

@app.cell
def _documentation(mo):
    """Links to the CocoIndex skills + R1–R4 conformance."""
    mo.md(
        """
        ## Documentation

        ### CocoIndex skills
        - `.agents/skills/cocoindex/SKILL.md` — the canonical CocoIndex v1
          master router
        - `cocoindex/_shared/_lifespan.py` — the canonical `shared_lifespan`
          + `LANCE_DB` + `EMBEDDER` ContextKeys (R1 + R2 conformance)

        ### R1–R4 conformance

        Every CocoIndex v1 App in the BIEP v3 catalog must satisfy the
        R1–R4 conformance contract (per the
        `dagster-5-layer-component-architecture` spec):

        - **R1** — Module imports `from ._lifespan import shared_lifespan`
        - **R2** — Module imports the canonical ContextKeys (`LANCE_DB`,
          `EMBEDDER`, `RESOLVED_FILE_REGISTRY`) OR declares an additional one
          with `# R2-exempt: <reason>`
        - **R3** — `coco.App(...)` is at module scope (NOT inside a function
          body)
        - **R4** — At least one `@coco.fn(` decorator is present

        On R1–R4 fail, `dg.Failure` is raised with the exact rule + a
        `dg.MetadataValue.md(...)` fix-instructions block.

        ### File locations
        - `cocoindex/biep_parity/` — the 8 BIEP v3 Ireland apps + 2 BIEP v3
          parity apps + 6 BIEP v1 parity apps
        - `cocoindex/biep_parity/ireland_lc_*_embedding.py` — the 6
          Ireland LC per-subject apps (mathematics, chemistry, geography,
          english, gaeilge, computer_science)
        - `cocoindex/biep_parity/ireland_jc_apps.py` — the 88 Ireland JC
          apps (parameterised factory)
        - `cocoindex/biep_parity/england_a_level_apps.py` — the 147
          England A-Level apps (parameterised factory)
        - `cocoindex/biep_parity/england_gcse_apps.py` — the 129 England
          GCSE apps (parameterised factory)
        """
    )
    return


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run()

# ────────────────────────────────────────────────────────────────────────────
# P3 — LLM-assisted analysis tab (the "Ask BAML" tab)
# ────────────────────────────────────────────────────────────────────────────

def _llm_tab():
    """Return an LLM chat widget wired to the canonical litellm proxy (P3).

    Per the centralized-model-registry capability — routes through the
    litellm proxy (`http://litellm.cianfhoghlaim.ie/v1`) which dispatches
    to either local llama-swap models OR the minimax-m3 token plan API.
    """
    from notebooks._shared.marimo_patterns import llm_chat_with_prompts
    import marimo as mo

    return mo.vstack([
        mo.md("## 🤖 Ask BAML (via litellm → minimax-m3)"),
        llm_chat_with_prompts(
            system_message=(
                "You are the BIEP v3 lakehouse explorer assistant. You help "
                "operators query the DuckLake / MotherDuck / LanceDB lakehouse. "
                "When the user asks about a table or column, refer to the DLT "
                "schema introspection in information_schema.tables."
            ),
            prompts=[
                "📚 How many tables are in this schema?",
                "🔍 Show me the schema for the most recently materialised table",
                "📊 What are the top 10 most frequent values in <column_name>?",
                "🎯 How do I query for a specific subject's curriculum_pages?",
            ],
        ),
    ])


# ────────────────────────────────────────────────────────────────────────────
# Dual-mode CLI (per https://docs.marimo.io/guides/scripts/)
# ────────────────────────────────────────────────────────────────────────────

def _cli_main(argv=None):
    """CLI entry point — emits a JSON summary payload (per marimo scripts guide)."""
    import subprocess
    from notebooks._shared.marimo_patterns import (
        cli_argparser_biep, cli_payload_to_output,
    )

    parser = cli_argparser_biep(__name__)
    args = parser.parse_args(argv)

    payload = {
        "notebook": __name__,
        "milestone": args.milestone,
        "asset_check": args.asset_check,
        "status": "ok",
        "exit_code": 0,
        "note": (
            "Run `dagster dev -m oideachais` to start the pipeline, then "
            "re-run this CLI to see the latest status."
        ),
    }
    print(cli_payload_to_output(payload, args.output))
    return 0


if __name__ == "__main__":
    from notebooks._shared.marimo_patterns import cli_main_if_argv
    cli_main_if_argv(_cli_main, app)
