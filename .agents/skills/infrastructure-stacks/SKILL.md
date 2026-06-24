---
name: infrastructure-stacks
description: Router for the infrastructure stacks capability. The Cianfhoghlaim platform has 94+ Docker Compose stacks under `infrastructure/stacks/` (the flat layout, no category subdirectory). Use when adding a new stack, fixing a broken stack, auditing the inventory, or wiring the 6-file GOLD_STANDARD pattern (compose.yaml + sidecar.yaml + pangolin.yaml + secrets.env + blueprint.yaml + .env.example). Covers the stack-doctor lint script, the Komodo GitOps deploy, the Pangolin Traefik routing, the Locket + Infisical secret injection, the 5-stage deploy procedure, and the 3-tier host convergence (arm1-oci / bunchloch / cax41-hetzner). Triggers: 'add a stack', 'fix stack', 'stack-doctor', 'GOLD_STANDARD', 'compose.yaml', 'sidecar.yaml', 'pangolin.yaml', 'blueprint.yaml', 'Locket sidecar', 'Infisical secret', '94 stacks', 'stacks inventory'.
---

# Infrastructure Stacks — Router

The Cianfhoghlaim platform runs 94+ Docker Compose stacks under
`infrastructure/stacks/`. This skill is the router — pick the
right skill for the task.

## The 6-file GOLD_STANDARD pattern

Every stack MUST have these 6 files:

| File | Purpose |
|:--|:--|
| `compose.yaml` | Docker service definitions (the actual stack) |
| `compose.dev.yaml` | Dev override: no-op `locket` shim, `env_file: ../../../../.env` |
| `sidecar.yaml` | Production override: real `locket:1.2.3` sidecar with Infisical secrets |
| `pangolin.yaml` | Traefik routing + TinyAuth (if web-facing) |
| `secrets.env` | Infisical URI references (zero plaintext) |
| `blueprint.yaml` | Komodo stack metadata (name, ports, depends_on) |

The `.env.example` is the 7th file (dev-only placeholder).

## The 5-stage deploy procedure

```
1. Pulumi + OCI   → arm1-oci instance, public IP, Infisical handoff
2. Ansible        → Pangolin + Komodo installed on each host
3. Pangolin       → VPN mesh + Traefik + Pocket ID SSO
4. Infisical      → dev-baile vault hydrated
5. Komodo         → fleet orchestrator with all 94 stack blueprints
```

After all 5 stages, the stack is deployable via
`komodo run <stack>`.

## The 3-tier host convergence

| Host | Role | Stacks |
|:--|:--|:--|
| `arm1-oci` (Oracle Cloud Ampere A1) | Control plane: Komodo + Pangolin + Pocket ID | Komodo, Pangolin, Pocket ID, Forgejo, agents |
| `bunchloch` (MacBook M4) | Workload: Dagster + LiteLLM + 70+ models + the lakehouse | oideachais, litellm, langfuse, lancedb, mlx-omni, dagster, all the ML stacks |
| `cax41-hetzner` (Hetzner) | Storage: Garage + Lakekeeper + Postgres | garage, lakekeeper, lakehouse, the storage layer |

The 94 stacks are not duplicated across hosts. Each stack has
a single `run_directory` and a `depends_on` list that names its
siblings.

## The 11 inventory categories (post-flattening)

The 5 legacy category subdirectories (`storage/`, `infrastructure/`,
`engineering/`, `machine_learning/`, `tools/`) have been
**removed** (commit `c27919921` — 2026-06-23). Every stack now
lives at `infrastructure/stacks/<name>/` directly. The 11
current categories (informational, not structural):

1. Control plane (10 stacks)
2. Storage (4 stacks)
3. Engineering (10 stacks)
4. Machine learning (12 stacks)
5. Tools (17 stacks)
6. Browser (1 stack)
7. Workflow + scheduling (5 stacks)
8. Web + frontend (3 stacks)
9. Knowledge + agents (6 stacks)
10. Data + DBs (8 stacks)
11. Observability + monitoring (5 stacks)

For the live inventory, see `infrastructure/AGENTS.md` "Stack
Inventory" table.

## The 5 integration points

| Point | What it is | Where to look |
|:--|:--|:--|
| **Pangolin Traefik** | Reverse proxy + forwardAuth | `pangolin.yaml` per stack |
| **Locket sidecar** | Per-stack Infisical secret injector | `sidecar.yaml` + `secrets.env` |
| **Komodo** | GitOps orchestrator | `blueprint.yaml` + `komodo/` procedure |
| **LiteLLM gateway** | LLM proxy (all agents + Dagster route through) | env vars: `LITELLM_URL`, `LITELLM_MASTER_KEY` |
| **Langfuse** | LLM observability | env vars: `LANGFUSE_HOST`, `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY` |

## The port allocation map

| Range | Reserved for | KCG stacks |
|:--|:--|:--|
| 3000-3499 | User apps | langfuse, forgejo, the web frontends |
| 3500-3999 | APIs | oideachais-api (8000, drift), croilar-hono-api |
| 4000-4499 | Dagster | dagster, oideachais-dagster |
| 5000-5499 | Data | lancedb, motherduck, duckdb, dbgate |
| 6000-6999 | AI/ML | mlx-omni, invokeai, langfuse-prompt, ollama |
| 7000-7999 | Dev tools | marimo, oideachais-agent-os (7777), oideachais-adk-agents (7778) |
| 8000-8999 | MMO + high-port APIs | tuatha-mmo, the oRPC servers |
| 9000-9999 | Infra | komodo, monitor, k8s panels |

For the full port map, see `kcg-convergence/SKILL.md`.

## Pair this skill with

- `kcg-convergence/SKILL.md` — the full flat layout + port map
- `kcg-bunchloch/SKILL.md` — the 3-tier host convergence detail
- `stack-ops/SKILL.md` — the operational skill for adding/fixing
  stacks
- `pangolin/SKILL.md` — the VPN + Traefik detail
- `komodo/SKILL.md` — the fleet orchestrator
- `secrets-management/SKILL.md` — Infisical + Locket pattern
- `dagger-pipelines/SKILL.md` — the Dagger CI/CD
- `pulumi/SKILL.md` — the cloud infrastructure (OCI + Hetzner)

## Cross-references

- [infrastructure/AGENTS.md](../infrastructure/AGENTS.md) — the
  canonical stack inventory
- [infrastructure/QUADRANT-TO-STACK-MAP.md](../infrastructure/QUADRANT-TO-STACK-MAP.md) — quadrant → stack routing
- [infrastructure/stacks/HEALTH_REPORT.md](../infrastructure/stacks/HEALTH_REPORT.md) — live health of all 94 containers
