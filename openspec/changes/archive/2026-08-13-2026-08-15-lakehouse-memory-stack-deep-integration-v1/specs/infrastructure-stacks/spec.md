## ADDED Requirements

### Requirement: All 5 memory backends are pinned to semver images

The system SHALL pin every `image:` line in the 5 memory backends'
`compose.yaml` files to a `<major>.<minor>.<patch>` semver tag,
matching the upstream releases verified 2026-08-15:

- `cognee/cognee:1.2.2` (the canonical Cognee v1.0 surface; verified
  live by the `cognee` SKILL.md)
- `falkordb/falkordb:v4.18.11` (the latest upstream; closes the
  open "vector on relationships" gap from Wave 1)
- `graphiti:local-<sha>` (the KCG-built image with the v0.29.2
  Graphiti + FalkorDB driver)
- `memgraph/memgraph:3.6.0` (the canonical Memgraph 3.x release line)
- `lance-namespace:v0.9.0` (the Lance Namespace sidecar with the
  0.9 contract)

The tag `:latest` SHALL NOT appear in any memory-backend compose.yaml.

#### Scenario: No `:latest` tags in memory-stack composes

- **GIVEN** `bonneagar/stacks/{cognee,graphiti,falkordb,memgraph,lancedb}/compose.yaml`
- **WHEN** each `image:` line is read
- **THEN** it SHALL match the regex `<image>:<X>.<Y>.<Z>` (semver)
- **AND** zero lines SHALL match `<image>:latest`

#### Scenario: stack-doctor reports zero unpinned-image warnings

- **WHEN** `mise run cic:stack-doctor` runs against the 5 memory backends
- **THEN** the validator SHALL report `UNPINNED: 0`
- **AND** the overall exit code SHALL be 0

### Requirement: FalkorDB loads `vector.so` for graphiti hybrid queries

The system SHALL add `command: ["falkordb", "--loadmodule",
"/etc/falkordb/vector.so"]` to `bonneagar/stacks/falkordb/compose.yaml`
so that FalkorDB's vector-search capability is enabled. The mount of
the `vector.so` module file SHALL be sourced from a pinned image
(`falkordb/falkordb:v4.18.11`) where the module is bundled at
`/etc/falkordb/vector.so`.

This requirement closes the open production drift alert flagged by
the `falkordb` SKILL.md since Wave 1 ("`infrastructure/stacks/falkordb/compose.yaml`
does NOT currently load `vector.so` — vector queries will silently fail
in prod").

#### Scenario: FalkorDB container starts with vector.so loaded

- **WHEN** `docker compose up -d falkordb` runs in `bonneagar/stacks/falkordb/`
- **THEN** the container SHALL log `Module loaded: /etc/falkordb/vector.so`
- **AND** `redis-cli -h falkordb MODULE LIST` SHALL include `vector`

#### Scenario: Graphiti hybrid vector+graph query succeeds

- **WHEN** Graphiti issues a hybrid query against the FalkorDB backend
- **THEN** the query SHALL return results from BOTH the Cypher graph
  traversal AND the vector similarity search
- **AND** the query SHALL NOT silently fall back to graph-only results

### Requirement: PlanetScale PG centralisation wiring for cognee + langfuse + mlflow + logfire-otel

The system SHALL wire the optional PlanetScale PostgreSQL
`DATABASE_URL` override path for the 4 stacks declared in the
umbrella spec R7 of `openspec/specs/planetscale-postgres-data-strategy/spec.md`:
`cognee`, `langfuse`, `mlflow`, and the `logfire-otel` collector
service. Each stack's `secrets.env` SHALL include a
`<svc>/planetscale_database_url` Infisical URI ref. When the operator
sets the corresponding vault secret, the stack SHALL prefer
PlanetScale PG over the local lakehouse-postgres fallback.

The local lakehouse-postgres connection SHALL remain the recommended
dev path. The PlanetScale override is opt-in (operators must
seed the secret in `dev-baile` to enable).

#### Scenario: cognee stack reads DATABASE_URL from PlanetScale when set

- **GIVEN** `dev-baile/cognee/planetscale_database_url` is set in the vault
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` starts the `cognee` service
- **THEN** `DATABASE_URL` SHALL resolve to the PlanetScale connection string
- **AND** the local `cognee-postgres` service SHALL NOT be used

#### Scenario: cognee stack falls back to local postgres when PlanetScale not set

- **GIVEN** `dev-baile/cognee/planetscale_database_url` is NOT set
- **WHEN** `bonneagar/stacks/cognee/compose.yaml` starts the `cognee` service
- **THEN** `DATABASE_URL` SHALL resolve to `postgresql://cognee:cognee_password@cognee-postgres:5432/cognee` (the local fallback)
- **AND** the cognee container SHALL start successfully

#### Scenario: langfuse / mlflow / logfire-otel declare the override env var

- **GIVEN** `bonneagar/stacks/{langfuse,mlflow}/secrets.env` and `bonneagar/stacks/logfire/config/otelcol.yaml`
- **WHEN** each file is read
- **THEN** it SHALL declare a `<svc>/planetscale_database_url` Infisical URI ref
- **AND** the override env var SHALL be wired into the container's environment