# Change: BIEP v3 Ireland + England dashboards refactor (marimo v14 features)

## Why

The 17 BIEP v3 dashboards under `notebooks/` (the 6 jurisdiction dashboards
+ the 7 lakehouse explorers + the 4 cross-cut dashboards) were deployed on
2026-08-08 (commit `be78f68be`) with the canonical 8-cell operator console
shape, but they are missing 6 high-impact marimo v14 features that are
present in the upstream marimo reference notebooks (`lance-demo.py`,
`chroma-db-search.py`, `motherduck-demo.py`, `iceberg-demo.py`,
`duckwow.py`, `polars-demo.py`, `claude-titanic.py`) that we cloned to
`docs/research/marimo/marimo/youtube-material/examples/`:

1. **`mo.ui.tabs` operator console** — the 8 cells are open-coded as
   top-level cells, so the operator sees all 8 simultaneously. Should
   collapse to a single 7-tab operator console (`Overview / Cohorts /
   Drill / Schedule / Asset Checks / Dives / Activity`).
2. **`mo.status.progress_bar` + `mo.ui.form`** — the `_asset_check_status`
   cell uses a blocking `subprocess.run("dagster asset check ...")` with no
   ETA / rate feedback. Should poll with a progress bar and gate submit.
3. **`mo.ui.chat` + `mo.ai.llm.openai(base_url=litellm)`** — no LLM-assisted
   analysis tab. Should add an "Ask BAML" tab wired to the canonical litellm
   proxy (which dispatches to local llama-swap models OR the minimax-m3
   token plan API per the `centralized-model-registry` capability).
4. **`@app.cell(column=N)` + `layout_file=".../grid.json"`** — single-column
   vertical layout. Should adopt a 3-column grid (left: filters + cohort
   matrix; center: drill-down + RAGAS gauge; right: asset checks + Dive
   link) per the `lance-demo.py` + `youtube-material/examples/layouts/`
   pattern.
5. **`mo.ui.anywidget(RAGASGaugeWidget)`** — no per-cohort visual RAGAS
   score widget. Should build a custom anywidget (circular progress gauge
   + colour band + sparkline of last 10 scores).
6. **Dual-mode (marimo + CLI) per https://docs.marimo.io/guides/scripts/**
   — only `10_biep_07_subject_full_pipeline.py` implements the canonical
   argparse + `if __name__ == "__main__":` dual-mode pattern today. Should
   roll out to all 17 dashboards so they can be invoked from
   `mise run biep:v3:gate --milestone=m1`.

Additionally 4 refactor patterns reduce duplication:

- **R1**: Hoist the 14-line `try: from meaisinfhoghlaim.models … except
  ImportError: _DEFAULT_LLM = "minimax-m3"` block from 18 notebooks into
  `notebooks/_shared/marimo_patterns.py:setup_biep_registry_header()`
  (−252 LOC).
- **R2**: Hoist the open-coded 8-cell BIEP v3 surface from 9 jurisdiction
  dashboards into `notebooks/_shared/area_shims/biiep_v3_dashboard.py:
  build_biep_v3_dashboard()` (−1,400 LOC).
- **R3**: Wrap the 8 cells in `mo.ui.tabs` (per P1).
- **R4**: Add the dual-mode CLI (per P6).

This brings the 17 dashboards to the same polish level as the upstream
marimo reference notebooks AND consolidates ~1,650 LOC of duplication
into 3 reusable helper modules + 2 educative notebooks.

## What changes

- **6 BIEP jurisdiction dashboards refactored** (notebooks 19, 20, 21, 22,
  26, 27) — apply R1+R2+R3+R4 + P1+P3+P4+P5+P6 to each.
- **7 BIEP lakehouse explorers refactored** (notebooks
  `10_biep_pipeline_lakehouse_01..11_*.py`) — apply R1+R3 + P3 to each.
  `02_lakehouse_inspector.py` and `06_exam_papers_explorer.py` already
  use `mo.ui.tabs`; `05_marking_scheme_analyzer.py` already uses
  `mo.ui.chat`; `07_subject_full_pipeline.py` is the reference for the
  dual-mode CLI.
- **4 cross-cut dashboards refactored** (notebooks 23, 24, 00, 40) —
  apply R1+R3+R4 + P3.
- **3 new helper modules**:
  - `notebooks/_shared/marimo_patterns.py` — `setup_biep_registry_header()`
    (R1) + `progress_bar_with_eta()` (P2) + `tabbed_biep_operator_console()`
    (P1) + `ragas_gauge_widget()` (P5) + `llm_chat_with_prompts()`
    (P3) + `form_gated_run_button()` (P2) + `cli_argparser_biep()`
    (P6) + `three_column_grid_app()` (P4).
  - `notebooks/_shared/area_shims/biiep_v3_dashboard.py` —
    `build_biep_v3_dashboard(jurisdiction, milestone, deferred=False)`
    (R2/R3) — the 8-cell operator console as a single composable function.
  - `notebooks/_shared/ragas_gauge.py` — `RAGASGaugeWidget` anywidget (P5).
- **2 new educative notebooks**:
  - `notebooks/00_marimo_patterns_tour.py` — the marimo-patterns tour
    demonstrating every marimo feature used by the BIEP dashboards.
  - `notebooks/00_biep_v3_dashboard_template.py` — the canonical 8-cell
    template that any new BIEP jurisdiction dashboard should start from.
- **17 `grid.json` layout files** — one per refactored dashboard,
  persisting the 3-column layout.
