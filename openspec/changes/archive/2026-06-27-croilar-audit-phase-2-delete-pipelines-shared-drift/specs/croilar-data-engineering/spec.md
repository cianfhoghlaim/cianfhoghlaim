# Spec Delta: no-drift-pipelines-shared-destinations

## ADDED Requirements

### Requirement: No drift in `pipelines/shared/`

The system SHALL NOT include `sruth/croilar/pipelines/shared/destinations.py`
(the 4-function destination factory that duplicates the canonical surface at
`sruth/oideachais/dlt_utils/destinations.py`).
The system SHALL NOT include `sruth/croilar/pipelines/shared/ducklake.py`
(the 352-line `DuckLakeCatalog` class that has no production callers).
The croilar data-engineering layer MUST consume the canonical destination
factory surface at `sruth/oideachais/dlt_utils/destinations.py` (the
`with_namespace("croilar")` shim introduced in round 11 phase 1 of croilar)
rather than re-implementing its own destination factory or its own
`DuckLakeCatalog`.

#### Scenario: Only `r2_client.py` + `__init__.py` remain in `pipelines/shared/`

- **WHEN** `ls sruth/croilar/pipelines/shared/` is run
- **THEN** the directory SHALL contain only `__init__.py` (1-line `R2Client` re-export) + `r2_client.py` (187 lines)
- **AND** the directory SHALL NOT contain `destinations.py` or `ducklake.py`

#### Scenario: Production callers of the canonical surface still work

- **WHEN** `pipelines/teaching/__init__.py:47` runs `from dlt_utils import get_dlt_destination`
- **THEN** the canonical `get_dlt_destination()` function SHALL be importable from `sruth/croilar.dlt_utils.destinations`
- **AND** the production `pipelines.teaching` module SHALL remain importable

#### Scenario: Production caller of `R2Client` still works

- **WHEN** `pipelines/soundcloud/downloader.py:18` runs `from pipelines.shared.r2_client import R2Client`
- **THEN** `R2Client` SHALL remain importable from `sruth.croilar.pipelines.shared.r2_client`
- **AND** the production `pipelines.soundcloud.downloader` module SHALL remain importable

#### Scenario: No fallback shims

- **WHEN** the round 11 change is committed
- **THEN** there SHALL be no `try/except ImportError` fallback, no `__getattr__` lazy import, no deprecation warning
- **AND** the deleted modules SHALL be removed outright (no `destinations.py.bak`, no `destinations.py.deprecated`)

#### Scenario: `tests/test_smoke.py::test_pipelines_shared_exports` updated

- **WHEN** `pytest sruth/croilar/tests/test_smoke.py::test_pipelines_shared_exports` runs
- **THEN** the test SHALL assert only `R2Client` is present on `pipelines.shared`
- **AND** the test SHALL NOT assert `create_duckdb_destination` or `create_ducklake_destination` (those names moved to the canonical `dlt_utils` surface in round 11 phase 1 of croilar)