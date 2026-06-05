# Croilar Dagster

## Overview
The Croilar Dagster stack runs a dedicated Dagster instance for the Croilar personal portfolio and data engineering pipeline. It uses a custom `ghcr.io/cianfhoghlaim/croilar-dagster:0.1.0` image and operates independently from the main Oideachais Dagster instance. The stack orchestrates data pipelines that aggregate personal analytics — Spotify listening history, SoundCloud activity, YouTube metrics, and professional CV data — into a DuckDB analytics database and LanceDB vector store.

## Why This Matters for Kings' College Galway
Croilar Dagster manages the personal data engineering backend that powers the Croilar web presence and portfolio. It ingests streaming media data (Spotify, SoundCloud, YouTube) for the "data-driven CV" feature, builds LanceDB vector embeddings of professional experience for semantic search, and maintains the DuckDB analytics layer that feeds the Croilar Marimo dashboard. While separate from the Celtic education data platform, it shares the same Dagster orchestration patterns and infrastructure — demonstrating the platform's ability to run multiple isolated data pipelines on the same orchestration fabric.

## Key Features
- Dedicated Dagster instance for personal data engineering pipelines
- DuckDB analytics database for media consumption metrics
- LanceDB vector store for CV and professional experience embeddings
- Spotify, SoundCloud, and YouTube API integrations for streaming data
- Encryption key support for sensitive personal data at rest

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/croilar-dagster
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/croilar-dagster
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `CROILAR_DAGSTER_PORT` | No | Host port for the webserver | `3336` |
| `DAGSTER_HOME` | No | Dagster home directory | `/opt/dagster/dagster_home` |
| `DAGSTER_ENV` | No | Dagster environment | `local` |
| `DUCKDB_PATH` | No | DuckDB database path | `./croilar.duckdb` |
| `LANCEDB_URI` | No | LanceDB vector store URI | `./lancedb_data_cv` |
| `SPOTIFY_CLIENT_ID` | No | Spotify API client ID | — |
| `SPOTIFY_CLIENT_SECRET` | No | Spotify API client secret | — |
| `SOUNDCLOUD_CLIENT_ID` | No | SoundCloud API client ID | — |
| `YOUTUBE_API_KEY` | No | YouTube Data API key | — |
| `CROILAR_ENCRYPTION_KEY` | No | Encryption key for sensitive data | — |
| `CROILAR_DB_URL` | No | External database URL | — |

## Access
- **URL**: `https://dagster.croilar.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 3000 (mapped to host port 3336)
- **Auth**: No built-in auth — protected by Pangolin/TinyAuth upstream

## Health Check
```bash
docker ps --filter name=croilar-dagster --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/dagster-io/dagster
- **Documentation**: https://docs.dagster.io
- **Latest release**: Custom image `ghcr.io/cianfhoghlaim/croilar-dagster:0.1.0` — built on Dagster 1.13.x.
