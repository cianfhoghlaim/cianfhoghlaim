## ADDED Requirements

### Requirement: BIEP Notebooks — ibis-first refactor of all 11 files

All 11 BIEP subject + leabharlann notebooks under
`cianfhoghlaim/notebooks/04_biep_motherduck/` MUST use
`ibis.duckdb.connect()` as the canonical KCG entrypoint (per the
`wire-biep-notebooks-to-lakehouse` change spec). The system SHALL
reject any raw `duckdb.connect()` call or any `.fetchdf()` call
in these notebooks.

#### Scenario: ibis is the canonical entrypoint in all 11 BIEP notebooks

- **WHEN** the 11 BIEP notebooks are grepped
- **THEN** every `duckdb.connect(uri)` call SHALL be replaced by
  `ibis.duckdb.connect(uri)` (was 0; now ≥ 20 across 11 files)
- **AND** every `.fetchdf()` call SHALL be replaced by
  `.to_pandas()` (was 3; now 0)
- **AND** every `duckdb.sql("SET motherduck_token=...")` SHALL be
  removed (the ibis.duckdb.connect() URL form picks up the token
  automatically)
- **AND** the `ibis` skill SHALL be referenced in each notebook's
  `## KCG patterns used` docstring

#### Scenario: All 11 BIEP notebooks boot against the live lakehouse

- **WHEN** the lakehouse stack is up (per the upgrade-4-stacks-with-infisical
  change) AND the 11 BIEP notebooks are launched via `marimo run`
- **THEN** the ibis.duckdb.connect() connection SHALL succeed (or
  fall back to MotherDuck if the local lakehouse is unreachable)
- **AND** the first data cell SHALL complete within 10 seconds
  (returns 0-row DataFrames, not errors)
- **AND** the marimo reactive graph SHALL resolve without "Pending"
  cells after 5 seconds