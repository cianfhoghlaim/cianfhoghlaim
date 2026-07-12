# Quadrant → Stack Map

A 1-page table that, for each of the 4 workspace-member
quadrants, lists which `bonneagar/stacks/*/` it depends
on, which ports those stacks expose, which Dagster
code-location they affect, and which `*.cianfhoghlaim.ie`
domains they touch.

This map was created as part of
`openspec/changes/audit-infrastructure-2026-06-15/`. The
static container inventory lives in
`bonneagar/stacks/HEALTH_REPORT.md`; the live
counterpart is produced by the audit scripts under
`bonneagar/audit/scripts/`.

## 1. Oideachais → lakehouse + LLM + observability + browser

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| lakehouse (Garage + Postgres + Lakekeeper + Lance NS) | `bonneagar/stacks/lakehouse/` | 3900-3904, 5433, 8181, 9100, 8182 | `dagster_defs.definitions` (228 assets) | none (internal only) |
| LiteLLM | `bonneagar/stacks/litellm/` | 4000, 9090 | (none — pure proxy) | none |
| llama-swap | `bonneagar/stacks/llama-swap/` | 8080 | (none — model router) | none |
| Langfuse | `bonneagar/stacks/langfuse/` | 3001, 3030, 9091, 5432, 6379, 8123 | (none — observability) | none |
| Cognee | `bonneagar/stacks/cognee/` | 8100, 5432 | (none — knowledge graph) | none |
| LanceDB | `bonneagar/stacks/lancedb/` | 8081 | (none — vector store) | none |
| browser (browser-grid + browser-litellm + browser-stagehand-proxy) | `bonneagar/stacks/browser/` | 9222-9223, 4001, 4005 | `oideachais.dlt_sources.{education,medicine,law}.*` (uses Stagehand for live scraping) | none |
| oRPC server + FastAPI (oideachais-api) | runs in `cianfhoghlaim-oideachais-api` (bunchloch) | 8000 | (none — API layer) | `api.oideachais.cianfhoghlaim.ie` (Pangolin) |
| TanStack Start (oideachais-frontend) | runs in `cianfhoghlaim-oideachais-frontend` (bunchloch) | 3080 | (none — SPA) | `oideachais.cianfhoghlaim.ie` (Pangolin) |
| Dagster (oideachais-dagster) | runs in `cianfhoghlaim-oideachais-dagster` (bunchloch) | 3335 | `dagster_defs.definitions` (280+ assets after C4.1) | `dagster.oideachais.cianfhoghlaim.ie` (Pangolin, VPN-only) |
| Agno AgentOS (oideachais-agent-os) | runs in `cianfhoghlaim-oideachais-agent-os` (bunchloch) | 7777 | `oideachais/agent_os/` (Agno agents) | `agent.os.cianfhoghlaim.ie` (Pangolin, VPN-only) |
| Google ADK (oideachais-adk-agents) | runs in `cianfhoghlaim-oideachais-adk-agents` (bunchloch) | 7778 | `oideachais/agents/adk/` (12 ADK agent files) | `adk.cianfhoghlaim.ie` (Pangolin, VPN-only) |

## 2. Tuatha → crypteolas + fibo_generation + asset_generation

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| (none live — pre-existing sruth import bug blocks the code-location) | — | — | (post-v4: lives at `cianfhoghlaim/dagster/`) | — |
| Rust crates (services, solana, stdb-modules, wgpu) | `tuatha/crates/` | n/a (compiled binaries) | n/a | n/a |
| Babylon.js / MMO client | `tuatha/game/` | n/a (build target) | n/a | n/a |

## 3. Croilar → 5 user-named stacks + croilar-postgres

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| croilar-convex (Convex backend + dashboard) | `bonneagar/stacks/croilar-convex/` | 3210-3211, 6791 | (none — BaaS) | none (internal Convex) |
| croilar-dagster | `bonneagar/stacks/croilar-dagster/` | per Komodo | `croilar/definitions.py` (broken — see `croilar/README.md` §Known issues) | none |
| croilar-hono-api (Hono + BAML on Bun) | `bonneagar/stacks/croilar-hono-api/` | per Komodo | (none — API) | none |
| croilar-marimo | `bonneagar/stacks/croilar-marimo/` | per Komodo | (none — notebooks) | none |
| croilar-web (TanStack Start + Convex auth) | `bonneagar/stacks/croilar-web/` | per Komodo | (none — SPA) | per Komodo |
| croilar-postgres | `bonneagar/stacks/croilar-postgres/` | 5432-5434 | (none — DB) | none |

## 4. Meaisínfhoghlaim → komodo-meaisinfhoghlaim-bunchloch + LLM gateway

| Stack | Path | Port | Dagster code-location | `*.cianfhoghlaim.ie` domain |
|:--|:--|:--|:--|:--|
| meaisínfhoghlaim-bunchloch (orchestrated via Komodo) | `bonneagar/komodo/stacks/meaisínfhoghlaim-bunchloch.toml` | per Komodo | `meaisinfhoghlaim/dagster_defs/__init__.py` (4 heartbeat assets) | none |
| LLM gateway (shared with oideachais) | `bonneagar/stacks/litellm/` | 4000 | (none — proxy) | none |
| llama-swap (shared) | `bonneagar/stacks/llama-swap/` | 8080 | (none — router) | none |

## 5. Cross-quadrant infrastructure (the 9 user-named deploy targets)

| Stack | Path | Host | `*.cianfhoghlaim.ie` domain | Runbook |
|:--|:--|:--|:--|:--|
| infisical | `bonneagar/stacks/infisical/` | arm1-oci | `infisical.cianfhoghlaim.ie` | `bonneagar/deploy-runbooks/infisical.md` |
| komodo | `bonneagar/komodo/` | arm1-oci + bunchloch | `komodo.cianfhoghlaim.ie` | `bonneagar/deploy-runbooks/komodo.md` |
| pangolin | `bonneagar/stacks/pangolin/` | arm1-oci | (Pangolin routes all `*.cianfhoghlaim.ie` domains) | `bonneagar/deploy-runbooks/pangolin.md` |
| olm-arm1-oci | `bonneagar/stacks/olm-arm1-oci/` | arm1-oci | (OLM TCP tunnel, not a public HTTP service) | (moved from `pangolin/olm-oracle/` in v5) |
| cal-diy | `bonneagar/stacks/cal-diy/` | arm1-oci | `calcom.cianfhoghlaim.ie` | `bonneagar/deploy-runbooks/cal-diy.md` |
| vikunja | `bonneagar/stacks/vikunja/` | bunchloch | (per Komodo) | `bonneagar/deploy-runbooks/vikunja.md` |
| n8n | `bonneagar/stacks/n8n/` | bunchloch | (per Komodo) | `bonneagar/deploy-runbooks/n8n.md` |
| changedetection | `bonneagar/stacks/changedetection/` | bunchloch | (per Komodo) | `bonneagar/deploy-runbooks/changedetection.md` |
| bytebase | `bonneagar/stacks/bytebase/` | arm1-oci | (per Komodo) | `bonneagar/deploy-runbooks/bytebase.md` |

> **v5 update:** The `bonneagar/ansible/` directory was pruned
> in the v5 drift refactor (functionally dead per the prior
> runbook's own admission). Hetzner is Pulumi-only (no
> `cax41-hetzner` references in inventory / IaC / ansible).
> The 2-host topology is `arm1-oci` + `bunchloch` only.

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
│   ├── komodo-periphery-bunchloch
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
│   ├── komodo-periphery-arm1-oci
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
