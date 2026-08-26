# `bonneagar/` — Infrastructure as Code (IaC) subdirectory

> **The unified TypeScript IaC + Docker Compose stack catalogue + Komodo GitOps fleet + Pangolin reverse-proxy + Infisical secrets + Locket sidecar injection for the Cianfhoghlaim self-hosted platform.**
>
> This subdirectory was re-merged into the cianfhoghlaim monorepo on **2026-07-17** (per the `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1` openspec change). Previously it was a separate GitHub repo at `github.com/cianfhoghlaim/bonneagar` (now an archived read-only remote at `archive-bonneagar`).

## Priority quick reference

The 8 priority commands + the 4 priority skills + the 4 priority compose stacks + the 4 priority openspec specs at a glance.

### Priority skills (4 of 53)

| Skill | When to load |
|:--|:--|
| `infrastructure-stacks` | The 6-file GOLD_STANDARD pattern for Docker Compose stacks + stack-doctor CI gate |
| `komodo-gitops` | The 4 resource-syncs + the 8-phase `iac:bootstrap` state machine |
| `pangolin-integrations-api` | The Pangolin Enterprise Edition Integrations API (the v2 REST surface) |
| `secrets-management` | The Infisical + Locket + mise three-way secrets contract |

### Priority commands

```bash
# Health check all 3 systems (Komodo + Pangolin + Infisical + Newt + Pocket ID + Tinyauth = 6-way)
mise run iac-health          # alias: bun run iac:health
# Plan (diff IaC-declared vs actual state across the 3 systems)
mise run iac-plan            # alias: bun run iac:plan
# Full bootstrap (Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs)
mise run iac-bootstrap        # alias: bun run iac:bootstrap
# Validate all 100 stacks against the 6-file GOLD_STANDARD
mise run cic:stack-doctor    # the stack-doctor audit (CI gate)
# CI-strict variant: stack-doctor --strict --check-grammar
mise run stack-doctor:strict # fails on missing infisical:// refs OR mixed bare/Jinja grammar in any secrets.env (NEW in Change 1, 2026-07-30)
# One-command 7-phase full-stack deploy orchestrator
mise run deploy:full         # resumable checkpoint at ~/.cianfhoghlaim/deploy-state.json (NEW in Change 3, 2026-08-01)
# Mandatory preflight before any arm1-oci mutation
mise run preflight-arm-oci   # ALIAS NOTE: docs say preflight:arm-oci but the canonical name uses a hyphen
```

### Priority compose stacks (the 6-stack critical path on `bunchloch`)

```
Infisical → Garage (garage) → Lakehouse (lakehouse)
  → LiteLLM (litellm) → Langfuse (langfuse)
  → Cognee (cognee)
```

These six must exist (in that order) before any data pipeline can run.

### Priority openspec specs (4 of 48)

| Spec | One-liner |
|:--|:--|
| [`infrastructure-stacks`](../../openspec/specs/infrastructure-stacks/spec.md) | The 88 Docker Compose stacks at `bonneagar/stacks/` + stack-doctor + Pangolin + Infisical + Locket + Komodo resource-syncs |
| [`bonneagar-iac-merge`](../../openspec/specs/bonneagar-iac-merge/spec.md) | The unified TypeScript IaC at `bonneagar/iac/` (Komodo + Pangolin + Infisical clients) |
| [`bonneagar-komodo-gitops`](../../openspec/specs/bonneagar-komodo-gitops/spec.md) | The 3 resource-syncs (`arm1-oci.toml`, `bunchloch.toml`, `cross-cutting.toml`) + 8-phase bootstrap state machine |
| [`agent-platform-cluster`](../../openspec/specs/agent-platform-cluster/spec.md) | The 8-stack agent-platform cluster (lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb) + 3 agent surfaces (openclaw + openchamber + hermes) |

### Priority mise tasks

```bash
mise run lint:skills         # validate .agents/skills/ metadata (53/53 pass)
mise run sync                # mise install + uv sync + bun install
mise run iac:health          # 6-way health check
```

## `deploy:full` orchestrator

