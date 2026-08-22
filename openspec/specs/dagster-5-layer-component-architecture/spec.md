# dagster-5-layer-component-architecture Specification

## Purpose

`dagster-5-layer-component-architecture` is a capability of the
Cianfhoghlaim platform. It defines the canonical 5-layer Dagster
architecture: **Ingestion → Materials → Model Lifecycle → Asset
Generation → Agent Operations**. The 5 layers map onto 5 KCG-specific
Dagster Components (`CelticIngestionComponent` /
`CelticMaterialsComponent` / `CelticModelLifecycleComponent` /
`CelticAssetGenerationComponent` / `CelticAgentOpsComponent`) at
`cianfhoghlaim/dagster/components/layer{1..5}_*.py`.

The architecture uses Dagster 1.13+ Declarative Automation
(`AutomationCondition.eager() | .cron(...)`), Virtual Assets
(`is_virtual=True` on the 17 L3 CocoIndex v1 Apps), and State-Backed
Components (the 5 L1 high-churn sources NCCA / SEC / CCEA / SQA / WJEC
with `state_refresh_interval="monthly"`). R1–R4 conformance is enforced
at scaffold time.

The 5-layer rewrite supersedes the legacy 3 KCG Components
(`celtic_dlt_source`, `celtic_cocoindex_v1`, `celtic_lancedb_hnsw`).
L5 Agent Operations adds 12 agents × 5 emitted assets = 60 new L5
assets, with RisingWave event stream at
`risingwave.cianfhoghlaim.ie:4566` + Letta memory + Langfuse traces
dropped.
## Requirements
### Requirement: 5-Layer Hierarchy
The Dagster asset graph SHALL be organised into exactly 5 layers:

- **Layer 1 — Ingestion** (`1_ingestion`): DLT sources → DuckLake raw tables
- **Layer 2 — Materials** (`2_materials`): BAML/Docling extraction → typed DuckLake + LanceDB
- **Layer 3 — Model Lifecycle** (`3_model_lifecycle`): CocoIndex v1 Apps + Cognee + FalkorDB
- **Layer 4 — Asset Generation** (`4_asset_generation`): marimo dashboards + TanStack Start pages + oRPC routes
- **Layer 5 — Agent Operations** (`5_agent_ops`): 12-agent fleet + OpenClaw/OpenChamber/Hermes + Letta + RisingWave + Langfuse

Every asset SHALL belong to exactly one layer. Cross-layer
dependencies SHALL flow downward only (L5 → L4 → L3 → L2 → L1).
The ONLY upward dependency allowed is the
`is_virtual=True` resolution in L3 + the `agent_event_*` /
`agent_trace_*` reads in L5.

#### Scenario: The 5 layers render as 5 nested groups in the UI

- **WHEN** `dg list defs --json | jq '.[].group_name' | cut -d/ -f1 | sort -u` runs
- **THEN** exactly 5 distinct layer prefixes appear: `1_ingestion`, `2_materials`, `3_model_lifecycle`, `4_asset_generation`, `5_agent_ops`

#### Scenario: Cross-layer dependency edges flow downward only

- **WHEN** `dg list defs --json | jq '.[] | .deps[]' | sort -u` runs
- **THEN** every dependency key SHALL start with one of the 5 layer prefixes
- **AND** the direction SHALL be from a higher-numbered layer to a lower-numbered layer (e.g. `2_materials/*` depends on `1_ingestion/*`, never the reverse)

### Requirement: 5 KCG-Specific Components (one per layer)

The Cianfhoghlaim platform SHALL provide exactly 5
`dg.Component` subclasses (one per layer):

1. `CelticIngestionComponent` (`cianfhoghlaim/dagster/components/layer1_ingestion.py`)
2. `CelticMaterialsComponent` (`cianfhoghlaim/dagster/components/layer2_materials.py`)
3. `CelticModelLifecycleComponent` (`cianfhoghlaim/dagster/components/layer3_model_lifecycle.py`)
4. `CelticAssetGenerationComponent` (`cianfhoghlaim/dagster/components/layer4_asset_generation.py`)
5. `CelticAgentOpsComponent` (`cianfhoghlaim/dagster/components/layer5_agent_ops.py`)

Each Component SHALL be registered in
`pyproject.toml:[tool.dg].registry_modules = ["cianfhoghlaim.dagster.components"]`
so `dg list components` discovers them.

Each Component SHALL be a subclass of `dg.Component` + `dg.Model`
(and `dg.StateBackedComponent` where noted) and SHALL provide:

