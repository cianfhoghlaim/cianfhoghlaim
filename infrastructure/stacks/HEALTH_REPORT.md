# Cianfhoghlaim Infrastructure Health Report — Live

> **This is the live health report.** The 3-session historical
> log (2026-06-12) — Komodo FerretDB swap, 76-stack
> destination migration, schema correction, frontend CSS
> fix, etc. — lives at
> [`infrastructure/archive/HEALTH_REPORT-2026-06-12.md`](../archive/HEALTH_REPORT-2026-06-12.md).
>
> **Last refreshed:** 2026-06-15 (the static report below is
> the most recent manual snapshot; the dynamic counterpart
> lives at
> [`infrastructure/audit/scripts/inventory-bunchloch.sh`](../audit/scripts/inventory-bunchloch.sh)
> and is run on demand).

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
