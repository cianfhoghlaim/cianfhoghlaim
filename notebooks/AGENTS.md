# `notebooks/` — Marimo Lakehouse Dashboards

> **The 52 active marimo notebooks for the British-Isles Education Pipeline (BIEP).** Each notebook is a reactive dashboard AND a standalone CLI script (dual-mode). The canonical entry-points are `notebooks/_shared/schema.py` (5 introspection helpers) + `00_control_panel.py` (the 5-tab deployment control panel that reads/writes `deployment-choice.yaml`) + `notebooks/_shared/marimo_patterns.py` (the 22 marimo v14 helper functions).

## Routing

Load this AGENTS.md when:

- You need to add / modify a BIEP dashboard (per-subject, per-jurisdiction, per-language)
- You need to query the BIEP lakehouse via the 5 introspection helpers
- You need to regenerate the WASM-exported marimo bundles
- You need to inspect the deployment control panel state
- You need to use the marimo v14 R1+R2+R3 helpers (`setup_biep_registry_header`, `build_biep_v3_dashboard`, `RAGASGaugeWidget`, `cli_argparser_biep`)

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
mise run notebook:control-panel              # Open the 5-tab deployment control panel (Models/Pipelines/Datasets/Stacks/Registry)
mise run biep:v3:marimo:all                 # Run marimo check on all 25 BIEP v3 marimo notebooks
# The canonical notebooks CLI (uses uv to resolve PEP 723 deps)
uv run notebooks/cli.py list                 # List all 52 active marimo notebooks
uv run notebooks/cli.py list 19_ireland      # List by prefix
uv run notebooks/cli.py edit 19_ireland_pipeline_dashboard  # Open in marimo edit
uv run notebooks/cli.py run 19_ireland_pipeline_dashboard -- --milestone m1 --asset-check documents_ingested  # Run as CLI
# Verify the v14 helpers import cleanly
uv run python -c "from notebooks import build_biep_v3_dashboard, setup_biep_registry_header; print(build_biep_v3_dashboard, setup_biep_registry_header)"
# The canonical cianfhoghlaim CLI (notebook:check + notebook:gate)
bun scripts/cianfhoghlaim-cli.ts notebook:check  # Run marimo check via the canonical CLI
bun scripts/cianfhoghlaim-cli.ts notebook:gate --milestone=m1 --jurisdiction=ireland  # Invoke the dual-mode CLI gate
```

> **Note**: The CLI commands above use `uv run <notebook>.py` (the standard marimo scripts-guide pattern per https://docs.marimo.io/guides/scripts/) rather than `python<version> <notebook>.py` directly. This ensures the PEP 723 inline dependency block is resolved automatically.

## The 52 active marimo notebooks (post-v7 flat layout)

Per the 2026-08-10-marimo-v14-cascading-effects-verification-v1
verification change. The legacy subdir-based layout (per the 2026-07-17
v7 flattening) has been replaced by a flat layout where every notebook
is directly under `notebooks/`.

### Tier 0 — Educative + templates (3 files)
- `00_biep_v3_dashboard_template.py` — the canonical 8-cell template (start any new BIEP dashboard from here)
- `00_control_panel.py` — the 5-tab deployment control panel
- `00_marimo_patterns_tour.py` — the educative marimo-patterns tour (demonstrates every P1-P6 feature)

### Tier 1 — BIEP v3 jurisdiction dashboards (6 files)
- `19_ireland_pipeline_dashboard.py` — Ireland LC + JC (100 cohorts)
- `20_england_pipeline_dashboard.py` — England A-Level + GCSE (276 cohorts)
- `21_sct_wls_ni_pipeline_dashboard.py` — SCT/WLS/NI (380 cohorts, deferred)
- `22_crown_dependencies_dashboard.py` — Crown Dependencies (360 cohorts, deferred)
- `26_aistear_dashboard.py` — Ireland Aistear (14 cohorts)
- `27_primary_dashboard.py` — Ireland Primary Curriculum (64 cohorts)

### Tier 1.5 — Cross-cut (3 files)
- `23_8_jurisdiction_overview.py` — all 8 British Isles jurisdictions (1,116 cohorts)
- `24_deployment_control_panel.py` — sync health + model registry + schema + stacks dashboard
- `40_leaving_cert_subject_panel.py` — 7-tab grouped marimo panel (per LC subject)

### Tier 2 — BIEP v3 lakehouse explorers (17 files, `10_biep_pipeline_lakehouse_*.py`)
- The 17 BIEP v3 lakehouse explorers covering DuckDB + Lakekeeper + Lance + CocoIndex + DLT + BAML + Cognee + marking scheme + exam papers + subject full pipeline + leabharlann + e2e + lag analysis + semantic search (see Tier 2 below)

### Tier 3 — Grouped consolidated dashboards (6 files)
- `meaisin_ops_console.py` — 12-agent fleet operator console
- `celtic_languages.py` — 7 Celtic languages
- `corpus_overview.py` — BIEP + Leabharlann corpus overview
- `speedrun_mmo.py` — Túatha educational MMO
- `academic_history.py` — M.Sc. AI 25/26 academic history
- `irish_law.py` — Irish legal corpus

### Tier 4 — Sync health (1 file)
- `sync_health.py` — 11 sync layer health (paths/ccc/cognee/skills/mcp/dagster/baml/stacks/agents/notebooks/drift-docs)

### Tier 5 — Legacy (not part of the v14 refactor)
- `01_overview_setup.py` — BIEP v1 welcome + architecture (legacy 0.13 PEP 723, pending refactor)
- `02_education_overview.py` — education stage overview
- `05_england_aqa_ocr_edexcel.py` — England AQA + OCR + Edexcel
- `07_junior_cycle_ireland.py` — Ireland Junior Cycle
- `08_ocr_ensemble_audit.py` — 4-path OCR ensemble audit
- `13_official_media_*.py` (7 files) — official media dashboards
- `18_cianfhoghlaim_subject_registry.py` — the Cianfhoghlaim subject registry
- `ie_law_explorer.py` — Ireland law explorer (legacy 0.13 PEP 723, pending refactor)

### Legacy retained (80 files, deprecated)
- `notebooks/legacy/v7_consolidation/{meaisin,celtic,corpus,speedrun,academic,irish_law,sync}/` — the 80 deprecated sub-notebooks migrated to the Tier 3+4 grouped dashboards

## The 3 v14 helper modules (per the 2026-08-10 trilogy)

### `notebooks/_shared/marimo_patterns.py` (~706 LOC, 22 public symbols)
| Function | Pillars | Purpose |
|:--|:--|:--|
| `setup_biep_registry_header()` | R1 | Collapses the 14-line `try/except ImportError` header into a single call returning `{default_llm, registry_summary, dlt_source_count, coco_app_count, baml_class_count, enabled_models}` |
| `tabbed_biep_operator_console(tabs, label)` | P1 | Wraps `mo.ui.tabs(tabs, label=label)` |
| `progress_bar_with_eta(title, total)` | P2 | Wraps `mo.status.progress_bar(..., show_eta=True, show_rate=True)` |
| `form_gated_run_button(label)` | P2 | Returns `(run_button, run_button.form())` |
| `run_dagster_asset_check(checks)` | P2 | `subprocess.run` wrapper for `dagster asset check` |
| `llm_chat_with_prompts(system_message, prompts)` | P3 | Wraps `mo.ui.chat(mo.ai.llm.openai(base_url=LITELLM_BASE_URL, ...))` |
| `three_column_grid_app(title, layout_filename)` | P4 | Returns `marimo.App(width="full", layout_file=...)` |
| `ragas_gauge_widget(score, history)` | P5 | Wraps `mo.ui.anywidget(RAGASGaugeWidget(...))` |
| `cli_argparser_biep(notebook_name)` | P6 | Canonical argparse (5 flags: `--milestone`, `--asset-check`, `--cohort-kind`, `--jurisdiction`, `--output`) |
| `cli_payload_to_output(payload, output)` | P6 | Renders payload in json/table/markdown |
| `cli_main_if_argv(_cli_main, app)` | P6 | The canonical `if __name__ == "__main__":` dispatcher |
| `ragas_color(score)` | P5 | Color band (green ≥0.85 / yellow ≥0.70 / red <0.70) |
| `ragas_status_emoji(score)` | P5 | Status emoji (✅ / ⚠️ / ❌) |
| `LITELLM_BASE_URL` constant | P3 | `http://litellm.cianfhoghlaim.ie/v1` (configurable via `CIANFHOGHLAIM_LITELLM_BASE_URL`) |
| `RAGAS_PASS_THRESHOLD` constant | P5 | `0.70` (the canonical BIEP v3 pass threshold) |

