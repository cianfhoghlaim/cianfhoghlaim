# Bonneagar — AI Agent Instructions

> **Bonneagar** — Scottish Gaelic for *infrastructure*. This repo
> is the standalone GitOps foundation layer for the
> cianfhoghlaim constellation. See [`README.md`](./README.md)
> for orientation and [`DEPLOYMENT-STRATEGY.md`](./DEPLOYMENT-STRATEGY.md)
> for the bring-up playbook.

> **v4 consolidation (2026-06-29):** the canonical stack
> location is **`bonneagar/stacks/`** (88 stacks). The previous
> v4-canonical `infrastructure/` dir + the premature
> `cianfhoghlaim/stacks/` split have both been removed. The
> 88 stacks are documented at
> [`../cianfhoghlaim/docs/stacks/<name>.md`](../../cianfhoghlaim/docs/stacks/)
> (the "purpose + why-GitOps" docs).

## Priority quick reference

The 4 priority compose stacks, the 4 priority skills, and the
4 priority commands at a glance. **Read this first**; the
rest of the file is the full 88-stack inventory + the IaC
entry points.

### Priority compose stacks (4 of 88)

| Stack | Port | Domain | Purpose |
|:--|--:|:--|:--|
| `oideachais` | 3080, 3335, 7777, 7778, 8000 | `oideachais.cianfhoghlaim.ie` | Celtic Education Lakehouse (Dagster + FastAPI + TanStack Start + Agno AgentOS + Google ADK) |
| `litellm` | 4000 | `litellm.cianfhoghlaim.ie` | LLM gateway (OpenAI-compatible proxy for 70+ models) |
| `langfuse` | 3000 | `langfuse.cianfhoghlaim.ie` | LLM observability (traces, prompts, A/B tests) |
| `lakehouse` | 3900-3904, 5433, 8181-8182 | internal | Garage S3 + Postgres + Lakekeeper (data plane) |
| `hermes` | 9119, 9120, 8443, 8090, 8080, 8645 | `hermes.cianfhoghlaim.ie` | Hermes autonomous agent runtime (3rd vertex; NousResearch/hermes-agent v0.17.0; bunchloch) |

### Priority skills (4 of 8)

The full `.agents/skills/` library lives in the
[cianfhoghlaim/cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim)
monorepo. The four skills below are the ones an agent working
in this repo will reach for first.

