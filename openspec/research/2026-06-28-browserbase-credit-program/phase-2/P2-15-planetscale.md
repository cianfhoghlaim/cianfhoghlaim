# P2-15 — planetscale (Phase 2, Infrastructure)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** infrastructure

## TL;DR

PlanetScale is the **managed MySQL-compatible Postgres provider** for the 7 Cianfhoghlaim stateful services (Lakehouse, Cognee, MotherDuck, Litellm, Langfuse, MLflow, Pangolin EE). It provides HA, automated backups, and per-database connection pooling via PgBouncer.

The canonical Cianfhoghlaim pattern: one PlanetScale cluster (`bunchloch` + `arm1-oci` for redundancy), one database per service, one user per database with least-privilege grants.

## Code

| Path | Purpose |
|:--|:--|
| `infrastructure/stacks/planetscale/schemas/bunchloch.sql` | Bunchloch cluster schema (7 databases + 7 users) |
| `infrastructure/stacks/planetscale/schemas/arm1-oci.sql` | arm1-oci cluster schema (mirror) |
| `infrastructure/pulumi/planetscale/` | Pulumi IaC for PlanetScale resources |
| `cognify/rules/planetscale_health.py` | Dagster asset check for both clusters |
| `stacks/planetscale/` | (Local dev: docker-compose Postgres + PlanetScale-shaped schema) |

**Canonical PlanetScale schema** (`infrastructure/stacks/planetscale/schemas/bunchloch.sql`):

```sql
-- 7 databases for the 7 stateful services
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

-- (etc. for each service)
```

**Pulumi IaC** (`infrastructure/pulumi/planetscale/__main__.py`):

```python
import pulumi_planetscale as ps

# Bunchloch cluster (primary)
bunchloch = ps.Database(
    "bunchloch-cluster",
    name="bunchloch",
    region="aws-us-east-1",
    kind="postgresql",
    cluster_size="PS-10",  # 10 vCPU, 40 GB RAM
)

# 7 databases (one per service)
for service in ["lakehouse_catalog", "cognee_metadata", "motherduck_state",
                "litellm_spend", "langfuse_traces", "mlflow_registry", "pangolin_ee"]:
    ps.Database(service, name=service, cluster=bunchloch)
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `PLANETSCALE_ORG` | `cianfhoghlaim` | Locket |
| `PLANETSCALE_TOKEN` | `infisical://dev-baile/planetscale/token` | Locket |
| `PLANETSCALE_BUNCHLOCH_HOST` | `aws-us-east-1.bunchloch.psdb.cloud` | Locket |
| `PLANETSCALE_ARM1_OCI_HOST` | `aws-us-east-1.arm1-oci.psdb.cloud` | Locket |

## CCC anchors

`infrastructure/stacks/planetscale/` · `infrastructure/pulumi/planetscale/` · `cognify/rules/planetscale_health.py` · 7 service compose files

Search terms: `"Database("`, `"bunchloch"`, `"GRANT ALL PRIVILEGES"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-08 | Migrated from self-hosted Postgres to PlanetScale |
| 2025-12 | Added arm1-oci mirror (geographic redundancy) |
| 2026-01 | Per-service least-privilege users |
| 2026-04 | Switched from MySQL to Postgres (Postgres 16 native) |
| 2026-06 | Added Pulumi IaC for declarative cluster management |

## Anti-patterns

1. Don't use the `root` user from services — always per-service users
2. Don't share connection strings across services — each has its own
3. Don't use raw port 5432 — use the PlanetScale pooler (port 5432 with TLS)
4. Don't skip the daily snapshot — PlanetScale handles it but verify

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Provider | PlanetScale | Managed + per-DB users + HA |
| Version | Postgres 16 | Native Iceberg + pgvector |
| Cluster size | PS-10 (10 vCPU, 40 GB RAM) | Enough for 7 databases |
| Backup | Daily snapshot (PlanetScale default) | 30-day retention |
| Replication | Cross-region (bunchloch + arm1-oci) | DR |
| Migration tool | pscale CLI + GitHub Actions | CI/CD for schema |
| Cost | ~$300/month for PS-10 | Worth the HA + ops savings |

## Files to read next

`infrastructure/stacks/planetscale/schemas/bunchloch.sql` · `infrastructure/pulumi/planetscale/` · `cognify/rules/planetscale_health.py`
