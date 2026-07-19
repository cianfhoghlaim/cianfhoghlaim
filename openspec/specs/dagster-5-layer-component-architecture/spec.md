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
separate `cianchoghlaim/` subdirectory containing the package source.

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
- **AND THEN** the resolution path SHALL be `orchestration/...` or `dlt/...` at the repo root (NOT from a non-existent `cianchoghlaim/` subdirectory)

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

