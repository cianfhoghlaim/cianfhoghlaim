# Spec Delta — oideachais-pipeline

This delta modifies existing requirements in the `oideachais-pipeline` capability (renamed `sruth.oideachais.X` → `oideachais.X` in canonical-positive scenarios + renamed `dagster_defs` → `orchestration.defs` + renamed `dlt_sources` → `dlt`) and adds one new requirement to codify the v4 namespace convention.

## MODIFIED Requirements

### Requirement: All Python imports inside cianfhoghlaim use the canonical namespace

The system SHALL have zero `from sruth.*` or `from oideachais.*` imports inside `cianfhoghlaim/`, except inside `.archive/` directories (point-in-time snapshots that are not part of the build) or inside `compat.py` build-time helpers.

The legacy `sruth.shared.*`, `sruth.browser`, and bare `oideachais.*` Python namespaces SHALL NOT be importable at runtime from the consolidated `cianfhoghlaim` package. The legacy `sruth.<quadrant>.*` namespaces were already removed by the v4 consolidation.

#### Scenario: Grep finds zero stale imports in active code

- **WHEN** `grep -rE "from sruth\.|from oideachais\." cianfhoghlaim/ --include='*.py' --exclude-dir=.archive --exclude=compat.py` runs
- **THEN** zero matches are returned

### Requirement: Dagster orchestration uses the v4 `orchestration/` namespace

The system SHALL organise all Dagster definitions under the v4 `oideachais.orchestration` namespace (formerly `oideachais.dagster_defs` pre-v4). The 5 canonical asset groups — `1_ingestion/`, `2_materials/`, `3_model_lifecycle/`, `4_asset_generation/`, `5_agent_ops/` — SHALL live under `oideachais.orchestration.defs.<group>/`. Consumers MUST import from the v4 path:

- `from oideachais.orchestration.defs.sensors import all_sensors` (was `from sruth.oideachais.dagster_defs.sensors import all_sensors`)
- `from oideachais.orchestration.definitions import defs` (was `from sruth.oideachais.dagster_defs.definitions import defs`)
- `from oideachais.orchestration.defs.assets.model_conversion import model_conversion_assets` (was `from sruth.oideachais.dagster_defs.assets.model_conversion import model_conversion_assets`)

The system SHALL fail CI if any code or doc references the v3 `sruth.oideachais.dagster_defs.*` namespace.

#### Scenario: All 5 canonical sensor groups aggregate via `oideachais.orchestration.defs.sensors.all_sensors`

- **GIVEN** the v4 Dagster orchestration tree at `orchestration/`
- **WHEN** a consumer does `from oideachais.orchestration.defs.sensors import all_sensors`
- **THEN** `all_sensors` MUST contain at least 5 sensors across the 5 canonical groups: `domain_sensors`, `curriculum_freshness_sensors`, `author_archive_sensors`, `leabharlann_sensors`, `cognee_cron_sensor`
- **AND** `defs.sensors` MUST contain all 5 canonical sensor groups (verified via `from oideachais.orchestration.defs.sensors import all_sensors; assert len(all_sensors) >= 5`)

#### Scenario: Dagster `defs.assets` loads via the v4 `orchestration/` namespace

- **WHEN** the Dagster Definitions load (`from oideachais.orchestration.definitions import defs`)
- **THEN** `defs.assets` MUST contain `model_conversion_assets` and `asset_generation_assets` (verified via `from oideachais.orchestration.defs.assets.model_conversion import model_conversion_assets; assert len(model_conversion_assets) >= 8`)

#### Scenario: Storage re-exports use the v4 `orchestration/core/storage` namespace

- **WHEN** a consumer does `from oideachais.orchestration.core.storage import (CogneeConfig, DuckLakeConfig, StorageManager, DuckLakeClient, LanceDBCloudClient, CurriculumVectorSearch)`
- **THEN** all 6 symbols MUST be importable from `orchestration/core/storage/__init__.py`
- **AND** the legacy `sruth.oideachais.storage.*` paths MUST raise `ModuleNotFoundError`

### Requirement: DLT sources use the v4 `dlt/` namespace

