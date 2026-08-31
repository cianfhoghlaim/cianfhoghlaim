# cianfhoghlaim-ducklake-tertiary Specification

## Purpose

Wire the 5 new DLT sources + the British Isles tertiary factory onto
**all three** destination shapes: local DuckDB
(`/tmp/cianfhoghlaim.duckdb`), MotherDuck (`md:cianfhoghlaim`),
and the Bonneagar lakehouse (Garage + Lakekeeper + Postgres).

The default destination is **local DuckDB** so CI + local dev
need zero external services. MotherDuck + Bonneagar are opt-in
via `SecretsResolver` for thesis-reviewer scenarios.

## ADDED Requirements

### Requirement: 3 Destination classes

The system SHALL provide at `dlt_sources/_lakehouse/destinations.py`:

```python
class LocalDuckLakeDestination:
    def __init__(self, path: str = "/tmp/cianfhoghlaim.duckdb"): ...

class MotherDuckLakeDestination:
    def __init__(
        self,
        uri: str = "md:cianfhoghlaim",
        mtoken_secret: str = "MOTHERDUCK_TOKEN",
    ): ...

class BonneagarLakehouseDestination:
    def __init__(
        self,
        uri: str = "ducklake:postgres:host=lakehouse-postgres "
                  "port=5432 dbname=ducklake_oideachais user=lakekeeper",
        uri_secret: str = "BONNEAGAR_LAKEHOUSE_URI",
        password_secret: str = "DUCKLAKE_POSTGRES_PASSWORD",
    ): ...
```

Each destination SHALL expose a
`def dlt_target(self) -> dlt.Destination` method that the
`*_source()` decorator consumes.

#### Scenario: Local destination is the no-network default

- **GIVEN** the source is constructed without any
  `destination=…` kwarg
- **WHEN** the DLT pipeline runs
- **THEN** `LocalDuckLakeDestination().dlt_target()` returns
  the canonical `dlt.destinations.duckdb("/tmp/...duckdb")`
- **AND** zero HTTP / PostgreSQL traffic is generated

#### Scenario: MotherDuck destination ATTACH succeeds

- **GIVEN** `MOTHERDUCK_TOKEN` is set in the env (via `.env`)
  OR via Infisical
- **WHEN** `MotherDuckLakeDestination().dlt_target()` is invoked
- **THEN** `duckdb.execute("INSTALL motherduck; LOAD
  motherduck; ATTACH 'md:cianfhoghlaim'")` succeeds
- **AND** every DLT `write_disposition="merge"` persists to
  MotherDuck

#### Scenario: Bonneagar lakehouse destination ATTACH succeeds

- **GIVEN** the `bonneagar/stacks/lakehouse` Docker stack is up
  AND `INFISICAL_TOKEN` is set
- **WHEN** `BonneagarLakehouseDestination().dlt_target()` is
  invoked
- **THEN** `duckdb.execute("INSTALL ducklake; LOAD ducklake;
  ATTACH '<uri>' AS lakehouse")` succeeds
- **AND** every DLT merge row is also written to the
  `lakehouse.cianfhoghlaim.uog_official_documents` table

### Requirement: DLT sources accept the destination

Every new `*_source()` SHALL accept `destination: Literal["local",
"motherduck","bonneagar"] = "local"`. The factory SHALL turn the
keyword into the concrete `dlt.Destination` object.

#### Scenario: The 5 sources all accept the same `destination` kwarg

- **GIVEN** any of the 5 new sources
  (`uog_official_docs_source`, `nui_federation_source`,
  `uog_students_union_source`, etc.)
- **WHEN** the source is constructed with `destination=…`
- **THEN** the source uses that destination
- **AND** if the destination throws on `ATTACH()`, the source
  re-raises as `LakehouseConnectionError`

### Requirement: `LAKEHOUSE_*` env vars

The system SHALL accept these environment variables (resolved
through `SecretsResolver` like every other secret):

| Env var | Used by | Default |
|---|---|---|
| `MOTHERDUCK_TOKEN` | `MotherDuckLakeDestination` | none (raises if missing) |
| `BONNEAGAR_LAKEHOUSE_URI` | `BonneagarLakehouseDestination` | `ducklake:postgres:host=lakehouse-postgres port=5432 dbname=ducklake_oideachais user=lakekeeper` |
| `DUCKLAKE_POSTGRES_PASSWORD` | `BonneagarLakehouseDestination` | none |
| `OOG_LOCAL_DUCKDB_PATH` | `LocalDuckLakeDestination` | `/tmp/cianfhoghlaim.duckdb` |

#### Scenario: Missing `MOTHERDUCK_TOKEN` raises cleanly

- **GIVEN** `MOTHERDUCK_TOKEN` is not set OR is `fixture-only`
- **WHEN** `MotherDuckLakeDestination().dlt_target()` is called
- **THEN** the constructor SHALL raise
  `LakehouseConnectionError("MOTHERDUCK_TOKEN is a placeholder;
  set INFISICAL_TOKEN or .env to a real value")`
