# Agent Memory Systems — Cognee postgres+pgvector Default Delta

> This file is the change-side delta for
> `2026-07-02-align-cianfhoghlaim-env-with-stacks`. It applies on
> top of the canonical `agent-memory-systems` spec at
> `../../../../specs/agent-memory-systems/spec.md` and on top of the
> prior `2026-07-02-replace-private-images-and-bring-wave2` delta.

## ADDED Requirements

### Requirement: CogneeMemoryResource uses postgres+pgvector (not Memgraph)

The `CogneeMemoryResource` default SHALL use a postgres+pgvector
backend (via `COGNEE_PG_HOST` + `COGNEE_PG_PASSWORD` env vars), not
the previous Memgraph `bolt://localhost:7687` default. The deployed
cognee stack uses `USE_UNIFIED_PROVIDER=pghybrid` per the cognee
compose; the same Postgres database serves both the relational and
graph layers.

#### Scenario: Cognee service connects to lakehouse-postgres
- **WHEN** the dagster code initializes
  `CogneeMemoryResource` without overriding `postgres_url`
- **THEN** the default postgres_url is constructed from env vars
  `COGNEE_PG_HOST` (default `cognee-postgres` in-docker or `localhost`
  on-host) + `COGNEE_POSTGRES_PASSWORD` (default `devpassword`)
- **AND** the cognee service uses the lakehouse-postgres
  `cognee_oideachais` database with the pgvector extension
- **AND** vector data is stored in LanceDB at
  `rest://lakehouse-lance-namespace:8182` (per the
  `LANCEDB_URI` env var)

#### Scenario: Memgraph + Neo4j + TemporalGraph resources are deprecated
- **WHEN** an agent or Dagster asset uses `MemgraphResource`,
  `Neo4jResource`, or `TemporalGraphResource`
- **THEN** the resource docstrings include a `.. deprecated::`
  admonition pointing to `FalkorDBResource` + lakehouse-postgres
  as the replacement
- **AND** the `dagster/resources.py` module-level instances are
  kept for backwards compatibility (existing assets still work)
  but new assets SHOULD use FalkorDB + lakehouse-postgres

## MODIFIED Requirements

### Requirement: New agent memory code MUST use FalkorDB + lakehouse-postgres (not Memgraph + Neo4j)

The system MUST use FalkorDB + lakehouse-postgres for new agent
memory code. Per the prior `agent-observability` spec which
removed Memgraph + Neo4j from the production stack lineup, new
code MUST use:
- `FalkorDBResource` (host `falkordb`, port `6379` in-docker or
  `6380` on-host, password `devpassword`) for the graph layer
- `DuckDBResource` or `DuckLakeResource` for the relational layer
  (lakehouse-postgres db=oideachais)
- `LanceDBResource` (via `LANCEDB_URI`) for the vector layer

`MemgraphResource`, `Neo4jResource`, `TemporalGraphResource` are
deprecated — see the prior ADDED Requirement.

#### Scenario: New agent asset uses FalkorDB + lakehouse
- **WHEN** a new Dagster asset is scaffolded with the
  `dagster dev -m cianfhoghlaim.dagster.definitions` 5-layer
  architecture
- **THEN** the asset uses `FalkorDBResource` + `LanceDBResource` +
  `DuckLakeResource` (NOT `MemgraphResource` / `Neo4jResource`)
- **AND** the asset's connections target the lakehouse services
  via docker DNS (e.g. `falkordb`, `lakehouse-lance-namespace`,
  `lakehouse-postgres`)
