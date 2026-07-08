# bonneagar/iac — The merged Komodo + Pangolin + Infisical IaC

The unified TypeScript IaC that orchestrates the 3 systems
(Komodo + Pangolin + Infisical) into a single codebase.

## What it does

Replaces the 5 v0 TypeScript files at `iac/komodo/` (config,
komodo-rpc, deploy-stacks, create-resources, read-state)
+ the 3 bash scripts at `scripts/` (setup-pangolin-komodo,
sync-blueprints, create-olm-clients) + the 2 vault scripts at
the repo root (create-env, init-vault).

## The 8 orchestration commands

The v5 drift refactor (per
`openspec/changes/2026-07-01-bonneagar-v5-drift-refactor-and-komodo-gitops`)
consolidated 15 → 8 IaC commands. The 2 removed commands
(`iac:sync:procedures` + `iac:sync:resource-syncs`) are now owned
by Komodo's resource-syncs (the 3 declared at
`komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml`).
Procedures and resource-syncs are GitOps artifacts, not state
mutations, so the IaC no longer pushes them — Komodo auto-pulls.

| Command | Purpose | Systems |
|:--|:--|:--|
| `iac` | Omnibus entry: `bun run iac/cli.ts <cmd>` | All 3 |
| `iac:plan` | Show diff between IaC-declared and actual state | All 3 |
| `iac:bootstrap` | 1-command full bootstrap (Pulumi → Infisical → Pangolin → Komodo Core → Komodo Periphery → Newt → resource-syncs → all syncs) | All 3 |
| `iac:deploy` | Deploy the 30 key stacks end-to-end (8 sync sub-commands) | All 3 |
| `iac:teardown` | Reverse of bootstrap (requires `--force`) | All 3 |
| `iac:health` | Health check all 3 systems + verify the 3 resource-syncs are registered | All 3 |
| `iac:sync:secrets` | Sync Infisical secrets from `secrets.env` refs | Infisical |
| `iac:sync:resources` | Sync Pangolin private resources (DELETE-then-CREATE the 3 manual ones) | Pangolin |
| `iac:sync:variables` | Sync Komodo variables (cross-stack env vars) | Komodo |
| `iac:sync:action-recipients` | Sync Komodo ActionRecipients | Komodo |
| `iac:sync:olm` | Sync Pangolin OLM clients (idempotent getOrCreateOlmClient) | Pangolin |
| `iac:sync:monitors` | Sync Komodo monitors (opt-in, deprecated post-v5) | Komodo |
| `iac:sync:alerts` | Sync Komodo alerts (opt-in, deprecated post-v5) | Komodo |
| `iac:sync:schedules` | Sync Komodo schedules (opt-in, deprecated post-v5) | Komodo |

> **Removed in v5 (no v0 backward-compat aliases):**
> - `iac:sync:procedures` — now owned by the 3 Komodo resource-syncs
> - `iac:sync:resource-syncs` — same; Komodo auto-pulls from `komodo/resource-syncs/*.toml`

## Flags

- `--dry-run` — don't mutate anything
- `--force` — skip confirmation prompts (required for `iac:teardown`)
- `--verbose` — verbose output
- `--stack=<name>` — limit to a single stack
- `--with-blueprint-import` — use the Pangolin blueprint-import API (faster bootstrap; not yet implemented)
- `--with-monitors` — also sync Komodo monitors
- `--with-alerts` — also sync Komodo alerts
- `--with-schedules` — also sync Komodo schedules
- `--skip=<phase>` — for `iac:bootstrap`: skip one of the 8 phases
  (`pulumi`, `infisical`, `pangolin`, `komodo-core`, `komodo-periphery`,
  `newt`, `resource-syncs`, `all-syncs`). Useful for re-running a single
  phase after a failure (e.g. `--skip=pulumi --skip=infisical` to
  re-run from Pangolin onwards).

## The 4 source-discoverers

- `sources/discover-stacks.ts` — walks `bonneagar/stacks/*/compose.yaml` (86 stacks post-v5)
- `sources/discover-resources.ts` — walks `bonneagar/stacks/*/pangolin.yaml` (~30 Pangolin-routed)
- `sources/discover-secrets.ts` — walks `bonneagar/stacks/*/secrets.env` (200+ Infisical refs, 2-segment canonical URI)
- `sources/key-stacks.ts` — the curated 30-stack list (5-group model filter; phantom names removed in v5)

## The 3 typed clients

- `clients/komodo-client.ts` — `KomodoClient` (18 methods, hand-rolled `fetch()`; the v0 `komodo_client` npm package has a `localStorage` browser bug)
- `clients/pangolin-client.ts` — `PangolinClient` (12 methods; uses the official Pangolin **Integrations API** at `${PANGOLIN_URL}/v1` + `/api/v1/integration/...`; verified by `PANGOLIN_LICENCE=PER-...`)
- `clients/infisical-client.ts` — `InfisicalClient` (10 methods; uses the official `@infisical/sdk`)

## The 4 blockers from `DEPLOYMENT-STRATEGY.md` that the IaC fixes

| # | Blocker | IaC fix |
|--:|:--|:--|
| 1 | Newt 1.12.5 + Pangolin 1.18.4 incompatible | `iac:bootstrap` pins compatible versions |
| 2 | 3 manual Pangolin resources override the blueprints | `iac:sync:resources` DELETE-then-CREATE |
| 3 | `PANGOLIN_API_KEY` returns 401 | `auth.ts:ensurePangolinAuth()` re-mints |
| 4 | `komodo-locket` sidecar `${INFISICAL_CLIENT_ID}` literal | `auth.ts:ensureInfisicalAuth()` mints new machine identity |

## Usage

```bash
# Add the @infisical/sdk (one-time)
cd bonnegar && bun install

# Health check
bun run iac:health

# Plan (diff IaC-declared vs actual)
bun run iac:plan

# Plan in dry-run mode
bun run iac:plan --dry-run

# Deploy the 30 key stacks
bun run iac:deploy

# Full bootstrap (Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs)
bun run iac:bootstrap

# Sync just the secrets
bun run iac:sync:secrets

# Sync just the resources (DELETE-then-CREATE the 3 manual ones)
bun run iac:sync:resources

# Sync monitors (opt-in)
bun run iac:sync:monitors --with-monitors
```

## Cross-references

- `openspec/specs/bonneagar-iac-merge/spec.md` — the canonical capability spec
- `openspec/changes/2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical/` — the openspec change artifacts
- `bonneagar/iac/README.md` — this file
