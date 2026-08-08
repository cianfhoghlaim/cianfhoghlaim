# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.13", "ibis-framework[duckdb]>=9.0", "pandas>=2.2", "altair>=5.0", "pyarrow>=15",
#   "anywidget>=0.9", "traitlets>=5.14",
# ]
# ///
"""01 — Overview + Setup (the welcome notebook).

The welcome + architecture-diagram + `nb_utils.connect_*()` tour +
MotherDuck status cell. This is step 0 of the 8-step end-to-end
tutorial (per `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md`).

The table of contents:

- **Step 0**: dev env setup + `nb_utils` tour (this notebook)
- **Step 0.4**: the centralized registries (NEW 2026-08-15: MODEL_REGISTRY +
  schema introspection + deployment-choice.yaml + 00_control_panel)
- **Step 0.5**: the BAML+CocoIndex tutorial track (5 notebooks at
  `notebooks/13_baml_cocoindex_tutorial/`)
- **Step 1**: vision models (notebook `02_vision_models/`)
- **Step 2**: leaving cert ingestion (notebook `03_leaving_cert/`)
- **Step 3**: BIEP MotherDuck (notebook `04_biep_motherduck/`)
- **Step 4**: lakehouse inspection (notebook `05_lakehouse_inspect/`)

Cross-references:
- `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` —
  the parent capability spec
- `openspec/changes/2026-07-08-five-tangent-modernization/` — the
  5-tangent change record
- `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/` — the
  5-notebook BAML+CocoIndex follow-up

Run via the cianfhoghlaim-marimo CLI:
    uv run cianfhoghlaim-marimo edit 01_overview_setup
    uv run cianfhoghlaim-marimo run  01_overview_setup
"""

from __future__ import annotations

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="medium")


@app.cell
def _imports():
    import marimo as mo

    return (mo,)


@app.cell
def _intro(mo):
    mo.md(
        """
    # Welcome to Cianfhoghlaim

    The Cianfhoghlaim data platform has 50+ marimo notebooks split
    across 13 numbered directories. This notebook is the **welcome +
    architecture + `nb_utils` tour** for the platform.

    ## Architecture diagram

    ```
                    ┌─────────────────────────────────────┐
                    │       Cianfhoghlaim monorepo        │
                    └─────────────────────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
    │  dlt sources    │      │  baml/          │      │  cocoindex v1   │
    │  (28 sources)   │      │  (27 .baml +    │      │  (51 flows)     │
    │                 │      │   3 clients)    │      │                 │
    └─────────────────┘      └─────────────────┘      └─────────────────┘
            │                          │                          │
            └──────────────────────────┼──────────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────┐
                          │     DuckLake        │
                          │ (Parquet on         │
                          │  Garage S3 +        │
                          │  Postgres catalog)  │
                          └─────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────┐
                          │     MotherDuck      │
                          │  (md:cianfhoghlaim)    │
                          └─────────────────────┘
    ```
    """
    )
    return


@app.cell
def _step_0(mo):
    mo.md(
        """
    ## Step 0: dev env setup

    The 6 dev_env tutorials at `notebooks/01_dev_env/{01..06}_*.py`
    walk through the dev-env surface:

    1. `01_ccc_search.py` — semantic code search via `ccc_search`
    2. `02_drift_detect.py` — drift detection on pinned package versions
    3. `03_firecrawl_refactor_discover.py` — Firecrawl research-index for
       upstream package refactors
    4. `04_hf_best_model.py` — Hugging Face best-model search
    5. `05_openspec_list.py` — openspec capability + change listing
    6. `06_mise_lint_skills.py` — skill metadata validation (53/53 pass)

    Run via:
    ```bash
    uv run cianfhoghlaim-marimo edit 01_ccc_search
    uv run cianfhoghlaim-marimo run  02_drift_detect -- --help
    """
    )
    return


