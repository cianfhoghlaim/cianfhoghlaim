---
title: "Services Outline by Year"
domain: platform-architecture
status: living-document
---

# Cianfhoghlaim — Services Outline by Year

A year-by-year launch calendar of every service in the Cianfhoghlaim
stack. Derived from `infrastructure-stacks.md` (89 stacks), the Celtic MMO
launch plan (`06-product/celtic-mmo.md`), and the Dagster 7-phase pipeline
rollout (`02-data-platform/dagster-orchestration.md`).

## 2026 (Active)

### Tier 1 — Core platform (live in production)

| Service | Stack | Port | Status | Notes |
|:--|:--|:--|:--|:--|
| `oideachais-web` | TanStack Start + Convex | 3001 | 🟢 | Bilingual (en/ga), 7-stage curriculum (aistear→tertiary) |
| `oideachais-api` | Hono + oRPC + CopilotKit AG-UI | 8787 | 🟢 | BAML extraction, Convex persistence, Langfuse tracing |
| `oideachais-dagster` | Dagster 7-phase pipeline | 3335 | 🟢 | Lakehouse orchestration, dlt+DLT+Pydantic+BAML+DuckDB |
| `oideachais-convex` | Convex self-hosted | 3210 | 🟢 | 5 tables: subject_sessions, practice_attempts, annotations, classmate_shares, extraction_budget |
| `oideachais-baml` | BAML curriculum extraction | – | 🟢 | 7 stage files (aistear → tertiary) + ui_components + image_generation |
| `oideachais-frontend` | Containerized SSR | 3000 | 🟢 | Prowides 80/tcp + 3000/tcp via Traefik + Pocket ID |

### Tier 2 — Control plane (live)

| Service | Stack | Port | Status | Notes |
|:--|:--|:--|:--|:--|
| `pangolin` | WireGuard + Traefik | 51820/udp, 443 | 🟢 | Two-tier convergence: arm1-oci (control) + bunchloch (workload) |
| `komodo` | Container orchestration | 9120 | 🟢 | GitOps workflow from Forgejo |
| `pocket-id` | OIDC identity | 1411 | 🟢 | SSO for all frontends |
| `forgejo` | Self-hosted git | 3000 | 🟢 | This repo lives here |
| `crowdsec` | Intrusion detection | – | 🟢 | Traefik bouncer |
| `locket` | Secret injection sidecar | – | 🟢 | Pattern: per-stack Infisical hydration |

### Tier 3 — Data plane (live)

| Service | Stack | Port | Status | Notes |
|:--|:--|:--|:--|:--|
| `litellm` | LLM gateway (19+ models) | 4000 | 🟢 | BAML, agents, embeddings, image gen, voice |
| `langfuse` | LLM observability v3 | 3001 | 🟢 | ClickHouse + MinIO + Postgres + Redis |
| `lakehouse-lakekeeper` | Iceberg REST catalog | 8181 | 🟢 | Postgres-backed catalog |
| `lakehouse-lance-namespace` | LanceDB-as-Iceberg | 8182 | 🟢 | Tables in Iceberg, vectors in LanceDB |
| `lancedb` | Vector search (standalone) | 8081 | 🟢 | Educational content vectors |
| `dragonfly` | Redis-compatible cache | 6381 | 🟢 | Session caching |
| `dagster-db` | Dagster Postgres | – | 🟢 | Pipeline metadata |
| `litellm-db` | LiteLLM Postgres | – | 🟢 | Model registry, usage tracking |
| `litellm-prometheus` | Prometheus | 9090 | 🟢 | LLM call metrics |

### Tier 4 — ML / Knowledge graph (live)

| Service | Stack | Port | Status | Notes |
|:--|:--|:--|:--|:--|
| `cognee` | AI memory | 8000 | 🟢 | Neo4j backend, 19-stage curriculum |
| `graphiti` | Temporal knowledge graph | 8080 | 🟢 | NPC conversations in Tuatha |
| `mlflow` | ML experiment tracking | 5000 | 🟢 | LoRA experiments, BAML eval |
| `qdrant` | Vector DB | 6333 | 🟢 | Alternative to LanceDB |
| `memgraph` | Graph DB + MAGE | 7687 | 🟢 | cypher queries on knowledge graph |
| `falkordb` | Vector+graph hybrid | 6379 | 🟢 | Real-time NPC dialogue |

### Tier 5 — Browser automation (live)

| Service | Stack | Port | Status | Notes |
|:--|:--|:--|:--|:--|
| `browserbase` | Browser automation MCP | 4001 | 🟢 | Self-hosted Stagehand |
| `stagehand-proxy` | Stagehand CDP | 4005 | 🟢 | Chromium grid |
| `browser-grid` | Selenium grid | 9222 | 🟢 | Multi-browser testing |
| `firecrawl` | Web scraping MCP | – | 🟢 | BAML training data, Celtic archive scraping |

### Tier 6 — Storage (live)

| Service | Stack | Port | Status | Notes |
|:--|:--|:--|:--|:--|
| `garage` | S3-compatible | 3900-3904 | 🟢 | Parquet + LanceDB data lake |
| `lakefs` | Git-for-data | 8000 | 🟢 | Versioned lake |
| `forgejo-runner` | CI runner | – | 🟢 | Forges builds |