- A `build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions` method
- A Pydantic-typed YAML schema (`ResolvableModel`)
- Optional `dg.Scaffolder` for `dg scaffold defs` ergonomics

#### Scenario: `dg list components` lists all 5 KCG Components

- **WHEN** `dg list components` runs
- **THEN** the output lists 5 Component types:
  - `cianfhoghlaim.dagster.components.CelticIngestionComponent`
  - `cianfhoghlaim.dagster.components.CelticMaterialsComponent`
  - `cianfhoghlaim.dagster.components.CelticModelLifecycleComponent`
  - `cianfhoghlaim.dagster.components.CelticAssetGenerationComponent`
  - `cianfhoghlaim.dagster.components.CelticAgentOpsComponent`

#### Scenario: `dg scaffold defs` scaffolds a new asset per Component

- **WHEN** `dg scaffold defs CelticIngestionComponent test_asset --source-id ie.test --domain test --nation ie` runs
- **THEN** a new YAML defs file is created at `defs/1_ingestion/test/test_asset/defs.yaml`
- **AND** `dg check yaml defs/1_ingestion/test/test_asset/defs.yaml` returns exit code 0
- **AND** `dg list defs` includes `1_ingestion/test/ie/test_asset`

### Requirement: Declarative Automation + Virtual Assets + State-Backed Components (Dagster 1.13+)

Every asset emitted by the 5 Components SHALL use the Dagster 1.13+
feature set:

- **`AutomationCondition`** in place of `@schedule`
- **`is_virtual=True`** on L3 CocoIndex v1 assets
- **`.resolve_through_virtual()`** on L3 + L5 automation conditions
- **Partition-aware `@asset_check`** on L2 BAML extraction assets
- **`dg.StateBackedComponent`** on the 5 high-churn L1 sources
  (NCCA/SEC/CCEA/SQA/WJEC) with `state_refresh_interval="monthly"` as
  the default (per user direction; per-source override is allowed)
- **Hierarchical `group_name`** of the form `"<N>_<layer>/<domain>/<slug>"`

#### Scenario: No legacy `@schedule` exists

- **WHEN** `ccc search "@schedule\(" cianfhoghlaim/dagster/` runs
- **THEN** 0 hits SHALL appear
- **AND** `dg list schedules` returns 0 schedules
- **AND** `dg list defs --json | jq '.[] | select(.automation_condition != null) | .key' | wc -l` returns at least 260

#### Scenario: L3 CocoIndex v1 assets use `is_virtual=True`

- **WHEN** `dg list defs --json | jq '.[] | select(.is_virtual == true) | .key' | wc -l` runs
- **THEN** the count SHALL be at least 17 (one per CocoIndex v1 App)

#### Scenario: A state-backed L1 source refreshes monthly

- **GIVEN** the `1_ingestion/curriculum/ie/ncca_curriculum` asset has `state_backed=True` and `state_refresh_interval="monthly"`
- **WHEN** the code-location is reloaded at the start of each calendar month
- **THEN** the `CelticIngestionState` cache is refreshed from the canonical `sources.yaml`
- **AND** between monthly refreshes, the cached state is used (no external metadata round-trip)
- **AND** per-source override is allowed via the Component YAML (a developer can set `state_refresh_interval="weekly"` for a high-volatility source)

### Requirement: CocoIndex v1 R1–R4 Conformance Enforced at Scaffold Time

The `CelticModelLifecycleComponent` SHALL call
`cocoindex_v1_conformance.check_module(module)` BEFORE emitting
the asset. The check enforces the 4-rule R1–R4 contract
(`cianfhoghlaim-cocoindex-v1` skill):

- **R1** — Module imports `from ._lifespan import shared_lifespan`
- **R2** — Module imports the canonical ContextKeys (`LANCE_DB`, `EMBEDDER`, `RESOLVED_FILE_REGISTRY`) OR declares an additional one with `# R2-exempt: <reason>`
- **R3** — `coco.App(...)` is at module scope (NOT inside a function body)
- **R4** — At least one `@coco.fn(` decorator is present

On R1–R4 fail, `dg.Failure` is raised with the exact rule + a
`dg.MetadataValue.md(...)` fix-instructions block.

#### Scenario: A conformant v1 App scaffolds successfully

