# Dagster Reference Library

Dagster is an asset-based data orchestration framework. The `docs/dagster/` library is consolidated from 27 root .md + 7 integration subdirs.

Last consolidated: 2026-06-14

---

## Core reference

| Document | Description |
|----------|-------------|
| [dagster-comprehensive.md](dagster-comprehensive.md) | 13,602-line merged doc — Dagster expert skill, API quick reference, design patterns, integration research, deployment guides (synthesis of 62 source files) |
| [dagster.md](dagster.md) | Top-level Dagster overview (the KCG summary) |
| [dagster-api-quick-reference.md](dagster-api-quick-reference.md) | API quick-reference card |
| [dagster-design-patterns-research.md](dagster-design-patterns-research.md) | 3,352-line design-patterns research |
| [dagster-orchestration.md](dagster-orchestration.md) | Orchestration for Cocoindex + Graphiti (our specific use case) |
| [dagster-research.md](dagster-research.md) + [dagster-research-2024-2025.md](dagster-research-2024-2025.md) | Multi-year research synthesis |
| [dagster-openapi-research.md](dagster-openapi-research.md) | OpenAPI surface analysis |

## Dagster official docs (scraped)

| Document | Topic |
|----------|-------|
| [Advanced config types _ Dagster Docs.md](Advanced%20config%20types%20_%20Dagster%20Docs.md) | ConfigurableResource + Pydantic |
| [Building machine learning pipelines with Dagster _ Dagster Docs.md](Building%20machine%20learning%20pipelines%20with%20Dagster%20_%20Dagster%20Docs.md) | ML pipelines |
| [Components _ Dagster Docs.md](Components%20_%20Dagster%20Docs.md) | Component system |
| [Creating workspaces to manage multiple projects _ Dagster Docs.md](Creating%20workspaces%20to%20manage%20multiple%20projects%20_%20Dagster%20Docs.md) | Workspaces |
| [Data Ingestion Patterns_ Push, Pull & Poll Explained _ Dagster.md](Data%20Ingestion%20Patterns_%20Push%2C%20Pull%20%26%20Poll%20Explained%20_%20Dagster.md) | Ingestion patterns |
| [datadog (dagster-datadog) _ Dagster Docs.md](datadog%20%28dagster-datadog%29%20_%20Dagster%20Docs.md) | Datadog integration |
| [Deploying Dagster to Google Cloud Platform _ Dagster Docs.md](Deploying%20Dagster%20to%20Google%20Cloud%20Platform%20_%20Dagster%20Docs.md) | GCP deployment |
| [dlt (dagster-dlt) _ Dagster Docs.md](dlt%20%28dagster-dlt%29%20_%20Dagster%20Docs.md) | DLT integration |
| [duckdb (dagster-duckdb) _ Dagster Docs.md](duckdb%20%28dagster-duckdb%29%20_%20Dagster%20Docs.md) | DuckDB integration |
| [github (dagster-github) _ Dagster Docs.md](github%20%28dagster-github%29%20_%20Dagster%20Docs.md) | GitHub integration |
| [graphql (dagster-graphql) _ Dagster Docs.md](graphql%20%28dagster-graphql%29%20_%20Dagster%20Docs.md) | GraphQL API |
| [iceberg (dagster-iceberg) _ Dagster Docs.md](iceberg%20%28dagster-iceberg%29%20_%20Dagster%20Docs.md) | Iceberg integration |
| [Manage concurrency of Dagster assets, jobs, and Dagster instances _ Dagster Docs.md](Manage%20concurrency%20of%20Dagster%20assets%2C%20jobs%2C%20and%20Dagster%20instances%20_%20Dagster%20Docs.md) | Concurrency control |
| [Managing machine learning models with Dagster _ Dagster Docs.md](Managing%20machine%20learning%20models%20with%20Dagster%20_%20Dagster%20Docs.md) | ML model mgmt |
| [mlflow (dagster-mlflow) _ Dagster Docs.md](mlflow%20%28dagster-mlflow%29%20_%20Dagster%20Docs.md) | MLflow integration |
| [postgresql (dagster-postgres) _ Dagster Docs.md](postgresql%20%28dagster-postgres%29%20_%20Dagster%20Docs.md) | Postgres integration |
| [Real-time system _ Dagster Docs.md](Real-time%20system%20_%20Dagster%20Docs.md) | Real-time / streaming |
| [Run configuration _ Dagster Docs.md](Run%20configuration%20_%20Dagster%20Docs.md) | Run config |
| [Using environment variables and secrets in Dagster code _ Dagster Docs.md](Using%20environment%20variables%20and%20secrets%20in%20Dagster%20code%20_%20Dagster%20Docs.md) | Env + secrets |

## Integrations (7 subdirs in `integrations/`)

Each is a focused reference for one integration:

- `integrations/dagster-ducklake/` — DuckLake table integration
- `integrations/dagster-evidence/` — Evidence.dev BI dashboards
- `integrations/dagster-iceberg/` — Iceberg table integration
- `integrations/dagster-modal/` — Modal deployment
- `integrations/dagster-sqlmesh/` — SQLMesh integration
- `integrations/deploy/` — Deployment patterns
- `integrations/dlt_github/` — DLT + GitHub

## Note on duplicates

`dagster_ducklake.md` and `dagster_iceberg.md` were byte-identical to their `integrations/<name>/README.md` counterparts; the README files (with upstream provenance) were kept and the standalone .md files removed. **`dagster-dspy/` (138 files)** was removed entirely per consolidation policy (separate project, not Dagster core).
