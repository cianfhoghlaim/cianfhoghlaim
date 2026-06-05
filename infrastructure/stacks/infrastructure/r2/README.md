# Cloudflare R2 — Multi-Bucket Object Storage via FUSE Mount

## Overview

Cloudflare R2 is an S3-compatible object storage service with zero egress fees. This stack uses rclone to mount multiple R2 buckets as local FUSE filesystem mounts, providing POSIX-compatible access to cloud object storage. Buckets are separated by purpose: curriculum data, embeddings, Iceberg tables, and pipeline exports.

## Why This Matters for Kings' College Galway

R2 complements the self-hosted Garage S3 setup by providing cloud-resilient object storage for data that must survive local infrastructure failures. The zero-egress-fee model means the 124 GB HuggingFace model cache, the curriculum Parquet files, and the LanceDB vector indexes can be stored in R2 and accessed without bandwidth costs — critical when running extraction pipelines that read large datasets repeatedly. The FUSE mount makes R2 appear as a local directory, so any tool that reads files (Dagster, DuckDB, LanceDB, Python `open()`) works transparently without S3 SDK integration.

## Key Features

- **Zero egress fees** — Bandwidth is free; only storage and operations are billed
- **S3-compatible** — Works with any S3 SDK or tool
- **FUSE mount** — POSIX filesystem access via rclone mount
- **Multi-bucket** — Separate buckets for curriculum data, embeddings, Iceberg tables, and exports
- **VFS caching** — Configurable disk cache for frequently accessed files

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/r2
docker compose up -d
```

### Production (with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
```

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `R2_ACCESS_KEY_ID` | Yes | Cloudflare R2 access key | — |
| `R2_SECRET_ACCESS_KEY` | Yes | Cloudflare R2 secret key | — |
| `R2_ACCOUNT_ID` | Yes | Cloudflare account ID | — |
| `RCLONE_CONFIG_R2_TYPE` | No | Storage type | `s3` |
| `RCLONE_CONFIG_R2_PROVIDER` | No | Provider label | `Cloudflare` |
| `RCLONE_CONFIG_R2_ENDPOINT` | No | R2 endpoint URL | `https://<account>.r2.cloudflarestorage.com` |

## Access

- **Mounted filesystem**: `/data/curriculum`, `/data/embeddings`, `/data/iceberg`, `/data/exports`
- **R2 Dashboard**: `https://dash.cloudflare.com/<account>/r2`
- **Auth**: R2 API tokens with bucket-scoped permissions

## Upstream

- **R2 Documentation**: <https://developers.cloudflare.com/r2/>
- **rclone Documentation**: <https://rclone.org/s3/#cloudflare-r2>
- **Latest**: R2 now supports event notifications, lifecycle policies, and custom domains

## Screenshot

Headless infrastructure service. The Cloudflare dashboard at `dash.cloudflare.com` provides bucket management, object browsing, usage analytics (storage, class A/B operations), and API token generation. The rclone FUSE mount appears as a standard directory on the host filesystem.