### `notebooks/_shared/area_shims/biiep_v3_dashboard.py` (~622 LOC, 26 symbols)
| Function | Purpose |
|:--|:--|
| `build_biep_v3_dashboard(jurisdiction, milestone, deferred)` | R2 — collapses the open-coded 8-cell BIEP v3 surface into a single composable function. Returns the 7-tab operator console. |
| `build_overview_cell(jurisdiction, milestone, deferred)` | Cell 1 |
| `build_ibis_conn_cell(deferred)` | Cell 2 |
| `build_commands_cell(jurisdiction)` | Cell 3 |
| `build_cohort_matrix_cell(conn, jurisdiction, mo)` | Cell 4 |
| `build_drill_down_cell(conn, jurisdiction, mo)` | Cell 5 |
| `build_schedule_cell(jurisdiction)` | Cell 6 |
| `build_asset_check_cell(jurisdiction, milestone)` | Cell 7 |
| `build_dive_link_cell(jurisdiction)` | Cell 8 |
| `build_llm_tab_cell(jurisdiction)` | Cell 9 (P3 LLM tab) |

### `notebooks/_shared/ragas_gauge.py` (~242 LOC)
| Class | Purpose |
|:--|:--|
| `RAGASGaugeWidget` | P5 — the `anywidget` subclass. Renders a circular SVG gauge + colour band + sparkline of last 10 scores. |

