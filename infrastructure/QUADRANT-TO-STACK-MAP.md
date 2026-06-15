# Quadrant → Stack Map

A 1-page table that, for each of the 4 workspace-member
quadrants, lists which `infrastructure/stacks/*/` it depends
on, which ports those stacks expose, which Dagster
code-location they affect, and which `*.cianfhoghlaim.ie`
domains they touch.

This map was created as part of
`openspec/changes/audit-infrastructure-2026-06-15/`. The
static container inventory lives in
`infrastructure/stacks/HEALTH_REPORT.md`; the live
counterpart is produced by the audit scripts under
`infrastructure/audit/scripts/`.

## 1. Oideachais → lakehouse + LLM + observability + browser

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| lakehouse (Garage + Postgres + Lakekeeper + Lance NS) | `infrastructure/stacks/storage/lakehouse/` | 3900-3904, 5433, 8181, 9100, 8182 | `dagster_defs.definitions` (228 assets) | none (internal only) |
| LiteLLM | `infrastructure/stacks/engineering/litellm/` | 4000, 9090 | (none — pure proxy) | none |
| llama-swap | `infrastructure/stacks/engineering/llama-swap/` | 8080 | (none — model router) | none |
| Langfuse | `infrastructure/stacks/engineering/langfuse/` | 3001, 3030, 9091, 5432, 6379, 8123 | (none — observability) | none |
| Cognee | `infrastructure/stacks/machine_learning/cognee/` | 8100, 5432 | (none — knowledge graph) | none |
| LanceDB | `infrastructure/stacks/machine_learning/lancedb/` | 8081 | (none — vector store) | none |
| browser (browser-grid + browser-litellm + browser-stagehand-proxy) | `infrastructure/stacks/engineering/browser/` | 9222-9223, 4001, 4005 | `oideachais.dlt_sources.{education,medicine,law}.*` (uses Stagehand for live scraping) | none |
| oRPC server + FastAPI (oideachais-api) | runs in `cianfhoghlaim-oideachais-api` (bunchloch) | 8000 | (none — API layer) | `api.oideachais.cianfhoghlaim.ie` (Pangolin) |
| TanStack Start (oideachais-frontend) | runs in `cianfhoghlaim-oideachais-frontend` (bunchloch) | 3000 | (none — SPA) | `oideachais.cianfhoghlaim.ie` (Pangolin) |
| Dagster (oideachais-dagster) | runs in `cianfhoghlaim-oideachais-dagster` (bunchloch) | 3335 | `dagster_defs.definitions` (228 assets) | `dagster.oideachais.cianfhoghlaim.ie` (Pangolin, VPN-only) |

## 2. Tuatha → crypteolas + fibo_generation + asset_generation

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| (none live — pre-existing sruth import bug blocks the code-location) | — | — | `tuatha/dagster_assets/definitions.py` (broken — see `tuatha/README.md` §Known issues) | — |
| Rust crates (services, solana, stdb-modules, wgpu) | `tuatha/crates/` | n/a (compiled binaries) | n/a | n/a |
| Babylon.js / MMO client | `tuatha/game/` | n/a (build target) | n/a | n/a |

## 3. Croilar → 5 user-named stacks + croilar-postgres

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| croilar-convex (Convex backend + dashboard) | `infrastructure/stacks/engineering/croilar-convex/` | 3210-3211, 6791 | (none — BaaS) | none (internal Convex) |
| croilar-dagster | `infrastructure/stacks/engineering/croilar-dagster/` | per Komodo | `croilar/definitions.py` (broken — see `croilar/README.md` §Known issues) | none |
| croilar-hono-api (Hono + BAML on Bun) | `infrastructure/stacks/engineering/croilar-hono-api/` | per Komodo | (none — API) | none |
| croilar-marimo | `infrastructure/stacks/engineering/croilar-marimo/` | per Komodo | (none — notebooks) | none |
| croilar-web (TanStack Start + Convex auth) | `infrastructure/stacks/engineering/croilar-web/` | per Komodo | (none — SPA) | per Komodo |
| croilar-postgres | `infrastructure/stacks/storage/croilar-postgres/` | 5432-5434 | (none — DB) | none |

