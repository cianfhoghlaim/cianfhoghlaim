# 2026-07-19-planetscale-postgres-landscape-v1

> **Status:** Draft — Text/Intelligence only. No code, IaC, or Python changes.

## Why

The Cianfhoghlaim platform currently ships **24+ PostgreSQL-bearing Docker Compose stacks** at `bonneagar/stacks/`. The proliferation incurs:

- Per-stack Postgres container + `komodo-postgres-data` / `lakekeeper-postgres-data` named volumes
- Per-stack backup strategy (or none)
- Per-stack env wiring (DATABASE_URL, POSTGRES_PASSWORD, etc.)
- The **PlanetScale MySQL** legacy for DuckLake metadata + 6 Bytebase-managed schemas (per `bonneagar/stacks/lakehouse/README.md` + `bytebase-config.yaml`)

The operator now has access to a **PlanetScale PostgreSQL server** as a managed remote DB. The goal:

1. Use PlanetScale Postgres as the **primary managed DB substrate** for the platform
2. Sunset the existing **PlanetScale MySQL** usage (since the operator asked: "we want to only be using planetscale postgresql, cloudflare d1 sqlite or local postgresql")
3. Keep **Cloudflare D1 SQLite** as the secondary substrate (serverless, read-mostly)
4. Keep **local Postgres** as the tertiary substrate (only for stacks needing extensions PlanetScale cannot provide — or already-deployed small state)
5. **Defer all Komodo work entirely** (Komodo's FerretDB v2 + MongoDB wire-protocol stack requires the `documentdb` extension which PlanetScale Postgres does NOT support — see the ADR)

This change is **landscape analysis only**. It produces no code, no IaC, no Python. It establishes a single canonical umbrella spec (`planetscale-postgres-data-strategy`) + 17 MODIFIED spec deltas that pin the decision per stack + 1 ADR (`0005-planetscale-postgres-centralisation.md`) recording the technical rationale.

The migration work itself is deferred to **Phase B** (`2026-07-XX-planetscale-postgres-migration-phase-b-v1`) and **Phase C** (`2026-07-XX-planetscale-mysql-sunset-v1`).

## Research findings (from external research, captured in proposal + ADR)

A targeted lookup against PlanetScale's published documentation confirmed:

- **PlanetScale PostgreSQL supported extensions** include: `pgvector` (0.8.0/0.8.1), `pg_cron` (1.6.5/1.6.7), `pg_partman` (5.2.4/5.3.1), `postgis` (3.5.3/3.6.1), `pg_duckdb` (1.0.0/1.1.0), TimescaleDB, `pg_trgm`, `cube`, `earthdistance`, `hstore`, `ltree`, `pg_strict` (PlanetScale-builtin), `pginsights` (PlanetScale-builtin)
- **PlanetScale PostgreSQL NOT supported extensions** include: `documentdb` (the FerretDB v2 hard requirement — confirmed absent from PlanetScale's published list)
- **PlanetScale PostgreSQL restrictions**: no superuser (so `CREATE DATABASE` and most `CREATE EXTENSION` operations must be done via the PlanetScale dashboard before the app connects), `?sslmode=verify-full` required for all connections, PgBouncer pool on port 6543 for serverless + direct on 5432 for long-running

## What changes

This change produces text only. Files written:

```
openspec/changes/2026-07-19-planetscale-postgres-landscape-v1/
├── proposal.md                                                    # this file
├── tasks.md                                                       # 4 analysis phases + follow-up queue
├── cross-repo-sync.md                                             # single-repo; no bonneagar worktree changes
└── specs/
    ├── planetscale-postgres-data-strategy/spec.md                 # NEW umbrella spec (R1–R8)
    ├── infrastructure-stacks/spec.md                             # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── agent-platform-cluster/spec.md                            # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── agent-observability/spec.md                               # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── agent-memory-systems/spec.md                              # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── bonneagar-iac-merge/spec.md                               # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── bonneagar-komodo-gitops/spec.md                           # MODIFIED +KomodoDeferralNote
    ├── dagster-5-layer-component-architecture/spec.md            # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── croilar-data-engineering/spec.md                          # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── indexing-and-cognition/spec.md                            # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── oideachais-cognify-knowledge-graph/spec.md                # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── meaisinfhoghlaim-platform/spec.md                         # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── agent-registry/spec.md                                    # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── agentic-frontend-frameworks/spec.md                       # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── oideachais-pipeline/spec.md                               # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── croilar-portfolio/spec.md                                 # MODIFIED +R-PlanetScalePostgresCentralisation
    ├── documentation/spec.md                                     # MODIFIED +R-PlanetScalePostgresCentralisation
    └── dagger-pipelines/spec.md                                  # MODIFIED +R-PlanetScalePostgresCentralisation

openspec/architecture-decisions/
└── 0005-planetscale-postgres-centralisation.md                   # NEW ADR
```

**Total: 19 files** (1 NEW umbrella spec + 1 ADR + 1 proposal + 1 tasks + 1 cross-repo-sync + 17 MODIFIED deltas − 3 = `proposal/tasks/cross-repo + 1 ADR + 1 umbrella + 17 modified deltas = 21 files total).

No code is changed in this PR. No IaC. No Python. No commit on the `bonneagar/` worktree.

## Per-stack decision matrix (R7 row in the umbrella spec)

This is the canonical output of the landscape analysis. Komodo is entirely deferred (no row).

| # | Stack | Current DB substrate | Target substrate | Compatibility | Env var | Notes |
|--:|---|---|---|---|---|---|
| 1 | Lakekeeper | local `postgres:16-alpine` | **PlanetScale PG** | ✅ trivial | `LAKEKEEPER__PG_DATABASE_URL_WRITE` | Requires PG schema bootstrap |
| 2 | Convex (self-hosted) | embedded SQLite | **PlanetScale PG** | ✅ trivial | `POSTGRES_URL` | Optional already in compose |
| 3 | Dagster / DuckLake | local Postgres (Lakehouse container) | **PlanetScale PG** | ✅ trivial | `DUCKLAKE_POSTGRES_HOST` | 1 database: `dagster_state` |
| 4 | DuckLake tables (Lakehouse) | **PlanetScale MySQL** | **PlanetScale PG (migration)** | ⚠ requires schema migration | `lakehouse.ducklake_postgres_url` | Schemas: `ducklake_*`. **Phase C** follow-up. |
| 5 | langfuse | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | (no schema-level extension needs) |
| 6 | mlflow | local Postgres | **PlanetScale PG** | ✅ trivial | `MLFLOW_TRACKING_URI` | |
| 7 | cognee | local Postgres (needs `pgvector`) | **PlanetScale PG** | ✅ pgvector supported | `DATABASE_URL` | (1 DB; `pgvector` extension verified available on PlanetScale PG) |
| 8 | bytebase | n/a (manages others) | n/a | n/a | n/a | Bridge between Phase B + C. |
| 9 | vikunja | PlanetScale MySQL | **PlanetScale PG (migration)** | ⚠ schema migration | `VIKUNJA_DATABASE_URL` | **Phase C** (Bytebase-managed). |
| 10 | n8n | PlanetScale MySQL | **PlanetScale PG (migration)** | ⚠ schema migration | `DB_POSTGRESDB_DATABASE_URL` | **Phase C** (Bytebase-managed). |
| 11 | cal-diy (calcom) | PlanetScale MySQL | **PlanetScale PG (migration)** | ⚠ schema migration | `DATABASE_URL` | **Phase C** (Bytebase-managed). |
| 12 | paperless | PlanetScale MySQL | **PlanetScale PG (migration)** | ⚠ schema migration | `PAPERLESS_DB_URL` | **Phase C** (Bytebase-managed). |
| 13 | glance | PlanetScale MySQL | **PlanetScale PG (migration)** | ⚠ schema migration | `GLANCE_DB_URL` | **Phase C** (Bytebase-managed). |
| 14 | changedetection | PlanetScale MySQL | **PlanetScale PG (migration)** | ⚠ schema migration | `DATABASE_URL` | **Phase C** (Bytebase-managed). |
| 15 | Wave2: immich | local Postgres | **PlanetScale PG** | ✅ trivial | `DB_DATABASE_URL` | (verify `cube` + `earthdistance` use if needed) |
| 16 | Wave2: khoj | local Postgres | **PlanetScale PG** | ✅ trivial | `POSTGRES_DB` | |
| 17 | Wave2: outline | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | |
| 18 | Wave2: mealie | local Postgres | **PlanetScale PG** | ✅ trivial | `MEALIE_DB_URL` | |
| 19 | Wave2: letta | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | |
| 20 | agent-os | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | |
| 21 | lmnr | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | |
| 22 | karakeep | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | |
| 23 | windmill | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_HOST_OVERRIDE` | |
| 24 | browser | local Postgres | **PlanetScale PG** | ✅ trivial | `DATABASE_URL` | |
| 25 | forgejo | local Postgres | **PlanetScale PG** | ✅ trivial | `FORGEJO_DB_HOST` | |
| 26 | actual | local Postgres | **PlanetScale PG** | ✅ trivial | `ACTUAL_DB_URL` | |
| 27 | infisical | local Postgres | **PlanetScale PG** | ✅ trivial | `DB_CONNECTION_URI` | |
| 28 | logfire | local | **PlanetScale PG** | ✅ trivial | `LOGFIRE_DATABASE_URL` | (added per agent-observability for RAGAS gating) |

**Total: 28 stack rows** (Komodo excluded entirely).

## Cross-references

- `openspec/specs/planetscale-postgres-data-strategy/spec.md` — NEW umbrella spec (canonical DB strategy)
- `openspec/specs/infrastructure-stacks/spec.md` — the 94-stack catalogue (cross-referenced)
- `openspec/architecture-decisions/0005-planetscale-postgres-centralisation.md` — NEW ADR (canonical record)
- `openspec/specs/oideachais-pipeline/spec.md` — the main 50-req spec (50reqs ship boundary)

## Dependencies

**Blocked by:** none. (Komodo work is explicitly **out-of-scope** per the operator's choice.)

**Soft dependencies (post-merge follow-ups, NOT blockers for archive):**
- `2026-07-XX-planetscale-postgres-migration-phase-b-v1` (will move the 18 ⭐-easy stacks onto PlanetScale PG; ~10 stack compose deltas)
- `2026-07-XX-planetscale-mysql-sunset-v1` (will migrate the 6 Bytebase-managed schemas from MySQL → PG; drops PlanetScale MySQL entirely)
- `2026-07-XX-komodo-ferretdb-rebuild-v1` (a separate future change for Komodo architecture; out of scope here)

## Risks

1. **Extension matrix drift** — PlanetScale's supported extension list could change. The umbrella spec R6 captures the procedure for verifying extensions at adoption time.
2. **Connection limits** — PlanetScale enforces a per-branch connection pool max. The umbrella spec R6 mandates PgBouncer pool mode for serverless apps (Convex) and direct mode for long-running (Lakekeeper, Dagster).
3. **Backup / DR semantics** — Phase B must re-document the per-stack backup strategy (since PlanetScale owns the snapshot cadence; we lose the explicit `komodo backup` cron for these stacks).
4. **Komodo deferral risk** — leaving Komodo on FerretDB+local means we carry that specialized dependency forward; explicitly out of scope.

## Open questions

1. **PlanetScale MySQL sunset timing** — when should the Phase C migration close? After all 6 Bytebase-managed schemas verify-data-integrity post-migration.
2. **PlanetScale region placement** — the existing PlanetScale MySQL is `eu-west-3 (bunchloch)` per the bytebase config. We assume the new PlanetScale PostgreSQL is colocated; if not, latency must be re-evaluated.
3. **The "winds/noise" stacks** — Cal-diy, paperless, glance are operator-personal tools; their migration priority is operator's call.

## Archive plan

- Archive after `openspec validate --strict` passes + the umbrella spec + 17 deltas + the ADR have been reviewed by the operator.
- Phase B (migration) and Phase C (MySQL sunset) open as separate, sequenced openspec changes.

## Effort & timeline

| Step | Hours |
|---|---|
| Survey 48 capability specs + 24+ stack `compose.yaml` files | ~3 h |
| Write the umbrella spec (R1–R8) | ~2 h |
| Write 17 MODIFIED spec deltas | ~5 h |
| Write the ADR | ~1 h |
| Write proposal + tasks + cross-repo-sync | ~1 h |
| `openspec validate --strict` | (free, included) |
| **Total** | **~12 h** (1.5 dev days) |
