# Coder

## Overview
Coder is an open-source cloud development environment (CDE) platform that provisions remote workspaces via Docker containers. Created by Coder Technologies and available at `ghcr.io/coder/coder`, it allows developers to spin up pre-configured development environments with consistent toolchains, VS Code server integration, and SSH access. The stack includes a Postgres 16 backend for persistent state and workspace metadata.

## Why This Matters for Kings' College Galway
Coder provides the remote development layer for the Kings' College Galway engineering team, enabling standardized environments for working on Dagster pipelines, DLT ingestion jobs, and the TanStack Start frontend. New contributors to the Celtic education platform can onboard instantly with pre-configured workspaces that have Python 3.12, uv, bun, DuckDB, and all project toolchains ready. Workspaces run on the MacBook M4 workload host through Coder's Docker provider, sharing GPU and unified memory for MLX model development.

## Key Features
- Self-hosted cloud development environments with VS Code, SSH, and web terminal access
- Docker provider for workspace isolation (mounts host Docker socket)
- Postgres 16 backend for workspace state and user metadata
- Configurable `CODER_ACCESS_URL` for workspace reachability
- Volume-backed persistent home directories per workspace

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/coder
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/coder
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `CODER_VERSION` | No | Coder Docker image version | `latest` |
| `CODER_PG_CONNECTION_URL` | No | Postgres connection URL (auto-constructed) | — |
| `CODER_HTTP_ADDRESS` | No | HTTP listen address | `0.0.0.0:7080` |
| `CODER_ACCESS_URL` | Yes | External URL workspaces can reach | — |
| `POSTGRES_USER` | No | Postgres username | `username` |
| `POSTGRES_PASSWORD` | Yes | Postgres password | — |
| `POSTGRES_DB` | No | Postgres database name | `coder` |

## Access
- **URL**: `https://coder.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 7080 (Coder), 5432 (Postgres)
- **Auth**: Coder's built-in authentication (OIDC-compatible)

## Health Check
```bash
docker ps --filter name=coder --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/coder/coder
- **Documentation**: https://coder.com/docs
- **Latest release**: Pulls `ghcr.io/coder/coder:latest` — continuously updated cloud development environment platform.
