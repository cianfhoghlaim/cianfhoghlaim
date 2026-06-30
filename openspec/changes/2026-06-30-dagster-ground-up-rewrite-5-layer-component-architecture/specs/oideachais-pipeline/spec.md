## MODIFIED Requirements

### Requirement: 5-Layer Component Architecture (L1 Ingestion)

The `oideachais-pipeline` capability SHALL emit every Ingestion-layer
asset through `CelticIngestionComponent` (defined in
`cianfhoghlaim/dagster/components/layer1_ingestion.py`). The
Component SHALL be registered as the canonical L1 factory and SHALL
emit exactly one `@asset` per `@dlt.source`, with:

- `group_name = "1_ingestion/<domain>/<nation>"`
- `compute_kind = "dlt"`
- `automation_condition = AutomationCondition.eager() | AutomationCondition.cron(automation_cron)`
- `deps = [<upstream asset keys>]` derived from the YAML defs
- The 5 high-churn sources (NCCA, SEC, CCEA, SQA, WJEC) SHALL be
  state-backed via `dg.StateBackedComponent` with
  `state_refresh_interval="monthly"` (per user direction; the default
  is monthly to minimise unnecessary refreshes of cached external
  metadata; per-source override is allowed via the Component YAML).

The legacy `celtic_dlt_source.py` Component and the hand-written
`@asset` functions in `cianfhoghlaim/dagster/assets/` SHALL NOT
be used after this change lands.

#### Scenario: A developer scaffolds a new L1 ingestion asset

- **WHEN** `dg scaffold defs CelticIngestionComponent ie_education_geography --source-id ie.education.geography --domain curriculum --nation ie --automation on_cron --automation_cron "0 4 * * *"` runs
- **THEN** a YAML defs file is created at `defs/1_ingestion/curriculum/ie_education_geography/defs.yaml`
- **AND** `dg check yaml` reports the new asset passes
- **AND** `dg list defs` shows `1_ingestion/curriculum/ie_education_geography` with `automation_condition=cron @ 0 4 * * *`

#### Scenario: A L1 ingestion asset fires on upstream cron

- **GIVEN** the `1_ingestion/curriculum/ie_education_geography` asset has `automation_cron="0 4 * * *"`
- **WHEN** 02:00 UTC daily is reached
- **THEN** Dagster triggers the materialisation via `AutomationCondition.cron("0 4 * * *")`
- **AND** the asset key `["1_ingestion", "curriculum", "ie", "education", "geography"]` is recorded
- **AND** the partition (if any) is set per the YAML's `partitions_def`

#### Scenario: A state-backed L1 ingestion source refreshes monthly

- **GIVEN** the `1_ingestion/curriculum/ie/ncca_curriculum` asset has `state_backed=True` and `state_refresh_interval="monthly"`
- **WHEN** the code-location is reloaded at the start of each calendar month
- **THEN** the `CelticIngestionState` cache is refreshed from the canonical `sources.yaml`
- **AND** any new source URLs or removed source URLs are reflected in the asset graph
- **AND** between monthly refreshes, the cached state is used (no external metadata round-trip)

### Requirement: Partition-Aware Asset Checks (L2 Materials)

Every L2 `CelticMaterialsComponent` SHALL emit a partition-aware
`@asset_check` with the same `partitions_def` as the parent asset.

#### Scenario: BAML fidelity check fires on a single partition

- **GIVEN** the `2_materials/baml_extraction/leaving_cert_math` asset is partitioned by `(cycle, language, subject)`
- **WHEN** the partition `(2026, en, mathematics)` is materialised
- **THEN** `2_materials/baml_extraction/leaving_cert_math_baml_fidelity_check(context, ducklake)` evaluates ONLY that partition
- **AND** the `AssetCheckResult.passed` flag is True if the BAML extraction recovered at least 95% of expected learning outcomes

#### Scenario: A failing partition blocks the parent asset

- **GIVEN** the `2_materials/baml_extraction/leaving_cert_math` asset has a partition-aware `@asset_check`
- **WHEN** the `baml_fidelity_check` returns `passed=False` for the partition `(2026, en, mathematics)`
- **THEN** Dagster marks the parent asset as `failed` for that partition
- **AND** downstream assets in L3 / L4 that depend on that partition are blocked via `AutomationCondition.all_deps_blocked()`

### Requirement: Virtual CocoIndex v1 Assets (L3 Model Lifecycle)
Every CocoIndex v1 App wrapped by `CelticModelLifecycleComponent` SHALL
be emitted as a `is_virtual=True` `@asset` so the LanceDB table mirrors
its upstream (the L1 filesystem scan) automatically. The Component
SHALL enforce the R1–R4 conformance contract
(`oideachais-cocoindex-v1` skill) at scaffold time by calling
`cocoindex_v1_conformance.check_module(module)` BEFORE emitting the
asset. On R1–R4 fail, `dg.Failure` is raised with the exact rule + fix
instructions.

#### Scenario: A developer scaffolds a new L3 v1 App asset

