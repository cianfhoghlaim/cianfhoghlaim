---
title: "Cianfhoghlaim Platform Overview & Architecture Rationale"
domain: architecture
status: stable
description: "Complete Cianfhoghlaim architecture including Pangolin convergence, the Quadrant Model, sovereign infrastructure philosophy, and end-to-end deployment flow"
supersedes:
  - docs/ARCHITECTURE_RATIONALE.md
  - docs/ARCHITECTURE_DEPLOYMENT.md
  - docs/bonneagar/overview.md
  - docs/bonneagar/ARCHITECTURE.md
  - docs/bonneagar/infrastructure-devops.md
  - docs/bonneagar/TECH_STACK.md
  - docs/bonneagar/IMPLEMENTATION_GUIDE.md
  - docs/bonneagar/DECISION_MATRICES.md
  - docs/bonneagar/bunchloch.md
  - docs/bonneagar/backend.md
  - docs/context/02-architecture/SRUTH_OVERVIEW.md
  - docs/context/02-architecture/OIDEACHAIS_PIPELINE.md
entities:
  - Cianfhoghlaim
  - QuadrantModel
  - PangolinConvergence
  - arm1oci
  - Bunchloch
related_skills:
  - .agents/skills/dagster/SKILL.md
  - .agents/skills/dlt/SKILL.md
  - .agents/skills/pangolin/SKILL.md
  - .agents/skills/komodo/SKILL.md
  - .agents/skills/stack-ops/SKILL.md
  - .agents/skills/oideachas-pipeline/SKILL.md
ccc_query_hints:
  - "Cianfhoghlaim architecture overview"
  - "sovereign infrastructure philosophy"
  - "Pangolin convergence architecture"
  - "what is the Quadrant Model"
  - "how does the platform deploy end to end"
last_reviewed: 2026-06-06
---

# Cianfhoghlaim Platform Overview

## The Quadrant Model

The project is decoupled into four sovereign quadrants ensuring strict separation of concerns and a "Local-First / Sovereign-First" deployment model.

### 1. `infrastructure/` — The Foundation

**Focus:** Zero-trust networking, fleet orchestration, and machine identity.

| Component | Role | Why Chosen |
|-----------|------|-----------|
| **Komodo** | Edge-first fleet orchestrator | Manages Docker Compose blueprints across disconnected servers (OCI control plane + local MacBook workload host). Replaces standard Ansible/Kubernetes for this use case. |
| **Pangolin (Newt/Gerbil)** | WireGuard-backed Service Mesh | Replaces Cloudflare Tunnels. Enables secure, internal, outbound-only communication between MacBook M4 and OCI instance without opening inbound firewall ports. |
| **Infisical + Locket** | Centralized secret vault + sidecar injection | Replaces scattered `.env` files. `Locket` injects secrets into Docker Compose clusters and CLI environments dynamically at runtime. |
| **Pocket ID + TinyAuth** | Identity-Aware Proxy | Strict `forwardAuth` middleware pattern. TinyAuth bounces unauthenticated requests to Pocket ID for Passkey login before traffic reaches internal apps. |

### 2. `oideachais/` — The Engine

**Focus:** Extract-Load-Transform (ELT), data orchestration, and the interactive frontend.

| Component | Role | Why Chosen |
|-----------|------|-----------|
| **Dagster** | Asset-driven orchestrator | Tracks materialized state of Irish curriculum (e.g., Junior Cycle Mathematics). Chosen over Airflow/Prefect for its asset-centric model. |
| **DLT (Data Load Tool)** | Declarative, typed ingestion | Configured with offline `stedding/site_scrape_samples` fallback for rapid iteration without API rate limits. |
| **DuckLake (DuckDB + Garage S3)** | Local Lakehouse architecture | Rejects expensive cloud data warehouses. DuckDB reads/writes Parquet/Iceberg tables directly to S3-compatible Garage hosted locally or on Cloudflare R2. |
| **TanStack Start** | SSR-first frontend | Complements local-first philosophy with offline differential data syncs via TanStack DB. |

### 3. `meaisínfhoghlaim/` — The Brain

**Focus:** Artificial Intelligence, LLM Routing, and Semantic Extraction.

