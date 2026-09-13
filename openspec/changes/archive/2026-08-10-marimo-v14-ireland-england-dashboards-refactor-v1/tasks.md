# Tasks: BIEP v3 Ireland + England dashboards refactor (marimo v14 features)

> **Phase plan**: 4 phases, ~10.5 days work.
> **Branch**: `token-plan-lc-pipeline-2026-08` (current working branch).
> **OpenSpec change**: `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`.

## Phase 1 — Build the 3 helper modules + 2 educative notebooks (2 days)

### T1.1 — Build `notebooks/_shared/marimo_patterns.py` (~350 LOC)

The canonical helper module that hoists the 14-line `try/except ImportError`
header (R1) + the `tabbed_biep_operator_console()` helper (P1) +
`progress_bar_with_eta()` (P2) + `llm_chat_with_prompts()` (P3) +
`form_gated_run_button()` (P2) + `cli_argparser_biep()` (P6) +
`three_column_grid_app()` (P4) + `ragas_gauge_widget()` (P5).

Public API:
```python
def setup_biep_registry_header() -> dict: ...
def tabbed_biep_operator_console(tabs: dict, label: str = "BIEP v3 operator console") -> Any: ...
def progress_bar_with_eta(title: str, total: int) -> Any: ...
def llm_chat_with_prompts(system_message: str, prompts: list[str], **kwargs) -> Any: ...
def form_gated_run_button(label: str) -> tuple[Any, Any]: ...
def cli_argparser_biep(notebook_name: str) -> argparse.ArgumentParser: ...
def three_column_grid_app(title: str, layout_filename: str | None = None) -> "marimo.App": ...
def ragas_gauge_widget(score: float, history: list[float] = None) -> Any: ...
```

- [ ] T1.1.a — Write `setup_biep_registry_header()` with the 14-line
  `try/except ImportError` block hoisted from 18 notebooks. Returns a
  dict with `_DEFAULT_LLM`, `_REGISTRY_SUMMARY`, `_DLT_SOURCE_COUNT`,
  `_COCO_APP_COUNT`, `_BAML_CLASS_COUNT`, `_ENABLED_MODELS`.
- [ ] T1.1.b — Write `tabbed_biep_operator_console(tabs)` that wraps
  the 7-cell BIEP v3 surface in `mo.ui.tabs`.
- [ ] T1.1.c — Write `progress_bar_with_eta(title, total)` that wraps
  `mo.status.progress_bar(range(total), show_eta=True, show_rate=True)`.
- [ ] T1.1.d — Write `llm_chat_with_prompts(system_message, prompts,
  **kwargs)` that wraps `mo.ui.chat(mo.ai.llm.openai(...), prompts=[...])`.
- [ ] T1.1.e — Write `form_gated_run_button(label)` that wraps
  `mo.ui.run_button(label).form()`.
- [ ] T1.1.f — Write `cli_argparser_biep(notebook_name)` that returns
  the canonical argparse for the BIEP v3 dashboards (--milestone,
  --asset-check, --cohort-kind, --jurisdiction, --output flags).
- [ ] T1.1.g — Write `three_column_grid_app(title, layout_filename)`
  that returns a `marimo.App(width="full",
  layout_file=Path(__file__).parent / layout_filename)`.
- [ ] T1.1.h — Write `ragas_gauge_widget(score, history)` that wraps
  `mo.ui.anywidget(RAGASGaugeWidget(score=score, history=history))`.
- [ ] T1.1.i — Add the `LITELLM_BASE_URL` constant
  (`http://litellm.cianfhoghlaim.ie/v1`).

### T1.2 — Build `notebooks/_shared/area_shims/biiep_v3_dashboard.py` (~450 LOC)

The canonical BIEP v3 jurisdiction dashboard builder. The single
function `build_biep_v3_dashboard(jurisdiction, milestone, deferred=False)`
returns the tabbed 8-cell operator console as a `mo.ui.tabs`.

Public API:
```python
def build_biep_v3_dashboard(
    jurisdiction: str,  # "ireland" | "england" | "scotland+wales+ni" | "crown" | "all"
    milestone: str | None = None,  # "M0" | "M1" | "M2" | "M3" | "M4" | None
    deferred: bool = False,
) -> Any: ...  # returns mo.ui.tabs
```

