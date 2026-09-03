# Tasks — PlanetScale Postgres Migration Phase B.0 v1

> Scope: Lakekeeper + Convex + Dagster/DuckLake → PlanetScale PG
> Mode: Hard switch for Lakekeeper + Convex; env swap only for Dagster
> Effort: ~8h across 4 phases

## Phase 0 — openspec skeleton (1 h)

- [x] `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/proposal.md`
- [x] `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/tasks.md` (this file)
- [ ] `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/cross-repo-sync.md`
- [ ] `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/specs/planetscale-postgres-data-strategy/spec.md` (MODIFIED +R9)
- [ ] `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/specs/infrastructure-stacks/spec.md` (MODIFIED +3 requirements)
- [ ] `openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/specs/dagster-5-layer-component-architecture/spec.md` (MODIFIED)
- [ ] `openspec validate 2026-07-19-planetscale-postgres-migration-phase-b0-v1 --strict` passes

## Phase 1 — bonneagar IaC side (2 h)

> All files in this phase live on the **`bonneagar/` worktree** (separate repo per `cross-repo-sync.md`).

- [ ] `bonneagar/iac/planetscale-postgres.ts` — NEW — the LCP resolver:
  - `resolvePlanetScaleDatabaseUrl(stack)` returns the canonical URL format
  - `listPlanetScaleDatabases()` queries the PlanetScale API
  - Reads Infisical secrets via Locket
- [ ] `bonneagar/iac/procedures/verify_planetscale_databases.ts` — NEW — read-only verifier:
  - Asserts the 3 Phase B.0 databases (`lakekeeper`, `dagster_state`, `convex_production`) exist
  - Throws clearly when missing
- [ ] `bonneagar/iac/auth-pocketid.ts` — MODIFIED (1 import added: `planetscale-postgres.ts`)
- [ ] `tests/iac/locket-planetscale-secret-loader.test.ts` — NEW (smoke test for the URL format)
- [ ] `tests/iac/verify_planetscale_databases.test.ts` — NEW (smoke test for the verifier error path)

## Phase 2 — stack swaps (3 h)

### 2.1 Lakekeeper (hard switch, ~1 h)

- [ ] `bonneagar/stacks/lakekeeper/compose.yaml` — REMOVE the `postgres` service + the `lakekeeper-migrate` service; UPDATE the `lakekeeper` service to use Infisical env vars
- [ ] `bonneagar/stacks/lakekeeper/secrets.env` — ADD `PLANETSCALE_LAKEKEEPER_URL=infisical://dev-baile/lakekeeper/database_url` + remove `LAKEKEEPER_DB_PASSWORD`
- [ ] `bonneagar/stacks/lakekeeper/README.md` — ADD the rollback recipe

### 2.2 Convex (hard switch, no data, ~1 h)

- [ ] `bonneagar/stacks/convex/compose.yaml` — REMOVE the `convex-data` volume; UPDATE `backend` to use Infisical `POSTGRES_URL` + `INSTANCE_SECRET`
- [ ] `bonneagar/stacks/convex/secrets.env` — ADD `PLANETSCALE_CONVEX_URL=infisical://dev-baile/convex/database_url`
- [ ] `bonneagar/stacks/convex/README.md` — ADD the rollback recipe + the "fresh-start only" warning

### 2.3 Dagster / DuckLake (env swap only, ~1 h)

- [ ] `bonneagar/stacks/dagster/Dockerfile.dagster` — ADD `DUCKLAKE_POSTGRES_SSLMODE=require` env var
- [ ] `bonneagar/stacks/dagster/secrets.env` — ADD `DUCKLAKE_POSTGRES_HOST=infisical://dev-baile/dagster/database_url`
- [ ] `bonneagar/stacks/dagster/README.md` — ADD notes that the local `dagster-postgres` container is kept as a fallback (retired in Phase B.1)

## Phase 3 — validate + commit + push (2 h)

- [ ] `openspec validate 2026-07-19-planetscale-postgres-migration-phase-b0-v1 --strict` PASSES
- [ ] `bun run iac:plan --stack lakekeeper + convex + dagster` — no diff (after operator pre-reqs)
- [ ] Run the IaC tests:
  - `bun test tests/iac/locket-planetscale-secret-loader.test.ts`
  - `bun test tests/iac/verify_planetscale_databases.test.ts`
- [ ] Commit in this repo: openspec change files + tests (cianfhoghlaim side)
- [ ] Commit in the `bonneagar/` worktree: IaC files + 3 stack changes (bonneagar side)
- [ ] Push both repos
- [ ] Operator reviews the PR

## Rollback (documented in Phase 5)

Within 5 minutes of a bad deploy:

```bash
git revert --no-ff <phase-b.0-sha>
git push
bun run iac:plan --stack lakekeeper + convex + dagster
bun run iac:deploy --stack lakekeeper + convex + dagster
```

Then restore from PlanetScale PITR (7-day retention).

## Cross-repo-sync plan

The change touches **2 repos** per the openspec `## Cross-repo` convention:

### Repo 1: cianfhoghlaim (this repo)

Branch: `feat/2026-07-19-planetscale-postgres-migration-phase-b0-v1`
Push target: `origin`

| Commit # | Phase | Message |
|--:|---|---|
| 1 | Phase 0–3 | `openspec(changes): planetscale-postgres-migration-phase-b0-v1 — Lakekeeper + Convex + Dagster → PlanetScale PG (3 stacks, hard switch + env swap, ~8h)` |

### Repo 2: bonneagar (separate worktree)

Branch: `feat/2026-07-19-planetscale-postgres-migration-phase-b0-v1`
Push target: `archive-bonneagar`

| Commit # | Message |
|--:|---|
| 1 | `iac(planetscale): LCP resolver + read-only DB verifier + 3 stack swaps (lakekeeper hard switch + convex hard switch + dagster env swap only)` |

### Order of operations

1. **First** push cianfhoghlaim (the openspec change archives after this push)
2. **Then** push bonneagar (the IaC deploys after this push)
3. **Then** open a draft PR for operator review

## Open follow-ups (after this archives)

| Order | Change | Description |
|---|---|---|
| 1 | `2026-07-XX-planetscale-postgres-migration-phase-b1-v1` | Tier β1 — observability: langfuse + mlflow + cognee + logfire + retire Dagster's local postgres |
| 2 | `2026-07-XX-planetscale-postgres-migration-phase-b2-v1` | Tier β2 — admin stacks: agent-os + lmnr + karakeep + windmill + browser + forgejo + actual + infisical |
| 3 | `2026-07-XX-planetscale-postgres-migration-phase-b3-v1` | Tier β3 — Wave2/* app stacks: immich + khoj + outline + mealie + letta |
| 4 | `2026-07-XX-planetscale-mysql-sunset-v1` | Tier γ — Bytebase-managed MySQL → PG migration for 6 schemas + DuckLake metadata swap |
| 5 | `2026-07-XX-komodo-ferretdb-rebuild-v1` | Komodo re-architecture (out of scope per R8) |