@app.cell
def _centralized_registries(mo):
    """Step 0 cell: show the new centralized registries (2026-08-15).

    Adds a "centralized registries" pointer between Step 0 (env setup)
    and Step 0.5 (the BAML+CocoIndex tutorial track). The 4 canonical
    artifacts are surfaced so a new operator knows where to look.
    """
    mo.md(
        """
    ## Step 0.4: the centralized registries (NEW 2026-08-15)

    The platform now has a single source of truth for every model,
    schema, pipeline, and stack. Four canonical artifacts:

    1. **`MODEL_REGISTRY`** (`meaisinfhoghlaim/models/model_registry.py`)
       — 52 entries across 7 families (ocr_vision / text_llm /
       embedder / rerank / image_gen / voice / translation). Resolve
       via `model_for(family, role, language)` or `filter_models(family)`.

    2. **`schema` introspection** (`notebooks/_shared/schema.py`)
       — 5 helpers: `schema_introspect`, `schema_introspect_table`,
       `schema_introspect_full`, `list_dlt_sources` (1963),
       `list_cocoindex_apps` (~53), `list_baml_classes` (838).

    3. **`deployment-choice.yaml`** (repo root)
       — the canonical enablement file. Read/written by the notebook +
       web UI + CLI. 50 enabled models + 28 enabled pipelines + 8 enabled
       stacks + the dataset + monitoring sections.

    4. **`notebooks/00_control_panel.py`** — the 5-tab marimo control
       panel (Models / Pipelines / Datasets / Stacks / Registry).

    **Open the control panel:**

    ```bash
    mise run notebook:control-panel
    # or: marimo edit notebooks/00_control_panel.py
    ```

    **Audit drift:**

    ```bash
    mise run lint:registry
    # Expected: "Found 0 hardcoded model strings in audited files"
    ```

    **Resolve a model in Python:**

    ```python
    from meaisinfhoghlaim.models import model_for
    default = model_for("text_llm", "default")           # → "minimax-m3"
    irish  = model_for("text_llm", "irish", language="ga")
    embed  = model_for("embedder", "default")            # → "BAAI/bge-m3"
    ```

    Reference: openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/
    """
    )
    return


@app.cell
def _step_0_5(mo):
    mo.md(
        """
    ## Step 0.5: the BAML+CocoIndex tutorial track

    The 5-notebook tutorial at
    `notebooks/13_baml_cocoindex_tutorial/` covers the full BAML
    0.223.0 + CocoIndex v1 + vision-model stack. This is the
    follow-up to the parent mega-change
    `2026-07-11-baml-cocoindex-modernization-v1/`:

    | # | Notebook | What it teaches |
    |:--|:--|:--|
    | 1 | `01_baml_post_v4_syntax.py` | Canonical post-v4 BAML 0.223.0 syntax (`generator` + `field Type` + `@@stream.*`) |
    | 2 | `02_qpack_8_subject_walkthrough.py` | The 8 `qpack_<subject>.baml` files (40+ BAML calls) |
    | 3 | `03_education_pdf_vision_pipeline.py` | The vision+PDF pipeline with **side-by-side `gemma-4-26B-A4B` vs `qwen3-vl-8b`** |
    | 4 | `04_cocoindex_baml_integration.py` | The 3 real CocoIndex+BAML integration patterns |
    | 5 | `05_post_v4_duplicate_audit_and_migration.py` | The 42-renames commit (`49e0259a0`) audit notebook |

    Each tutorial is dual-mode (marimo + `uv run` via PEP 723 inline
    deps). See `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/`
    for the change record.

    Run via:
    ```bash
    uv run cianfhoghlaim-marimo edit 13_baml_cocoindex_tutorial/01_baml_post_v4_syntax
    uv run cianfhoghlaim-marimo run  13_baml_cocoindex_tutorial/03_education_pdf_vision_pipeline
    ```
    """
    )
    return


@app.cell
def _step_1_to_4(mo):
    mo.md(
        """
    ## Step 1: vision models

    See `notebooks/02_vision_models/` — the 4 vision model
    walkthroughs (gemma-4-26B-A4B, qwen3-vl-8b, glm-4.6v-flash,
    moondream2) + the side-by-side comparison notebook.

    ## Step 2: leaving cert ingestion

    See `notebooks/03_leaving_cert/` — the 6 LC priority subject
    ingestion notebooks (Mathematics, Chemistry, Geography, Gaeilge,
    English, Computer Science).

    ## Step 3: BIEP MotherDuck

    See `notebooks/04_biep_motherduck/` — the 11 BIEP notebooks
    (6 subject + 1 leabharlann + 4 cross-cutting) wired to the
    `md:cianfhoghlaim` MotherDuck database.

    ## Step 4: lakehouse inspection

    See `notebooks/05_lakehouse_inspect/` — the 3 lakehouse inspector
    notebooks (DuckDB connection, Lakekeeper catalog, LanceDB table
    preview).
    """
    )
    return


