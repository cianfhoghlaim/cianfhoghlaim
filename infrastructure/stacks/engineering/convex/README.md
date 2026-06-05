# Convex

## Overview
Convex is a reactive backend-as-a-service platform that provides real-time data sync, serverless functions, and automatic caching. Created by Convex Dev and distributed at `ghcr.io/get-convex/convex-backend`, it replaces traditional REST APIs with a declarative, function-based backend where queries automatically update when data changes. The stack includes the core backend server (ports 3210/3211) and a Next.js dashboard (port 6791).

## Why This Matters for Kings' College Galway
Convex provides the real-time backend for the Túatha educational MMO and the Oideachais web frontend. When a student progresses through a Leaving Cert Irish module, their progress is synced in real-time across all their devices via Convex's WebSocket layer. Study group sessions broadcast quiz results to all participants instantly through Convex's reactive queries. For the Túatha MMO, Convex manages real-time player state, world positions, and educational quest progress — all with automatic optimistic updates and conflict resolution. It connects to the Garage S3 lakehouse for file storage and module persistence.

## Key Features
- Reactive backend with automatic real-time sync and WebSocket push
- Serverless function execution with ACID transactions
- Self-hosted deployment with optional S3/R2 storage backend
- Next.js dashboard for function monitoring and data inspection
- Configurable document retention with action timeout controls

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/convex
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/convex
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `CONVEX_PORT` | No | Backend server port | `3210` |
| `CONVEX_SITE_PORT` | No | Site server port | `3211` |
| `CONVEX_DASHBOARD_PORT` | No | Dashboard port | `6791` |
| `CONVEX_CLOUD_ORIGIN` | No | Cloud origin URL | `http://127.0.0.1:3210` |
| `CONVEX_SITE_ORIGIN` | No | Site origin URL | `http://127.0.0.1:3211` |
| `CONVEX_INSTANCE_NAME` | No | Instance name | `convex` |
| `CONVEX_INSTANCE_SECRET` | Yes | Instance secret | — |
| `CONVEX_DATABASE_URL` | No | Database connection URL (optional) | — |
| `CONVEX_POSTGRES_URL` | No | External Postgres URL (optional) | — |
| `CONVEX_MYSQL_URL` | No | External MySQL URL (optional) | — |
| `AWS_ACCESS_KEY_ID` | No | S3 access key | — |
| `AWS_SECRET_ACCESS_KEY` | No | S3 secret key | — |
| `AWS_REGION` | No | S3 region | `auto` |
| `AWS_ENDPOINT_URL` | No | S3 endpoint URL (Garage) | — |
| `S3_STORAGE_FILES_BUCKET` | No | S3 files bucket | — |
| `S3_STORAGE_MODULES_BUCKET` | No | S3 modules bucket | — |
| `S3_STORAGE_SEARCH_BUCKET` | No | S3 search bucket | — |
| `S3_STORAGE_EXPORTS_BUCKET` | No | S3 exports bucket | — |
| `S3_STORAGE_SNAPSHOT_IMPORTS_BUCKET` | No | S3 snapshot imports bucket | — |
| `AWS_S3_FORCE_PATH_STYLE` | No | Force path-style S3 URLs | `true` |
| `DOCUMENT_RETENTION_DELAY` | No | Document retention in seconds | `172800` |
| `RUST_LOG` | No | Rust log level | `info` |
| `NEXT_PUBLIC_DEPLOYMENT_URL` | No | Dashboard deployment URL | `http://127.0.0.1:3210` |

## Access
- **URLs**: `https://convex-api.cianfhoghlaim.ie` (API), `https://convex-site.cianfhoghlaim.ie` (Site), `https://convex.cianfhoghlaim.ie` (Dashboard)
- **Internal ports**: 3210 (backend), 3211 (site), 6791 (dashboard)
- **Auth**: Instance secret (`CONVEX_INSTANCE_SECRET`)

## Health Check
```bash
docker ps --filter name=convex --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/get-convex/convex-backend
- **Documentation**: https://docs.convex.dev
- **Latest release**: Pulls `ghcr.io/get-convex/convex-backend:latest` and `ghcr.io/get-convex/convex-dashboard:latest`.
