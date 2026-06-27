# Spec Delta: Round 11 Phase 12 (croilar Phase 1) — No local fallback in `sruth/croilar/dlt_utils/destinations.py`

## ADDED Requirements

### Requirement: No local fallback in `sruth/croilar/dlt_utils/destinations.py`

The system SHALL NOT include a local pre-Phase-2.3 fallback
implementation in `sruth/croilar/dlt_utils/destinations.py`.
The file SHALL be a thin re-export shim from the canonical
`sruth.oideachais.dlt_utils.destinations` module via the
`with_namespace("croilar")` factory.

The local fallback was originally needed because the croilar
packaging fix (commit `e9e0fc7d2`) had not yet been applied,
so `import sruth.oideachais.dlt_utils.destinations` would
fail from inside the croilar venv. The packaging fix
introduced `croilar/__init__.py` + changed pyproject
`packages = ["."]` + post-install `croilar/scripts/fix-pth.sh`
that rewrites the broken uv-generated `.pth` to put `sruth/`
on `sys.path` (so both `import croilar` and
`import sruth.oideachais` work).

After the packaging fix, the canonical import always succeeds,
so the local fallback is dead code (~88 lines of duplication).
It also creates a maintenance burden: 2 places to update when
the destination API changes.

#### Scenario: Canonical import is the only code path

- **GIVEN** the croilar packaging fix is in place (commit `e9e0fc7d2`)
- **AND** `sruth/croilar/scripts/fix-pth.sh` has been run
- **WHEN** a developer imports
  `from sruth.croilar.dlt_utils.destinations import NAMESPACE`
- **THEN** the import succeeds
- **AND** `NAMESPACE == "croilar"`
- **AND** the value comes from the canonical
  `sruth.oideachais.dlt_utils.destinations.with_namespace("croilar")`
  factory (not from a local fallback)

#### Scenario: The 4 canonical exports are all available

- **GIVEN** the thin shim is in place
- **WHEN** a developer imports the 4 canonical names
  ```python
  from sruth.croilar.dlt_utils.destinations import (
      NAMESPACE,
      create_pipeline,
      get_dlt_destination,
      get_duckdb_fallback_destination,
  )
  ```
- **THEN** all 4 imports succeed

#### Scenario: The 3 fallback-only exports are NOT available

- **GIVEN** the thin shim is in place
- **WHEN** a developer tries to import the 3 names that
  the local fallback used to export (`DuckLakeConfig`,
  `_get_local_config`, `get_duckdb_fallback`)
- **THEN** `ImportError` is raised
- **AND** the 3 names are not in `dir(sruth.croilar.dlt_utils.destinations)`

#### Scenario: `sruth/croilar/dlt_utils/__init__.py` re-exports the canonical surface

- **GIVEN** the thin shim is in place
- **AND** `sruth/croilar/dlt_utils/__init__.py` has been updated
  to import from `.destinations`
- **WHEN** a developer imports the public surface
  ```python
  from dlt_utils import (
      NAMESPACE,
      create_pipeline,
      get_dlt_destination,
      get_duckdb_fallback_destination,
  )
  ```
- **THEN** all 4 imports succeed