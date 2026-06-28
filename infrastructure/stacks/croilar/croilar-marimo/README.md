# Croilar Marimo

## Overview
The Croilar Marimo stack serves a reactive Python notebook dashboard for the Croilar personal portfolio. It uses a custom `ghcr.io/cianfhoghlaim/croilar-marimo:0.1.0` image and runs on port 2718, providing live analytics visualizations backed by DuckDB and LanceDB. The stack operates independently from the main Oideachais Marimo instance.

## Why This Matters for Kings' College Galway
Croilar Marimo is the analytics frontend for the personal data engineering backend. It connects to the same DuckDB and LanceDB stores that Croilar Dagster populates, rendering interactive charts of streaming media consumption patterns, professional experience timelines, and skill embeddings. The dashboard demonstrates the full reactive notebook pattern — Marimo connecting to DuckLake-backed DuckDB and LanceDB vector stores — that the Celtic education platform uses for curriculum analytics. It serves as both a personal analytics tool and a reference implementation for the data visualization patterns used across the platform.

## Key Features
- Reactive Python notebook dashboard for personal analytics
- DuckDB backend for media consumption and CV data queries
- LanceDB vector store for professional experience semantic search
- Configurable lazy/eager runtime for performance tuning
- Standalone deployment separate from Oideachais Marimo

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/croilar-marimo
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/croilar-marimo
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `CROILAR_MARIMO_PORT` | No | Host port for the dashboard | `2718` |
| `MARIMO_RUNTIME` | No | Marimo execution runtime | `lazy` |
| `DUCKDB_PATH` | No | DuckDB database path | `./croilar.duckdb` |
| `LANCEDB_URI` | No | LanceDB vector store URI | `./lancedb_data_cv` |
| `CROILAR_DB_URL` | No | External database URL | — |

## Access
- **URL**: `https://marimo.croilar.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 2718 (default, configurable via `CROILAR_MARIMO_PORT`)
- **Auth**: No built-in auth — protected by Pangolin/TinyAuth upstream

## Health Check
```bash
docker ps --filter name=croilar-marimo --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/marimo-team/marimo
- **Documentation**: https://docs.marimo.io
- **Latest release**: Custom image `ghcr.io/cianfhoghlaim/croilar-marimo:0.1.0` — built on Marimo 0.23.x.