- **WHEN** `dg scaffold defs CelticModelLifecycleComponent apple_photos_metadata --app-name ApplePhotosMetadata --module cianfhoghlaim.cocoindex.apple_photos_metadata --embedding-model BAAI/bge-large-en-v1.5 --hnsw-index` runs
- **THEN** a YAML defs file is created at `defs/3_model_lifecycle/cocoindex_v1/apple_photos_metadata/defs.yaml`
- **AND** `cocoindex_v1_conformance.check_module("cianfhoghlaim.cocoindex.apple_photos_metadata")` returns `passed=True`
- **AND** `dg check yaml` reports the new asset passes
- **AND** `dg list defs` shows `3_model_lifecycle/cocoindex_v1/apple_photos_metadata` with `is_virtual=True`

#### Scenario: A developer tries to scaffold a non-conformant v1 App

- **WHEN** `dg scaffold defs CelticModelLifecycleComponent test_app --module cianfhoghlaim.cocoindex.test_app` runs against a module that fails R2 (no shared_lifespan import)
- **THEN** `dg.Failure` is raised with `R2: no from ._lifespan import shared_lifespan line; add the import to delegate to the canonical lifespan`
- **AND** no YAML defs file is created
- **AND** `dg list defs` does NOT show the failed asset

#### Scenario: A virtual L3 asset resolves through to its L1 upstream

- **GIVEN** the `3_model_lifecycle/cocoindex_v1/leabharlann_books` asset is `is_virtual=True` with `deps=["1_ingestion/filesystem/leabharlann_books"]`
- **WHEN** a new file lands in the leabharlann books directory
- **THEN** the L1 asset materialises (or refreshes its state-backed cache)
- **AND** the L3 virtual asset's `AutomationCondition.eager().resolve_through_virtual()` chain sees the L1 update
- **AND** the L3 virtual asset materialises (which is a no-op for the LanceDB table; the table is updated by the v1 App's `@coco.fn` directly)

### Requirement: Hierarchical Asset Groups (Dagster 1.13+)

Every asset emitted by the 5 KCG Components SHALL use a
hierarchical `group_name` of the form
`"<N>_<layer>/<domain>/<slug>"` where `<N>` is the layer number
(1–5) and `<layer>` is one of {`ingestion`, `materials`,
`model_lifecycle`, `asset_generation`, `agent_ops`}.

Wildcard selection (`group:"1_*"`, `group:"3_model_lifecycle/*"`,
`group:"5_agent_ops/adk"`) SHALL work in the Dagster UI search bar
and via `dg list defs --select`.

#### Scenario: The Dagster UI renders 5 nested groups

- **GIVEN** the 5 KCG Components have emitted 260+ assets across 5 layers
- **WHEN** a developer opens the Dagster UI at `http://localhost:3335`
- **THEN** the asset catalog displays 5 top-level groups: `1_ingestion`, `2_materials`, `3_model_lifecycle`, `4_asset_generation`, `5_agent_ops`
- **AND** each top-level group nests its domain sub-groups (e.g. `1_ingestion/curriculum`, `1_ingestion/law`, `1_ingestion/medicine`)
- **AND** the search bar accepts `group:"3_model_lifecycle/*"` and returns the 17+ L3 assets

#### Scenario: `dg list defs --select` filters by hierarchical group

- **WHEN** `dg list defs --select "group:5_agent_ops/adk"` runs
- **THEN** the output includes only the 40 L5 ADK assets (8 agents × 5 emitted assets per agent)
- **AND** the output excludes L5 custom + agno assets

### Requirement: Declarative Automation Replaces @schedule

The system SHALL NOT use `@schedule` after this change lands. Every
asset's automation SHALL be expressed via `AutomationCondition`
operators (`eager()`, `cron(...)`, `in_progress()`,
`any_deps_updated()`, `all_deps_blocked()`, etc.) on the asset
itself, composed with `.resolve_through_virtual()` for L3
CocoIndex v1 assets.

#### Scenario: A legacy `@schedule` is migrated

- **WHEN** `ccc search "@schedule\(" cianfhoghlaim/dagster/` runs
- **THEN** 0 hits SHALL appear (every `@schedule` is replaced by `AutomationCondition.cron(...)` on the asset)
- **AND** `dg list schedules` returns 0 schedules
- **AND** `dg list defs --json | jq '.[] | select(.automation_condition != null) | .key' | wc -l` returns at least 260

### Requirement: DBT Bridge via Upstream DbtProjectComponent
The 3 dbt-duckdb models SHALL be wired through the upstream
`dagster_dbt.DbtProjectComponent` (NOT a hand-written `@dbt_assets`
decorator + `DbtCliResource`). The 3 models are `weekly_downloads`,
`language_distribution`, and `ocr_confidence_by_model`. The Component
SHALL live at `defs/2_materials/dbt/defs.yaml`. The legacy
`oideachais_dbt_assets` function in `definitions.py` and the
hand-written `_parse_dbt_manifest()` helper SHALL be removed.

#### Scenario: The dbt bridge appears as a single Component

- **WHEN** `dg list defs` runs
- **THEN** 3 new assets appear under `2_materials/dbt/`:
  - `2_materials/dbt/weekly_downloads`
  - `2_materials/dbt/language_distribution`
  - `2_materials/dbt/ocr_confidence_by_model`
- **AND** no hand-written `@dbt_assets` decorator remains in `dagster/`
- **AND** the `DbtProjectComponent` reads the manifest from
  `cianfhoghlaim/dbt_project/target/manifest.json` (refreshed by `dbt parse` on the
  `AutomationCondition.cron("0 6 * * *")` schedule)
