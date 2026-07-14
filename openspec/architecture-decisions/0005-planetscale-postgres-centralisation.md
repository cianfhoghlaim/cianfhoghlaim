# ADR 0005: PlanetScale Postgres Centralisation

> **Status:** Accepted
> **Date:** 2026-07-19
> **Deciders:** Operator + build agents
> **Linked openspec change:** [`2026-07-19-planetscale-postgres-landscape-v1`](../changes/2026-07-19-planetscale-postgres-landscape-v1/proposal.md)
> **Linked spec:** [`planetscale-postgres-data-strategy`](../specs/planetscale-postgres-data-strategy/spec.md)

## Context

The Cianfhoghlaim platform (post-v7-flatten monorepo) ships **24+ PostgreSQL-bearing Docker Compose stacks** under `bonneagar/stacks/`. Each stack runs its own `postgres:<version>` container with a named volume, an unwritten (or per-stack) backup strategy, and bespoke env wiring (`DATABASE_URL`, `POSTGRES_PASSWORD`, etc.).

In addition, the platform already uses **PlanetScale MySQL** for:

- **DuckLake table metadata** (per `bonneagar/stacks/lakehouse/README.md` + `secrets.env`)
- **6 Bytebase-managed schemas**: `vikunja`, `n8n`, `calcom`, `paperless`, `glance`, `changedetection` (per `bonneagar/stacks/bytebase/bytebase-config.yaml`)

The operator now has access to a **PlanetScale PostgreSQL server** as a managed remote DB and has explicitly stated:

> *"we want to only be using planetscale postgresql, cloudflare d1 sqlite or local postgresql or relevant local db if necessary"*

This ADR captures the technical decision to standardise on PlanetScale PostgreSQL as the primary managed DB substrate for the platform.

## Decision

Adopt the following **canonical data-substrate strategy** for the Cianfhoghlaim platform:

1. **Primary substrate**: **PlanetScale PostgreSQL** (managed remote DB)
2. **Secondary substrate**: **Cloudflare D1 SQLite** (serverless, read-mostly)
3. **Tertiary substrate**: **local Postgres container** (only when PlanetScale cannot provide a required extension)

This is codified in `openspec/specs/planetscale-postgres-data-strategy/spec.md` R1–R8.

### Key technical findings (verified 2026-07-19)

