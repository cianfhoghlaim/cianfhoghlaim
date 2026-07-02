# Cianfhoghlaim Infrastructure Health Report — Live

> **This is the live health report.** The 3-session historical
> log (2026-06-12) — Komodo FerretDB swap, 76-stack
> destination migration, schema correction, frontend CSS
> fix, etc. — lives at
> [`infrastructure/archive/HEALTH_REPORT-2026-06-12.md`](../archive/HEALTH_REPORT-2026-06-12.md).
>
> **Last refreshed:** 2026-07-02 (Session 5 cold-boot of Wave 1;
> 11 containers running, 2 lakehouse services disabled for dev).
> The dynamic counterpart lives at
> [`infrastructure/audit/scripts/inventory-bunchloch.sh`](../audit/scripts/inventory-bunchloch.sh)
> and is run on demand.

## Session 5 — 2026-07-02 (Wave 1 cold-boot, dev mode)

This session's output is the openspec change sequence
[`2026-07-02-bunchloch-stack-bootstrap`](/Users/cianmacandeisigh/dev/kings_college_galway/openspec/changes/2026-07-02-bunchloch-stack-bootstrap/)
+ the 3 sibling changes
(`2026-07-02-add-lancedb-and-logfire-stacks`,
`2026-07-02-add-marimo-stack`,
`2026-07-02-add-agent-surface-stacks`).
The 4 changes produce 4 openspec change dirs + 9 compose
edits + 1 new runbook.

**Wave 1 bring-up status: 4 of 4 stacks UP, 11 containers
running.** All in dev mode (no Locket, no live Infisical
round-trip); uses `compose.dev.yaml` overlays + `.env.dev`
files per stack.

### Container inventory at 2026-07-02 (live, dev mode)

#### `bunchloch` (MacBook M4 — `Cians-MacBook-Pro.local`) — 11 running containers

| Container | Image | Port → Host | Health | Notes |
|:--|:--|:--|:--|:--|
| `dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly:latest` | `0.0.0.0:6379` → `6379` | healthy | in-memory cache (replaces Redis for the cache layer) |
| `falkordb` | `falkordb/falkordb:latest` | `0.0.0.0:6380` → `6379`, `0.0.0.0:3001` → `3000` | healthy | graph DB (port-shifted to :6380 to avoid dragonfly :6379 conflict); GRAPH.QUERY verified |
| `falkordb-locket-dev` | `alpine:3.20` | — | healthy | no-op Locket sidecar (sleep infinity + always-healthy) |
| `lancedb` | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | `0.0.0.0:8081` → `8080` | healthy | LanceDB table viewer (UI) |
| `lakehouse-postgres` | `postgres:16-alpine` | `0.0.0.0:5433` → `5432` | healthy | centralised PG (12 databases) |
| `lakehouse-clickhouse` | `clickhouse/clickhouse-server:24.3` | `127.0.0.1:8123` → `8123`, `127.0.0.1:9000` → `9000` | healthy | columnar engine |
| `lakehouse-redis` | `redis:7-alpine` | `127.0.0.1:6390` → `6379` | healthy | queue (port-shifted to :6390 to avoid dragonfly :6379) |
| `lakehouse-garage` | `dxflrs/garage:v1.0.1` | `0.0.0.0:3900-3904` → `3900-3904` | healthy | S3-compatible storage |
| `lakehouse-lakekeeper` | `quay.io/lakekeeper/catalog:latest` | `0.0.0.0:8181` → `8181`, `0.0.0.0:9100` → `9000` | healthy | Iceberg REST catalog |
| `lakehouse-lance-namespace` | `lakehouse-lance-namespace:latest` (built from `./lance-sidecar/Dockerfile`) | `0.0.0.0:8182` → `8182` | healthy | Lance adapter sidecar (local build) |
| `lakehouse-lancedb-viewer` | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | `0.0.0.0:8082` → `8080` | healthy | in-stack LanceDB viewer (port-shifted to :8082) |
| `lakehouse-locket-dev` | `alpine:3.20` | — | healthy | no-op Locket sidecar for the lakehouse stack |

### Lakehouse services deliberately disabled in dev mode