| Component | Role | Why Chosen |
|-----------|------|-----------|
| **BAML** | Compiled, type-safe schema definitions | Replaces brittle raw JSON prompt engineering. Extracts complex entities (Learning Outcomes, Examiner Reports) from unstructured PDFs. |
| **LiteLLM** | Centralized LLM gateway | Unifies API keys (Anthropic, OpenAI, Gemini) with agentic routing, fallback handling, and spend tracking. |
| **Graphiti + Neo4j** | Temporal knowledge graph | Tracks episodic "Builds On" relationships between curriculum concepts. Outperforms vector databases for complex curriculum reasoning. |
| **LanceDB + CocoIndex** | Vectorized semantic search | CocoIndex orchestrates chunking of BAML-extracted markdown and syncs embeddings into LanceDB. |

### 4. `tuatha/` — The Edge

**Focus:** Distributed node state, real-time MMO mechanics, and Web3 integration.

| Component | Role | Why Chosen |
|-----------|------|-----------|
| **SpacetimeDB** | Embedded ECS database + application server | Synchronizes Entity-Component-System updates in real-time for the "Anam" educational MMO. |
| **x402 (HTTP 402)** | Cryptographic micropayments over HTTP | Facilitates "Learn-to-Earn" token economy without heavy smart contract deployments. |

## Pangolin Convergence Architecture

The deployment strategy utilizes a **Two-Tier "Pangolin Convergence" Architecture**:

### Control Plane (`arm1.oci`)

An Oracle Cloud ARM Ampere A1 instance hosting:

- **Pangolin** — Routing and zero-trust perimeter (Traefik + WireGuard)
- **Komodo Core** — Deployment orchestration
- **Pocket ID** — Passkey-based OIDC provider
- **Infisical** — Centralized secret vault
- **Garage S3** — Object storage for artifacts

### Workload Host (`bunchloch` — MacBook M4)

High-performance environment connected via zero-trust WireGuard tunnels:

- **Dagster** — Stateful processing of syllabus extraction
- **DLT** — Declarative ingestion pipelines
- **LanceDB** — Vector embeddings for semantic search
- **Neo4j** — Knowledge graph for curriculum relationships
- **LiteLLM** — LLM gateway with local model support
- **SpacetimeDB** — Real-time MMO game state
- **Local AI inference** — MLX/llama.cpp for on-device models

### Network Flow

```
External Request → Traefik (TLS) → TinyAuth (forwardAuth) → Pocket ID (OIDC)
    ↓
Gerbil (WireGuard controller) → Newt (site connector) → Internal Service
```

## Infrastructure Principles

1. **Container-First** — All services run in containers for consistency and portability
2. **Secrets Never in Git** — Only URI references in `.infisical.env`; actual values never committed
3. **Zero-Trust Networking** — Services accessible only through authenticated Pangolin tunnels
4. **Infrastructure as Code** — Everything defined in code (Pulumi, Ansible, Docker Compose, TOML)
5. **Modular Pipelines** — Build, test, deploy steps organized as reusable Dagger modules
6. **Sovereign-First** — Local-first data processing, self-hosted infrastructure, no vendor lock-in

## Technology Stack

| Category | Tool | Purpose |
|----------|------|---------|
| **Git Hosting** | Forgejo | Self-hosted Git with Actions |
| **CI/CD** | Dagger | Programmable pipelines in TypeScript/Python/Go |
| **Deployment** | Komodo | Docker Compose orchestration across servers |
| **Networking** | Pangolin | Zero-trust tunnel access + reverse proxy |
| **Secrets** | Infisical + Locket | Vault-based secrets with sidecar injection |
| **IaC** | Pulumi | Cloud resource provisioning (OCI, Hetzner, Cloudflare) |
| **Config** | Ansible | Server configuration and bootstrap |
| **Orchestration** | Dagster | Asset-driven data pipeline orchestration |
| **Ingestion** | DLT | Declarative typed data extraction |
| **Lakehouse** | DuckDB + Garage S3 | Local analytics engine with S3-compatible storage |
| **LLM Gateway** | LiteLLM | Multi-provider routing, fallback, cost tracking |
| **Vector DB** | LanceDB | Semantic search embeddings |
| **Graph DB** | Neo4j / Memgraph | Knowledge graph and curriculum relationships |
| **Identity** | Pocket ID + TinyAuth | Passkey-based OIDC + forward auth |
| **Runtime** | bun + uv + mise | Polyglot package and environment management |
| **Monitoring** | Langfuse + Dozzle | LLM observability + container log viewing |