- **GIVEN** the module `cianfhoghlaim.cocoindex.leabharlann_embedding` passes R1–R4
- **WHEN** `dg scaffold defs CelticModelLifecycleComponent leabharlann_books --app-name LeabharlannBooksEmbedding --module cianfhoghlaim.cocoindex.leabharlann_embedding` runs
- **THEN** the YAML defs file is created at `defs/3_model_lifecycle/cocoindex_v1/leabharlann_books/defs.yaml`
- **AND** `dg check yaml` returns exit code 0
- **AND** `dg list defs` includes `3_model_lifecycle/cocoindex_v1/leabharlann_books`

#### Scenario: A non-conformant module fails the scaffold

- **GIVEN** the module `cianfhoghlaim.cocoindex.test_non_conformant` fails R2 (declares a new ContextKey without `# R2-exempt:`)
- **WHEN** `dg scaffold defs CelticModelLifecycleComponent test_app --app-name TestApp --module cianfhoghlaim.cocoindex.test_non_conformant` runs
- **THEN** `dg.Failure` is raised with `R2: no from ._lifespan import shared_lifespan line; add the import to delegate to the canonical lifespan`
- **AND** no YAML defs file is created
- **AND** `dg list defs` does NOT include `3_model_lifecycle/cocoindex_v1/test_app`

#### Scenario: A weekly drift check detects a conformance regression

- **GIVEN** the asset `3_model_lifecycle/cocoindex_v1/cocoindex_v1_conformance_drift` is scheduled weekly via `AutomationCondition.cron("0 6 * * 1")`
- **WHEN** the weekly cron fires and a v1 App has drifted out of R1–R4 compliance
- **THEN** the `AssetCheckResult.passed` flag is False with `metadata={"violation": "R2", "module": "cianfhoghlaim.cocoindex.<X>"}`
- **AND** a Dagster alert is sent via the existing `upstream_breaking_change_sensor` (the 4-layer monitor)

### Requirement: 5-Layer `defs/` Tree

The Cianfhoghlaim Dagster definitions SHALL be organised into
exactly 5 `defs/<layer>/` folders (one per layer), each with a
`defs.yaml` root mount + per-domain sub-folders. The previous
6-sub-folder shape (`cianfhoghlaim_pipeline`, `celtic_asset_generation`,
`cognify`, `croilar`, `meaisinfhoghlaim_platform`, `tuatha`) SHALL
be retired and replaced by the 5-layer shape.

#### Scenario: The `defs/` tree has exactly 5 layer folders

- **WHEN** `ls cianfhoghlaim/dagster/defs/` runs
- **THEN** the output includes exactly: `1_ingestion/`, `2_materials/`, `3_model_lifecycle/`, `4_asset_generation/`, `5_agent_ops/`
- **AND** the previous 6 sub-folders (`cianfhoghlaim_pipeline/`, `celtic_asset_generation/`, `cognify/`, `croilar/`, `meaisinfhoghlaim_platform/`, `tuatha/`) do NOT exist

#### Scenario: Each layer has at least 1 sub-folder

- **WHEN** `find cianfhoghlaim/dagster/defs/<layer> -mindepth 1 -maxdepth 1 -type d` runs
- **THEN** the output for `1_ingestion/` SHALL include at least: `curriculum/`, `law/`, `medicine/`, `site_analysis/`, `filesystem/`
- **AND** the output for `2_materials/` SHALL include at least: `baml_extraction/`, `ocr_comparison/`, `pdf_processing/`, `embedding_pivot/`, `dbt/`
- **AND** the output for `3_model_lifecycle/` SHALL include at least: `cocoindex_v1/`, `cognify/`, `cross_archive/`
- **AND** the output for `4_asset_generation/` SHALL include at least: `marimo_dashboards/`, `tanstack_pages/`, `orpc_routes/`
- **AND** the output for `5_agent_ops/` SHALL include at least: `custom/`, `adk/`, `agno/`
- **AND** the `5_agent_ops/pipecat/` sub-folder is INTENTIONALLY ABSENT (the voice agent is deferred to a follow-on change per user direction)

### Requirement: Canonical v7 flattened package layout

The system SHALL treat the repository root as the canonical location of the
`cianfhoghlaim` Python package. Every `from cianfhoghlaim.X import Y` import
SHALL resolve against the flat repo-root layout — there SHALL NOT be a
separate `cianfhoghlaim/` subdirectory containing the package source.

The package marker files (`__init__.py`, `__main__.py`, `__deployment__.py`,
`cli.py` for the cianfhoghlaim CLI) SHALL live at the repository root and
SHALL use the `__double_underscore__` naming convention so they sort first in
directory listings.

The top-level sub-directories SHALL serve as `cianfhoghlaim` sub-modules
either by (a) carrying an `__init__.py` (regular package) or (b) relying on
Python 3.12+ implicit namespace package semantics. The following
directories SHALL be importable as `cianfhoghlaim.<name>`:

- `agents/` → `cianfhoghlaim.agents`
- `baml_src/` → `cianfhoghlaim.baml_src`
- `bonneagar/` → `cianfhoghlaim.bonneagar`
- `cocoindex/` → `cianfhoghlaim.cocoindex`
- `dlt/` → `cianfhoghlaim.dlt`
- `meaisinfhoghlaim/` → `cianfhoghlaim.meaisinfhoghlaim`
- `notebooks/` → `cianfhoghlaim.notebooks`
- `orchestration/` → `cianfhoghlaim.orchestration`

The web and spaces directories SHALL NOT be part of the Python package
(the web/ sub-tree is bun-managed; spaces/ is a separate project with its own
`pyproject.toml`).

The Dagster code-location entry point SHALL be
`orchestration.definitions` (the file `orchestration/definitions.py` at the
repository root). The historical path `cianfhoghlaim.dagster.definitions`
SHALL NOT be the entry point. Any `from cianfhoghlaim.dagster.X import Y`
import in test code or documentation SHALL be rewritten to
`from orchestration.X import Y`.

#### Scenario: uv sync succeeds

- **WHEN** the user runs `uv sync` from the repository root
- **THEN** uv SHALL resolve all dependencies (including dagster >= 1.13, duckdb >= 1.4, cocoindex >= 1.0,<2.0,!=1.0.8, lancedb >= 0.15)
- **AND THEN** exit 0

#### Scenario: Python imports resolve

- **WHEN** the user runs `python -c "from cianfhoghlaim.dlt.common.cli import main"`
- **THEN** the import SHALL succeed
- **AND THEN** the resolution path SHALL be `orchestration/...` or `dlt/...` at the repo root (NOT from a non-existent `cianfhoghlaim/` subdirectory)

#### Scenario: Dagster code-location loads

- **WHEN** the user runs `mise run cic:dagster:dev`
- **THEN** Dagster SHALL load the 5-layer component architecture from the
  `orchestration/defs/` directory tree
- **AND THEN** the code location SHALL report 199 assets + 31 jobs + 6 schedules + 16 sensors + 22 asset checks

#### Scenario: Dagster module-name canonical

- **WHEN** the user reads `dg.toml`
- **THEN** the `module_name` field SHALL equal `orchestration.definitions`
- **AND THEN** the `mise.toml:138` `cic:dagster:dev` task body SHALL run
      `uv run dagster dev -m orchestration.definitions`

### Requirement: BIEP v3 2-axis scope/year partition

The Dagster 5-layer component architecture SHALL provide a BIEP v3
2-axis `MultiPartitionsDefinition` for the BIEP v3 jurisdiction pipeline
assets (defined in `orchestration/partitions_v2.py:39-64` as
`biiep_v3_scope_year_partition`):

```text
{
  "scope": DynamicPartitionsDefinition(name="cianhoghlaim_scope"),
  "year": StaticPartitionsDefinition(<2017-2027 + "undated">),
}
```

The `scope` axis uses a `DynamicPartitionsDefinition` because the 428+
cohort keys
(`<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>`)
are seeded at runtime by the British Isles Subject Registry. The `year`
axis is static (2017–2027 + "undated") because the curriculum refresh
cadence is on a known annual cycle.

The `CelticIngestionComponent` SHALL use this partition for all BIEP v3
jurisdiction pipeline assets (Ireland LC + JC + England A-Level + GCSE).
The `CelticMaterialsComponent` SHALL propagate the partition to all
downstream L2 extraction / embedding / audit assets.

The helper `scope_partition_key(jurisdiction, stage, subject_slug, board,
qualification_level, language)` SHALL build the canonical 6-token shape:

```text
<jurisdiction>__<stage>__<subject_slug>__<board>__<qualification_level>__<language>
```

(e.g. `ireland__leaving_cycle__mathematics__na__higher__en`).

#### Scenario: An Ireland LC Mathematics Higher English 2024 asset lands in the right partition

- **WHEN** the `ireland_lc_mathematics_higher_en_documents_ingested` asset
  materialises against the 2024 syllabus PDF
- **THEN** the partition key SHALL be
  `(scope="ireland__leaving_cycle__mathematics__na__higher__en", year="2024")`
- **AND** the asset_check SHALL enforce that every emitted row's
  `jurisdiction`, `stage`, `subject_slug`, `board`, `qualification_level`,
  and `language` columns match the `scope` partition