| Service | Reason | How to re-enable |
|:--|:--|:--|
| `lakehouse-olake` | `ghcr.io/olake-io/olake:0.1.5` is private (401 on GHCR); source build (`github.com/datazip-inc/olake@v0.1.5`) requires Go 1.25.11 + Java 17 + Maven + a pre-built `olake-iceberg-java-writer-0.0.1-SNAPSHOT.jar` (none available in this env). Disabled via `profiles: ["never-active"]` in the dev overlay. | Either (a) add credentials for `ghcr.io/olake-io/olake`, or (b) build the image locally and tag it. |
| `lakehouse-nimtable` | Requires a `config.yaml` file that the base compose doesn't mount; crashes on startup with `FileNotFoundException: config.yaml`. Disabled the same way as olake. | Mount a valid `config.yaml` into `/var/lib/nimtable/`. |

### Wave 1 bring-up procedure

```bash
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar

# Dragonfly + lancedb (no Locket needed)
./scripts/stack.sh dragonfly up -d
./scripts/stack.sh lancedb up -d

# Falkordb (needs --env-file + sidecar + dev overlay for dev mode)
docker compose \
  --env-file stacks/falkordb/.env.dev \
  -f stacks/falkordb/compose.yaml \
  -f stacks/falkordb/sidecar.yaml \
  -f stacks/falkordb/compose.dev.yaml \
  up -d

# Lakehouse (needs --env-file + sidecar + dev overlay; 8 services UP, 2 disabled)
docker compose \
  --env-file stacks/lakehouse/.env.dev \
  -f stacks/lakehouse/compose.yaml \
  -f stacks/lakehouse/sidecar.yaml \
  -f stacks/lakehouse/compose.dev.yaml \
  up -d
```

### Known issues discovered + fixed in this session (10 fixes)

