# DAGSTER — PlanetScale PG migration (Phase B.0 env swap only)

Per `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/`,
this stack was migrated to **PlanetScale PostgreSQL** as an **ENV SWAP
ONLY** (not a hard switch).

## What changed

- The `DUCKLAKE_POSTGRES_HOST` env var is now `infisical://dev-baile/dagster/database_url`
- A new `DUCKLAKE_POSTGRES_SSLMODE=require` env var is set
- A new `DUCKLAKE_POSTGRES_DB=dagster_state` env var is set
- The local `dagster-postgres` container **remains** in compose.yaml as a fallback

## Pre-requisites (the operator creates these BEFORE the PR merges)

1. Create the PlanetScale PG branch (e.g. `bunchloch-prod`) via the PlanetScale dashboard
2. Create the `dagster_state` database on that branch
3. Create the Infisical secret `dev-baile/dagster/database_url` → `postgresql://<user>:<pwd>@<host>.pg.psdb.cloud/dagster_state?sslmode=verify-full`
4. Create the Infisical secret `dev-baile/dagster/database_password` (the password portion)

## Why env swap only (not hard switch)?

The local `dagster-postgres` container is shared with other Lakehouse pieces. Removing it in Phase B.0 would break:
- The Dagster assets that use a separate catalog DB
- The Dagster run history (until Phase B.1 retires it)

Phase B.1 will:
- Retire the local `dagster-postgres` container
- Move the per-asset catalog DBs to PlanetScale PG

## Rollback

This is **env swap only**, so rollback is straightforward:

1. `git revert --no-ff <phase-b.0-commit-sha>` and push
2. The reverted `secrets.env` reverts `DUCKLAKE_POSTGRES_HOST` to `lakehouse-postgres` (local)
3. Restart Dagster via Komodo

No data migration needed (the local `dagster-postgres` still works).

## See also

- `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/specs/dagster-5-layer-component-architecture/spec.md`