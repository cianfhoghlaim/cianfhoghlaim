# Dragonfly

## Overview
Dragonfly is a modern, drop-in Redis replacement that achieves 25x the throughput of Redis on the same hardware while maintaining full API compatibility. Created by DragonflyDB and distributed as `docker.dragonflydb.io/dragonflydb/dragonfly:latest`, it uses a multi-threaded, shared-nothing architecture optimized for modern multi-core CPUs. This stack runs on port 6379 with 8GB maxmemory in cache mode, backed by 10GB memory and 4 CPU cores.

## Why This Matters for Kings' College Galway
Dragonfly provides the high-throughput caching and message queue layer for the Celtic education platform's real-time services. When the Túatha educational MMO needs sub-millisecond leaderboard queries, when Convex caches real-time study session state, or when the Dagster daemon queues pipeline execution jobs, Dragonfly handles it at memory speed with Redis protocol compatibility. Its cache mode (LRU eviction) automatically manages the 8GB working set without manual TTL management — ideal for caching frequently-accessed curriculum data, student progress state, and AI-generated flashcard caches. The 10GB memory limit ensures it never starves the MacBook M4 of unified memory for MLX model inference.

## Key Features
- Drop-in Redis replacement with 25x throughput improvement
- Multi-threaded, shared-nothing architecture for modern CPUs
- Cache mode with LRU eviction for automatic memory management
- Full Redis protocol compatibility (RESP2/RESP3)
- Password-protected with Infisical-backed secret injection

## Deployment

### Docker Compose (Local Development)
```bash
cd infrastructure/stacks/engineering/dragonfly
docker compose up -d
```

### Docker Compose (Production with Locket Secret Injection)
```bash
cd infrastructure/stacks/engineering/dragonfly
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)
This stack is deployed via Komodo on the MacBook M4 workload host (bunchloch). Komodo syncs from the Forgejo repository and applies `compose.yaml` + `sidecar.yaml`. No `.env` file is needed — Locket resolves all secrets from the Infisical `dev-baile` vault at runtime.

## Environment Variables
| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `DRAGONFLY_PASSWORD` | No | Password for Redis AUTH | `devpassword` |

## Access
- **URL**: `https://dragonfly.cianfhoghlaim.ie` (TCP, Pangolin Member role required)
- **Internal port**: 6379 (TCP)
- **Auth**: Password authentication (`DRAGONFLY_PASSWORD`)

## Health Check
```bash
docker ps --filter name=dragonfly --format "table {{.Names}}\t{{.Status}}"
```

## Upstream
- **Repository**: https://github.com/dragonflydb/dragonfly
- **Documentation**: https://www.dragonflydb.io/docs
- **Latest release**: Pulls `docker.dragonflydb.io/dragonflydb/dragonfly:latest` — modern Redis-compatible in-memory datastore.
