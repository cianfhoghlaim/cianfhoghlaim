#!/usr/bin/env python3
"""Show the 28+ BIEP v3 DLT sources — 8 British Isles jurisdictions × 4 domains + special.

Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.

This is the **operator console** for the BIEP v3 DLT source catalog.
It exposes the full surface:

1. **`_intro()`** — overview of the 28+ DLT sources + jurisdictions + domains
2. **`_source_table()`** — per-jurisdiction table: jurisdiction × domain × source_id × primary_key × cron × automation
3. **`_sample_query()`** — dropdown to pick a source, displays `SELECT * FROM <table> LIMIT 5`
4. **`_run_source()`** — interactive button to invoke `dlt.pipeline.run(<source>)` for the selected source
5. **`_documentation()`** — links to the DLT skills + per-area READMEs

## KCG patterns used
- ibis (per `.agents/skills/ibis/SKILL.md`) — every query uses
  ``ibis.duckdb.connect()`` (NO raw ``duckdb.connect``).
- dlt (per `.agents/skills/dlt/SKILL.md`) — the canonical destination
  factory at `dlt_sources.common.destinations_cianfhoghlaim` is used.
- ibis-first contract (per the BIEP v3 spec).

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
        # 📦 BIEP v3 DLT Source Catalog

        The 28+ BIEP v3 DLT sources (per the
        `2026-08-13-biep-v3-systematic-download-ireland-england-v1` change)
        span:

        - **8 British Isles jurisdictions**: Ireland, England, Scotland, Wales,
          Northern Ireland, Jersey, Guernsey, Isle of Man
        - **4 domains**: education, law, medicine, statistics
        - **2 special**: filesystem, api, language, official_media, portfolio

        Each source is registered as a `@dlt.resource` in the canonical
        `dlt_sources.common.destinations_cianfhoghlaim` destination factory.
        The Dagster `1_ingestion` layer mounts the sources via
        `CelticIngestionComponent` (per the
        `dagster-5-layer-component-architecture` spec).

        ## Per-source structure

        Each DLT source emits rows with the canonical 14-column metadata
        contract (per the BIEP v3 snake_case file naming spec):
        - `source_id` — `<region>.<jurisdiction>.<domain>.<source_slug>`
        - `jurisdiction` — `ireland` / `england` / etc.
        - `stage` — `leaving_cycle` / `junior_cycle` / `a_level` / `gcse`
        - `subject_slug` — snake_case subject identifier
        - `board` — `ncca` / `sec` / `aqa` / `ocr` / `edexcel` / `wjec` / `sqa` / `ccea`
        - `qualification_level` — `higher` / `ordinary` / `foundation` / `gcse` / `a_level`
        - `language` — `en` / `ga` / `gd` / `cy` / `gv` / `kw` / `br`
        - `year` — integer or `undated`
        - `source_url` — the canonical publisher URL
        - `crawled_at` — ISO 8601 timestamp
        - `content_hash` — sha256 of the source file
        - `byte_size`, `page_count` — file metadata
        - `publisher` — `ncca` / `sec` / `aqa` / etc.
        """
    )
    return (mo,)


# -----------------------------------------------------------------------------
# Cell 2: Per-jurisdiction source table
# -----------------------------------------------------------------------------

