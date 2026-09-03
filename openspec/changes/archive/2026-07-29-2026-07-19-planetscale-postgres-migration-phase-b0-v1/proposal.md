## Deferred — PlanetScale Postgres phase on hold

This change is **deferred indefinitely**. The PlanetScale Postgres centralisation was proposed in 2026-07-19 as a future architecture direction, but the operator confirmed the BIEP v3 lakehouse pattern (Garage S3 + DuckLake + Lakekeeper + Lance namespace, fully wired in `bonneagar/stacks/lakehouse/`) is the canonical data plane. PlanetScale migration was a hypothetical future path, not an active deliverable.

All 17 spec deltas in `specs/<various>/spec.md` reference MODIFIED headers that don't exist verbatim in the canonical specs (the canonical specs were built around the BIEP v3 lakehouse architecture, not PlanetScale). Archived alongside the deferred state to preserve the audit trail. No code or IaC changes made — the BIEP v3 lakehouse (`md:cianfhoghlaim`) remains the canonical data plane.

# 2026-07-19-planetscale-postgres-migration-phase-b0-v1

> **Scope:** Phase B.0 — the first PlanetScale PG migration wave. Touches 3 stacks (Lakekeeper + Convex + Dagster). Per the operator's locked decisions:
> - **Hard switch for Lakekeeper + Convex** (remove local Postgres / SQLite containers)
> - **Env-var swap only for Dagster** (keep local `dagster-postgres` container for now; Phase B.1 retires it)
> - **Manual PlanetScale dashboard provisioning** (operator creates the 2 databases + the 3 Infisical secrets)
> - **Sequential, single PR per phase** (this is the one PR)

## Why

The landscape analysis (`2026-07-19-planetscale-postgres-landscape-v1`, shipped) established PlanetScale PostgreSQL as the primary managed DB substrate. Phase B.0 is the **first migration wave** that puts that policy into production for the 3 named candidates from the operator's asks:

1. **Lakekeeper** — the Iceberg REST catalog for the BIEP lakehouse
2. **Convex (self-hosted)** — the realtime agent backend for the leaving-cert + croilar-portal surfaces
3. **Dagster / DuckLake** — the orchestration + DuckLake metadata store

The 3 stacks together power the most user-visible pipeline in the platform (the BIEP → Lakekeeper → Dagster → leaving-cert portal flow). Shipping them first means the most-used pipeline runs on a managed remote DB; the remaining 15 ⭐-easy stacks (Phase B.1+) + the 6 MySQL migrations (Phase C) are sequenced after.

## Pre-requisites (operator, before this PR merges)

| # | Action | Where |
|--:|---|---|
| 1 | Create the PlanetScale PG branch (e.g. `bunchloch-prod`) | PlanetScale dashboard |
| 2 | Create 2 databases on that branch: `lakekeeper`, `dagster_state` | PlanetScale dashboard |
| 3 | Create 3 Infisical secrets in `dev-baile/`: `lakekeeper/database_url`, `dagster/database_url`, `convex/database_url` (format: `postgresql://<user>:<pwd>@<host>.pg.psdb.cloud/<db>?sslmode=verify-full`) | Infisical |
| 4 | Create the 3rd PlanetScale database: `convex_production` | PlanetScale dashboard |
| 5 | Verify each connection works from a local `psql` client | local shell |

Once those are done, this change can be opened as a PR.

## What changes

### Per-stack swap matrix