- **17 `mise.toml` tasks** — `biep:v3:marimo:dev` (open all 17
  dashboards simultaneously) + `biep:v3:marimo:wasm:export` (export all
  17 to WASM) + `biep:v3:marimo:lint` (the marimo `marimo check` lint
  for all 17) + 17 `biep:v3:<jurisdiction>:gate` tasks for CI.
- **5 educative outline patterns** (E1-E5) applied to every cell of every
  refactored notebook: section header per cell (E1), inline KCG pattern
  callout (E2), inline marimo reactivity explanation (E3), inline BIEP v3
  milestone callout (E4), footer references per cell (E5).
- **4 ADDED Requirements** to
  `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md` (tabbed operator
  console, LLM-assisted analysis tab, dual-mode CLI unification, RAGAS
  gauge widget).

## Out of scope

- The 36+ Tier 3 notebooks (meaisin + Celtic + corpus + speedrun MMO +
  academic + Irish law) — tracked by the follow-up change
  `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1`.
- The 10 sync layer dashboards (14, 15, 25, 26_baml, 27_stacks, 28_dlt,
  29_agents, 30_notebooks) — tracked by the follow-up change
  `2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1`.
- The 4 Tier 4 legacy notebooks (`notebooks/legacy/*` + `ie_law_explorer.py`)
  — only R1 applied (header hoist); no other refactor.
- The 6 deferred jurisdictions (M5-M10: SCT/WLS/NI + Crown) — the
  notebooks `21_sct_wls_ni_pipeline_dashboard.py` + `22_crown_dependencies_dashboard.py`
  are refactored in this change but the DAGSTER assets remain DEFERRED
  per the BIEP v3 spec.
- Re-enabling the Qwen DashScope API as a production path (the wiring
  stays, but the agents do not route through it). Tracked by issue #147.
- Cross-repo changes (`leabharlann/` is a read-only consumer).

## Dependencies

```markdown
## Dependencies

`Blocked by: none` (the 17 dashboards are already on `md:cianfhoghlaim`;
no infrastructure work needed).

`Blocked by (soft): 2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1`
(the Aistear + Primary CocoIndex + Dagster wiring; this change reuses the
`notebooks/26_aistear_dashboard.py` + `27_primary_dashboard.py` files
from that change as inputs).

`Affected repos: cianfhoghlaim`
```

## Impact

- **Affected specs**: `cianfhoghlaim-marimo-dashboards` (4 ADDED
  Requirements).
- **Affected code/config**:
  - `notebooks/_shared/marimo_patterns.py` (new; ~350 LOC)
  - `notebooks/_shared/area_shims/biiep_v3_dashboard.py` (new; ~450 LOC)
  - `notebooks/_shared/ragas_gauge.py` (new; ~150 LOC)
  - `notebooks/00_marimo_patterns_tour.py` (new; ~400 LOC)
  - `notebooks/00_biep_v3_dashboard_template.py` (new; ~250 LOC)
  - 17 dashboard files refactored (R1+R2+R3+R4 + selective P1-P6):
    `notebooks/{00,19,20,21,22,23,24,26,27,40}_*.py` +
    `notebooks/10_biep_pipeline_lakehouse_{01..11}_*.py`
  - 17 `grid.json` files (one per refactored dashboard)
  - `mise.toml` (add 17 `biep:v3:marimo:dev` + 17 `wasm:export` +
    `lint` + 17 `<jurisdiction>:gate` tasks)
- **LOC saved**: ~1,650 LOC across the 17 dashboards (R1+R2).
- **No secret values written to disk**: all `infisical://dev-baile/...`
  refs hydrated by mise + Locket.

## Cross-references

- `openspec/specs/cianfhoghlaim-marimo-dashboards/spec.md` — the
  capability this change extends (4 ADDED Requirements)
- `openspec/specs/british-isles-education-pipeline-v3/spec.md` — the
  BIEP v3 spec that drives the dashboard layout (the 8-cell surface)
- `openspec/specs/centralized-model-registry/spec.md` — the litellm proxy
  + `model_for()` helper for the LLM tab (P3)
- `openspec/changes/2026-08-09-biiep-v3-4-stage-ireland-education-rollout-v1/`
  — the Aistear + Primary rollout this change refactors
- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/`
  — the BIEP v3 umbrella change (the 8-cell surface is defined there)
- `notebooks/_shared/db.py` — the ibis-first connect helper (R1's
  `setup_biep_registry_header()` builds on this)
- `notebooks/_shared/schema.py` — the 5 introspection helpers (R1
  references `list_dlt_sources()` / `list_cocoindex_apps()` /
  `list_baml_classes()`)
- `notebooks/_shared/area_shims/leaving_cert.py` — the BIEP v3 overview
  helper (R2's `build_biep_v3_dashboard()` calls `biiep_v3_overview()`)
- `.agents/skills/marimo/SKILL.md` — the marimo skill (P1-P6 patterns)
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract (BIEP v3 mandate)
- `.agents/skills/centralized-registry/SKILL.md` — the centralized
  model + schema registry (P3's LLM integration)
- `docs/research/marimo/marimo/youtube-material/examples/` — the
  upstream marimo reference notebooks (lance-demo, chroma-db-search,
  motherduck-demo, iceberg-demo, duckwow, polars-demo, claude-titanic)
- https://docs.marimo.io/guides/scripts/ — the canonical dual-mode
  CLI pattern (P6)