## End-to-End Deployment Flow

### Step 1: Secret Hydration (Infisical + Mise)

Never manually create `.env` files. The platform uses `mise` directory hooks and a `locket` sidecar pattern.

```bash
# Sync template to vault
bun run secrets:init
# or
mise run secrets:init

# Local hydration (automatic on cd)
# mise hook runs: infisical export --env=dev-baile > .env
```

### Step 2: Infrastructure Provisioning (Pulumi & Komodo)

```bash
cd infrastructure/pulumi/oci/
bun run setup.ts save-cloudflare --token <token> --zone-id <zone-id>
bun run deploy.ts deploy
```

This automates: ARM Ampere A1 provisioning, Cloudflare DNS/WAF configuration, iptables, Ansible inventory regeneration, and execution of `deploy-infrastructure.yml` (installs Docker, Komodo Core, Pangolin).

### Step 3: Zero-Trust Networking (Pangolin)

```bash
cd infrastructure/pangolin/
docker compose -f compose.yaml -f sidecar.yaml up -d
./scripts/sync-blueprints.sh
```

### Step 4: Intelligence Layer (meaisínfhoghlaim)

- Unstructured documents processed through BAML type-safe schemas
- Structured data ingested into Cognee (graph pipeline routing) and Graphiti (temporal tracking)

### Step 5: Lakehouse Data Pipelines (oideachais)

```bash
cd oideachais/data_platform
uv sync
dagster dev -m dagster_defs.definitions
```

Set `os.environ['USE_LOCAL_SCRAPES'] = 'true'` to hit the `stedding/ingest_queue/` cache.

### Step 6: Application Layer (Tuatha & TanStack Start)

```bash
# Edge MMO Layer
cd tuatha/
docker compose -f docker-compose.yaml -f compose.dev.yaml up -d

# Web App
cd oideachais/web_app
bun install && bun run dev
```

## Server Provisioning Architecture

### Pulumi Multi-Cloud

| Stack | Provider | Resources |
|-------|----------|-----------|
| `oci-production` | OCI | Compute (ARM Ampere A1), VCN, Object Storage |
| `hetzner-production` | Hetzner | Servers, Volumes, Networks |
| `cloudflare-production` | Cloudflare | DNS, Pages, Workers, R2, D1 |

### Ansible Bootstrap

The full OS-level bootstrap is codified in Ansible playbooks:

```yaml
# playbooks/setup-server.yml
- name: Setup production server
  hosts: production
  become: yes
  tasks:
    - name: Install Docker
    - name: Install Komodo Periphery
    - name: Install Pangolin Newt
```

### Decision Matrix: Deployment Approach

| Approach | Complexity | Scalability | Best For |
|----------|------------|-------------|----------|
| **Systemd** | Low | Single server | Edge deployments |
| **Docker Compose** | Medium | Single server | Development |
| **Komodo** | Medium-High | Multi-server | Production |
| **Kubernetes** | High | Cluster | Large-scale |

## Agent Workflows (MCPs & Subagents)

Specialized Model Context Protocol servers augment CLI agents:

| MCP Server | Purpose |
|-----------|---------|
| **Docling / Marker MCP** | Converts complex SEC Examination PDFs and multi-column Marking Schemes into structured Markdown |
| **Crawl4AI MCP** | Powers asynchronous browser automation for legacy government website dropdowns |
| **ChunkHound** | AST-aware semantic codebase indexing for efficient monorepo navigation |
| **Filesystem MCP** | Secure file operations within the platform |

## Key Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| Core initiates to Periphery | Periphery can be behind NAT |
| Passkey authentication (Komodo) | Simple shared-secret model |
| Stateless Periphery | Easy deployment, no local persistence |
| Private by default (Pangolin) | All services require WireGuard + Pocket ID |
| Three-way secret contract | Source of truth (Infisical) → Template (`.infisical.env`) → Runtime (`.env`) |
| uv + mise instead of pip + asdf | 10-100x faster resolution, polyglot support |
| DuckLake over Snowflake/BigQuery | Local sovereignty, zero cloud warehouse costs |
