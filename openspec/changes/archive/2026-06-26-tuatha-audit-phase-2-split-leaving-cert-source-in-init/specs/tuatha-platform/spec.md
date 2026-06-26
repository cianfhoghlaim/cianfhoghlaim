# Spec Delta: Round 11 Phase 10 (tuatha Phase 2) — No `@dlt.source` functions in package `__init__.py`

## ADDED Requirements

### Requirement: No `@dlt.source` functions in tuatha DLT package `__init__.py`

The system SHALL NOT define a `@dlt.source` or `@dlt.resource`
function inside the `__init__.py` of any DLT package under
`sruth/tuatha/dlt_sources/`. All `@dlt.source` and
`@dlt.resource` definitions MUST live in a sibling module
file matching the `{entity}.py` naming pattern, where
`{entity}` matches the package name.

The convention (as of Round 11 Phase 10) is:

- `dlt_sources/<entity>/__init__.py` — a thin re-export shim:
  `from .<entity> import <entity>_source`
- `dlt_sources/<entity>/<entity>.py` — the actual
  `@dlt.source` + `@dlt.resource` function bodies

This matches the oideachais Phase 3D convention (see
`openspec/changes/archive/2026-06-26-oideachais-audit-phase-3d-split-multi-source-files/`)
and the existing tuatha convention used by
`dlt_sources/mythology/{celtic_mythology.py, __init__.py}` and
`dlt_sources/geospatial/{gaeltacht_boundaries.py, gaelic_communities.py, welsh_language_areas.py}`.

#### Scenario: A new tuatha DLT package follows the convention

- **GIVEN** a developer wants to add a new tuatha DLT package
  `dlt_sources/<new_entity>/`
- **WHEN** the developer creates the package
- **THEN** the `__init__.py` is a thin re-export shim
  (≤10 lines) importing the source function from a sibling
  `<new_entity>.py` file
- **AND** the `<new_entity>.py` file contains the actual
  `@dlt.source` + `@dlt.resource` function definitions
- **AND** the package is importable as
  `from dlt_sources.<new_entity> import <new_entity>_source`

#### Scenario: Repo-wide grep finds no `@dlt.source` in any tuatha `__init__.py`

- **GIVEN** the Phase 2 fix that splits `leaving_cert/__init__.py`
  into `leaving_cert/{__init__.py, leaving_cert.py}`
- **WHEN** the developer runs
  `grep -rn "^@dlt\.\(source\|resource\)" sruth/tuatha/dlt_sources/**/__init__.py`
- **THEN** the output is empty (zero matches)
- **AND** every `@dlt.source` or `@dlt.resource` decorator
  appears in a sibling `.py` file
