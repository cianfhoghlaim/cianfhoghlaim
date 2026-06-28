---
name: kcg-bunchloch
description: KCG's 3-tier host convergence architecture — `arm1-oci` (control plane: Komodo + Pangolin + Pocket ID + CrowdSec), `cax41-hetzner` (storage: Garage + Lakekeeper + Postgres), `bunchloch` M4 MacBook (workload: Dagster + LiteLLM + 70+ models). Use when onboarding a new host, debugging cross-host connectivity, planning a workload migration, or asking "where does X run in KCG?".
---

# KCG Bunchloch Convergence

## When to use this skill

Use when you need to:

- "Where does Y run in KCG?" (the canonical answer)
- "Add a new host to the cluster"
- "Debug a cross-host connectivity issue (bunchloch ↔ arm1-oci)"
- "Plan a workload migration (bunchloch → cax41-hetzner)"
- "Onboard a new dev to the 3-tier topology"

## The 3-tier model

| Tier | Host | Role | Key stacks |
|:--|:--|:--|:--|
| **Control plane** | `arm1-oci` (Oracle Cloud ARM free tier) | Komodo (GitOps) + Pangolin (zero-trust) + Pocket ID (OIDC) + CrowdSec (WAF) | Komodo :9120, Pangolin :3001, Gerbil :51820/udp, Pocket ID :1411 |
| **Storage** | `cax41-hetzner` (Hetzner Cloud ARM, cax41) | Garage (S3) + Lakekeeper (Iceberg REST) + Postgres (catalog) + LakeFS (data versioning) | Garage :3900-3904, Lakekeeper :8181, Lance Namespace :8182, Postgres :5433 |
| **Workload** | `bunchloch` (MacBook M4 Max, 48GB) | Dagster (orchestration) + LiteLLM (LLM gateway) + CocoIndex (embedding) + the 70+ model backends (GGUF/MLX/safetensors) | Dagster :3335, LiteLLM :4000, llama-swap :8080, mlx-omni-server :10240, invokeai :9090 |

**Why 3 tiers and not 1 or 2:**

- **arm1-oci is free** (Oracle Cloud ARM free tier, 4 OCPU +
  24GB) but has 200GB storage + 10TB/month egress. Ideal for
  the control plane (low CPU, low storage, high network reach).
- **cax41-hetzner** is €4-8/month for 4 vCPU + 16GB + 320GB
  NVMe. Ideal for storage (the S3 + Iceberg catalog).
- **bunchloch** is the M4 Max with 48GB unified memory. Ideal
  for **LLM inference** (the Apple Silicon GPU is fast for
  MLX + GGUF quantised models) and **Dagster** (the
  orchestration needs lots of RAM for BAML extraction +
  CocoIndex embedding).

The 3 tiers are wired by **Pangolin WireGuard tunnels**
(`arm1-oci` Gerbil :51820/udp) and **Locket sidecars** that
inject Infisical secrets into every container (no plaintext
on disk).

## Service relationships

```
                        ┌──────────────────────┐
                        │  arm1-oci (control)  │
                        │  Komodo + Pangolin   │
                        │  + Pocket ID + CSec  │
                        └──────────┬───────────┘
                                   │ WireGuard + Pangolin
                  ┌────────────────┼────────────────┐
                  ▼                ▼                ▼
        ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
        │  cax41-hetzner   │ │  bunchloch   │ │  cax41-hetzner   │
        │  (storage)       │ │  (workload)  │ │  (storage replica)│
        │  Garage+Lake-    │ │  Dagster+    │ │  optional         │
        │  keeper+Postgres │ │  LiteLLM+ML  │ │                   │
        └──────────────────┘ └──────────────┘ └──────────────────┘
```

### 1. Komodo (Control plane → Workload)

- **Komodo Core** runs on `arm1-oci` (port 9120)
- **Periphery agents** run on every host (`arm1-oci`,
  `cax41-hetzner`, `bunchloch`)
- Communication is **outbound-only** (Periphery → Core) via
  passkeys. No inbound ports needed on the workload host.
- Each host's `compose.yaml` is **deployed by Komodo** from
  the Git repo (Komodo reads the file from disk, runs
  `docker compose up -d` on the Periphery).

### 2. Pangolin (Zero-trust)

- **Pangolin Core** on `arm1-oci` (Traefik :80/:443 + Gerbil
  :51820/udp)
- **Newt** tunnel client on every host
- **OLM** lightweight client on remote / mobile sites
- **Pocket ID** on `arm1-oci` (:1411) is the **single OIDC
  provider** for the whole cluster
- **Traefik routes** every `*.cianfhoghlaim.ie` domain to the
  right host:port

### 3. Locket + Infisical (Secrets)

- **Infisical** (`dev-baile` env) is the source of truth for
  secrets. Hosted on `arm1-oci` (or cloud).
- **Locket** sidecars run in every stack that needs secrets.
  They watch Infisical and write decrypted values to
  `/run/secrets/locket/*` (tmpfs).
