## ADDED Requirements

### Requirement: Round 11 Phase 2A — Pure-Duplicate Surface Removal (2026-06-25)

The `oideachais-pipeline` capability spec MUST acknowledge that Round 11
phase 2A (executed 2026-06-25) removed 4 confirmed-pure-duplicate surface
pairs from `sruth/oideachais/`, with a total of 5,527 LOC and 17 files
removed. All deletions were byte-identical to canonical surfaces and verified
to have zero external importers (excluding the deprecated stub's single test
importer, which was updated to use the canonical replacement).

The canonical surfaces that retain all functionality:

| Pair | Duplicate (removed) | Canonical (kept) | LOC removed |
|:--|:--|:--|--:|
| 1 | `sruth/oideachais/routes/` | `sruth/oideachais/api/routes/` | 2,836 |
| 2 | `sruth/oideachais/sensors/` | `sruth/oideachais/dagster_defs/sensors/` | 994 |
| 3 | `sruth/oideachais/middleware/` | `sruth/oideachais/api/middleware/` | 1,668 |
| 4 | `sruth/oideachais/storage/serial_executor.py` (deprecated) | `sruth/oideachais/core/storage/serial_executor.py` | 29 |

#### Scenario: A developer imports from a canonical route

- **WHEN** any caller needs a FastAPI router from the oideachais API
- **THEN** they MUST import from `sruth.oideachais.api.routes.{agent,curriculum,search,geospatial,tts,cross_archive_graph,leaving_cert,official_media}` (8 routers total — 5 from before + 3 added in canonical during the Phase 6 leabharlann cross-archive work)
- **AND** NOT import from `sruth.oideachais.routes.*` (the deleted duplicate)

#### Scenario: A developer imports a Dagster sensor

- **WHEN** any caller needs a Dagster sensor from the oideachais platform
- **THEN** they MUST import from `sruth.oideachais.dagster_defs.sensors.all_sensors` (which aggregates all 5 canonical sensor groups: `domain_sensors`, `curriculum_freshness_sensors`, `author_archive_sensors`, `leabharlann_sensors`, `cognee_cron_sensor`)
- **AND** NOT import from `sruth.oideachais.sensors.*` (the deleted duplicate; its stale `__init__.py` only loaded 2 of 5 sensor groups)

#### Scenario: A developer imports FastAPI middleware

- **WHEN** any caller needs the AG-UI / streaming / auth middleware
- **THEN** they MUST import from `sruth.oideachais.api.middleware.{AuthMiddleware, agui.event_translator, agui.session_manager, agui.streaming}` (4 middleware components)
- **AND** NOT import from `sruth.oideachais.middleware.*` (the deleted duplicate)

#### Scenario: A developer imports the serial database executor

- **WHEN** any caller needs `SerialDatabaseExecutor` or `get_executor`
- **THEN** they MUST import from `sruth.oideachais.core.storage.{SerialDatabaseExecutor, get_executor, run_serial}` (the canonical authoritative implementation)
- **AND** NOT import from `sruth.oideachais.storage.serial_executor` (the deleted deprecated stub)

#### Scenario: The canonical surface contract is preserved

- **GIVEN** `openspec/changes/oideachais-audit-phase-2a-remove-pure-duplicates` is archived
- **WHEN** the Dagster Definitions load (`sruth.oideachais.dagster_defs.definitions`)
- **THEN** `defs.sensors` MUST contain all 5 canonical sensor groups (verified via `from sruth.oideachais.dagster_defs.sensors import all_sensors; assert len(all_sensors) >= 5`)
- **AND** `sruth/oideachais/api/main.py` MUST successfully `include_router` all 6 routers from `api.routes` (verified via FastAPI app construction without ImportError)
- **AND** `sruth/oideachais/api/middleware/AuthMiddleware` MUST be importable from the canonical `api.middleware` package

#### Scenario: No residual references after deletion

- **WHEN** any developer runs `grep -rn "from sruth.oideachais.routes\b\|from sruth.oideachais.sensors\b\|from sruth.oideachais.middleware\b\|from oideachais.storage.serial_executor" --include="*.py" --include="*.md"`
- **THEN** zero matches MUST appear outside `openspec/changes/archive/` (the only residual refs are in archived openspec change metadata, which is intentional)