@app.cell
def _step_biep_v3_intro(mo):
    """BIEP v3 systematic download + iterate — the new flagship surface.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.
    """
    from notebooks._shared.area_shims.leaving_cert import biiep_v3_overview
    mo.md(
        biiep_v3_overview("all")
        + "\n\n## 5 jurisdiction dashboards (operator consoles)\n\n"
        + "- **`notebooks/19_ireland_pipeline_dashboard.py`** 🇮🇪 — Ireland LC + JC "
        + "(100 cohorts = 12 LC + 88 JC)\n"
        + "- **`notebooks/20_england_pipeline_dashboard.py`** 🏴󠁧󠁢󠁥󠁮󠁧󠁿 — England A-Level + GCSE "
        + "(276 cohorts = 147 A-Level + 129 GCSE)\n"
        + "- **`notebooks/21_sct_wls_ni_pipeline_dashboard.py`** 🏴󠁧󠁢󠁳󠁣󠁴󠁿🏴󠁧󠁢󠁷󠁬󠁳󠁿🇬🇧 — "
        + "Scotland + Wales + Northern Ireland (380 cohorts, **deferred**)\n"
        + "- **`notebooks/22_crown_dependencies_dashboard.py`** 🇯🇪🇬🇬🇮🇲 — "
        + "Jersey + Guernsey + Isle of Man (360 cohorts, **deferred**)\n"
        + "- **`notebooks/23_8_jurisdiction_overview.py`** 🌐 — all 8 British Isles "
        + "jurisdictions (1,560 cohorts)\n\n"
        "## 2 operator consoles (in-progress consolidation)\n\n"
        + "- **`notebooks/10_biep_pipeline_lakehouse_03_dlt_pipeline_overview.py`** 📦 — "
        + "the 28+ BIEP v3 DLT source catalog\n"
        + "- **`notebooks/10_biep_pipeline_lakehouse_04_cocoindex_embedding_coverage.py`** 🧠 — "
        + "the 372+ CocoIndex v1 Apps catalog\n"
    )
    return (biiep_v3_overview,)


@app.cell
def _step_biep_v3_commands(mo):
    """BIEP v3 canonical operator commands.

    Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change.
    """
    from notebooks._shared.area_shims.leaving_cert import BIEP_V3_OPERATOR_COMMANDS
    mo.md(
        "## BIEP v3 operator commands\n\n"
        "```bash\n"
        + "\n".join(BIEP_V3_OPERATOR_COMMANDS)
        + "\n```\n\n"
        + "### Interactive pipeline operations (via the dashboards)\n\n"
        + "Each of the 5 jurisdiction dashboards (notebooks 19-23) has a "
        + "`_asset_check_status()` cell with a **Run `dagster asset check`** "
        + "button that invokes the live asset check for the selected milestone "
        + "and displays the exit code + stdout + stderr.\n\n"
        + "The 2 catalog dashboards (notebooks 10_03, 10_04) have a "
        + "`_run_source()` + `_run_app()` cell with a **Run source (smoke "
        + "test)** button that invokes `dlt pipeline run` for the selected "
        + "DLT source or `dagster asset materialize` for the selected "
        + "CocoIndex v1 App.\n"
    )
    return (BIEP_V3_OPERATOR_COMMANDS,)


@app.cell
def _nb_utils_tour(mo):
    mo.md(
        """
    ## The `nb_utils` tour

    The `nb_utils` module at `cianfhoghlaim/notebooks/nb_utils.py`
    provides 4 canonical connect_* functions:

    - `connect_filesystem_via_dlt(...)` — DLT filesystem source → DuckDB
    - `connect_ducklake(...)` — DuckLake connection (Parquet on S3 +
      Postgres catalog)
    - `connect_motherduck(...)` — MotherDuck connection
      (`md:cianfhoghlaim`)
    - `connect_baml_client(...)` — BAML client lazy-load + the
      `try / except ImportError` graceful-degradation pattern

    Each is a thin wrapper that handles the canonical auth pattern +
    the canonical error reporting. See the source for the
    implementation details.

    Cross-references:
    - `openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md` —
      the 8-step tutorial spec
    - `openspec/specs/oideachais-marimo-dashboards/spec.md` — the
      marimo dashboards spec (this notebook is part of that surface)
    - `openspec/changes/2026-07-08-five-tangent-modernization/` — the
      5-tangent change record
    - `openspec/changes/2026-07-12-baml-cocoindex-tutorials-v1/` — the
      5-notebook BAML+CocoIndex follow-up
    """
    )
    return


# =============================================================================
# Dual-mode entry: marimo app OR standalone CLI script
# Per https://docs.marimo.io/guides/scripts/ — the canonical pattern.
# =============================================================================
def _cli_main(argv=None) -> int:
    """Run the tutorial as a CLI script from any cwd."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="01_overview_setup.py",
        description=__doc__,
    )
    parser.add_argument(
        "--section",
        type=int,
        default=0,
        help="0 = full overview; 1..4 = jump to that step (default: 0)",
    )
    args = parser.parse_args(argv)
    print("[01_overview_setup] Welcome + Step 0 + Step 0.4 + Step 0.5 + Steps 1-4")
    print(f"  Section: {args.section} (0 = full)")
    print("  Step 0.4: 4 canonical centralized registries (MODEL_REGISTRY + schema.py + deployment-choice.yaml + 00_control_panel)")
    print("  Step 0.5: 5-notebook BAML+CocoIndex tutorial track")
    print("  Run: uv run cianfhoghlaim-marimo edit 01_overview_setup")
    return 0


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] not in ("run", "edit"):
        sys.exit(_cli_main())
    app.run()