### `notebooks/_shared/area_shims/leaving_cert.py` (311 LOC)
The canonical BIEP v3 operator surface (per the 2026-08-13 BIEP v3 change):
- `biiep_v3_overview(jurisdiction)` — markdown string for the Overview cell
- `BIEP_V3_OPERATOR_COMMANDS` — tuple of strings for the Commands cell
- `BIEP_V3_CRON_SCHEDULE` — tuple of dicts for the Schedule cell

### `notebooks/_shared/area_shims/{meaisin,celtic_languages,corpus_overview,speedrun_mmo,academic_history,irish_law,sync_health}.py`
The 7 per-domain per-tab overview helpers for the Tier 3+4 grouped dashboards.

### `notebooks/_shared/db.py` (403 LOC)
The ibis-first connect helpers:
- `connect_md()` — the canonical MotherDuck connect (returns `ibis.duckdb.connect("md:cianfhoghlaim")`)
- `connect_local()` — local DuckDB fallback
- `connect_local_lakehouse()` — full DuckLake attach (for the bunchloch host)
- `connect_lance()` — LanceDB connect
- `format_snake_case_cohort_path(...)` — the canonical BIEP v3 cohort path builder
- `compute_ragas_distribution(cohort_kind)` — per-cohort RAGAS score distribution

### `notebooks/_shared/schema.py` (691 LOC)
The 5 introspection helpers:
- `schema_introspect(conn)` — every BIEP DuckDB table + every LanceDB table + every BAML class
- `schema_introspect_table(conn, name)`
- `schema_introspect_full(conn)` — the union of DuckDB + LanceDB + BAML
- `list_dlt_sources()` — every `@dlt.source` decorated function (~920)
- `list_cocoindex_apps()` — every CocoIndex v1 App (~53)
- `list_baml_classes()` — every BAML class (~838)

### Legacy modules (DEPRECATED — kept for back-compat)
- `notebooks/nb_utils.py` — marked `@deprecated` (use `_shared.marimo_patterns` instead)
- `notebooks/cli.py` — rewritten post-v7 (flat layout, 52 active notebooks)
- `notebooks/LEGACY_ALIASES.md` — DELETED (stale pre-v7 docs)

## The dual-mode CLI pattern (per https://docs.marimo.io/guides/scripts/)

Every BIEP v3 dashboard + grouped dashboard is dual-mode:
- **Marimo mode**: `marimo edit notebooks/<name>.py`
- **CLI mode**: `uv run notebooks/<name>.py --milestone m1 --asset-check documents_ingested --output json`

The canonical CLI implementation (from `notebooks/19_ireland_pipeline_dashboard.py`):

