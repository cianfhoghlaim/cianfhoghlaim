# Mathesar

## Overview
Mathesar is an open-source web application that provides a spreadsheet-like interface for PostgreSQL databases. Created by the Mathesar team and available at `mathesar/mathesar:0.2.2`, it allows non-technical users to explore, filter, sort, and edit database tables through an intuitive UI without writing SQL. The stack includes a dedicated Postgres 16 backend for Django and a configurable port for the web interface.

## Why This Matters for Kings' College Galway
Mathesar provides the database exploration layer for the Celtic education data platform. Curriculum specialists and content editors who don't write SQL can browse the Oideachais Postgres tables — inspecting ingested exam questions, reviewing extracted curriculum topics, and validating bilingual Irish/English content mappings — through a familiar spreadsheet interface. It connects to any of the platform's 6+ Postgres instances (Litellm, n8n, windmill, langfuse, cognee, lakehouse) for ad-hoc data exploration without requiring Dagster UI or DuckDB CLI access. This bridges the gap between the engineering data layer and the education content team.

## Key Features
- Spreadsheet-like interface for PostgreSQL databases
- Table exploration with filtering, sorting, and inline editing
- Django-based web application with production settings
- Separate internal Postgres 16 for Django metadata
- Configurable connection to any external PostgreSQL database

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/mathesar
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/mathesar
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `MATHESAR_VERSION` | No | Mathesar Docker image version | `0.2.2` |
| `MATHESAR_PORT` | No | Host port for the web UI | `8000` |
| `MATHESAR_DB_USER` | No | Internal Django Postgres user | `mathesar` |
| `MATHESAR_DB_PASSWORD` | Yes | Internal Django Postgres password | — |
| `MATHESAR_SECRET_KEY` | Yes | Django secret key | — |
| `MATHESAR_ALLOWED_HOSTS` | No | Django allowed hosts | `*` |
| `POSTGRES_HOST` | No | Django Postgres host | `postgres` |
| `POSTGRES_PORT` | No | Django Postgres port | `5432` |
| `POSTGRES_DB` | No | Django Postgres database | `mathesar_django` |

## Access
- **URL**: `https://mathesar.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 8000
- **Auth**: Django admin authentication

## Health Check
```bash
docker ps --filter name=mathesar --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/mathesar-foundation/mathesar
- **Documentation**: https://docs.mathesar.org
- **Latest release**: Pinned at `mathesar/mathesar:0.2.2` — spreadsheet interface for PostgreSQL.