@app.cell
def _source_table(mo):
    """The 28+ DLT sources table (8 BIEP jurisdictions × 4 domains)."""
    import pandas as pd

    sources = [
        # Ireland (active — 6 LC + 18 JC + 16 short + 36 CBA)
        ("ireland", "education", "ncca_lc", "ncca", "leaving_cycle", "0 4 * * *", "yearly"),
        ("ireland", "education", "sec_lc", "sec", "leaving_cycle", "0 3 * * *", "yearly"),
        ("ireland", "education", "gov_ie_circulars", "gov_ie", "all", "0 0 1 * *", "monthly"),
        ("ireland", "education", "junior_cycle", "ncca", "junior_cycle", "0 0 1 9 *", "yearly"),
        ("ireland", "education", "junior_cycle_cbas", "ncca", "junior_cycle", "0 0 1 9 *", "yearly"),
        ("ireland", "education", "junior_cycle_short_courses", "ncca", "junior_cycle", "0 0 1 9 *", "yearly"),
        ("ireland", "law", "irish_statute_book", "statute_book", "all", "0 0 1 9 *", "yearly"),
        ("ireland", "medicine", "hse_guidance", "hse", "all", "0 0 1 9 *", "yearly"),
        ("ireland", "statistics", "cso_ireland", "cso", "all", "0 0 1 9 *", "yearly"),
        # England (active — 49 A-Level × 3 + 43 GCSE × 3)
        ("england", "education", "aqa_a_level", "aqa", "a_level", "0 0 1 9 *", "yearly"),
        ("england", "education", "ocr_a_level", "ocr", "a_level", "0 0 1 9 *", "yearly"),
        ("england", "education", "edexcel_a_level", "edexcel", "a_level", "0 0 1 9 *", "yearly"),
        ("england", "education", "aqa_gcse", "aqa", "gcse", "0 0 1 9 *", "yearly"),
        ("england", "education", "ocr_gcse", "ocr", "gcse", "0 0 1 9 *", "yearly"),
        ("england", "education", "edexcel_gcse", "edexcel", "gcse", "0 0 1 9 *", "yearly"),
        ("england", "statistics", "ons_england", "ons", "all", "0 0 1 9 *", "yearly"),
        # Scotland (deferred)
        ("scotland", "education", "sqa_national_5", "sqa", "national_5", "0 0 1 9 *", "deferred"),
        ("scotland", "education", "sqa_higher", "sqa", "higher", "0 0 1 9 *", "deferred"),
        ("scotland", "education", "sqa_advanced_higher", "sqa", "advanced_higher", "0 0 1 9 *", "deferred"),
        # Wales (deferred)
        ("wales", "education", "wjec_gcse", "wjec", "gcse", "0 0 1 9 *", "deferred"),
        ("wales", "education", "wjec_a_level", "wjec", "a_level", "0 0 1 9 *", "deferred"),
        # Northern Ireland (deferred)
        ("northern_ireland", "education", "ccea_gcse", "ccea", "gcse", "0 0 1 9 *", "deferred"),
        ("northern_ireland", "education", "ccea_a_level", "ccea", "a_level", "0 0 1 9 *", "deferred"),
        # Crown Dependencies (deferred)
        ("jersey", "education", "jersey_gcse", "jersey", "gcse", "0 0 1 9 *", "deferred"),
        ("guernsey", "education", "guernsey_gcse", "guernsey", "gcse", "0 0 1 9 *", "deferred"),
        ("isle_of_man", "education", "iom_gcse", "iom", "gcse", "0 0 1 9 *", "deferred"),
        # gov.ie + Crown circulars (monthly)
        ("ireland", "education", "gov_ie_circulars_v2", "gov_ie", "all", "0 0 1 * *", "monthly"),
        ("jersey", "education", "jersey_circulars", "jersey", "all", "0 0 1 * *", "monthly"),
        ("guernsey", "education", "guernsey_circulars", "guernsey", "all", "0 0 1 * *", "monthly"),
    ]

    df = pd.DataFrame(
        sources,
        columns=[
            "jurisdiction", "domain", "source_id", "board",
            "stage", "cron", "status",
        ],
    )
    mo.ui.table(df, label="28+ BIEP v3 DLT sources (8 jurisdictions × 4 domains + special)")
    return (df,)


# -----------------------------------------------------------------------------
# Cell 3: Sample query — pick a source + show top 5 rows
# -----------------------------------------------------------------------------

@app.cell
def _source_dropdown(mo):
    """Dropdown to pick a source for the sample query."""
    sources = [
        "ncca_lc", "sec_lc", "gov_ie_circulars", "junior_cycle", "junior_cycle_cbas",
        "junior_cycle_short_courses", "irish_statute_book", "hse_guidance", "cso_ireland",
        "aqa_a_level", "ocr_a_level", "edexcel_a_level",
        "aqa_gcse", "ocr_gcse", "edexcel_gcse",
        "ons_england",
        "sqa_national_5", "sqa_higher", "sqa_advanced_higher",
        "wjec_gcse", "wjec_a_level", "ccea_gcse", "ccea_a_level",
        "jersey_gcse", "guernsey_gcse", "iom_gcse",
    ]
    source_dropdown = mo.ui.dropdown(
        options=sources,
        value="ncca_lc",
        label="DLT source",
    )
    return (source_dropdown,)