`mise run deploy:full` is the one-command, end-to-end bringup for the entire platform. It is invoked as a **shell entry** (`scripts/deploy-full.sh`) that runs `preflight-arm-oci` then delegates to a **TypeScript state machine** (`scripts/deploy-full.ts`) which owns the resumable checkpoint at `~/.cianfhoghlaim/deploy-state.json`. The state machine walks 10 ordered phases — `(1) preflight-arm-oci → (2) iac-auth-rotate → (3) pocketid-oidc-wire → (4) pangolin-client-install → (5) control-plane-up → (6) lakehouse-up → (7) data-stacks-up → (8) ocr-backends-up → (9) agent-surfaces-up → (10) dagster-materialize-and-sensor-health-gate` — and skips any phase whose checkpoint is already `success`. Re-run with no args to resume from the last failed phase; pass `--phase=N` to run a single phase or `--dry-run` to log without mutating state. Shipped by openspec Change 3 (`2026-08-01-lakehouse-and-reproducible-deploy-v1`) and extended to 10 phases by the `2026-08-15-pangolin-pocketid-komodo-infisical-mesh-remediation-v1` change; see [`scripts/deploy-full.ts`](scripts/deploy-full.ts) + [`scripts/deploy-full.sh`](scripts/deploy-full.sh).

## Overview

`bonneagar/` is the **IaC subdirectory** of the Cianfhoghlaim monorepo. It houses:

- **`iac/`** — The merged TypeScript IaC (3 typed clients + 4 discoverers + 26 CLI commands — added `iac:bootstrap-pangolin-client` + `iac:sync:clients` in the 2026-08-15 openspec change). The canonical entry point for `iac:*` operations.
- **`stacks/`** — **93 directories** forming the Docker Compose stack catalogue (added `stacks/newt-arm1-oci/` in the 2026-08-15 openspec change). 81 of them follow the 6-file GOLD_STANDARD pattern (`compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`).
- **`komodo/`** — Raw GitOps resources that Komodo Core pulls via Forgejo: **116 stack TOML files**, **63 procedure TOML files** (added 2 for deploy-pangolin-client-arm1-oci + deploy-pangolin-client-bunchloch), **4 resource-syncs**, **3 builds**, **1 server**.
- **`pangolin/`** — Pangolin config: 3 YAML files (`agent-fleet.yaml` + `blueprint.yaml` + `private-resources.blueprint.yaml`) + 4 sub-dirs.
- **`deploy-runbooks/`** — 7 markdown runbooks for the user-named deploy targets (full-local-agent-platform-stack, local-infisical, openclaw-hermes, pocketid-pangolin-komodo, repair-pangolin, agent-fleet-arm1-oci, agent-fleet-bunchloch).
- **`dagger/`** — Dagger CI/CD module (Python + TS) with 8 callable functions across 3 pipelines.
- **`locket-shim/`** — Drop-in replacement for the `bpbradley/locket:infisical` sidecar. Fixes the camelCase Infisical v0.161+ REST API mismatch.
- **`scripts/`** — Three seeded scripts (bons-locket-shim.py duplicate, seed-bunchloch-fallback-vault.sh, seed-bunchloch-litellm-langfuse-fallback.sh).
- **`blueprints/`** — 1 Pangolin blueprint (`agent-fleet-bp.yaml`) bundling the 12-agent private resources.
- **`legacy/`** — 1 README explaining the migration of 4 legacy TS scripts to Komodo actions/procedures.
- **`_archive/`** — 1 archived file (the Komodo-flavoured 6-file contract, superseded by `bonneagar/stacks/GOLD_STANDARD.md`).
- **`stedding/`** — Empty placeholder; canonical GGUF cache mount path.

## The 93-stack inventory

The canonical inventory lives at `bonneagar/stacks/INDEX.md` (auto-generated by the stack-doctor audit). The live count is 100 stacks (lowercase directories; added `stacks/newt-arm1-oci/` in the 2026-08-15 openspec change). 86 of them follow the 6-file GOLD_STANDARD contract; the 12 outliers are:

| Stack | Missing | Reason |
|:--|:--|:--|
| `browser` | `sidecar.yaml` + `secrets.env` + `blueprint.yaml` + `.env.example` | Deferred per stack-doctor TODO |
| `chartdb` | Same as above | Deferred |
| `komga` | Same as above | Deferred |
| `ludusavi` | Same as above | Deferred |
| `moonlight` | Same as above | Deferred |
| `mylar3` | Same as above | Deferred |
| `storybook` | Same as above | Deferred |
| `wave2` | Same as above | Meta-stack (sentinel placeholder) |
| `motherduck` | `blueprint.yaml` (no komodo.toml either) | Pangolin-exempt |
| `pangolin` | `blueprint.yaml` | Self-referential (the Pangolin control plane itself) |
| `croilar` | `blueprint.yaml` | Pangolin-exempt |
| `newt` | `compose.yaml` | Non-Docker stack (WireGuard tunnel client binary) |