## 2026 Q3-Q4 (In Progress)

| Service | Stack | Port | Target Date | Notes |
|:--|:--|:--|:--|:--|
| `tuatha-ui` | TanStack Start + Babylon.js | 3004 | Q3 | Babylon.js + SpacetimeDB multiplayer, SIWE, x402 |
| `croilar-hono-api` | Hono + Better Auth + Drizzle | 4000 | Q3 | SIWE + passkey + 2FA + 5 MCP servers + x402 |
| `croilar-portal` | TanStack Start + AI SDK + MCP-UI | 3000 | Q4 | Internal admin portal, multi-tenant themes |
| `croilar-web` | Vite + Radix + i18n | 3003 | Q4 | Personal portfolio, CV/research/identity pages |
| `cypress` | E2E tests | – | Q4 | Component-level e2e for all 5 frontends |
| `baml-eval` | BAML evaluation pipeline | – | Q4 | LoRA regression, curriculum extraction accuracy |

## 2027 (Planned)

### Q1-Q2 — Knowledge graph expansion

| Service | Stack | Notes |
|:--|:--|:--|
| `cognee-v2` | Cognee 1.1 | Migrate from Neo4j to Memgraph backend, add tri-modal embeddings |
| `graphiti-v2` | Graphiti with bi-temporal | Full conversation history for NPC dialogue |
| `lrng` (Learning) | Custom RL-based tutoring | Adaptive difficulty, student modeling |
| `lance-namespace` | Lance Namespace 1.0 | Stable Iceberg integration |

### Q3-Q4 — Celtic MMO production launch

| Service | Stack | Notes |
|:--|:--|:--|
| `tuatha-game` | Babylon.js + SpacetimeDB | Full Celtic MMO client, 6 Celtic nations |
| `spacetimedb` | SpacetimeDB | Real-time multiplayer, 1000+ concurrent users |
| `crypteolas` | Federated learning + x402 | On-device Irish LLM fine-tuning |
| `fedlearn` | Syft Flower | Federated curriculum data from 4 schools |

## 2028+ (Future)

| Service | Notes |
|:--|:--|
| `x402-token` | Web3 token for premium content (5% of users) |
| `crypteolas-defi` | DeFi integration for education microgrants |
| `siwe-everywhere` | EIP-4361 wallet auth across all services |
| `crypteolas-llm` | On-device 7B Irish LLM (Llama 4 fine-tuned) |
| `tier-2-cdn` | Cloudflare R2 + Workers for educational content |
| `crypteolas-protocol` | Open-source Celtic education LLM protocol |

## Service Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 7 — Browser Apps (TanStack Start, Vite SPA)          │
│  oideachais-web, tuatha-ui, croilar-web, croilar-portal      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Layer 6 — API Servers (Hono, oRPC)                         │
│  oideachais-api, croilar-hono-api                           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Layer 5 — LLM Gateway (LiteLLM, Langfuse)                  │
│  19+ models, observability, fallback chains                 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Layer 4 — Data Platform (Convex, LanceDB, BAML)            │
│  Real-time reactive, vector search, curriculum extraction    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Layer 3 — Pipeline (Dagster + dlt + CocoIndex + DuckDB)     │
│  7-phase: scrape → extract → dlt → transform → embed →       │
│  semantic_layer → serve                                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Layer 2 — Knowledge Graph (Cognee, Graphiti, Memgraph)      │
│  Bi-temporal, entity resolution, NPC dialogue                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│  Layer 1 — Storage (Garage S3, Lakekeeper Iceberg, LakeFS)   │
│  Parquet, vector indexes, versioned data                    │
└─────────────────────────────────────────────────────────────┘
```

## Port Allocation Map

| Range | Purpose |
|:--|:--|
| 3000-3009 | Frontend dev (5 apps) |
| 3210-3211 | Convex backend |
| 3335 | Dagster webserver |
| 3900-3904 | Garage S3 (admin, web, rpc) |
| 4000-4099 | LLM gateway (litellm, hono-api, browser) |
| 51820/udp | Pangolin WireGuard |
| 5432-5434 | Postgres instances (langfuse, lakehouse, croilar) |
| 6381 | Dragonfly cache |
| 7687 | Memgraph Bolt |
| 8000-8099 | MCP servers (cognee, graphiti, lancedb, mlflow) |
| 8181-8182 | Iceberg REST + Lance Namespace |
| 9090 | Prometheus |
| 9120 | Komodo |
| 1411 | Pocket ID OIDC |

## How to Update This Document

After deploying a new service:

1. Add a row to the appropriate tier/quarter table
2. Update the "Status" column (🟢 live, 🟡 deploying, ⏳ planned, ❌ deprecated)
3. Add a new port to the port allocation map
4. Update the parent `infrastructure-stacks.md` if the new service is part
   of `infrastructure/stacks/`

This document is part of the OpenSpec
[`state-of-art-5-workspaces`](../../changes/state-of-art-5-workspaces/proposal.md)
change.
