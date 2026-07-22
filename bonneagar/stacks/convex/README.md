# CONVEX — PlanetScale PG migration (Phase B.0)

Per `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/`,
this stack was migrated to **PlanetScale PostgreSQL** as a **hard switch**.

## What changed

- The local `convex-data` SQLite volume is **removed**
- Convex connects directly to PlanetScale PG via `infisical://dev-baile/convex/database_url`
- `INSTANCE_SECRET` is now resolved via Locket

## Pre-requisites (the operator creates these BEFORE the PR merges)

1. Create the PlanetScale PG branch (e.g. `bunchloch-prod`) via the PlanetScale dashboard
2. Create the `convex_production` database on that branch
3. Create 2 Infisical secrets in `dev-baile/`:
   - `convex/database_url` → `postgresql://<user>:<pwd>@<host>.pg.psdb.cloud/convex_production?sslmode=verify-full`
   - `convex/instance_secret` → a random string (Convex instance isolation)

## Clean-start warning

Per the operator's confirmation, **this is a clean-start migration** —
the self-hosted Convex deployments had no production data. The empty
PlanetScale `convex_production` database is initialised by Convex on
first connect.

Any future production Convex deployment that previously used embedded
SQLite MUST follow the SQLite → Postgres export-import procedure
documented in the Convex docs before this stack can be redeployed.

## Rollback

This is a **hard switch** (no local fallback). To rollback:

1. `git revert --no-ff <phase-b.0-commit-sha>` and push
2. The reverted `compose.yaml` re-introduces the local `convex-data` SQLite volume
3. Restart Convex via Komodo (it falls back to embedded SQLite)
4. **Data lost from the PlanetScale `convex_production` database is unrecoverable from this stack** (PlanetScale PITR is the only recovery path)

## See also

- `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/specs/infrastructure-stacks/spec.md`