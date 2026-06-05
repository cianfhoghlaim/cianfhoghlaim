# Marimo

## Overview
Marimo is a reactive Python notebook that runs reproducible experiments, executes SQL queries, deploys as interactive web apps, and versions cleanly with git. Created by the marimo team and distributed as `marimo/marimo:latest`, notebooks are stored as pure Python files (`.py`) — not JSON — making them git-friendly, deterministic, and free of hidden state. The stack runs in headless mode on port 2718, serving the `mission_control.py` notebook as the Oideachais analytics dashboard.

## Why This Matters for Kings' College Galway
Marimo is the primary data exploration and analytics dashboard for the Celtic education platform. The `mission_control.py` notebook connects to DuckDB (querying the Garage S3 Parquet lake) and LanceDB (vector searching curriculum embeddings) to produce live, reactive charts of curriculum coverage, exam extraction progress, and AI-generated study asset quality metrics. When a curriculum specialist wants to see how many Leaving Cert Irish oral exam topics have been ingested, or a data engineer needs to debug a DLT pipeline's output distribution, they open the Marimo dashboard — no Jupyter server, no hidden state, just deterministic Python that reacts to changes instantly. The reactive model ensures every chart updates when underlying data changes, making it the single source of truth for platform analytics.

## Key Features
- Reactive Python notebooks — cells automatically re-execute when dependencies change
- Pure Python file format (`.py`) — git-friendly, no JSON blobs
- SQL support with DuckDB and ibis backends via the lakehouse
- Headless mode serving `mission_control.py` as a live dashboard
- 2GB / 2 CPU allocation with configurable lazy/eager runtime

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/marimo
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/marimo
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on arm1-oci. Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — this stack has no secrets; the placeholder secrets.env exists for Locket compatibility only.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| *(none)* | — | This stack has no environment variables; it serves the Oideachais notebook directory as read-only | — |

## Access
- **URL**: `https://marimo.cianfhoghlaim.ie` (private, Pangolin Member role required)
- **Internal port**: 2718
- **Auth**: No built-in auth — protected by Pangolin/TinyAuth upstream

## Health Check
```bash
docker ps --filter name=marimo --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/marimo-team/marimo
- **Documentation**: https://docs.marimo.io
- **Latest release**: v0.23.9 (2026-06-04) — Non-destructive multi-tab notebooks (read-only viewer + bidirectional takeover), `mo.ui.table` column visibility controls, cells with no output now appear in slides minimap, removed Marimo sharing, per-provider `max_tokens` defaults, WASM compatibility checks, and multiple SQL/UX fixes.