**PlanetScale PostgreSQL supported extensions** (per https://planetscale.com/docs/postgres/extensions):

- **Vector**: `pgvector` 0.8.0/0.8.1 ✅ (1.0 for Postgres 18.4 planned; supports AI/ML workloads)
- **Scheduling**: `pg_cron` 1.6.5/1.6.7 ✅ (restart required)
- **Partitioning**: `pg_partman` 5.2.4/5.3.1 ✅ + `pg_partman_bgw` ✅
- **Geospatial**: `postgis` 3.5.3/3.6.1 ✅ + `postgis_*` family ✅
- **Analytical**: `pg_duckdb` 1.0.0/1.1.0 ✅ + TimescaleDB ✅
- **Text search**: `pg_trgm` ✅, `unaccent` ✅
- **Specialised**: `cube` ✅, `earthdistance` ✅, `hstore` ✅, `ltree` ✅
- **PlanetScale-builtin**: `pg_strict` ✅ (unmodifiable; prevents accidental `UPDATE`/`DELETE` without WHERE), `pginsights` ✅

**PlanetScale PostgreSQL NOT supported**:

- ❌ **`documentdb`** — the FerretDB v2 hard requirement (Postgres-side store for MongoDB documents). The `ghcr.io/ferretdb/postgres-documentdb:17` image is the ONLY Postgres flavor with `documentdb` support; PlanetScale Postgres uses Aurora-fork vanilla Postgres without it.

**PlanetScale PostgreSQL connection requirements**:

- `?sslmode=verify-full` (TLS enforced)
- PgBouncer pool mode on port 6543 for serverless apps (e.g., Convex)
- Direct mode on port 5432 for long-running apps (e.g., Lakekeeper, Dagster)
- No superuser privileges (no `CREATE DATABASE` after branch creation; `CREATE EXTENSION` only for restart-not-required extensions unless pre-configured via dashboard)

### Per-stack decisions (excerpt — full 28-row matrix in the umbrella spec R7)

| Category | Stacks | Decision |
|---|---|---|
| **Easy swaps** (PlanetScale PG default) | Lakekeeper, Convex, Dagster/DuckLake, langfuse, mlflow, cognee, logfire, agent-os, lmnr, karakeep, windmill, browser, forgejo, actual, infisical, wave2/{immich,khoj,outline,mealie,letta} | Phase B: trivial env-var swap |
| **Migration from PlanetScale MySQL** | DuckLake tables, vikunja, n8n, cal-diy, paperless, glance, changedetection | Phase C: schema-migration under Bytebase |
| **Serverless read-mostly** | per-subject `conic-<subject>` Convex deployments | Phase B: Cloudflare D1 SQLite |
| **Out of scope (deferred)** | Komodo + FerretDB (the only MongoDB-stacks-compatible system in the platform) | Per operator choice: deferred to a separate future change |

## Status

**Accepted (2026-07-19)** as the canonical DB strategy for the platform. The text-only landscape analysis change (`2026-07-19-planetscale-postgres-landscape-v1`) ships the umbrella spec + 17 cross-reference spec deltas. Phase B + C + Komodo follow-ups are tracked in `tasks.md` § "Open follow-up changes".

## Consequences

### Positive

- **✅ Centralised managed DB**: one PlanetScale branch hosts ~23 stacks vs. ~24 separate local containers today
- **✅ PITR backups**: PlanetScale owns the snapshot cadence + 7-day PITR; we lose the per-stack backup cron complexity
- **✅ Disaster recovery**: regional + cross-region replicas available; per-branch backups are trivial
- **✅ TLS-by-default**: `?sslmode=verify-full` enforced at the connection layer
- **✅ Single source of truth**: DDL migrations land in one branch per environment; per-stack migration order = PlanetScale branch order
- **✅ Sunset PlanetScale MySQL**: removes the dual-engine operational burden once Phase C completes

### Negative

- **⚠ Komodo + FerretDB remains local**: the operator chose to defer indefinitely; we carry the `documentdb` extension + FerretDB v2 stack until a separate future change re-architects Komodo
- **⚠ 6 Bytebase-managed schemas need schema migration**: Phase C will DROP+CREATE each MySQL schema in Postgres, then data-migrate; data-integrity verification required
- **⚠ Superuser restrictions**: pre-creation of databases / extensions must happen via the PlanetScale dashboard BEFORE the app connects (automated via the new `planetscale-postgres.ts` IaC procedure)
- **⚠ Extension matrix drift**: PlanetScale's supported extension list could change; R6 mandates operator verification at adoption time
- **⚠ Backup semantics change**: losing the explicit `komodo backup` cron for non-Komodo stacks (acceptable trade-off for PlanetScale's PITR)

## Alternatives Considered

### Alt A — Self-host Postgres on `arm1-oci`

- **Pros**: full superuser; no per-cloud lock-in; can use any extension
- **Cons**: operational cost (PG tuning + PITR + backups + monitoring); defeats "remote backed-up" goal; we've already mentally trialled and branched off due to ops cost
- **Decision**: rejected

### Alt B — Use Neon or Supabase instead of PlanetScale PG

- **Pros**: established managed PG platforms
- **Cons**: introduced a 2nd vendor; we already standardised on PlanetScale for MySQL; consolidation wins
- **Decision**: rejected

### Alt C — Keep everything local (no managed DB)

- **Pros**: no vendor lock-in
- **Cons**: directly contradicts the operator's stated goal ("remote backed-up")
- **Decision**: rejected

### Alt D — Standardise on Cloudflare D1 SQLite only

- **Pros**: ultra-cheap; edge-replicated; serverless
- **Cons**: SQLite is not Postgres; many stacks depend on Postgres-specific features (JSONB indexes, pgvector, postgis, etc.)
- **Decision**: rejected — D1 is a viable secondary substrate but not a primary Postgres replacement

## References

- PlanetScale PG extension matrix — https://planetscale.com/docs/postgres/extensions (verified 2026-07-19)
- `openspec/changes/2026-07-19-planetscale-postgres-landscape-v1/proposal.md` — the 28-row matrix + the Phase B + C plan
- `openspec/specs/planetscale-postgres-data-strategy/spec.md` — the canonical DB strategy spec (R1–R8)
- `bonneagar/stacks/lakehouse/README.md` — the existing PlanetScale MySQL usage (the bifurcation research doc)
- `bonneagar/stacks/bytebase/bytebase-config.yaml` — the production PlanetScale PG connection (region `eu-west-3 (bunchloch)`)
- `https://www.ferretdb.com/` — FerretDB docs (relevant for the deferred Komodo re-architecture)
- 2026-07-12 (pre-v7 flatten) — current local-Postgres proliferation baseline
