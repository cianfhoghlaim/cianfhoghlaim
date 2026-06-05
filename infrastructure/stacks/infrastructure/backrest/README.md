# Backrest — Web UI for Restic Backups

## Overview

Backrest is a web-based management interface for Restic, the fast and secure backup program. It provides a graphical dashboard for configuring backup schedules, monitoring backup health, browsing snapshots, and restoring files — all backed by Restic's deduplicated, encrypted, and versioned repository format.

## Why This Matters for Kings' College Galway

The 89 Docker Compose stacks hold irreplaceable state: the Dagster database (pipeline run history), the Langfuse database (LLM traces), the Cognee and Graphiti knowledge graphs (curriculum prerequisite chains), and the LanceDB vector indexes (curriculum embeddings). Rebuilding any of these from scratch would take days of compute. Backrest ensures every Docker volume is backed up to Garage S3 with Restic's deduplication (only changed blocks are stored) and encryption (AES-256). The web UI makes it trivial to verify backup health and restore individual files or entire volumes.

## Key Features

- **Restic-powered** — Industry-standard deduplicated, encrypted, versioned backups
- **Web UI** — Schedule management, snapshot browser, restore interface
- **S3-compatible** — Backs up to Garage S3 (or any S3-compatible storage)
- **Docker volume awareness** — Mount `/var/run/docker.sock` to discover and backup named volumes
- **Scheduled snapshots** — Configurable retention policies (daily, weekly, monthly)

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/backrest
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Configure the Restic repository to point to the Garage S3 bucket (`s3:backrest`) after initial Garage bootstrap.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `BACKREST_DATA` | No | Backrest data directory | `/data` |
| `BACKREST_HOST` | No | Listen address | `0.0.0.0:9898` |
| `XDG_CONFIG_HOME` | No | Restic config directory | `/config` |
| `RESTIC_REPOSITORY` | Yes | Restic repository URL (S3) | — |
| `RESTIC_PASSWORD` | Yes | Restic repository encryption password | — |
| `AWS_ACCESS_KEY_ID` | Yes | Garage S3 access key | — |
| `AWS_SECRET_ACCESS_KEY` | Yes | Garage S3 secret key | — |

## Access

- **Web UI**: `https://backrest.cianfhoghlaim.ie` (private, Admin role)
- **Auth**: Built-in admin account

## Upstream

- **Repository**: <https://github.com/garethgeorge/backrest>
- **Documentation**: <https://garethgeorge.github.io/backrest/>
- **Latest**: Active development (2025) — improved snapshot browser, backup health dashboard, multi-repository support

## Screenshot

Backrest's web UI shows a dashboard with backup repository status (last backup time, next scheduled run, repository size), a snapshot timeline browser, individual file restore interface, and backup configuration panel with schedule and retention policy settings.