| Skill | When to load |
|:--|:--|
| [`stack-ops`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/stack-ops/SKILL.md) | Add / fix / audit a Docker Compose stack (the 6-file GOLD_STANDARD pattern) |
| [`infrastructure-stacks`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/infrastructure-stacks/SKILL.md) | The router for the 88 stacks + the 3-tier host convergence + the 5-stage deploy |
| [`secrets-management`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/secrets-management/SKILL.md) | Infisical + Locket + mise 3-way contract (no manual `.env`) |
| [`pangolin`](https://github.com/cianfhoghlaim/cianfhoghlaim/tree/main/.agents/skills/pangolin/SKILL.md) | VPN + Traefik + Pocket ID SSO (Pangolin Convergence Architecture) |

### Priority commands

```bash
bun run validate-stacks           # stack-doctor: lint all 88 compose.yaml files
mise run lint:skills              # validate skill frontmatter (lives in cianfhoghlaim)
bun run iac:bootstrap              # Komodo deploy-stacks + create-resources + read-state
./scripts/stack.sh <name> up -d   # start a stack with optional Locket injection
```

### IaC entry points (4 scripts at the root of `bonneagar/`)

```bash
bun run iac:deploy-stacks          # upsert the 88 stacks into Komodo
bun run iac:create-resources       # upsert the 88 Pangolin private resources
bun run iac:read-state             # dump current Komodo + Pangolin state
bun run iac:bootstrap              # the 1-command full sync
```

The IaC TypeScript client lives at `iac/komodo/` (5 files:
`config.ts`, `komodo-rpc.ts`, `deploy-stacks.ts`,
`create-resources.ts`, `read-state.ts`). The
`package.json` + `tsconfig.json` + `bun.lock` are hoisted
to the root of `bonneagar/` for the future split into
`github.com/cianfhoghlaim/bonneagar`.

## The 5-group model (88 stacks)

The 88 stacks are organised into 5 logical groups
(informational only; not a deploy-time constraint):

| Group | Count | Host | Examples |
|:--|--:|:--|:--|
| **infrastructure** | 9 | arm1-oci | Pangolin, Pocket ID, TinyAuth, Traefik, Infisical, Locket, Komodo Core + Periphery, Backrest |
| **data-engineering** | 12 | bunchloch | Dagster, Lakehouse, Marimo, CocoIndex, Cognify, Litellm, Langfuse, Llama-swap |
| **agent-platform** | 7 | bunchloch | Agno AgentOS, Google ADK, OpenClaw, OpenChamber, Cognee, Graphiti, Letta |
| **language-model** | 6 | bunchloch | LiteLLM, llama-swap, MLX-Omni, Logfire, Langfuse, mlflow |
| **user-facing-web** | 6 | bunchloch | oideachais-web, oideachais-api, oideachais-dagster, oideachais-agent-os, oideachais-adk-agents, openclaw |
| **ci** | 1 | bunchloch | hf-watchdog |

The remaining 47 stacks are personal/utility (audiobookshelf,
beszel, bytebase, cal-diy, changedetection, coder, convex,
crawl4ai, dozzle, enclosed, forgejo, forgejo-runner, frontend,
glance, gluetun, headplane, headscale, it-tools, Kapowarr,
karakeep, lakefs, lakehouse-oci, lakekeeper, LetterFeed,
linkwarden, lmnr, …).

## Where things live

| Concern | Location |
|:--|:--|
| Stack catalogue (88 stacks) | [`stacks/`](./stacks/) |
| Stack conventions | [`GOLD_STANDARD.md`](./GOLD_STANDARD.md) |
| Bring-up playbook | [`DEPLOYMENT-STRATEGY.md`](./DEPLOYMENT-STRATEGY.md) |
| Per-stack docs (purpose + why-GitOps) | [`../cianfhoghlaim/docs/stacks/`](../../cianfhoghlaim/docs/stacks/) |
| IaC TypeScript client (5 files) | [`iac/komodo/`](./iac/komodo/) |
| IaC root manifest (package.json + tsconfig.json + bun.lock) | [`package.json`](./package.json), [`tsconfig.json`](./tsconfig.json), [`bun.lock`](./bun.lock) |
| Pangolin mesh | [`pangolin/`](./pangolin/) + [`PANGOLIN-SETUP.md`](./PANGOLIN-SETUP.md) |
| Komodo fleet | [`komodo/`](./komodo/) (procedures, servers, sites, stacks) |
| Pulumi IaC | [`pulumi/`](./pulumi/) (OCI / Cloudflare / Azure) |
| Ansible bootstrap | [`ansible/`](./ansible/) (playbooks, roles, inventory) |
| Dagger pipelines (future) | [`dagger/`](./dagger/) (4 pipelines, 8 callable functions) |
| Secrets | [`SECRETS-MANAGEMENT.md`](./SECRETS-MANAGEMENT.md) |
| Long-form ops docs | [`docs/`](./docs/) |
| Per-host deploy runbooks | [`deploy-runbooks/`](./deploy-runbooks/) |

## Working with this repo

This repo is GitOps-first. All stack definitions live in
version control. Changes flow through PRs, not through manual
SSH. The Pangolin + Komodo + Pulumi stack ingests this repo
as the source of truth for fleet state.

### Code/ops split

- **`cianfhoghlaim/`** = the code (Python package, agents,
  web apps, BAML schemas, DLT sources, etc.)
- **`bonneagar/`** = the ops (Docker compose, Pangolin
  routing, Infisical secrets, Komodo orchestration, Backrest
  backups, IaC TypeScript client)

For each stack, the Python code (if any) lives at
`cianfhoghlaim/<code-path>` and the ops live at
`bonneagar/stacks/<name>/` (6-file GOLD_STANDARD). The
per-stack doc at `cianfhoghlaim/docs/stacks/<name>.md`
cross-references both.

### Secrets

Secrets are **never** in plaintext in this repo. Every
`secrets.env` is an Infisical-reference template
(`infisical://dev-baile/<stack>/<key>`). The Locket sidecar
resolves them at container runtime.

## Related repos

- [cianfhoghlaim/cianfhoghlaim](https://github.com/cianfhoghlaim/cianfhoghlaim)
  — the application monorepo that consumes this
  infrastructure. The `cianfhoghlaim/docs/stacks/<name>.md`
  per-stack docs live there.
- [cianfhoghlaim/leabharlann](https://github.com/cianfhoghlaim/leabharlann)
  — the digital library that also consumes parts of this
  mesh (e.g. the Gemma inference target via LiteLLM).