| Stack | Hard switch? | Local container | Migration |
|---|---|---|---|
| **Lakekeeper** | ✅ Yes | removed | `lakekeeper-migrate` companion also removed (migrations are idempotent on first start) |
| **Dagster / DuckLake** | ❌ No (env swap only) | kept (retired in Phase B.1) | `DUCKLAKE_POSTGRES_HOST` → PlanetScale PG via Infisical |
| **Convex** | ✅ Yes (clean SQLite) | removed | No data export (the self-hosted Convex deployments are dev-only per the operator's confirmation) |

### File-level diffs

**Bonneagar side** (committed to the `bonneagar/` worktree per `cross-repo-sync.md`):

```
bonneagar/iac/
├── auth-pocketid.ts                                         # MODIFIED (1 import added)
├── planetscale-postgres.ts                                  # NEW — the LCP resolver
└── procedures/
    └── verify_planetscale_databases.ts                      # NEW — read-only verifier (NO auto-provisioning)

bonneagar/stacks/lakekeeper/                                 # hard switch
├── compose.yaml                                             # MODIFIED (postgres + migrate removed; env swap)
├── secrets.env                                              # MODIFIED (+ PLANETSCALE_LAKEKEEPER_URL)
└── README.md                                                # MODIFIED (+ rollback recipe)

bonneagar/stacks/dagster/                                   # env swap only
├── Dockerfile.dagster                                        # MODIFIED (+ DUCKLAKE_POSTGRES_* env)
├── compose.yaml                                             # NO CHANGE (dagster-postgres stays)
└── secrets.env                                              # MODIFIED (+ DUCKLAKE_POSTGRES_HOST infisical://)

bonneagar/stacks/convex/                                    # hard switch (no data)
├── compose.yaml                                             # MODIFIED (SQLite volume removed; POSTGRES_URL infisical://)
├── secrets.env                                              # MODIFIED (+ PLANETSCALE_CONVEX_URL)
└── README.md                                                # MODIFIED (+ rollback recipe)
```

**Cianfhoghlaim side** (this repo):

```
openspec/changes/2026-07-19-planetscale-postgres-migration-phase-b0-v1/
├── proposal.md                                              # this file
├── tasks.md                                                 # 4 phases × ~8h
├── cross-repo-sync.md                                       # 2 repos (cianfhoghlaim + bonneagar)
└── specs/
    ├── planetscale-postgres-data-strategy/spec.md           # MODIFIED +R9 (per-stack hard-switch procedure)
    ├── infrastructure-stacks/spec.md                       # MODIFIED (3 new requirements)
    └── dagster-5-layer-component-architecture/spec.md      # MODIFIED (DUCKLAKE_POSTGRES_HOST swap)

tests/iac/                                                   # NEW IaC tests
├── locket-planetscale-secret-loader.test.ts
└── verify_planetscale_databases.test.ts
```

## Cross-references

- [`openspec/specs/planetscale-postgres-data-strategy/spec.md`](../../specs/planetscale-postgres-data-strategy/spec.md) — the umbrella spec (R1–R8)
- [`openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md`](../../architecture-decisions/0005-planetscale-postgres-centralisation.md) — ADR
- [`openspec/changes/2026-07-19-planetscale-postgres-landscape-v1/proposal.md`](../2026-07-19-planetscale-postgres-landscape-v1/proposal.md) — the parent change

## Dependencies

**Blocked by**: the operator's pre-requisites above (create 2 databases + 3 Infisical secrets). The PR can be opened before these are done; the IaC tests + the `verify_planetscale_databases.ts` procedure FAIL until the secrets exist.

**Soft dependencies**:

- The landscape analysis change (`2026-07-19-planetscale-postgres-landscape-v1`) — already shipped.
- Phase B.1 (observability: langfuse + mlflow + cognee + logfire) — sequenced after Phase B.0 archives.
- Phase C (MySQL sunset for the 6 Bytebase-managed schemas) — separate change, sequenced after Phase B.

## Risks

1. **Hard switch = no automatic rollback at the container layer.** Rollback is `git revert --no-ff` + PlanetScale PITR snapshot restore. Documented in `tasks.md` Phase 5.
2. **Lakekeeper migrations on first connect** require the PlanetScale branch's `lakekeeper` database to be empty. The migration is idempotent; subsequent restarts do not re-run.
3. **Convex's hard switch is clean only because there's no production data** (per operator confirmation). Any future production Convex deployment must go through a SQLite → Postgres export-import step.
4. **Dagster's local postgres container stays** — if it has its own state, that state is now stale. Phase B.1 retires it.

## Archive plan

Archive after:

- The operator's pre-requisites are complete
- `bun run iac:plan --stack lakekeeper + convex + dagster` returns "no diff"
- `openspec validate --strict` passes
- The IaC tests pass

## Effort

| Phase | Hours |
|---|---:|
| Phase 0 — openspec skeleton | 1 |
| Phase 1 — bonneagar IaC side | 2 |
| Phase 2 — stack swaps (3) | 3 |
| Phase 3 — IaC tests + validate + commit + push | 2 |
| **Total** | **~8h** |