- [ ] T1.2.a — Build the `_overview` cell (calls
  `notebooks/_shared/area_shims/leaving_cert.py:biiep_v3_overview()`).
- [ ] T1.2.b — Build the `_ibis_conn` cell (calls
  `notebooks/_shared/db.py:connect_md()`).
- [ ] T1.2.c — Build the `_commands` cell (renders the canonical
  `BIEP_V3_OPERATOR_COMMANDS` bash block).
- [ ] T1.2.d — Build the `_cohort_matrix` cell (renders the
  jurisdiction-specific cohort matrix — Ireland 100 rows, England 276
  rows, SCT/WLS/NI 380 rows, Crown 360 rows, all 1,116 rows).
- [ ] T1.2.e — Build the `_drill_down` cell (jurisdiction-specific
  dropdown chain → RAGAS gauge + per-cohort chart).
- [ ] T1.2.f — Build the `_schedule` cell (renders the BIEP v3
  scheduling policy + per-jurisdiction cron).
- [ ] T1.2.g — Build the `_asset_check_status` cell (calls the
  jurisdiction-specific `dagster asset check` via subprocess).
- [ ] T1.2.h — Build the `_dive_link` cell (renders the canonical
  MotherDuck Dives + Flights per jurisdiction).
- [ ] T1.2.i — Wrap all 8 cells in `mo.ui.tabs` with the 7-tab label
  pattern: `Overview / Cohorts / Drill / Schedule / Asset Checks /
  Dives / Activity`.
- [ ] T1.2.j — Add the deferred banner for the 5 deferred
  jurisdictions (SCT/WLS/NI + Crown).

### T1.3 — Build `notebooks/_shared/ragas_gauge.py` (~150 LOC)

The `RAGASGaugeWidget` anywidget class (P5). Renders a circular
progress gauge + colour band (green ≥0.85 / yellow ≥0.70 / red <0.70)
+ sparkline of last 10 scores.

Public API:
```python
class RAGASGaugeWidget(anywidget.AnyWidget):
    score = traitlets.Float(0.0).tag(sync=True)
    history = traitlets.List([]).tag(sync=True)
    cohort_slug = traitlets.Unicode("").tag(sync=True)
    color = traitlets.Unicode("#22c55e").tag(sync=True)
```

- [ ] T1.3.a — Write the class with the 4 traitlets (score, history,
  cohort_slug, color).
- [ ] T1.3.b — Write the `_update_color` observer (auto-colour based
  on score).
- [ ] T1.3.c — Add the SVG rendering (circular progress gauge with
  colour band + sparkline).
- [ ] T1.3.d — Add the PEP 723 inline dependency block
  (`anywidget>=0.9`, `traitlets>=5.14`).

### T1.4 — Build `notebooks/00_marimo_patterns_tour.py` (~400 LOC)

The marimo-patterns tour. 6 cells demonstrating every marimo feature
used by the BIEP jurisdiction dashboards (P1-P6, R1-R4, E1-E5).

Designed to be the first notebook an operator opens when learning
marimo.

- [ ] T1.4.a — Cell 1: `@app.cell` + PEP 723 + `width="full"`
- [ ] T1.4.b — Cell 2: `mo.ui.dropdown` + `mo.stop` + reactive chain
- [ ] T1.4.c — Cell 3: `mo.ui.tabs` (operator console pattern)
- [ ] T1.4.d — Cell 4: `mo.status.progress_bar` + `mo.ui.form`
- [ ] T1.4.e — Cell 5: `mo.ui.chat` + `mo.ai.llm.openai`
- [ ] T1.4.f — Cell 6: `mo.ui.anywidget(RAGASGaugeWidget)` +
  `@app.cell(column=N)` + `layout_file` + dual-mode CLI

### T1.5 — Build `notebooks/00_biep_v3_dashboard_template.py` (~250 LOC)

The canonical 8-cell template. Single function call
`build_biep_v3_dashboard(jurisdiction="new_jurisdiction")` returns the
tabbed operator console.