#### Scenario: An England AQA GCSE Mathematics 2025 asset lands in the right partition

- **WHEN** the `england_gcse_mathematics_aqa_documents_ingested` asset
  materialises against the 2025 spec
- **THEN** the partition key SHALL be
  `(scope="england__gcse__mathematics__aqa__gcse__en", year="2025")`
- **AND** the asset_check SHALL enforce that every emitted row's `board`
  matches `aqa` and `qualification_level` matches `gcse`

### Requirement: BIEP v3 daily Declarative Automation (per-milestone cron)

The `CelticAgentOpsComponent` SHALL provide daily Declarative Automation
(`AutomationCondition.cron(...)`) for each of the 4 BIEP v3 jurisdiction
pipelines, defined in `orchestration/automation/biiep_daily_automation.py`:

- `ireland_leaving_cycle_documents_ingested` — `AutomationCondition.cron("@daily")` at 02:00 UTC
- `ireland_junior_cycle_documents_ingested` — `AutomationCondition.cron("@daily")` at 02:30 UTC
- `england_a_level_documents_ingested` — `AutomationCondition.cron("@daily")` at 03:00 UTC
- `england_gcse_documents_ingested` — `AutomationCondition.cron("@daily")` at 03:30 UTC

The 6-hour `ScheduleDefinition` at
`orchestration/defs/2_materials/ocr_comparison/ensemble_comparison/biiep_ocr_ensemble.py:126-132`
SHALL be retired in favour of the per-milisdiction daily automation.

#### Scenario: Ireland LC daily automation fires at 02:00 UTC

- **WHEN** the daily cron fires at 02:00 UTC
- **THEN** the `ireland_leaving_cycle_documents_ingested` asset job fires
- **AND** the `ireland_lc_documents_ingested_check` asset_check resolves
  through the asset dependency chain
- **AND** the asset graph re-materialises the LC partition for the
  current year

#### Scenario: England AQA ChangeDetection sensor triggers

- **WHEN** the `england_aqa_a_level_jcq_monitor` ChangeDetection.io sensor
  fires (a new AQA A-Level spec is published)
- **THEN** the `england_a_level_documents_ingested` asset re-materialises
- **AND** the 4-path OCR ensemble runs against the new PDF
- **AND** the asset check `england_a_level_extractions_ragas_check` MUST
  pass with `ragas_score >= 0.70`
- **AND** an alert is posted to the `#kcg-biep-v3` Slack channel via the
  `biiep_daily_automation` post-hook

### Requirement: PlanetScale Postgres Centralisation (dagster-5-layer-component-architecture)

The system SHALL migrate the Dagster 5-layer component architecture's Postgres-backed run history + event log storage to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 3: Dagster / DuckLake).

#### Scenario: Dagster connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/dagster/Dockerfile.dagster` env is read
- **THEN** `DUCKLAKE_POSTGRES_HOST` SHALL point at PlanetScale PG
- **AND** the `dagster_state` database SHALL be pre-created on the PlanetScale branch

#### Scenario: DuckLake tables migrate (Phase C)

- **GIVEN** the Phase C change has archived
- **WHEN** DuckLake metadata is queried
- **THEN** the underlying database SHALL be PlanetScale PG (not PlanetScale MySQL)
- **AND** the schema SHALL match the prior MySQL schema after the migration

### Requirement: Dagster DuckLake Postgres substrate — PlanetScale PG (Phase B.0 env swap)

The system SHALL migrate Dagster's DuckLake metadata backend connection to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R9 (row 3: Dagster / DuckLake, row 4: DuckLake tables).

#### Scenario: DUCKLAKE_POSTGRES_HOST env var after Phase B.0

- **GIVEN** the operator has created `dagster_state` on the PlanetScale branch
- **WHEN** `bonneagar/stacks/dagster/Dockerfile.dagster` env is read
- **THEN** `DUCKLAKE_POSTGRES_HOST` SHALL point at `infisical://dev-baile/dagster/database_url`
- **AND** `DUCKLAKE_POSTGRES_PORT` SHALL be `5432`
- **AND** `DUCKLAKE_POSTGRES_SSLMODE` SHALL be `require`
- **AND** `DUCKLAKE_POSTGRES_DB` SHALL be `dagster_state`

#### Scenario: The local dagster-postgres container stays as a fallback

- **GIVEN** Phase B.0 has shipped
- **WHEN** `bonneagar/stacks/dagster/compose.yaml` is inspected
- **THEN** the local `dagster-postgres` service SHALL still be present
- **AND** it SHALL be marked as a fallback (Phase B.1 retires it)