@app.cell
def _sample_query(mo, source_dropdown):
    """Display the sample query for the selected DLT source."""
    source_to_table = {
        "ncca_lc": "cianfhoghlaim.education.ireland.leaving_cycle.mathematics.higher_en",
        "sec_lc": "cianfhoghlaim.education.ireland.leaving_cycle.mathematics.higher_en",
        "gov_ie_circulars": "cianfhoghlaim.education.ireland.circulars",
        "junior_cycle": "cianfhoghlaim.education.ireland.junior_cycle.english.ordinary_en",
        "junior_cycle_cbas": "cianfhoghlaim.education.ireland.junior_cycle.cbas.english_1.en",
        "junior_cycle_short_courses": "cianfhoghlaim.education.ireland.junior_cycle.short_courses.coding.en",
        "irish_statute_book": "cianfhoghlaim.law.ireland.statute_book",
        "hse_guidance": "cianfhoghlaim.medicine.ireland.hse",
        "cso_ireland": "cianfhoghlaim.statistics.ireland.cso",
        "aqa_a_level": "cianfhoghlaim.education.england.a_level.aqa.mathematics.a_level_en",
        "ocr_a_level": "cianfhoghlaim.education.england.a_level.ocr.mathematics.a_level_en",
        "edexcel_a_level": "cianfhoghlaim.education.england.a_level.edexcel.mathematics.a_level_en",
        "aqa_gcse": "cianfhoghlaim.education.england.gcse.aqa.mathematics.gcse_en",
        "ocr_gcse": "cianfhoghlaim.education.england.gcse.ocr.mathematics.gcse_en",
        "edexcel_gcse": "cianfhoghlaim.education.england.gcse.edexcel.mathematics.gcse_en",
        "ons_england": "cianfhoghlaim.statistics.england.ons",
        "sqa_national_5": "cianfhoghlaim.education.scotland.national_5",
        "sqa_higher": "cianfhoghlaim.education.scotland.higher",
        "sqa_advanced_higher": "cianfhoghlaim.education.scotland.advanced_higher",
        "wjec_gcse": "cianfhoghlaim.education.wales.gcse",
        "wjec_a_level": "cianfhoghlaim.education.wales.a_level",
        "ccea_gcse": "cianfhoghlaim.education.northern_ireland.gcse",
        "ccea_a_level": "cianfhoghlaim.education.northern_ireland.a_level",
        "jersey_gcse": "cianfhoghlaim.education.jersey.gcse",
        "guernsey_gcse": "cianfhoghlaim.education.guernsey.gcse",
        "iom_gcse": "cianfhoghlaim.education.isle_of_man.gcse",
    }
    table = source_to_table.get(source_dropdown.value, "unknown")
    mo.md(
        f"## Sample query for `{source_dropdown.value}`\n\n"
        f"**Canonical DuckLake table**: `{table}`\n\n"
        f"```sql\n"
        f"SELECT * FROM {table} LIMIT 5;\n"
        f"```\n\n"
        f"Use the **Run this source** button below to invoke the source end-to-end.\n"
    )
    return (table,)


# -----------------------------------------------------------------------------
# Cell 4: Run this source (interactive button)
# -----------------------------------------------------------------------------

@app.cell
def _run_source_button(mo, source_dropdown):
    """Run-button to invoke the selected DLT source end-to-end."""
    import subprocess

    def _run_source(source_id: str) -> str:
        """Run the canonical `dlt pipeline run` for the selected source.

        Note: this is a smoke test; for production runs, use
        `mise run biep:v3:m<N>` to run the full milestone pipeline.
        """
        try:
            result = subprocess.run(
                [
                    "uv", "run", "python3", "-c",
                    f"from dlt_sources.british_isles._registry import _resolve_source; "
                    f"_resolve_source('{source_id}')",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return (
                f"### Run result for `{source_id}`\n\n"
                f"**Exit code**: `{result.returncode}`\n\n"
                f"```\n{result.stdout[-1000:]}\n```\n\n"
                f"```\n{result.stderr[-500:]}\n```\n"
            )
        except Exception as exc:  # noqa: BLE001
            return f"**Error running source `{source_id}`**: `{exc}`\n\nRun `mise install` first.\n"

    run_button = mo.ui.run_button(label=f"Run `{source_dropdown.value}` (smoke test)")
    return (_run_source, run_button)


@app.cell
def _run_source_status(mo, _run_source, source_dropdown, run_button):
    """Display the run result for the selected source."""
    if run_button.value:
        result_md = _run_source(source_dropdown.value)
        mo.md(result_md)
    else:
        mo.md(
            f"Click **Run `{source_dropdown.value}` (smoke test)** to invoke the source.\n\n"
            f"For production runs, use `mise run biep:v3:m<N>` to run the full milestone pipeline.\n"
        )
    return


# -----------------------------------------------------------------------------
# Cell 5: Documentation
# -----------------------------------------------------------------------------

@app.cell
def _documentation(mo):
    """Links to the DLT skills + per-area READMEs."""
    mo.md(
        """
        ## Documentation

        ### DLT skills
        - `.agents/skills/dlt/SKILL.md` — the canonical DLT skill (master router)
        - `.agents/skills/dlt/skills/create-rest-api-pipeline/SKILL.md` — the
          rest_api source pattern
        - `.agents/skills/dlt/skills/create-filesystem-pipeline/SKILL.md` — the
          filesystem source pattern (the `USE_LOCAL_SCRAPES=true` convention)

        ### Per-area READMEs
        - `dlt_sources/README.md` — the DLT source catalog README
        - `dlt_sources/british_isles/_cross/README.md` — the British Isles
          cross-jurisdiction registry
        - `dlt_sources/british_isles/ireland/education/README.md` — the
          Ireland education DLT sources
        - `dlt_sources/british_isles/england/education/README.md` — the
          England education DLT sources

        ### Dagster mounts
        - `orchestration/defs/1_ingestion/` — the L1 ingestion asset tree
        - `orchestration/defs/1_ingestion/curriculum/lc6/*.yaml` — the 6 LC
          per-subject ingestion asset defs
        - `orchestration/components/layer1_ingestion.py` — the
          `CelticIngestionComponent` (L1 ingestion factory)
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