`wave2/` is a meta-stack directory containing 7 sub-stacks (`kavita/`, `immich/`, `khoj/`, `outline/`, `mealie/`, `siyuan/`, `letta/`); its `compose.yaml` is a sentinel placeholder.

`newt/` is a non-Docker stack (WireGuard tunnel client binary); it has `newt.yaml` + `newt.sidecar.yaml` + `newt.secrets.env` but no `compose.yaml`.

## The IaC TypeScript sub-package (`iac/`)

**`bonneagar/iac/`** contains **24 CLI commands** in `commands/` + **3 typed clients** in `clients/` + **4 discoverers** in `sources/` + **3 Pulumi modules** in `pulumi/`.

### The 24 CLI commands

| Command | Purpose |
|:--|:--|
| `iac:plan` | Show diff between IaC-declared and actual state (filesystem-only in CI; full API diff with credentials) |
| `iac:deploy` | Deploy the 30 key stacks end-to-end |
| `iac:bootstrap` | 1-command full bootstrap (Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs) |
| `iac:teardown` | Reverse of bootstrap (requires `--force`) |
| `iac:health` | 6-way health check |
| `iac:rotate-auth` | Rotate Pocket ID OIDC client secret |
| `iac:sync:secrets` | Sync Infisical secrets from `secrets.env` refs |
| `iac:sync:resources` | Sync Pangolin private resources (DELETE-then-CREATE the 3 manual ones) |
| `iac:sync:procedures` | Sync Komodo procedures from `*.toml` |
| `iac:sync:resource-syncs` | Sync Komodo resource-syncs from `*.toml` |
| `iac:sync:monitors` | Sync Komodo monitors (opt-in via `--with-monitors`) |
| `iac:sync:alerts` | Sync Komodo alerts (opt-in via `--with-alerts`) |
| `iac:sync:variables` | Sync Komodo variables (cross-stack env vars) |
| `iac:sync:schedules` | Sync Komodo schedules (opt-in via `--with-schedules`) |
| `iac:sync:action-recipients` | Sync Komodo ActionRecipients |
| `iac:sync:olm` | Sync Pangolin OLM clients |
| `iac:bootstrap-pocketid-admin` | Bootstrap Pocket ID admin user |
| `iac:bootstrap-infisical` | Bootstrap the Infisical instance |
| `iac:bootstrap-locket-binary` | Build the bons-locket-shim Docker image |
| `iac:bootstrap-control-plane` | Bootstrap the control plane (arm1-oci + bunchloch) |
| `iac:bootstrap-control-plane-bunchloch` | Bootstrap control plane on `bunchloch` |
| `iac:bootstrap-control-plane-arm1-oci` | Bootstrap control plane on `arm1-oci` |
| `iac:wire-pocketid-as-oidc` | Wire Pocket ID as OIDC for Komodo |
| `iac:deploy-periphery` | Deploy a Komodo Periphery agent |
| `iac:deploy-newt` | Deploy a Newt Pangolin client |

### Flags (common to all commands)

- `--dry-run` — don't mutate anything
- `--force` — skip confirmation prompts (required for `iac:teardown`)
- `--verbose` — verbose output
- `--stack=<name>` — limit to a single stack
- `--with-blueprint-import` — use the Pangolin blueprint-import API (faster bootstrap; not yet implemented)
- `--with-monitors` / `--with-alerts` / `--with-schedules` — opt-in extras

### The 4 source-discoverers

- `sources/discover-stacks.ts` — walks `bonneagar/stacks/*/compose.yaml` (100 stacks)
- `sources/discover-resources.ts` — walks `pangolin.yaml` files (~30 Pangolin-routed)
- `sources/discover-secrets.ts` — walks `secrets.env` files (200+ Infisical refs)
- `sources/key-stacks.ts` — the curated 30-stack list (5-group model filter)

### The 3 typed clients

- `clients/komodo-client.ts` — `KomodoClient` (27 methods, hand-rolled `fetch()`; the v0 `komodo_client` npm package has a `localStorage` browser-only bug)
- `clients/pangolin-client.ts` — `PangolinClient` (16 methods; uses the official Pangolin **Enterprise Edition Integrations API** at `${PANGOLIN_URL}/v1` + `/api/v1/integration/...`; verified by `PANGOLIN_LICENCE=PER-...`)
- `clients/infisical-client.ts` + `clients/infisical-rest.ts` — `InfisicalClient` (10 class delegations) + `infisical-rest.ts` (14 REST helpers that bypass the buggy `@infisical/sdk` v5.0.2)