#### Scenario: Dagster assets read from PlanetScale PG

- **GIVEN** the Phase B.0 PR has merged
- **WHEN** a Dagster asset materializes
- **THEN** the DuckLake metadata read SHALL go to PlanetScale PG
- **AND** the BIEP lakehouse queries (which join Lance + DuckLake) SHALL continue to work

### Requirement: Model Lifecycle Component consumes MODEL_REGISTRY

The system SHALL update the 5-layer KCG Component architecture so
that the Model Lifecycle layer consumes `MODEL_REGISTRY` for its
CocoIndex v1 Apps + LLM routing + embedder configuration. The
Ingestion / Materials / Asset Generation / Agent Operations layers
remain unchanged.

#### Scenario: Model Lifecycle layer reads from MODEL_REGISTRY

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator runs
  `mise run cocoindex:conformance`
- **THEN** the R1+R2+R3+R4 linter reports that every CocoIndex App
  imports `MODEL_REGISTRY` (or the legacy `VISION_MODELS` subset view)
- **AND** the L3 Component `defs.yaml` files reference
  `MODEL_REGISTRY.filter(family="ocr_vision")` for the embedder

#### Scenario: Dagster 1_ingestion cleanup is registered

- **GIVEN** the 619 empty placeholder YAMLs across
  `orchestration/defs/1_ingestion/european_nations/`,
  `orchestration/defs/1_ingestion/commonwealth/{canada,nigeria,australia}/`,
  `orchestration/defs/1_ingestion/american_nations/`
- **WHEN** the operator runs `mise run dagster:dev`
- **THEN** the empty YAMLs are not loaded
- **AND** the 10 per-jurisdiction `generic_<jur>_assets.py` files
  use the new `JurisdictionAssetsBase`

### Requirement: Dagster 5-layer architecture MUST reference the 10 JurisdictionAssetsBase subclasses

The system SHALL update `openspec/specs/dagster-5-layer-component-architecture/spec.md`
to reference the 10 `JurisdictionAssetsBase` subclasses at
`orchestration/defs/2_materials/_base/<jurisdiction>_assets.py`. Each
emits one canonical `<jurisdiction>_documents_ingested` Dagster asset
backed by the corresponding `<jurisdiction>_jurisdiction_pipeline`.

#### Scenario: Dagster definitions.py loads the 10 jurisdiction assets

- **GIVEN** the 10 `JurisdictionAssetsBase` subclasses created in commits
  `4ea9c1eed` + `64659a6ad`
- **WHEN** `mise run dagster:dev` launches
- **THEN** the 10 assets (`ireland_documents_ingested`, `england_documents_ingested`, etc.) appear in the Dagster UI
- **AND** they are registered in `orchestration/definitions.py` via the "Jurisdiction-level ingestion assets" section

#### Scenario: The 5-layer architecture registers the 3 CocoIndex factories

- **GIVEN** the 3 CocoIndex factory L3 Component `defs.yaml` files at:
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/european_nations_factory/defs.yaml`
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/ireland_lc_factory/defs.yaml`
  - `orchestration/defs/3_model_lifecycle/cocoindex_v1/biep_parity_factory/defs.yaml`
- **WHEN** the Dagster `dg.load_defs()` walks the tree
- **THEN** the 3 factory components emit their 40 + 11 + 8 = 59 Apps
- **AND** each factory's Apps conform to R1+R2+R3+R4

### Requirement: registry_drift_alert Dagster sensor

The system MUST wire the `registry_drift_alert` asset +
`materialize_registry_drift_alert_job` + `registry_drift_alert_sensor`
in `orchestration/defs/sync_assets.py` so that:

1. The `registry_drift_alert` asset (key: `["registry", "drift_alert"]`,
   group `3_model_lifecycle/sync_health`) emits `drift_count` +
   `drift_files` + `last_check` + `alert` metadata on every evaluation.
2. The `materialize_registry_drift_alert_job` runs the
   `materialize_registry_drift_alert_op` which:
   - Re-invokes `scripts/registry_audit.py --json`
   - Emits a Dagster `AssetMaterialization` for the
     `registry/drift_alert` asset
   - Raises a Dagster `Failure` if drift > 0 (so the job fails loudly)
3. The `registry_drift_alert_sensor`:
   - Polls every hour (`minimum_interval_seconds=3600`)
   - Yields a `RunRequest` for `materialize_registry_drift_alert_job`
     when drift > 0 AND the count differs from the cursor value
     (cursor key: `registry_drift_count`)
   - Always emits a `SensorResult` with an `AssetMaterialization` for
     the `registry/drift_alert` asset (per-tick audit record)
