## ADDED Requirements

### Requirement: DuckDB pin (>=1.5.4,<1.5.5) — MotherDuck-supported upgrade

The system SHALL pin `duckdb>=1.5.4,<1.5.5` per the 2026-08-21 upstream-version alignment audit. DuckDB 1.5.4 is the highest MotherDuck-supported line on the 1.5.x series (1.5.5 not yet supported by MD).

The bump brings:
- **VARIANT** type (semi-structured data — JSON/Parquet nested without schema)
- **GEOMETRY** type
- Bloom-filter join pushdown
- Stats-only min/max for I/O reduction
- Faster TopN with late materialization
- Lazy view binding

#### Scenario: A local BIEP Ireland LC pipeline DuckDB query runs on 1.5.4

- **GIVEN** the platform is on DuckDB 1.5.4
- **WHEN** `duckdb -c "SELECT version();"` is called
- **THEN** the output MUST start with `v1.5.4`
- **AND** `SELECT * FROM duckdb_extensions()` MUST include `vss` 0.13+ + `iceberg` 1.1+

#### Scenario: MotherDuck rejects VARIANT types in the BIEP schema

- **GIVEN** any of the 24 BIEP tables + `gov_circulars_archive` schema definitions use `VARIANT` type
- **WHEN** the schema is materialized into MotherDuck
- **THEN** the migration MUST fail with a clear "VARIANT not supported" error
- **AND** the operator MUST strip the VARIANT type and use `JSON` or `VARCHAR` instead

### Requirement: DuckDB 2.0 transition window

The system MUST track DuckDB 2.0 (shipping **September 2026**) and prepare a separate openspec change to land the major bump.

#### Scenario: DuckDB 2.0 ships

- **WHEN** DuckDB 2.0 GA is released
- **THEN** a new openspec change (`2026-XX-XX-duckdb-2.0-migration-v1`) MUST be opened
- **AND** the migration MUST include a separate MotherDuck compatibility assessment