## The Komodo resource-syncs (`komodo/resource-syncs/`)

The 4 resource-syncs pull from `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway` on every commit (interval 60s, `on_pull: true`, `delete: false`, `managed: true`):

| Resource-sync | Hosts | What it pulls |
|:--|:--|:--|
| `arm1-oci.toml` | arm1-oci | control plane (pangolin + komodo + infisical + backrest + hermes + openclaw + openchamber + observability/logfire/dozzle/beszel) |
| `bunchloch.toml` | bunchloch | workload plane (cianfhoghlaim + meaisínfhoghlaim + croílár + litellm + langfuse + mlflow + logfire + dagster + lakehouse + cognee + lancedb + hermes + openclaw + openchamber + mailcow + browser + media + newt + komodo-periphery) |
| `cross-cutting.toml` | both | 10 cross-host prerequisite procedures (pangolin-first + komodo-core + infisical-first + locket-deploy + 5 deploy procedures) — must run before per-host syncs |
| `storage-infrastructure.toml` | both | Covers `komodo/{servers,stacks,procedures,actions,resource-syncs}/*.toml` |

## The Locket shim (`locket-shim/`)

A 295-line Python script (`cianfhoghlaim-locket-shim.py`) that replicates the `bpbradley/locket:infisical` sidecar but uses the **correct camelCase field names** (`projectId`, `secretPath`, `secretType`) for the Infisical v0.161+ REST API. The upstream `locket v0.17.3` ships snake_case and 422s on every call; this shim is the workaround until `locket v0.18.0-rc.1` ships.

Built as `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` on `python:3.12-alpine` with a non-root user (`65532:65532`).

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new Docker Compose stack | `bonneagar/stacks/<name>/` (6-file GOLD_STANDARD pattern) |
| Modify the IaC CLI surface | `bonneagar/iac/commands/<command>.ts` |
| Add a new IaC command | `bonneagar/iac/commands/<command>.ts` + register in `iac/cli.ts` + register in `bonneagar/package.json` `scripts` block |
| Add a Komodo procedure | `bonneagar/komodo/procedures/<name>.toml` |
| Add a Komodo resource-sync | `bonneagar/komodo/resource-syncs/<host>.toml` |
| Modify the 12-agent fleet's Pangolin routes | `bonneagar/pangolin/agent-fleet.yaml` |
| Bootstrap a new cluster | `./scripts/onboard-pocketid.sh` (3-question wizard) |
| Wire Pocket ID to Pangolin + Komodo | `./scripts/wire-pocketid-pangolin-komodo.sh` |
| Bind PocketID to all Pangolin Resources | `./scripts/wire-pocketid-resource-idp.sh --all` |
| Diagnose IaC health | `mise run iac:health` |
| Pull all current state | `mise run iac:plan` |

## Cross-references

- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../openspec/specs/infrastructure-stacks/spec.md`](../openspec/specs/infrastructure-stacks/spec.md) — canonical spec for the 89-stack catalogue
- [`../openspec/specs/bonneagar-iac-merge/spec.md`](../openspec/specs/bonneagar-iac-merge/spec.md) — canonical spec for the TypeScript IaC
- [`../openspec/specs/bonneagar-komodo-gitops/spec.md`](../openspec/specs/bonneagar-komodo-gitops/spec.md) — canonical spec for the Komodo resource-syncs
- [`./iac/README.md`](iac/README.md) — the IaC sub-package doc
- [`./stacks/README.md`](stacks/README.md) — the stacks sub-package doc
- [`./stacks/GOLD_STANDARD.md`](stacks/GOLD_STANDARD.md) — the 6-file template
- [`./stacks/INDEX.md`](stacks/INDEX.md) — the live stack inventory (auto-generated)
- [`./komodo/README.md`](komodo/README.md) — the Komodo sub-package doc
- [`./deploy-runbooks/`](./deploy-runbooks/) — 7 user-facing deploy runbooks
- [`../.agents/skills/stack-ops/SKILL.md`](../.agents/skills/stack-ops/SKILL.md) — the agent skill for adding/fixing stacks