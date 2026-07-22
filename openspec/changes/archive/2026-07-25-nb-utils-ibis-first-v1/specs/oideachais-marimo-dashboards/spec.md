## MODIFIED Requirements

### Requirement: nb_utils.py uses ibis-first connection

The system SHALL require `notebooks/nb_utils.py` to use the ibis-first
canonical connection pattern (`ibis.duckdb.connect("md:oideachais")`
with `:memory:` fallback), NOT raw `duckdb.connect()`.

The single source of truth SHALL be `notebooks/_shared/db.py:connect_md()`,
re-exported by `nb_utils.py` for backward compatibility.

#### Scenario: nb_utils.connect_md uses ibis.duckdb.connect

- **WHEN** any notebook calls `from nb_utils import connect_md; conn = connect_md()`
- **THEN** the returned connection SHALL be an `ibis.duckdb.connect("md:oideachais")` handle (NOT a raw `duckdb.connect` handle)
- **AND** it SHALL work identically to the pattern in `marimo_dashboards/06_per_subject_analytics.py:84–95`

#### Scenario: per-area _shared shims available

- **WHEN** a notebook imports `from <area>_shared import connect_md`
- **THEN** the import SHALL resolve to `notebooks/_shared/db.py:connect_md()`
- **AND** the 5 per-area shims (leabharlann, leaving_cert, celtic_language, marimo_dashboards, mmo) SHALL all expose the same interface

#### Scenario: nb_utils.py has no raw duckdb.connect calls in the canonical path

- **WHEN** `grep -n "duckdb\.connect(" notebooks/nb_utils.py` runs
- **THEN** the ONLY `duckdb.connect(...)` matches are inside the
  `connect_md_oideachais(legacy_raw=True)` backward-compat shim (opt-in only)
- **AND** the canonical path (default `legacy_raw=False`) routes through
  `notebooks/_shared/db.py:connect_md()` which uses `ibis.duckdb.connect`
- **AND** the file is ≤ 300 LOC total (includes the BIEP contracts +
  query helpers + CLI helpers + dev_env import that the public API requires)