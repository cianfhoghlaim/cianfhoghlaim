# LAKEKEEPER — PlanetScale PG migration (Phase B.0)

Per `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/`,
this stack was migrated to **PlanetScale PostgreSQL** as a **hard switch**.

## What changed

- The local `lakekeeper-postgres` container is **removed**
- The `lakekeeper-migrate` companion container is **removed** (migrations become idempotent on first start)
- The `lakekeeper` service now uses `infisical://dev-baile/lakekeeper/database_url` for both `LAKEKEEPER__PG_DATABASE_URL_READ` and `_WRITE`
- The encryption key now uses `infisical://dev-baile/lakekeeper/encryption_key`

## Pre-requisites (the operator creates these BEFORE the PR merges)

1. Create the PlanetScale PG branch (e.g. `bunchloch-prod`) via the PlanetScale dashboard
2. Create the `lakekeeper` database on that branch
3. Create 2 Infisical secrets in `dev-baile/`:
   - `lakekeeper/database_url` → `postgresql://<user>:<pwd>@<host>.pg.psdb.cloud/lakekeeper?sslmode=verify-full`
   - `lakekeeper/encryption_key` → a 64-char hex key (Lakekeeper catalog encryption)

## First-deploy notes

When Lakekeeper starts against the empty PlanetScale PG database, it runs its migrations **idempotently on first start**. No `lakekeeper-migrate` companion is needed.

## Rollback

This is a **hard switch** (no local fallback). To rollback:

1. `git revert --no-ff <phase-b.0-commit-sha>` and push
2. The reverted `compose.yaml` re-introduces the local `lakekeeper-postgres` container
3. The reverted `secrets.env` re-introduces `LAKEKEEPER_DB_PASSWORD`
4. Restart Lakekeeper via Komodo
5. **Restore data from PlanetScale PITR** (the PlanetScale branch retains 7 days of PITR)

## See also

- `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/specs/infrastructure-stacks/spec.md`
- `openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md`