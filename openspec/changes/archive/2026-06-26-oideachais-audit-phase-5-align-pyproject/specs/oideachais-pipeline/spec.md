# Spec Delta: oideachais-pipeline

## ADDED Requirements

### Requirement: pyproject.toml + canonical docstrings use oideachais.* namespace

The `sruth/oideachais/pyproject.toml` file MUST NOT reference the legacy
`oideachais/data_platform/*` namespace that was deleted in post-cleanup
commit `8484a6353`. The canonical Python package is `oideachais`
(the uv workspace name), and the canonical Dagster code-location entry
point is `sruth/oideachais/dagster_defs/definitions.py`. The 4 sections
in `pyproject.toml` that historically pointed at
`data_platform.dagster_defs.*` MUST all reference the canonical
`oideachais.dagster_defs.*` namespace. The 3 canonical docstrings at
`sruth/oideachais/dlt_utils/destinations.py`,
`sruth/oideachais/dlt_sources/dg.toml`, and
`sruth/oideachais/dlt_sources/__init__.py` MUST NOT reference the
legacy namespace either.

#### Scenario: pyproject.toml has no data_platform references

- **WHEN** `sruth/oideachais/pyproject.toml` is parsed (TOML)
- **THEN** the 4 sections MUST point at the canonical
  `oideachais.dagster_defs.*` namespace
- **AND** the legacy `"data_platform.dagster_defs"` entry MUST be
  REMOVED from `[tool.hatch.build.targets.wheel] packages` (the
  package does not exist on disk; it was dead weight in the wheel
  build)

#### Scenario: docstrings use canonical import paths

- **WHEN** `dlt_utils/destinations.py` documents its usage example
- **THEN** it MUST reference `from dlt_utils import …` (not
  `from oideachais.data_platform.dlt_utils import …`)
- **AND** `dlt_sources/dg.toml` header comment MUST reference the
  canonical path `sruth/oideachais/dagster_defs/` (not the legacy
  `sruth/oideachais/data_platform/dagster_defs/`)

#### Scenario: shim docstring excludes deleted crown_dependencies

- **WHEN** `dlt_sources/__init__.py` enumerates legacy shim directories
- **THEN** it MUST NOT include `crown_dependencies` (deleted in
  Phase 3E on 2026-06-26)
- **AND** the remaining list MUST reflect the actual on-disk legacy
  trees as of Phase 5 completion (the `crown_dependencies` entry
  MUST be removed from the shim enumeration; the other entries
  MAY stay as documentation of remaining legacy areas)