- **mise** directory hooks re-inject on every `cd`.

### 4. Forgejo (Git)

- **Forgejo** on `arm1-oci` (HTTP :3000, SSH :2222) is the
  self-hosted Git for the KCG monorepo + Docker image
  registry + PyPI registry.
- Komodo reads `infrastructure/stacks/*/compose.yaml` from
  the Forgejo clone on the workload host.

### 5. Ansible (periphery deployment)

- The `bpbradley.komodo` Ansible role (in
  `infrastructure/bunchloch/automation/`) deploys Komodo
  Periphery agents to new hosts.
- Runs in the Ansible Execution Environment container
  (`ghcr.io/bpbradley/ansible/komodo-ee:latest`).

## Component directory structure

```
infrastructure/bunchloch/
├── authentication/              # Standalone auth testing
│   └── docker-compose.yml       # Pocket ID + TinyAuth + Traefik
├── automation/                  # Ansible orchestration
│   ├── compose.yaml             # Ansible Execution Environment
│   ├── SETUP.md
│   └── ansible/
│       ├── inventory/
│       │   └── komodo.yml       # Server definitions
│       └── playbooks/
│           ├── komodo.yml       # Periphery deployment
│           └── periphery.yml    # With Locket integration
├── forgejo/                     # Git + Package Registry
│   ├── compose.yaml
│   └── README.md
├── komodo/                      # Container Orchestration
│   ├── komodo-core/
│   │   ├── mongo.compose.yaml   # Core + MongoDB + Periphery
│   │   └── compose.env
│   └── periphery/
│       └── compose.yaml         # Remote periphery agents
└── pangolin/                    # Zero-Trust Networking
    ├── pangolin-core/
    │   ├── compose.yaml
    │   └── config/
    │       ├── config.yml
    │       ├── traefik/
    │       └── middleware-manager/
    ├── newt/                    # Tunnel agents
    │   └── compose.yaml
    └── olm/                     # Lightweight tunnel client
        └── compose.yaml
```

## Startup order

For full stack deployment, services should start in this order:

1. **Infisical** (the secrets source) — must be running first
2. **Locket sidecars** — wait for Infisical to be healthy
3. **PostgreSQL** (Pangolin & Forgejo) — database initialization
4. **MongoDB** (Komodo) — state storage
5. **Pangolin services** — depend on Locket & PostgreSQL
6. **Komodo Core** — depends on MongoDB
7. **Forgejo** — depends on PostgreSQL
8. **Newt/OLM tunnels** — depend on Pangolin network
9. **Komodo Periphery** — depends on Core

## Ports reference

| Service | Host | Port | Protocol | Purpose |
|:--|:--|:--|:--|:--|
| Infisical | arm1-oci | 8080 | HTTP | Secret retrieval |
| Komodo Core | arm1-oci | 9120 | TCP/WSS | Cluster control |
| Pangolin | arm1-oci | 3001 | HTTP | Identity proxy |
| Gerbil | arm1-oci | 51820 | UDP | WireGuard tunnel |
| Traefik | arm1-oci | 80, 443 | TCP | HTTP/S routing |
| Pocket ID | arm1-oci | 1411 | HTTP | OIDC provider |
| TinyAuth | arm1-oci | 8443 | HTTP | Forward auth |
| Forgejo HTTP | arm1-oci | 3000 | HTTP | Git web UI |
| Forgejo SSH | arm1-oci | 2222 | SSH | Git clone |
| Dagster | bunchloch | 3335 | HTTP | Orchestration UI |
| LiteLLM | bunchloch | 4000 | HTTP | LLM gateway |
| llama-swap | bunchloch | 8080 | HTTP | GGUF model server |
| mlx-omni-server | bunchloch | 10240 | HTTP | MLX model server |
| invokeai | bunchloch | 9090 | HTTP | safetensors model server |
| Garage | cax41-hetzner | 3900-3904 | HTTP | S3 API |
| Lakekeeper | cax41-hetzner | 8181 | HTTP | Iceberg REST |
| Lance Namespace | cax41-hetzner | 8182 | HTTP | Lance REST |
| Postgres | cax41-hetzner | 5433 | TCP | Catalog metadata |

## Cross-references

- `.agents/skills/kcg-convergence/SKILL.md` — the 6
  docker-compose categories
- `.agents/skills/kcg-leabharlann-pipeline/SKILL.md` — the
  5-stage PDF flow
- `.agents/skills/stack-ops/SKILL.md` — the GOLD_STANDARD
  6-file pattern
- `.agents/skills/pangolin/SKILL.md` — the Fossorial
  Pangolin stack
- `.agents/skills/komodo/SKILL.md` — the Komodo GitOps
  stack
- `.agents/skills/secrets-management/SKILL.md` — Infisical
  + Locket
- `infrastructure/AGENTS.md` — the canonical 3-tier
  reference
- `docs/06-infrastructure/leabharlann-stack-overview.md` —
  the canonical end-to-end diagram (round 7 deletes this
  doc; content absorbed into the kcg-* skills)