## 4. Meaisínfhoghlaim → komodo-meaisinfhoghlaim-bunchloch + LLM gateway

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| meaisínfhoghlaim-bunchloch (orchestrated via Komodo) | `infrastructure/komodo/stacks/meaisínfhoghlaim-bunchloch.toml` | per Komodo | `meaisinfhoghlaim/dagster_defs/__init__.py` (4 heartbeat assets) | none |
| LLM gateway (shared with oideachais) | `infrastructure/stacks/engineering/litellm/` | 4000 | (none — proxy) | none |
| llama-swap (shared) | `infrastructure/stacks/engineering/llama-swap/` | 8080 | (none — router) | none |

## 5. Cross-quadrant infrastructure (the 9 user-named deploy targets)

| Stack | Path | Host | `*.cianfhoghlaim.ie` domain | Runbook |
|:--|:--|:--|:--|:--|
| infisical | `infrastructure/infisical/` | arm1-oci | `infisical.cianfhoghlaim.ie` | `infrastructure/deploy-runbooks/infisical.md` |
| komodo | `infrastructure/komodo/` | arm1-oci + bunchloch | `komodo.cianfhoghlaim.ie` | `infrastructure/deploy-runbooks/komodo.md` |
| pangolin | `infrastructure/pangolin/` | arm1-oci | (Pangolin routes all `*.cianfhoghlaim.ie` domains) | `infrastructure/deploy-runbooks/pangolin.md` |
| ansible | `infrastructure/ansible/` | n/a (provisioning automation) | n/a | `infrastructure/deploy-runbooks/ansible.md` |
| cal-diy | `infrastructure/stacks/tools/cal-diy/` | arm1-oci | `calcom.cianfhoghlaim.ie` | `infrastructure/deploy-runbooks/cal-diy.md` |
| vikunja | `infrastructure/stacks/tools/vikunja/` | (intended: bunchloch) | (per Komodo) | `infrastructure/deploy-runbooks/vikunja.md` |
| n8n | `infrastructure/stacks/engineering/n8n/` | (intended: bunchloch) | (per Komodo) | `infrastructure/deploy-runbooks/n8n.md` |
| changedetection | `infrastructure/stacks/tools/changedetection/` | (intended: bunchloch) | (per Komodo) | `infrastructure/deploy-runbooks/changedetection.md` |
| bytebase | `infrastructure/stacks/engineering/bytebase/` | (intended: arm1-oci) | (per Komodo) | `infrastructure/deploy-runbooks/bytebase.md` |

## 6. Domain → Host routing summary

```
bunchloch (35 containers)
├── data plane
│   ├── lakehouse (Garage + Postgres + Lakekeeper + Lance NS)
│   ├── Langfuse + Clickhouse + Redis + Postgres + Minio
│   ├── Cognee + cognee-postgres
│   ├── LanceDB + Langfuse worker
│   ├── oideachais (frontend + api + dagster)
│   ├── oRPC server (in oideachais-api)
│   └── newt (Pangolin client → arm1-oci)
├── control plane
│   ├── komodo-core (the MacBook is the Core)
│   ├── komodo-periphery-macbook
│   └── komodo-postgres + komodo-ferretdb
├── LLM
│   ├── LiteLLM + litellm-db + litellm-prometheus
│   ├── llama-swap
│   └── browser-litellm + browser-stagehand-proxy + browser-grid
└── misc
    ├── Convex backend + dashboard
    ├── croilar-postgres
    ├── aleyum-dragonfly + aleyum-postgres
    ├── dagger-engine
    └── alanode-agent-runtime (if present)

arm1-oci (~10 containers)
├── control plane
│   ├── Pangolin + Gerbil + Traefik
│   ├── Pocket ID + TinyAuth + Middleware Manager + CrowdSec
│   ├── komodo-core (the orchestrator UI lives here)
│   ├── komodo-periphery-oci
│   ├── Infisical + infisical-postgres
│   └── Dozzle + Beszel + Qdrant
├── user-facing
│   ├── calcom-web + calcom-db + calcom-redis (cal-diy)
│   └── garage (arm1 copy of the S3 cluster)
└── observability
    └── (beszel scrapes everything; no separate exporter)
```

## 7. How to update this map

When you add a new stack, append a row to the relevant
quadrant section above. When you migrate a stack between
hosts (e.g. move cal-diy from `arm1-oci` to `bunchloch`),
update the row in the relevant quadrant section AND the
`6. Cross-quadrant infrastructure` table. When you wire a
new Dagster code-location, register it in the root
`dg.toml` AND list it in the relevant quadrant section.