```python
import marimo
from notebooks._shared.marimo_patterns import (
    cli_argparser_biep, cli_main_if_argv, cli_payload_to_output,
    setup_biep_registry_header,
)

app = marimo.App(width="full", layout_file="19_ireland_pipeline_dashboard.grid.json")

@app.cell(column=0, hide_code=True)
def _intro(mo):
    _ctx = setup_biep_registry_header()
    ...

def _cli_main(argv=None):
    import subprocess
    parser = cli_argparser_biep("19_ireland_pipeline_dashboard")
    args = parser.parse_args(argv)
    # ... invoke dagster asset check ...
    return 0

if __name__ == "__main__":
    cli_main_if_argv(_cli_main, app)
```

The 5 canonical CLI flags are:
- `--milestone` (m0-m4)
- `--asset-check` (documents_ingested / extractions_ragas / lance_chunks)
- `--cohort-kind` (lc_spec / jc_spec / jc_short_course / jc_cba / a_level / gcse)
- `--jurisdiction` (ireland / england / scotland+wales+ni / crown)
- `--output` (json / table / markdown)

## Key sources

| Path | Why it matters |
|:--|:--|
| `notebooks/_shared/schema.py` | The 5 introspection helpers |
| `notebooks/_shared/db.py` | The ibis-first connect helpers |
| `notebooks/_shared/marimo_patterns.py` | The 22 marimo v14 R1+R3+P1-P6 helpers |
| `notebooks/_shared/area_shims/biiep_v3_dashboard.py` | The R2/R3 BIEP v3 8-cell builder |
| `notebooks/_shared/area_shims/leaving_cert.py` | The canonical BIEP v3 operator surface |
| `notebooks/_shared/ragas_gauge.py` | The P5 RAGASGaugeWidget anywidget |
| `notebooks/00_control_panel.py` | The 5-tab deployment control panel |
| `notebooks/_marimo/` | The WASM-exported marimo bundles (per-jurisdiction) |
| `notebooks/cli.py` | The standalone CLI script entry-point |

## Adjacent specs

- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 spec that drives the dashboard layout
- [`centralize-cross-cutting-docs`](../openspec/specs/centralize-cross-cutting-docs/spec.md) — the `lint:drift-docs` gate that audits the in-notebook number claims
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the marimo notebook + web UI + CLI for `deployment-choice.yaml`
- [`cianfhoghlaim-marimo-dashboards`](../openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md) — the 4 ADDED Requirements for the v14 trilogy (tabbed operator console + LLM tab + dual-mode CLI + RAGAS gauge)
- [`centralized-model-registry`](../openspec/specs/centralized-model-registry/spec.md) — the `LITELLM_BASE_URL` + `model_for()` helper for the LLM tab

## DO NOT

- **Never** use raw `duckdb.connect()` — use `ibis.duckdb.connect("md:cianfhoghlaim")` (the BIEP v3 contract is ibis-first; prefer the canonical helper `notebooks/_shared/db.py:connect_md()` over the direct connection).
- **Never** hardcode a table name — resolve via `_shared/schema.py:list_tables()`.
- **Never** ship a notebook that doesn't run as a CLI script (`marimo edit` + `python notebooks/<name>.py` both modes).
- **Never** ship a notebook without the v14 PEP 723 dependency block (`marimo>=0.13` + `ibis-framework[duckdb]>=9.0` + `pandas>=2.2` + `altair>=5.0` + `pyarrow>=15` + `anywidget>=0.9` + `traitlets>=5.14`).
- **Never** import from `notebooks/nb_utils` (use `notebooks/_shared/` instead).
- **Never** hardcode a model name (use `model_for(family, role)` from the centralized model registry).

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`marimo`](../.agents/skills/marimo/SKILL.md) | Marimo reactive Python notebooks (v14 features + dual-mode + WASM export) |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | The MotherDuck / DuckLake lakehouse the notebooks query |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry (the control panel reads) |
| [`ibis`](../.agents/skills/ibis/SKILL.md) | The ibis-first contract (BIEP v3 mandate) |
| [`notebooks-sync`](../.agents/skills/notebooks-sync/SKILL.md) | Layer 11 of the knowledge sync loop (validates the 59 notebooks) |

<!-- generated: 2026-08-10; updated per the 2026-08-10-marimo-v14-cascading-effects-verification-v1 change -->