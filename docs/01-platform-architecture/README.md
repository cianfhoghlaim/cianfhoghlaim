---
title: "Platform Architecture — Canonical Index"
domain: architecture
status: stable
description: "Canonical index for the Cianfhoghlaim platform architecture documentation, consolidating 163+ files from docs/bonneagar/"
supersedes:
  - docs/bonneagar/INDEX.md
  - docs/bonneagar/INDEX1.md
  - docs/bonneagar/README.md
entities:
  - Cianfhoghlaim
  - PlatformArchitecture
related_skills:
  - .agents/skills/stack-ops/SKILL.md
  - .agents/skills/dagster/SKILL.md
  - .agents/skills/dlt/SKILL.md
ccc_query_hints:
  - "platform architecture overview"
  - "Cianfhoghlaim infrastructure docs"
  - "how is the platform deployed"
last_reviewed: 2026-06-06
---

# Cianfhoghlaim Platform Architecture

This directory contains the **consolidated canonical** platform architecture documentation, migrated from `docs/bonneagar/` (163+ files) and root-level architecture docs.

## Documents

| # | File | Description |
|---|------|-------------|
| 1 | [platform-overview.md](platform-overview.md) | Cianfhoghlaim architecture, Pangolin convergence (OCI ARM1 + MacBook M4), sovereign infrastructure philosophy, the Quadrant Model |
| 2 | [infrastructure-stacks.md](infrastructure-stacks.md) | All 89 Docker Compose stacks, compose patterns, network topology, health checks, restart policies, storage architecture |
| 3 | [kubernetes-deployment.md](kubernetes-deployment.md) | Kubernetes deployment patterns, Talos on Hetzner, Pulumi/OpenTofu IaC, Ansible server provisioning |
| 4 | [secrets-management.md](secrets-management.md) | Three-way secret contract (Infisical → `.infisical.env` → `.env`), Locket sidecar, mise hooks, provider configuration |
| 5 | [komodo-gitops.md](komodo-gitops.md) | Komodo Core/Periphery architecture, GitOps workflows, Resource Sync, Procedures, Actions, Ansible integration |
| 6 | [pangolin-networking.md](pangolin-networking.md) | Pangolin zero-trust reverse proxy, Traefik, WireGuard VPN, Pocket ID OIDC, CrowdSec, Blueprints, Docker label config |
| 7 | [monorepo-strategy.md](monorepo-strategy.md) | bun + uv + turbo polyglot monorepo, mise toolchain, workspace topology, Dagger CI/CD, Taskipy vs Mise analysis |

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│              CIANFHOGHLAIM PLATFORM                      │
├─────────────────────────────────────────────────────────┤
│  Control Plane: arm1-oci (Oracle Cloud ARM Ampere A1)    │
│  - Pangolin (Traefik + WireGuard + Pocket ID)            │
│  - Komodo Core (deployment orchestration)                 │
│  - Infisical (secret vault)                               │
│  - Garage S3 (object storage)                             │
├─────────────────────────────────────────────────────────┤
│  Workload Host: bunchloch (MacBook M4)                    │
│  - Dagster + DLT (data pipelines)                         │
│  - LanceDB + Neo4j (vector + graph stores)                │
│  - LiteLLM (LLM gateway)                                  │
│  - 89 Docker Compose stacks                               │
├─────────────────────────────────────────────────────────┤
│  Edge: tuatha (SpacetimeDB + x402 MMO)                    │
│  Web: TanStack Start + Hono (oideachais-web)              │
│  Python: uv workspace (oideachais, tuatha, códeolas)      │
└─────────────────────────────────────────────────────────┘
```

## Navigation

- **New to the platform?** Start with [platform-overview.md](platform-overview.md)
- **Debugging a stack?** See [infrastructure-stacks.md](infrastructure-stacks.md)
- **Rotating secrets?** See [secrets-management.md](secrets-management.md)
- **Deploying a service?** See [komodo-gitops.md](komodo-gitops.md)
- **Networking issue?** See [pangolin-networking.md](pangolin-networking.md)
- **Toolchain questions?** See [monorepo-strategy.md](monorepo-strategy.md)
- **Scaling to K8s?** See [kubernetes-deployment.md](kubernetes-deployment.md)

## Migration Notes

All source files from `docs/bonneagar/` (163 files) have been consolidated into these 7 canonical documents and archived to `docs/archive/2026-06-06-bonneagar/`. Root-level `ARCHITECTURE_RATIONALE.md` and `ARCHITECTURE_DEPLOYMENT.md` have been subsumed into [platform-overview.md](platform-overview.md).
