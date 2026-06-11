---
title: 'Cloudflare R2 — Zero-Egress Object Storage SDK'
domain: 'infrastructure'
status: 'stable'
description: 'Cloudflare R2 is an S3-compatible object storage service with zero egress fees. The SDK provides Python and TypeScript libraries for programmatic access — uploading, downloading, listing, and managing objects in R2 buckets. Unlike AWS S3, R2 charges only for storage and operation'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/cloudflare-r2.md
ccc_query_hints:
  - cloudflare r2 — zero-egress object stora
---

# Cloudflare R2 — Zero-Egress Object Storage SDK

## Overview

Cloudflare R2 is an S3-compatible object storage service with zero egress fees. The SDK provides Python and TypeScript libraries for programmatic access — uploading, downloading, listing, and managing objects in R2 buckets. Unlike AWS S3, R2 charges only for storage and operations, not bandwidth.

## Why This Matters for Kings' College Galway

The project stores curriculum datasets, HuggingFace model weights, and LanceDB vector indexes in R2 as a cloud-resilient complement to self-hosted Garage S3. The zero-egress model means the 124 GB HuggingFace cache and the 50+ GB of curriculum Parquet files can be accessed from any location without bandwidth costs. R2 serves as the off-site backup target for Backrest (Restic snapshots) and the distribution layer for sharing curriculum datasets with collaborators.

## Key Features

- **Zero egress fees** — Bandwidth is free; pay only for storage and operations
- **S3-compatible API** — Works with boto3, s3fs, rclone, and any S3 SDK
- **Global replication** — Data replicated across Cloudflare's network
- **Lifecycle policies** — Auto-expire old snapshots and temporary data
- **Custom domains** — Serve bucket content from `data.cianfhoghlaim.ie`

## Installation

```bash
uv add boto3  # Standard S3 SDK works with R2
```

## Integration with Our Stack

R2 buckets are mounted as FUSE filesystems via the `infrastructure/stacks/infrastructure/r2/` compose stack. The Dagster pipeline writes to R2 via S3 API, DuckDB queries R2 via `httpfs`, and Backrest backs up Docker volumes to R2 via Restic.

## Upstream

- **Documentation**: <https://developers.cloudflare.com/r2/>
- **SDK Reference**: <https://developers.cloudflare.com/r2/api/s3/>
- **Latest**: Event notifications, S3 Object Lambda, lifecycle policies, custom domains

## Screenshot

The Cloudflare R2 dashboard at `dash.cloudflare.com` shows bucket list, object browser, usage metrics (storage, class A/B operations), and API token management. The S3-compatible API is headless — all operations are programmatic via boto3 or AWS CLI with R2 endpoints.
