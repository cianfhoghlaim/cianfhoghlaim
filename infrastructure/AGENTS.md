# Bonneagar — AI Agent Instructions

> **Bonneagar** — Scottish Gaelic for *infrastructure*. This repo is the
> standalone GitOps foundation layer for the cianfhoghlaim constellation.
> See [`README.md`](./README.md) for orientation and
> [`DEPLOYMENT-STRATEGY.md`](./DEPLOYMENT-STRATEGY.md) for the bring-up
> playbook.

## Priority quick reference

The 4 priority compose stacks, the 4 priority skills, and the
3 priority commands at a glance. **Read this first**; the rest
of the file is the full 90-stack inventory.

### Priority compose stacks (4 of 90)

| Stack | Port | Domain | Purpose |
|:--|--:|:--|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `oideachais.cianfhoghlaim.ie` | Celtic Education Lakehouse (Dagster + FastAPI + TanStack Start + Agno AgentOS + Google ADK) |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` | LLM gateway (OpenAI-compatible proxy for 70+ models) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` | LLM observability (traces, prompts, A/B tests) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal | Garage S3 + Postgres + Lakekeeper (data plane) |

### Priority skills (4 of 8)

The full `.agents/skills/` library lives in the
[cianfhoghlaim/cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim)
monorepo. The four skills below are the ones an agent working in
this repo will reach for first; the others are referenced by relative
link so an agent inside the monorepo can resolve them.

| Skill | When to load |
|:--|:--|
| [`stack-ops`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/stack-ops/SKILL.md) | Add / fix / audit a Docker Compose stack (the 6-file GOLD_STANDARD pattern) |
| [`infrastructure-stacks`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/infrastructure-stacks/SKILL.md) | The router for the 90 stacks + the 3-tier host convergence + the 5-stage deploy |
| [`secrets-management`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/secrets-management/SKILL.md) | Infisical + Locket + mise 3-way contract (no manual `.env`) |
| [`pangolin`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/pangolin/SKILL.md) | VPN + Traefik + Pocket ID SSO (Pangolin Convergence Architecture) |

### Priority commands

```bash
bun run validate-stacks           # stack-doctor: lint all 90 compose.yaml files
mise run lint:skills              # validate skill frontmatter (lives in cianfhoghlaim)
./scripts/stack.sh <name> up -d   # start a stack with optional Locket injection
```

## Where things live

| Concern | Location |
|:--|:--|
| Stack catalogue (90 stacks) | [`stacks/`](./stacks/) |
| Stack conventions | [`GOLD_STANDARD.md`](./GOLD_STANDARD.md) |
| Bring-up playbook | [`DEPLOYMENT-STRATEGY.md`](./DEPLOYMENT-STRATEGY.md) |
| Pangolin mesh | [`pangolin/`](./pangolin/) + [`PANGOLIN-SETUP.md`](./PANGOLIN-SETUP.md) |
| Komodo fleet | [`komodo/`](./komodo/) (procedures, servers, sites, stacks) |
| Pulumi IaC | [`pulumi/`](./pulumi/) (OCI / Cloudflare / Azure) |
| Ansible bootstrap | [`ansible/`](./ansible/) (playbooks, roles, inventory) |
| Dagger pipelines | [`dagger/`](./dagger/) (4 pipelines, 8 callable functions) |
| Secrets | [`SECRETS-MANAGEMENT.md`](./SECRETS-MANAGEMENT.md) |
| Long-form ops docs | [`docs/`](./docs/) |
| Per-host deploy runbooks | [`deploy-runbooks/`](./deploy-runbooks/) |

## Working with this repo

This repo is GitOps-first. All stack definitions live in version control.
Changes flow through PRs, not through manual SSH. The
[Pangolin](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/pangolin/SKILL.md) +
[Komodo](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/komodo/SKILL.md)
+ [Pulumi](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/pulumi/SKILL.md)
stack ingests this repo as the source of truth for fleet state.

Secrets are **never** in plaintext in this repo. Every `secrets.env` is an
Infisical-reference template (`infisical://dev-baile/<stack>/<key>`). The
[Locket](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/secrets-management/SKILL.md)
sidecar resolves them at container runtime.

## Related repos

- [cianfhoghlaim/cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim)
  — the application monorepo that consumes this infrastructure.
- [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann)
  — the digital library that also consumes parts of this mesh (e.g. the
  Gemma inference target via LiteLLM).