4. All 3 symbols are wired into `orchestration/definitions.py` via
   `dg.Definitions.merge(defs, dg.Definitions(assets=[...],
   jobs=[...], sensors=[...]))`.
5. A sibling helper `_get_registry_drift_files()` is added next to
   the v1 helper `_get_registry_drift_count()` in
   `orchestration/defs/sync_assets.py` for the file list (the v1
   helper only returns the count).

#### Scenario: Sensor detects drift and fires the job

- **GIVEN** the v2 cascading change has added the 3 new symbols
- **AND** `scripts/registry_audit.py` reports `count: 1` (drift detected)
- **WHEN** the `registry_drift_alert_sensor` evaluates
- **THEN** it yields a `RunRequest` for `materialize_registry_drift_alert_job`
- **AND** it emits a `SensorResult` with an `AssetMaterialization`
  for `registry/drift_alert` with metadata `drift_count=1, drift_files=['<file>']`
- **AND** the cursor is updated to `{"registry_drift_count": 1}`

#### Scenario: Sensor dedupes consecutive identical drift counts

- **GIVEN** the cursor is `{"registry_drift_count": 1}` (last reported)
- **AND** `scripts/registry_audit.py` still reports `count: 1`
- **WHEN** the sensor evaluates again
- **THEN** it does NOT yield a `RunRequest` (dedup)
- **AND** it still emits a `SensorResult` with an `AssetMaterialization`
  (per-tick audit record)
- **AND** the cursor remains `{"registry_drift_count": 1}`

#### Scenario: Sensor fires when drift count increases

- **GIVEN** the cursor is `{"registry_drift_count": 1}`
- **AND** `scripts/registry_audit.py` now reports `count: 3` (new drift)
- **WHEN** the sensor evaluates
- **THEN** it yields a `RunRequest` (count changed from 1 → 3)
- **AND** the cursor updates to `{"registry_drift_count": 3}`

#### Scenario: definitions.py loads the 3 new symbols

- **GIVEN** the 3 new symbols are defined in `orchestration/defs/sync_assets.py`
- **WHEN** `dagster dev` loads `orchestration/definitions.py`
- **THEN** the asset `registry/drift_alert` appears in the Dagster UI
- **AND** the job `materialize_registry_drift_alert` is launchable
- **AND** the sensor `registry_drift_alert_sensor` is active

### Requirement: Component YAML mount convention

The system MUST enforce that every directory in `orchestration/defs/`
that contains Component YAML children has an explicit mount point. The
mount point is EITHER:

1. A bare `defs.yaml` at the directory root (the directory IS a Component, via `dg.Component` + `build_defs()`), OR
2. An `_layer/defs.yaml` inside the directory (using `type: dagster.DefsFolderComponent` with `attributes: {}` to mount the children recursively)

A directory that has Component YAML children but NEITHER mount point
is silently unreachable by `dg.load_defs()` — the assets are dead code.

The system MUST additionally enforce that every loadable Component YAML
is named exactly `defs.yaml` (Dagster 1.13+ only walks files with that
magic filename; `mything.yaml` is silently skipped).

Per the 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1
change: this invariant is enforced by the existing
`scripts/audit_defs_yaml.py` (CI gate) + the new
`scripts/dagster_load_smoke.py` companion.

#### Scenario: A new subdirectory with Component YAML children has a mount point

- **GIVEN** a developer adds `orchestration/defs/2_materials/foo/bar/defs.yaml`
- **WHEN** they run `dg check yaml`
- **THEN** Dagster reports the addition as a loadable Component
- **AND** `dg list defs` includes `2_materials/foo/bar`

#### Scenario: A directory missing the mount point is unreachable

- **WHEN** `python3 scripts/dagster_load_smoke.py` runs
- **THEN** it reports any directory with `defs.yaml` children but no mount point
- **AND** it exits 1 if any such directory is found

#### Scenario: A YAML file not named `defs.yaml` is unreachable

- **WHEN** `python3 scripts/dagster_load_smoke.py` runs
- **THEN** it reports any `*.yaml` file under `orchestration/defs/` whose name is not `defs.yaml` (and not `.planned`)
- **AND** it exits 1 if any such file is found

### Requirement: L3 cognify + federated_ocr assets default to manual automation

