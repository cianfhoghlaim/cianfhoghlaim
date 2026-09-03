# P2-16 — postgresql (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

PostgreSQL is the **metadata store** for 7 Cianfhoghlaim services (Lakehouse Iceberg catalog, Cognee, MotherDuck, Litellm, Langfuse, MLflow, Pangolin EE). The primary instance runs on PlanetScale (managed); the lakehouse stack includes a local Postgres 16 for the Iceberg catalog.

The canonical Cianfhoghlaim pattern: every stateful service has its **own database** in a shared PlanetScale Postgres cluster (or local Postgres container in lakehouse). Each database uses a dedicated user with least-privilege grants.

## Code

| Path | Purpose |
|:--|:--|
| `infrastructure/stacks/planetscale/schemas/bunchloch.sql` | Database + user setup for bunchloch services |
| `stacks/lakehouse/compose.yaml` (postgres service) | Local Postgres 16 (Iceberg catalog) |
| `stacks/lakehouse/init-db.sql` | Iceberg catalog schema initialization |
| `stacks/cognee/compose.yaml` (cognee-postgres) | Cognee metadata store |
| `stacks/langfuse/compose.yaml` (langfuse-postgres) | Langfuse metadata store |
| `stacks/mlflow/compose.yaml` (mlflow-postgres) | MLflow backend store |
| `cognify/rules/postgres_health.py` | Dagster asset check for all 7 Postgres instances |

**Canonical postgres compose snippet** (`stacks/lakehouse/compose.yaml`):

```yaml
postgres:
  image: postgres:16-alpine
  container_name: lakehouse-postgres
  restart: unless-stopped
  environment:
    POSTGRES_DB: lakehouse_catalog
    POSTGRES_USER: ${POSTGRES_USER:-lakehouse}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    PGDATA: /var/lib/postgresql/data/pgdata
  volumes:
    - lakehouse-postgres-data:/var/lib/postgresql/data
    - ./init-db.sql:/docker-entrypoint-initdb.d/init.sql:ro
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Canonical schema setup** (`infrastructure/stacks/planetscale/schemas/bunchloch.sql`):

```sql
-- 6 schemas for the 7 services that need metadata storage
CREATE DATABASE lakehouse_catalog;
CREATE DATABASE cognee_metadata;
CREATE DATABASE motherduck_state;
CREATE DATABASE litellm_spend;
CREATE DATABASE langfuse_traces;
CREATE DATABASE mlflow_registry;
CREATE DATABASE pangolin_ee;

-- Per-service users (least-privilege)
CREATE USER lakehouse WITH ENCRYPTED PASSWORD '...';
GRANT ALL PRIVILEGES ON DATABASE lakehouse_catalog TO lakehouse;

CREATE USER cognee WITH ENCRYPTED PASSWORD '...';
GRANT ALL PRIVILEGES ON DATABASE cognee_metadata TO cognee;
-- (etc.)
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `POSTGRES_HOST` | (per-service) | Locket |
| `POSTGRES_PORT` | `5432` | default |
| `POSTGRES_DB` | (per-service) | compose env |
| `POSTGRES_USER` | (per-service) | Locket |
| `POSTGRES_PASSWORD` | `infisical://dev-baile/<service>/postgres_password` | Locket |

## CCC anchors

`infrastructure/stacks/planetscale/` · `stacks/lakehouse/init-db.sql` · `cognify/rules/postgres_health.py` · 7 stack compose files

Search terms: `"postgres:16-alpine"`, `"pg_isready"`, `"POSTGRES_DB"`, `"GRANT ALL"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-08 | Migrated from SQLite (LiteLLM) to Postgres (managed) |
| 2025-12 | Adopted PlanetScale Postgres for shared cluster |
| 2026-01 | Added per-service least-privilege users |
| 2026-04 | Added `postgres_health` Dagster asset check |

## Anti-patterns

1. Don't share one database across multiple services — separate DBs per service
2. Don't use `postgres` superuser in production — create per-service users
3. Don't skip the `pg_isready` healthcheck — orchestrators need it
4. Don't store Postgres data in a docker volume on MacBook — use managed cloud DB

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Version | Postgres 16 | Latest stable + Iceberg + pgvector support |
| Hosting (prod) | PlanetScale (managed) | HA + scaling |
| Hosting (local) | Docker container in stack | Offline dev |
| Backup | PlanetScale daily snapshots | Off-host retention |
| Per-service DBs | Yes | Isolation + easier migrations |
| Connection pooler | PgBouncer (PlanetScale) | Reduce connection overhead |
| Migrations | sqitch (or Drizzle for TS) | Reversible + per-stack |

## Files to read next

`infrastructure/stacks/planetscale/schemas/bunchloch.sql` · `stacks/lakehouse/init-db.sql` · `cognify/rules/postgres_health.py` · `.agents/skills/secrets-management/SKILL.md`
