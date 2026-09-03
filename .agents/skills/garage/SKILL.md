---
name: garage
description: |
  Self-hosted, S3-compatible object storage by Deuxfleurs (Garage v2.3.0+,
  Rust, distroless Docker ~27 MB). Use when designing cluster layouts,
  wiring the v2 admin API /v2/ contract, single-node init via --single-node,
  multi-zone geographic replication, or migrating from v1.x (which had
  replication_mode removed in v2.0.0 2025-06-14).
when_to_load:
  - "Garage", "S3", "object storage", or "Deuxfleurs" mentioned
  - Touching `bonneagar/stacks/lakehouse/` (Garage v2.3.0 runs embedded here)
  - Wiring Dagster/DLT/DuckLake to S3 endpoints
  - Adding a Firecrawl monitor for Garage releases
---

# Garage S3 (v2.3.0+, April 2026)

## TL;DR
- **Upstream latest**: v2.3.0 (2026-04-16). Cianfhoghlaim pinned: v1.0.1 — 18 months stale.
- **Critical drift**: `bonneagar/stacks/lakehouse/garage.toml` uses `replication_mode = "1"` (removed v2.0.0). Will fail to start on v2.x.
- **The single-node flag** (v2.3.0) obsoletes the 90-line `garage-init` service in `bonneagar/stacks/lakehouse/compose.yaml:71-160`.
- **Garage is no longer a standalone stack**: the legacy `infrastructure/stacks/garage/` was retired in the 2026-08-01 trilogy; Garage v2.3.0 runs as an embedded service inside `bonneagar/stacks/lakehouse/` (port 3900-3904).

## Verified-live v2.3.0 single-node init inside the lakehouse stack (REPLACES garage-init)
```bash
docker run -d --name garage-container \
  -p 3900:3900 -p 3901:3901 -p 3902:3902 -p 3903:3903 \
  -v $(pwd)/garage.toml:/etc/garage.toml \
  -e GARAGE_DEFAULT_ACCESS_KEY -e GARAGE_DEFAULT_SECRET_KEY -e GARAGE_DEFAULT_BUCKET \
  dxflrs/garage:v2.3.0 \
  /garage server --single-node --default-bucket
```

## Verified-live 3-node HA garage.toml (`/documentation/cookbook/real-world/`)
```toml
metadata_dir = "/var/lib/garage/meta"
data_dir = "/var/lib/garage/data"
db_engine = "lmdb"
metadata_auto_snapshot_interval = "6h"
replication_factor = 3        # NOT replication_mode (removed v2.0.0)
compression_level = 2
rpc_bind_addr = "[::]:3901"
rpc_public_addr = "<ip>:3901"
rpc_secret = "<32-byte hex: openssl rand -hex 32>"
[s3_api]
s3_region = "garage"
api_bind_addr = "[::]:3900"
root_domain = ".s3.lakehouse.cianfhoghlaim.ie"
[s3_web]
bind_addr = "[::]:3902"
root_domain = ".web.garage"
index = "index.html"
```

## v1 → v2 migration cheat sheet
| v1.x | v2.x |
|:--|:--|
| `replication_mode = "1"` | `replication_factor = 1` + `consistency_mode = "degraded"` |
| `replication_mode = "3"` | `replication_factor = 3` (omit `consistency_mode` for default = "strict") |
| `POST /v1/layout` | `POST /v2/layout` |
| `GET /v1/health` (`storage_nodes_ok`) | `GET /v2/health` (`storage_nodes_up` — renamed v2.1.0) |
| `admin_token = "..."` | Multiple tokens via `garage admin token create` |
| `garage init` (manual bash) | `garage server --single-node --default-access-key --default-bucket` |

## Ports
3900 S3 API, 3901 RPC, 3902 K2V, 3903 web, 3904 admin.

## Source
Docs: https://garagehq.deuxfleurs.fr/documentation/quick-start/
Cookbook: https://garagehq.deuxfleurs.fr/documentation/cookbook/real-world/
Releases: https://git.deuxfleurs.fr/Deuxfleurs/garage/releases
Docker: https://hub.docker.com/r/dxflrs/garage/tags
Wave 1: openspec/research/2026-06-28-browserbase-program-2/agent-12-garage.md
Wave 2 (this): openspec/research/2026-06-28-browserbase-program-2/live-docs/82-live-garage-23.md

## Cross-references
- `.agents/skills/change-detection/SKILL.md` — Firecrawl monitor on /releases
- `.agents/skills/secrets-management/SKILL.md` — Locket for rpc_secret/admin_token
- `openspec/specs/infrastructure-stacks/spec.md:288,815`
- `openspec/changes/2026-06-28-browserbase-phase-1b-decisions/specs/cianfhoghlaim-storage/`
