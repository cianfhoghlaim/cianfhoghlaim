# Bytebase

## Overview
Bytebase is an open-source database CI/CD tool that provides SQL review, GitOps-based schema migration, and database change management. Created by Bytebase Inc. and distributed at `bytebase/bytebase:latest`, it acts as a developer-tooling entry point for managing SQL migrations. The stack includes a dedicated Postgres 16 backend for Bytebase's own metadata.

## Why This Matters for Kings' College Galway
Bytebase manages SQL migrations across all 6+ Postgres instances in the Cianfhoghlaim platform — LiteLLM's model registry, Langfuse's observability store, n8n's workflow database, Windmill's job queue, Cognee's knowledge graph, and the Lakehouse catalog. As the platform evolves with new curriculum schemas, analytics tables, and vector embedding metadata, Bytebase ensures that every database migration is reviewed, versioned, and applied consistently. It enforces SQL review policies that prevent accidental schema drift across the Celtic education data layer — critical for maintaining data integrity in a multi-database, multi-service architecture.

## Key Features
- GitOps-driven database change management with SQL review
- Schema migration versioning and rollback support
- Multi-database support across all platform Postgres instances
- Web UI at port 8080 (mapped to host port 5670) with health check endpoint
- Dedicated Postgres 16 backend for Bytebase metadata

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/bytebase
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/bytebase
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PG_URL` | No | Bytebase Postgres connection URL (auto-constructed) | — |
| `EXTERNAL_URL` | No | External access URL | `http://bytebase.cianfhoghlaim.ie` |
| `BYTEBASE_PG_PASSWORD` | Yes | Bytebase Postgres password | — |

## Access
- **URL**: `https://bytebase.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 5670 (mapped to container port 8080)
- **Auth**: Bytebase's built-in authentication

## Health Check
```bash
docker ps --filter name=bytebase --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/bytebase/bytebase
- **Documentation**: https://www.bytebase.com/docs
- **Latest release**: Pulls `bytebase/bytebase:latest` — database CI/CD with SQL review and GitOps.