1. **mlflow port** was actually fine (false positive from earlier diagnostic)
2. **cognee** image: `cognee/cognee:latest` → `cognee/cognee:1.2.2`
3. **olmocr** image: `allenai/olmocr:latest` → `alleninstituteforai/olmocr:0.4.27` (also fixed wrong registry path; `allenai/olmocr` doesn't exist on Docker Hub)
4. **paddleocr** image: `paddlecloud/paddleocr:latest` → `paddlecloud/paddleocr:2.6-cpu-latest`
5. **docling-serve** image: `ghcr.io/ds4sd/docling-serve:latest` → `v0.4.0`
6. **lancedb/rclone** image: `rclone/rclone:latest` → `rclone/rclone:v1.74-stable`
7. **dragonfly** compose: split semicolon-separated healthcheck into 4 proper YAML lines
8. **marimo** compose: fixed wrong registry (`marimo/marimo` → `ghcr.io/marimo-team/marimo:0.11.19`), v3 volume path, v4 notebook path
9. **hermes / openclaw / openchamber**: removed `@sha256:0000...` placeholder digests; fixed openclaw tag (`1.0.0` doesn't exist → `2026.2.6`)
10. **lakehouse compose**: nimtable `0.1.6` → `:latest`; `REDIS_PORT` 6379→6390; `LANCEDB_VIEWER_PORT` 8081→8082; lakekeeper-migrate `networks:` block added (was on default network, couldn't reach postgres)

### Deferred for separate changes (this session's stop list)

- **dots-ocr** (compose references `dots-ocr/dots-ocr:latest` which doesn't exist on Docker Hub; upstream `rednote-hilab/dots.ocr` is source-only)
- **browser** stack (missing 5 of 6 GOLD_STANDARD files)
- **Wave 2 (12 stacks) + Wave 3 (4 stacks) + Wave 4 (3 stacks)** — all require their own Locket/Infisical overlays or Locket setup
- **mailcow-dockerized, mlx-omni, ollama, letta** — separate future changes
- **Komodo IaC registration** — blocked on the in-flight `2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops` change

### Related openspec changes in this session

- `2026-07-02-bunchloch-stack-bootstrap` (main repo, commit 70e3110a7) — 19 stacks, 4 waves
- `2026-07-02-add-lancedb-and-logfire-stacks` (main repo, commit 70e3110a7) — 2 stacks + 5 image pins
- `2026-07-02-add-marimo-stack` (main repo, commit 70e3110a7) — 1 stack + 3 fixes
- `2026-07-02-add-agent-surface-stacks` (main repo, commit 70e3110a7) — 3 stacks + new capability spec
- `516e1054a` (bonneagar) — 9 compose edits + 1 runbook
- `a14f52ca8` (bonneagar) — dragonfly YAML fix
- `c008e40d7` (bonneagar) — falkordb + lakehouse dev overlays
- `c8478d54a` (bonneagar) — lakehouse 4 compose fixes

## Session 4 — 2026-06-15 (static audit + deferred deploy plan)

This session's output is the openspec change
[`audit-infrastructure-2026-06-15`](../../../openspec/changes/archive/2026-06-15-audit-infrastructure-2026-06-15/).
The change produces:

- 4 live-state audit scripts under `infrastructure/audit/scripts/`
  (deferred content — committed, not yet run)
- Status + Known-issues sections in each quadrant README
  (`oideachais/`, `tuatha/`, `croilar/`, `meaisinfhoghlaim/`)
- 1 new playbook at `infrastructure/DEPLOYMENT-STRATEGY.md`
- 1 new map at `infrastructure/QUADRANT-TO-STACK-MAP.md`
- 9 runbooks at `infrastructure/deploy-runbooks/<name>.md`
  (one per user-named deploy target)

The **actual deploy** of the 9 user-named targets is **deferred**
to a follow-up change that consumes the runbooks.

### Container inventory at 2026-06-15 (per `infrastructure/archive/HEALTH_REPORT-2026-06-12.md`)

#### `bunchloch` (MacBook M4) — 35 running containers, 47h uptime

| Container | Image | Port → Host | Health |
|:--|:--|:--|:--|
| `cianfhoghlaim-oideachais-frontend` | `oideachais-dev-frontend` (TanStack Start + Vite) | 3000 → 3000 | healthy |
| `cianfhoghlaim-oideachais-api` | `oideachais-dev-api` (FastAPI AG-UI) | 8000 → 8000 | healthy |
| `cianfhoghlaim-oideachais-dagster` | `oideachais-dev-dagster` | 3000 → 3335 | healthy (code location `dagster_defs.definitions` loads 228 assets post-Phase-0.1) |
| `cianfhoghlaim-cognee` | `cognee 1.1.2-local` | 8000 → 8100 | healthy (was unhealthy in Session 1, recovered) |
| `lancedb` | `lancedb/lancedb` | 8080 → 8081 | healthy |
| `langfuse-web` | `langfuse/langfuse` | 3000 → 3001 | healthy |
| `langfuse-worker` | `langfuse/langfuse-worker` | 3030 | healthy (internal) |
| `langfuse-minio` | `minio` | 9000 → 9091 | healthy |
| `langfuse-postgres` | `postgres` | 5432 | healthy |
| `langfuse-clickhouse` | `clickhouse` | 8123, 9000 | healthy |
| `langfuse-redis` | `redis` | 6379 | healthy |
| `litellm` | `ghcr.io/berriai/litellm` | 4000 → 4000 | healthy |
| `litellm-db` | `postgres` | 5432 | healthy |
| `litellm-prometheus` | `prom/prometheus` | 9090 → 9090 | healthy |
| `llama-swap` | `ghcr.io/mostlygeek/llama-swap` | 8080 → 8080 | healthy |
| `convex-backend` | `ghcr.io/get-convex/convex-backend` | 3210-3211 → 3210-3211 | healthy |
| `convex-dashboard` | `ghcr.io/get-convex/convex-dashboard` | 6791 → 6791 | healthy |
| `lakehouse-garage` | `dxflrs/garage` | 3900-3904 → 3900-3904 | healthy |
| `lakehouse-postgres` | `postgres:16` | 5432 → 5433 | healthy |
| `lakehouse-lakekeeper` | `ghcr.io/lakekeeper/lakekeeper` | 9000 → 8181, 9100 | healthy |
| `lakehouse-lance-namespace` | custom | 8182 → 8182 | healthy |
| `komodo-core` | `ghcr.io/moghtech/komodo-core:2` | 9120 → 9120 | healthy |
| `komodo-periphery` | `ghcr.io/moghtech/komodo-periphery:2-dev` | 8120 | healthy |
| `komodo-postgres` | `ghcr.io/ferretdb/postgres-documentdb:17` | 5432 | healthy |
| `komodo-ferretdb` | `ghcr.io/ferretdb/ferretdb:2` | 27017 | healthy |
| `komodo-postgres-init` | one-shot | — | exited 0 |
| `browser-grid` | `browserless/chrome` | 9222-9223 → 9222-9223 | healthy |
| `browser-litellm` | `ghcr.io/berriai/litellm` | 4000 → 4001 | healthy |
| `browser-stagehand-proxy` | `ghcr.io/browserbase/stagehand` | 4005 → 4005 | healthy |
| `aleyum-dragonfly` | `docker.dragonflydb.io/dragonflydb/dragonfly` | 6379 → 6381 | healthy |
| `aleyum-postgres` | `postgres` | 5432 | healthy |
| `croilar-postgres` | `postgres` | 5432 → 5434 | healthy |
| `dagger-engine-v0.20.8` | `daggerdev/dagger` | — | healthy |
| `newt-bunchloch` | `fosrl/newt` | 2112 (WireGuard) | healthy (periodic token-endpoint EOF; recovers) |

#### `arm1-oci` (Oracle Cloud London) — ~10 containers, control plane

| Container | Image | Port | Health |
|:--|:--|:--|:--|
| `pangolin` | `fosrl/pangolin` | 80, 443, 9443 | healthy |
| `gerbil` | `fosrl/gerbil` | 51820/udp | healthy |
| `traefik` | `traefik:v3` | 80, 443 | healthy |
| `pocket-id` | `pocket-id/pocket-id` | 1411 | healthy |
| `tinyauth` | `steveiliop56/tinyauth` | 10000 | healthy |
| `middleware-manager` | `pangolin/middleware-manager` | 3456 | healthy |
| `crowdsec` | `crowdsecurity/crowdsec` | 8080, 7422 | healthy |
| `komodo-core` | shared with `bunchloch` if `komodo.toml` configures it that way; otherwise a separate instance on arm1 | per Komodo | see Session 1 fix |
| `infisical-backend` | `infisical/infisical` | 8080 | healthy |
| `infisical-postgres` | `postgres` | 5432 | healthy |
| `calcom-web` | `ghcr.io/cianfhoghlaim/cal-diy:local` | 3000 | healthy (post healthcheck fix) |
| `calcom-db` | `postgres` | 5432 | healthy |
| `calcom-redis` | `redis` | 6379 | healthy |
| `garage` (arm1) | `dxflrs/garage` | 3900-3902 | healthy |
| `dozzle` | `amir20/dozzle` | 8080 | healthy |
| `beszel` | `henrygd/beszel` | 8090 | healthy |
| `qdrant` | `qdrant/qdrant` | 6333, 6334 | healthy |

### Known blockers (deferred, from Session 3 of the historical log)

| # | Blocker | First surfaced | Fix |
|--:|:--|:--|:--|
| 1 | Newt 1.12.5 + Pangolin 1.18.4 version mismatch | Session 3 | Upgrade Pangolin to ≥1.13.0 OR pin newt to 1.11.x |
| 2 | 3 manually-created private resources (`komodo`, `cal-diy`, `infisical`) override blueprints | Session 3 | Delete manually in Pangolin UI; blueprint reapplies |
| 3 | `PANGOLIN_API_KEY` + `PANGOLIN_API_KEY_0` expired (return 401) | Session 3 | Mint fresh token in Pangolin UI; update `.env` |
| 4 | `komodo-locket` production credentials missing | Session 1 (still open) | Provision Infisical machine identity with `/komodo` access |

## Cross-references

- Historical 3-session log: [`../archive/HEALTH_REPORT-2026-06-12.md`](../archive/HEALTH_REPORT-2026-06-12.md)
- Live audit scripts: [`../audit/scripts/`](../audit/scripts/)
- Deployment playbook: [`../DEPLOYMENT-STRATEGY.md`](../DEPLOYMENT-STRATEGY.md)
- 6-file standard: [`../GOLD_STANDARD.md`](../GOLD_STANDARD.md)
- 9 runbooks: [`../deploy-runbooks/`](../deploy-runbooks/)
- 4 quadrant READMEs: [`../../oideachais/README.md`](../../oideachais/README.md), [`../../tuatha/README.md`](../../tuatha/README.md), [`../../croilar/README.md`](../../croilar/README.md), [`../../meaisinfhoghlaim/README.md`](../../meaisinfhoghlaim/README.md)

## How to refresh this report

```bash
# Snapshot the local host
bash infrastructure/audit/scripts/inventory-bunchloch.sh

# Snapshot arm1-oci (requires passwordless SSH)
bash infrastructure/audit/scripts/inventory-arm1-oci.sh

# Diff against the filesystem composes
bash infrastructure/audit/scripts/diff-against-composes.sh

# Probe the public Pangolin URLs
bash infrastructure/audit/scripts/probe-public-urls.sh
```

Update the table above with the new container counts and
health states. Commit the JSON snapshots and the updated
report together.