- [ ] T1.5.a — Write the PEP 723 header
- [ ] T1.5.b — Write the imports (`build_biep_v3_dashboard`,
  `setup_biep_registry_header`, `cli_argparser_biep`)
- [ ] T1.5.c — Write the 3-column grid app
- [ ] T1.5.d — Write the single `build_biep_v3_dashboard("ireland")`
  call
- [ ] T1.5.e — Write the dual-mode CLI (`_cli_main` + `if __name__ ==
  "__main__":` per https://docs.marimo.io/guides/scripts/)

## Phase 2 — Refactor the 6 Tier 1 BIEP jurisdiction dashboards (5.5 days)

### T2.1 — Refactor `notebooks/19_ireland_pipeline_dashboard.py` (1.5 days, FLAGSHIP)

- [ ] T2.1.a — Replace the 14-line `try/except ImportError` header
  with `_ctx = setup_biep_registry_header()`
- [ ] T2.1.b — Replace the 8 open-coded cells with
  `tabs = build_biep_v3_dashboard(jurisdiction="ireland",
  milestone="M1"); tabs`
- [ ] T2.1.c — Add the `Ask BAML` cell (P3 — `llm_chat_with_prompts`)
- [ ] T2.1.d — Add the `RAGAS Gauge` cell (P5 — `ragas_gauge_widget`)
- [ ] T2.1.e — Add the 3-column grid (`layout_file` +
  `19_ireland_pipeline_dashboard.grid.json`)
- [ ] T2.1.f — Add the dual-mode CLI (`cli_argparser_biep` +
  `_cli_main` + `if __name__ == "__main__":`)
- [ ] T2.1.g — Add the 5 educative outline patterns (E1-E5)
- [ ] T2.1.h — Target LOC: ~280 (from 402)

### T2.2 — Refactor `notebooks/20_england_pipeline_dashboard.py` (1 day)

- [ ] T2.2.a — Same as T2.1 but for England (M3 + M4 milestones,
  276 cohorts)
- [ ] T2.2.b — Target LOC: ~230 (from 308)

### T2.3 — Refactor `notebooks/26_aistear_dashboard.py` (1 day)

- [ ] T2.3.a — Same as T2.1 but for Aistear (M-Aistear milestone, 14
  cohorts, 4 themes × 4 age bands × 3 lang mediums)
- [ ] T2.3.b — Target LOC: ~220 (from 291)

### T2.4 — Refactor `notebooks/27_primary_dashboard.py` (1 day)

- [ ] T2.4.a — Same as T2.1 but for Primary (M-Primary milestone, 64
  cohorts, 4 areas × 8 year levels × 2 langs)
- [ ] T2.4.b — Target LOC: ~220 (from 291)

### T2.5 — Refactor `notebooks/21_sct_wls_ni_pipeline_dashboard.py` (0.5 day)

- [ ] T2.5.a — Same as T2.1 but for SCT/WLS/NI (DEFERRED, 380 cohorts)
- [ ] T2.5.b — Keep the DEFERRED banner visible
- [ ] T2.5.c — Target LOC: ~210 (from 277)

### T2.6 — Refactor `notebooks/22_crown_dependencies_dashboard.py` (0.5 day)

- [ ] T2.6.a — Same as T2.1 but for Crown Dependencies (DEFERRED, 360
  cohorts)
- [ ] T2.6.b — Keep the DEFERRED banner visible
- [ ] T2.6.c — Target LOC: ~210 (from 274)

## Phase 3 — Refactor the 11 Tier 2 dashboards (3 days)

### T3.1 — Refactor `notebooks/23_8_jurisdiction_overview.py` (1 day)

- [ ] T3.1.a — Apply R1+R3+R4 + P3 (LLM tab)
- [ ] T3.1.b — Wrap the 8 cells in `mo.ui.tabs`
- [ ] T3.1.c — Add the dual-mode CLI

### T3.2 — Refactor `notebooks/24_deployment_control_panel.py` (0.5 day)

- [ ] T3.2.a — Apply R1 + R3 (wrap the 9 sync layer statuses in tabs)
- [ ] T3.2.b — Add the LLM tab (P3)

### T3.3 — Refactor `notebooks/00_control_panel.py` (0.5 day)

- [ ] T3.3.a — Apply R1 + add the marimo-patterns tour as a 6th tab
- [ ] T3.3.b — Verify the 5-tab control panel still works

### T3.4 — Refactor `notebooks/40_leaving_cert_subject_panel.py` (0.5 day)

- [ ] T3.4.a — Apply R1 + R3 (each of the 7 subject tabs gets its
  own `mo.ui.tabs`)
- [ ] T3.4.b — Add the dual-mode CLI (R4)
- [ ] T3.4.c — Add the LLM "Ask the Syllabus" tab (P3)

### T3.5-T3.11 — Refactor the 7 BIEP lakehouse explorers (1.5 days, 7 files)

- [ ] T3.5 — `notebooks/10_biep_pipeline_lakehouse_01_ducklake_explorer.py`
  (R1+R3)
- [ ] T3.6 — `notebooks/10_biep_pipeline_lakehouse_02_lakehouse_inspector.py`
  (R1+R3; already uses tabs — verify)
- [ ] T3.7 — `notebooks/10_biep_pipeline_lakehouse_03_all_nations.py`
  (R1+R3)
- [ ] T3.8 — `notebooks/10_biep_pipeline_lakehouse_04_cocoindex_embedding_coverage.py`
  (R1+R3)
- [ ] T3.9 — `notebooks/10_biep_pipeline_lakehouse_05_marking_scheme_analyzer.py`
  (R1 only; already uses `mo.ui.chat`)
- [ ] T3.10 — `notebooks/10_biep_pipeline_lakehouse_06_exam_papers_explorer.py`
  (R1+R3; already uses 8 tabs — verify)
- [ ] T3.11 — `notebooks/10_biep_pipeline_lakehouse_07_subject_full_pipeline.py`
  (R1 only; already implements the reference dual-mode CLI)
- [ ] T3.11.b — `notebooks/10_biep_pipeline_lakehouse_08..11_*.py`
  (R1+R3, batch refactor)

## Phase 4 — Validate + mise.toml + archive (0.5 day)

### T4.1 — `mise.toml` updates

- [ ] T4.1.a — Add `biep:v3:marimo:dev` task that opens all 6 BIEP
  dashboards + the 7 lakehouse explorers simultaneously
- [ ] T4.1.b — Add `biep:v3:marimo:wasm:export` task that exports
  all 17 to WASM
- [ ] T4.1.c — Add `biep:v3:marimo:lint` task that runs `marimo
  check` on all 17
- [ ] T4.1.d — Add 17 `biep:v3:<jurisdiction>:gate` tasks (one per
  dashboard) that invoke the dual-mode CLI
- [ ] T4.1.e — Add 17 grid.json layout files

### T4.2 — OpenSpec validation

- [ ] T4.2.a — Run `openspec validate
  2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1
  --strict`
- [ ] T4.2.b — Run `marimo check` on all 17 refactored dashboards
- [ ] T4.2.c — Run `mise run biep:v3:marimo:lint` (the marimo lint)

### T4.3 — Archive

- [ ] T4.3.a — Run `openspec archive
  2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1 --yes`
- [ ] T4.3.b — Commit + push the change (per the AGENTS.md mandatory
  push policy)

## Acceptance gates

- [ ] All 17 refactored dashboards open via `marimo edit` without
  errors
- [ ] All 17 refactored dashboards run as scripts via
  `python <name>.py --milestone m1 --asset-check documents_ingested`
  and emit JSON to stdout
- [ ] All 17 grid.json layout files are valid JSON
- [ ] All 17 dashboards use `setup_biep_registry_header()` (no
  duplicated 14-line `try/except ImportError` block)
- [ ] All 17 dashboards use `build_biep_v3_dashboard()` (no
  open-coded 8-cell surface)
- [ ] All 6 BIEP jurisdiction dashboards use the 3-column grid +
  `Ask BAML` tab + `RAGAS Gauge` widget
- [ ] `openspec validate --strict` passes
- [ ] `marimo check` passes on all 17
- [ ] `mise run biep:v3:marimo:lint` passes
- [ ] `mise run biep:v3:ireland:gate --milestone=m1` exits 0 (JSON
  payload to stdout)
- [ ] Total LOC saved: ~1,650 across the 17 dashboards