The system MUST emit the 3 L3 components that wrap the cognify +
federated_ocr stack (`KCGCognifyComponent`,
`CognifyIngestSensorsComponent`, `CelticFederatedOcrComponent`) with
the default `automation_condition: Manual()` -- i.e. they MUST NOT
trigger on cron or on upstream freshness signals. Operators launch
them by hand once the cognify stack (cognee + graphiti + falkordb +
lancedb + memgraph) is brought up.

The fail-loudly contract documented in `kcg_cognify_component.py` is
preserved: when the assets ARE materialised manually and the cognify
stack is not up, they raise informative errors.

#### Scenario: The L3 cognify assets are not auto-triggered in BIEP M1-M4

- **WHEN** `mise run biep:v3:m1` runs
- **THEN** the 3 cognify + federated_ocr assets are NOT in the materialisation set
- **AND** the asset graph shows them as "manual-only" badges
- **AND** the BIEP milestone exits 0 (no fail-loudly raise)

#### Scenario: An operator can manually materialise the L3 cognify assets

- **GIVEN** the cognify stack is up (cognee + graphiti + falkordb + lancedb + memgraph)
- **WHEN** the operator clicks "Materialize" on a `3_model_lifecycle/cognify/*` asset in the Dagster UI
- **THEN** the asset materialises successfully
- **OR** fails informatively with the fail-loudly contract error

### Requirement: Dagster BIEP Ireland LC asset materialization contract

The system SHALL materialize the 62 Ireland-LC Dagster assets (the 5-layer KCG component chain: ingestion → materials → model lifecycle → asset generation → agent operations) for the 80 pre-downloaded PDFs at `/leaving_certificate/`. The materialization MUST run as a single Dagster job + produce 80 row outputs across the 6 LC subjects (chemistry, computer_science, english, gaeilge, geography, mathematics).

#### Scenario: A new LC PDF is added to /leaving_certificate/

- **GIVEN** the operator drops a new PDF at `/leaving_certificate/<subject>/<en|ga>/<file>.pdf`
- **WHEN** they trigger the canonical LC job via `dagster job launch` (or the marimo notebook CLI)
- **THEN** the new PDF is picked up by the layer 1 filesystem scanner
- **AND** the layer 2 ingestion asset materializes the PDF → 1 new row
- **AND** the layer 3 BAML extraction asset runs the 5 canonical lc extraction functions (ExtractCurriculumSyllabus, ExtractExamPaperLayout, ExtractMarkingSchemeGuideline, ExtractCrossLinguisticConcept, ExtractSyllabusDiagram)
- **AND** the layer 4 cognify asset adds the extraction results to the Cognee knowledge graph
- **AND** the layer 5 umbrella asset asserts the 6 per-subject assets all succeeded

#### Scenario: The BIEP Ireland LC pipeline runs end-to-end in <30s

- **GIVEN** the platform is on dlt 1.30 + DuckDB 1.5.x + litellm 1.97 + langfuse v4 + mlflow 3.15
- **WHEN** the canonical LC job materializes all 62 assets
- **THEN** the total wall-clock MUST be <5 minutes
- **AND** the 80-row output MUST land in the destination (either /tmp DuckDB for the test, or the actual lakehouse-postgres for prod)
- **AND** each layer's per-asset output rows MUST match the expected count (6 per subject × 13.3 PDFs average = 80)

### Requirement: BIEP Ireland LC asset counts

The system MUST have the following asset counts in the Dagster asset graph (per the v3.30 dlt + v3.15 mlflow + v1.97 litellm + v4.16 langfuse stack):

- **Layer 1 (Ingestion)**: ≥6 `sf_filesystem_leaving_cert_<subject>` assets (one per LC subject)
- **Layer 2 (Materials)**: ≥6 `lc5_<subject>_ingested` assets
- **Layer 3 (Model Lifecycle)**: ≥24 `lc5_<subject>_<stage>_extracted` assets (6 subjects × 4 stages: syllabus, exam, marking, diagrams)
- **Layer 4 (Asset Generation)**: ≥6 `lc5_<subject>_cognified` assets
- **Layer 5 (Agent Operations)**: ≥1 `lc5_all_baml_extraction` umbrella asset

#### Scenario: The 62 Ireland-LC assets are present in Dagster

- **WHEN** the operator runs `bun run ccc:search "leaving_cert" --type graphql-assets`
- **THEN** the response MUST include ≥62 asset keys matching `lc5_*` or `sf_filesystem_leaving_cert_*`
- **AND** the 5 KCG components (Ingestion, Materials, Model Lifecycle, Asset Generation, Agent Operations) MUST each be represented

