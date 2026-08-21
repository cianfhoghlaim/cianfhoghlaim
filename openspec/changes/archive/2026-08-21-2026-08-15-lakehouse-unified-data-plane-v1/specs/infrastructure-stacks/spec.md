# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Unified lakehouse data plane (graph DB consolidation)

The lakehouse stack at `bonneagar/stacks/lakehouse/compose.yaml` SHALL
be the single canonical entry point for the entire data engineering
pipeline (lakehouse data plane + 5 graph DB backends). The 5 graph DB
backends (Cognee + Graphiti + FalkorDB + Memgraph + LanceDB Viewer)
SHALL be defined as services in the SAME `compose.yaml` file — NOT as
separate stacks under `bonneagar/stacks/<name>/compose.yaml`.

Each graph DB service SHALL:
- Run on the shared `lakehouse_lakehouse` external network (the same
  network the existing lakehouse services use)
- Be resolved by the single Locket sidecar (no separate Locket per graph DB)
- Use canonical `infisical://dev-baile/<svc>/<key>` URIs for every secret
- Join the unified `blueprint.yaml` private-resources list

Cognee SHALL use the shared `lakehouse-postgres` at the
`cognee_cianfhoghlaim` database (created in `init-db.sql`) — NOT a
dedicated `cognee-postgres` container. FalkorDB SHALL run with
`--appendonly yes --appendfsync everysec` and
`FALKORDB_ARGS=THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000`.

The 5 deprecated stacks (`cognee/`, `graphiti/`, `falkordb/`,
`memgraph/`, `lancedb/`) SHALL each carry a 1-line deprecation banner
at the top of their `compose.yaml` pointing at the unified
`bonneagar/stacks/lakehouse/` stack. The banner SHALL NOT delete the
files; deletion is deferred to a follow-up change after one release
cycle.

#### Scenario: Operator brings up the entire data plane with one command

- **WHEN** `cd bonneagar/stacks/lakehouse && docker compose -f compose.yaml -f sidecar.yaml up -d` runs
- **THEN** all 16 services come up healthy (11 existing + 5 new graph DB services: cognee + graphiti + falkordb + memgraph + memgraph-lab)
- **AND** `mise run lakehouse:preflight` reports `9/9` required endpoints healthy + `13/13` databases present + `8/8` buckets present

#### Scenario: Cognee uses shared lakehouse-postgres

- **WHEN** the lakehouse stack deploys
- **THEN** the `cognee` service connects to `postgres:5432/cognee_cianfhoghlaim` (the shared lakehouse-postgres)
- **AND** the `cognee-postgres` container does NOT exist in the compose (it's gone — replaced by the shared Postgres)
- **AND** `COGNEE_POSTGRES_PASSWORD` resolves to the same value as `POSTGRES_PASSWORD` (Locket-resolved)

#### Scenario: FalkorDB persistence + production args

- **WHEN** the lakehouse stack deploys
- **THEN** the `falkordb` service runs with `--appendonly yes --appendfsync everysec` (AOF persistence enabled)
- **AND** `FALKORDB_ARGS=THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000` is set in the service environment
- **AND** the vector-search module `vector.so` is loaded via `--loadmodule` (the hybrid query capability is available)

#### Scenario: Deprecated stacks carry banners

- **WHEN** the operator opens `bonneagar/stacks/cognee/compose.yaml`
- **THEN** the first non-comment line is a 1-line banner pointing at `bonneagar/stacks/lakehouse/`
- **AND** the banner references `2026-08-15-lakehouse-unified-data-plane-v1`
- **AND** the banner explicitly says "do NOT deploy this stack — deploy the unified lakehouse instead"

#### Scenario: Komodo bunchloch resource-sync no longer pulls the 5 deprecated stacks

- **WHEN** `bonneagar/komodo/resource-syncs/bunchloch.toml` is read
- **THEN** the resource_path list does NOT contain references to `cognee-bunchloch.toml` + `graphiti-bunchloch.toml` + `falkordb-bunchloch.toml` + `memgraph-bunchloch.toml` + `lancedb-bunchloch.toml`
- **AND** the resource_path references `lakehouse-bunchloch.toml` (the single unified entry point)

## REMOVED Requirements

### Requirement: Standalone graph DB stacks (cognee / graphiti / falkordb / memgraph / lancedb)

**Reason**: The 5 standalone graph DB stacks each declare their own bridge network (NOT the shared `lakehouse_lakehouse` external network), so the graph backends cannot resolve `lakehouse-postgres` / `lakehouse-redis` / `lakehouse-garage` by Docker DNS — the #1 critical gap per the 2026-07-29 full-tree audit. Each requires its own docker compose + Locket + Pangolin blueprint + Komodo registration. The data plane is NOT self-sufficient.

**Migration**: All 5 graph DB backends are now services in the unified `bonneagar/stacks/lakehouse/compose.yaml`. Bring up the entire data plane with `docker compose -f compose.yaml -f sidecar.yaml up -d` from `bonneagar/stacks/lakehouse/`. The standalone stacks carry 1-line deprecation banners; deletion is deferred to `2026-XX-XX-delete-deprecated-graph-db-stacks`.

This requirement is REMOVED from the spec but the standalone stacks remain on disk with banners for one release cycle.