## MODIFIED Requirements

### Requirement: Declarative Automation + Virtual Assets + State-Backed Components (Dagster 1.13+)

Every asset emitted by the 5 Components SHALL use the Dagster 1.13+
feature set. The canonical group_name convention MUST use the
underscore-separated form (`"<N>_<layer>_<domain>_<slug>"`) rather than
the slash-separated form (`"<N>_<layer>/<domain>/<slug>"`) so that
each value matches the strict `^[A-Za-z0-9_]+$` regex that Dagster
1.13.1 enforces. (As of the 2026-07-16 pre-pick-4 audit, the previous
slash-separated form was rejected by `dg.load_defs()` for 63 group_name
sites across 11 orchestration files, causing the entire `defs/` tree
to fall back to an empty `Definitions` per `definitions.py:57-65`.)

The system SHALL enforce:

- **`AutomationCondition`** in place of `@schedule`
- **`is_virtual=True`** on L3 CocoIndex v1 assets
- **`.resolve_through_virtual()`** on L3 + L5 automation conditions
- **Partition-aware `@asset_check`** on L2 BAML extraction assets
- **`dg.StateBackedComponent`** on the 5 high-churn L1 sources
  (NCCA/SEC/CCEA/SQA/WJEC) with `state_refresh_interval="monthly"` as
  the default (per user direction; per-source override is allowed)
- **`group_name` value MUST match `^[A-Za-z0-9_]+$`** (the canonical
  Dagster 1.13.1 regex). The MUST-MATCH constraint forbids `/`
  characters. Each `group_name` is constructed by joining the 5-layer
  + 6-prefix taxonomy with `_` (single underscore).
  Examples of valid values: `1_ingestion_curriculum_lc5`,
  `2_materials_ie_law_courts`, `3_model_lifecycle_lc_cognify_lc5_chemistry`,
  `3_model_lifecycle_federated_ocr_irish_ocr_federated`,
  `4_asset_generation_marimo_chemistry`.
- **Canonical M4-Max dispatch**: the
  `select_optimal_for_m4_max(model_name: str) -> str` function
  (alias `get_default_for_m4_max`) SHALL be exposed for M4-Max
  hardware dispatch. It returns the canonical low-VRAM model selection
  using the same `"select_ocr_backend"` pattern from
  `cianfhoghlaim-cocoindex-v1/SKILL.md`.

#### Scenario: No legacy `@schedule` exists

- **WHEN** `ccc search "@schedule\(" dagster/` runs
- **THEN** 0 hits SHALL appear
- **AND** `dg list schedules` returns 0 schedules
- **AND** `dg list defs --json | jq '.[] | select(.automation_condition != null) | .key' | wc -l` returns at least 260

#### Scenario: L3 CocoIndex v1 assets use `is_virtual=True`

- **WHEN** `dg list defs --json | jq '.[] | select(.is_virtual == true) | .key' | wc -l` runs
- **THEN** the count SHALL be at least 17 (one per CocoIndex v1 App)

#### Scenario: A state-backed L1 source refreshes monthly

- **GIVEN** the `1_ingestion_curriculum_ie_ncca_curriculum` asset has `state_backed=True` and `state_refresh_interval="monthly"`
- **WHEN** the code-location is reloaded at the start of each calendar month
- **THEN** the `CelticIngestionState` cache is refreshed from the canonical `sources.yaml`
- **AND** between monthly refreshes, the cached state is used (no external metadata round-trip)
- **AND** per-source override is allowed via the Component YAML (a developer can set `state_refresh_interval="weekly"` for a high-volatility source)

#### Scenario: All `group_name` values MUST match `^[A-Za-z0-9_]+$`

- **WHEN** `python3 -c "import re, glob; [print(f) for f in sorted(glob.glob('orchestration/**/*.py', recursive=True)) if re.search(r'group_name\\s*=\\s*\"[^\"]*/[^\"]*\"', open(f).read())]"` runs
- **THEN** 0 files are printed
- **AND** `dg.load_defs()` from `dagster.load_defs` returns successfully (no Pydantic validation error)
- **AND** the post-migration count is 63+ group_name values across 11 files, all matching the regex

#### Scenario: The 36+ lc5 assets load into the Dagster graph

- **WHEN** `dg.load_defs(defs_root=cianfhoghlaim.orchestration.defs)` runs (per `definitions.py:57-65`)
- **THEN** the loading succeeds with no `DgRuntimeApiError` or Pydantic validation error
- **AND** `dg list defs --json | jq '.[] | select(.group_name | startswith("1_ingestion_curriculum_lc5")) | .key' | wc -l` returns at least 6 (the 6 LC subjects × per-subject asset)
- **AND** `dg list defs --json | jq '.[] | select(.group_name | startswith("3_model_lifecycle_lc_cognify")) | .key' | wc -l` returns at least 6 (the 6 cognify assets)
- **AND** `dg list defs --json | jq '.[] | select(.group_name == "3_model_lifecycle_lc_cross_subject_lc5") | .key' | wc -l` returns at least 1 (the cross-subject Graphiti stream)

#### Scenario: The M4-Max dispatch helper is exposed

- **WHEN** `python3 -c "from cianfhoghlaim.cocoindex._lifespan import select_optimal_for_m4_max"` runs
- **THEN** the import succeeds (module + helper are exposed)
- **AND** `select_optimal_for_m4_max("qwen3-vl-8b")` returns a non-empty string
- **AND** `get_default_for_m4_max("qwen3-vl-8b")` is callable as an alias and returns the same value
