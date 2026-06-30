# Dagster 5-Layer Component Architecture Capability

This spec is the change delta for the new
`dagster-5-layer-component-architecture` capability (added by the
`2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture`
change). The canonical version of this spec lives at
`openspec/specs/dagster-5-layer-component-architecture/spec.md`.

The corresponding source code lives at:

- `cianfhoghlaim/dagster/components/` (the 5 Components)
- `cianfhoghlaim/dagster/defs/<1..5>_<layer>/` (the YAML defs tree)
- `cianfhoghlaim/dagster/definitions.py` (the ~30-line bootstrap)

## ADDED Requirements

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
(`oideachais-cocoindex-v1` skill):

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
6-sub-folder shape (`oideachais_pipeline`, `celtic_asset_generation`,
`cognify`, `croilar`, `meaisinfhoghlaim_platform`, `tuatha`) SHALL
be retired and replaced by the 5-layer shape.

#### Scenario: The `defs/` tree has exactly 5 layer folders

- **WHEN** `ls cianfhoghlaim/dagster/defs/` runs
- **THEN** the output includes exactly: `1_ingestion/`, `2_materials/`, `3_model_lifecycle/`, `4_asset_generation/`, `5_agent_ops/`
- **AND** the previous 6 sub-folders (`oideachais_pipeline/`, `celtic_asset_generation/`, `cognify/`, `croilar/`, `meaisinfhoghlaim_platform/`, `tuatha/`) do NOT exist

#### Scenario: Each layer has at least 1 sub-folder

- **WHEN** `find cianfhoghlaim/dagster/defs/<layer> -mindepth 1 -maxdepth 1 -type d` runs
- **THEN** the output for `1_ingestion/` SHALL include at least: `curriculum/`, `law/`, `medicine/`, `site_analysis/`, `filesystem/`
- **AND** the output for `2_materials/` SHALL include at least: `baml_extraction/`, `ocr_comparison/`, `pdf_processing/`, `embedding_pivot/`, `dbt/`
- **AND** the output for `3_model_lifecycle/` SHALL include at least: `cocoindex_v1/`, `cognify/`, `cross_archive/`
- **AND** the output for `4_asset_generation/` SHALL include at least: `marimo_dashboards/`, `tanstack_pages/`, `orpc_routes/`
- **AND** the output for `5_agent_ops/` SHALL include at least: `custom/`, `adk/`, `agno/`
- **AND** the `5_agent_ops/pipecat/` sub-folder is INTENTIONALLY ABSENT (the voice agent is deferred to a follow-on change per user direction)