The system SHALL organise all DLT sources under the v4 `oideachais.dlt` namespace (formerly `oideachais.dlt_sources` pre-v4). The 6 DLT subdirs — `british_isles/`, `language/`, `filesystem/`, `api_sources/`, `apple_photos/`, `official_media/`, `portfolio/`, `common/` — SHALL live under `dlt/`.

Consumers MUST import from the v4 path:

- `from oideachais.dlt.ireland.examinations import examinations_source` (was `from sruth.oideachais.dlt_sources.ireland.examinations import examinations_source`)

The system SHALL fail CI if any code or doc references the v3 `sruth.oideachais.dlt_sources.*` namespace.

#### Scenario: All Ireland examinations DLT sources live under the v4 `dlt/` namespace

- **GIVEN** the v4 DLT tree at `dlt/` containing `british_isles/`, `language/`, `filesystem/`, `api_sources/`, `apple_photos/`, `official_media/`, `portfolio/`, `common/`
- **WHEN** a consumer does `from oideachais.dlt.ireland.examinations import examinations_source`
- **THEN** the import succeeds from `dlt/british_isles/ireland/examinations.py`
- **AND** the legacy `from sruth.oideachais.dlt_sources.ireland.examinations import examinations_source` path raises `ModuleNotFoundError`

## ADDED Requirements

### Requirement: Openspec spec text uses v4 namespace convention (no `sruth.X` drift)

The `oideachais-pipeline` capability spec SHALL use the v4 namespace convention throughout. Concretely:

1. **Python import paths** in canonical-positive scenarios SHALL use the v4 form: `from oideachais.<module> import <symbol>` — NOT `from sruth.oideachais.<module> import <symbol>`. The `sruth.oideachais.*` namespace no longer exists post-v4.
2. **Negative-test scenarios** (e.g. "NOT import from `sruth.X`") SHALL retain their `sruth.X` references — these are intentional checks that the codebase doesn't have stale v3 imports. Renaming them would defeat the test logic.
3. **Historical refs** (e.g. "formerly `sruth.X`", commit `e9e0fc7d2` packaging-fix context) SHALL be preserved verbatim.
4. **Stale subpaths** SHALL be renamed to their v4 equivalents:
   - `oideachais.dlt_sources.X` → `oideachais.dlt.X`
   - `oideachais.dagster_defs.X` → `oideachais.orchestration.defs.X`
   - `oideachais.dagster_assets` → `oideachais.orchestration.defs.assets`
5. **Bare `oideachais.X` refs** for DB schemas (e.g. `oideachais.education.ie.leaving_cert`), CLI invocations (e.g. `oideachais.cocoindex_flows.api_indexing:api_app`), and agent paths (e.g. `oideachais.agents.adk.celtic_tutor_agent`) are the **legitimate post-v4 quadrant-namespace shorthand** and SHALL be preserved.

#### Scenario: A spec contributor edits the oideachais-pipeline spec

- **GIVEN** a contributor wants to add a new scenario to the oideachais-pipeline spec at `openspec/specs/oideachais-pipeline/spec.md`
- **WHEN** the contributor writes a Python import statement in the scenario
- **THEN** the import SHALL use the v4 form `from oideachais.<module> import <symbol>` (NOT `from sruth.oideachais.<module> import <symbol>`)
- **AND** the contributor SHALL use `oideachais.orchestration.defs.X` for Dagster references (NOT `oideachais.dagster_defs.X`)
- **AND** the contributor SHALL use `oideachais.dlt.X` for DLT source references (NOT `oideachais.dlt_sources.X`)

#### Scenario: The openspec drift cleanup baseline is preserved

- **GIVEN** the `2026-07-13-openspec-drift-cleanup-v1` change has landed
- **WHEN** `grep -rE "sruth\.oideachais\." openspec/specs/oideachais-pipeline/spec.md` runs
- **THEN** the count of `sruth.oideachais.*` refs in canonical-positive contexts is 0
- **AND** the remaining `sruth.*` refs (if any) are negative-test scenarios, historical contexts, or the broad-regex check on line 1533
- **AND** `openspec validate oideachais-pipeline --strict` returns the same pre-existing errors as HEAD `54c21dd52` (no new errors introduced by this drift cleanup)