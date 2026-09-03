# Spec Delta: planetscale-postgres-data-strategy

## ADDED Requirements

### Requirement: Per-stack hard-switch procedure (R9)

The system SHALL define a canonical per-stack hard-switch procedure for migrating a stack from a local Postgres container to PlanetScale PostgreSQL. The procedure applies to ⭐-easy stacks (rows 5–28 of R7) and consists of:

1. **Pre-check** — confirm the PlanetScale branch has the required database (via the operator or `verify_planetscale_databases.ts`)
2. **Infisical secret registration** — store the connection URL in `dev-baile/<stack>/database_url`
3. **env var swap** — change `DATABASE_URL` (or equivalent) from `postgres://...@<service-name>:5432/<db>` to `infisical://dev-baile/<stack>/database_url`
4. **Local container disposition** — either REMOVE (full hard switch) or KEEP (env-swap-only fallback), per the per-stack decision in the change proposal
5. **Locket reload** — restart the sidecar so the new secret is fetched
6. **Migration bootstrap** — for stacks that have an explicit `migrate` companion (e.g. Lakekeeper's `lakekeeper-migrate`), the companion container is REMOVED and migrations become idempotent on first start
7. **Verification** — `bun run iac:health --stack <stack>` returns green + the RAGAS gate (if applicable) passes

The procedure is per-stack, atomic, and reverts via `git revert` + PlanetScale PITR.

#### Scenario: Lakekeeper hard switches to PlanetScale PG

- **GIVEN** the operator has created `lakekeeper` on the PlanetScale branch
- **WHEN** Phase B.0 ships
- **THEN** `bonneagar/stacks/lakekeeper/compose.yaml` SHALL remove the `postgres` + `lakekeeper-migrate` services
- **AND** the `lakekeeper` service env SHALL use `infisical://dev-baile/lakekeeper/database_url`
- **AND** migrations SHALL run idempotently on first start
- **AND** `bun run iac:health --stack lakekeeper` SHALL return green

#### Scenario: Dagster env-swaps only (local postgres retained)

- **GIVEN** the operator has created `dagster_state` on the PlanetScale branch
- **WHEN** Phase B.0 ships
- **THEN** `bonneagar/stacks/dagster/Dockerfile.dagster` SHALL add `DUCKLAKE_POSTGRES_HOST` pointing at `infisical://dev-baile/dagster/database_url`
- **AND** the local `dagster-postgres` container SHALL remain in compose.yaml (retired in Phase B.1)
- **AND** `bun run iac:health --stack dagster` SHALL return green

#### Scenario: Convex hard switches with no data export (clean start)

- **GIVEN** the operator has created `convex_production` on the PlanetScale branch
- **AND** the self-hosted Convex deployment has no production data (per the operator's confirmation)
- **WHEN** Phase B.0 ships
- **THEN** `bonneagar/stacks/convex/compose.yaml` SHALL remove the `convex-data` SQLite volume
- **AND** the `backend` service env SHALL use `infisical://dev-baile/convex/database_url`
- **AND** Convex SHALL auto-initialise the schema on first connect (its `init` step)