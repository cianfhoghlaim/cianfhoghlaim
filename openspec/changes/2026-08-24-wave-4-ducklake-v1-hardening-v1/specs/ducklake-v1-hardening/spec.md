# ducklake-v1-hardening Specification

## Purpose

`ducklake-v1-hardening` is a capability of the Cianfhoghlaim
platform that codifies the layer-grouped destinations namespace and
the DuckLake v1.0 feature usage. After this spec is implemented:

- `dlt_sources/common/destinations/{ducklake,motherduck,filesystem,iceberg}.py`
  are the canonical homes for the 4 destination types
- `named_destinations(name)` factory resolves any of the 15 registered
  destination names (6 legacy aliases + 9 canonical names)
- DuckLake 1.0 features (data inlining, sort expressions, bucket
  partitioning, time travel, data change feed) are available via
  helper functions
- The 6 legacy `dlt_sources/common/destinations_*.py` + `named_destinations.py`
  + `_lakehouse/destinations.py` + `_lakehouse/personal_archive_destinations.py`
  files become re-export shims that preserve backwards compatibility

This spec captures Wave 4 of the 2026-08-24 master refactor plan.

## Requirements

### Requirement: Layer-grouped destinations namespace

The `dlt_sources/common/destinations/` package SHALL be organised by
infrastructure layer:

```
dlt_sources/common/destinations/
├── __init__.py          # named_destinations() factory + DESTINATIONS registry
├── ducklake.py           # DuckLake + Postgres catalog + Garage S3
├── motherduck.py         # MotherDuck managed DuckLake
├── filesystem.py         # local FS + S3 + GCS + Azure
└── iceberg.py            # Iceberg REST catalog via Lakekeeper (:8181)
```

#### Scenario: All 4 layer modules import cleanly

- **WHEN** `uv run python -c "from dlt_sources.common.destinations.{ducklake,motherduck,filesystem,iceberg} import *"` runs
- **THEN** no ImportError is raised

### Requirement: named_destinations factory

`dlt_sources.common.destinations.named_destinations(name: str)` SHALL
return a `@dlt.destination`-decorated function for the requested
destination name.

#### Scenario: 15 registered destination names

- **WHEN** `from dlt_sources.common.destinations import DESTINATIONS; len(DESTINATIONS)` runs
- **THEN** the count SHALL equal 15

- **AND** the names SHALL include:
  - `ducklake_cianfhoghlaim` (canonical)
  - `ducklake_oideachais`, `ducklake_educational`, `ducklake_crypteolas`,
    `ducklake_tertiary`, `ducklake_uog`, `ducklake_cie` (legacy aliases)
  - `motherduck`, `motherduck_ducklake`
  - `filesystem_local`, `filesystem_s3`, `filesystem_gcs`, `filesystem_azure`
  - `iceberg_rest`, `iceberg_lakekeeper`

### Requirement: DuckLake 1.0 features

The `dlt_sources/common/destinations/ducklake.py` module SHALL expose:

- `get_ducklake_destination(...)` — the canonical destination factory
- `ducklake_cianfhoghlaim_at_timestamp(ts)` — time-travel SQL
- `ducklake_cianfhoghlaim_at_version(version)` — version-pinned SQL
- `ducklake_cianfhoghlaim_table_changes(table, since)` — change-feed query
- `apply_sort_to_table(table, sort_columns)` — `SORTED BY` SQL
- `apply_bucket_partitioning_to_table(table, bucket_count, bucket_column)` — `PARTITIONED BY` SQL
- `apply_data_inlining_to_table(table, row_limit)` — `data_inlining_row_limit` SQL

#### Scenario: Time-travel SQL has the right ATTACH shape

- **WHEN** `ducklake_cianfhoghlaim_at_timestamp("2025-09-01")` runs
- **THEN** the returned SQL SHALL match `ATTACH 'ducklake:postgres://...' AS cianfhoghlaim (DATA_PATH '...', AT (TIMESTAMP => '2025-09-01'))`

### Requirement: Legacy compatibility (6 shim files)

The 6 legacy destination files SHALL become re-export shims that
import from `dlt_sources.common.destinations`:

- `dlt_sources/common/destinations_cianfhoghlaim.py`
- `dlt_sources/common/destinations_tuatha.py`
- `dlt_sources/common/named_destinations.py`
- `dlt_sources/_lakehouse/destinations.py`
- `dlt_sources/_lakehouse/personal_archive_destinations.py`

#### Scenario: All legacy imports resolve

- **WHEN** any of the 6 legacy files is imported
- **THEN** the import succeeds (no ImportError)
- **AND** the legacy symbols (`LocalDuckLakeDestination`,
  `MotherDuckLakeDestination`, `BonneagarLakehouseDestination`,
  `DESTINATION_CHOICES`, `get_destination`, `DEFAULT_SCHEMA`,
  `register_personal_archive_tables`, etc.) are accessible

### Requirement: Namespace consolidation

The 6 legacy DuckLake namespaces SHALL all route to the consolidated
`ducklake_cianfhoghlaim` namespace. The DESTINATIONS registry
explicitly aliases each legacy name to `get_ducklake_destination`.

#### Scenario: All aliases point to the same destination

- **WHEN** `named_destinations("ducklake_oideachais")` runs
- **THEN** the returned destination SHALL be the same function object as `named_destinations("ducklake_cianfhoghlaim")`

### Requirement: MotherDuck token wire-up

The `get_motherduck_destination(...)` factory SHALL require the
`CIANFHOGHLAIM_MOTHERDUCK_TOKEN` env var. If the token is missing,
it SHALL raise `RuntimeError`.

#### Scenario: MotherDuck without token raises

- **WHEN** `get_motherduck_destination()` runs without `CIANFHOGHLAIM_MOTHERDUCK_TOKEN`
- **THEN** a `RuntimeError` is raised with a message about the missing token

### Requirement: Iceberg REST catalog interop

The `get_iceberg_destination(...)` factory SHALL connect to the
Lakekeeper Iceberg REST catalog at `http://lakekeeper:8181/catalog`
(or the `CIANFHOGHLAIM_LAKEKEEPER_URI` env var).

#### Scenario: Iceberg destination has the right catalog URI

- **WHEN** `get_iceberg_destination()` runs
- **THEN** the returned destination's `catalog_uri` SHALL be
  `http://lakekeeper:8181/catalog` (or the env var override)

### Requirement: Migration tooling

The Wave 4 PR SHALL include `scripts/wave_4_consolidate_namespaces.py`
that generates the SQL to migrate the 6 legacy namespaces into the
consolidated `ducklake_cianfhoghlaim`. This script is run manually
as part of a Wave 4 follow-up PR (NOT in this PR — the actual
data migration is too risky to do automatically).

### Requirement: Documentation

The `dlt_sources/LEGACY_ALIASES.md` SHALL be extended with the
Wave 4 mapping table:

- All 6 legacy DuckLake namespaces → `ducklake_cianfhoghlaim`
- All 5 legacy destination files → `dlt_sources.common.destinations.*`
