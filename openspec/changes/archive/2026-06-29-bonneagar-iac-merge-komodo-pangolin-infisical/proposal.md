# Change: 2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical

## Why

The bonneagar IaC is currently split across 3 disconnected
sub-circuits:

1. **Komodo** — `bonneagar/iac/komodo/{config,komodo-rpc,deploy-stacks,read-state}.ts` (4 files, ~430 LoC). Hand-rolled `fetch()` against the Komodo RPC API. Hardcodes 6 stacks + 2 servers. No auth recovery, no diff engine, no Blueprint/Monitor/Alert/Variable/Schedule coverage.

2. **Pangolin** — `bonneagar/iac/komodo/create-resources.ts` (1 file, 170 LoC). Uses the official Pangolin **Integrations API** at `${PANGOLIN_URL}/v1` (Enterprise Edition, confirmed by `PANGOLIN_LICENCE=PER-D09BF259-...`). Hardcodes 3 resources (komodo, calcom, infisical). No auto-derivation from `bonneagar/stacks/*/pangolin.yaml`. No blueprint import (the `/api/v1/integration/blueprint` bulk endpoint is unused).

3. **Infisical** — 0 IaC. The IaC reads vault refs from env vars but doesn't CREATE/UPDATE secrets. The 2 vault scripts (`scripts/create-env.ts` + `scripts/init-vault.ts`) are at the repo root, separate from the IaC.

Plus 3 pre-existing bash scripts at `bonneagar/scripts/`:
- `setup-pangolin-komodo.sh` (230 LoC) — 9-phase bootstrap (Pulumi → Infisical → Pangolin → Komodo → Newt → stacks)
- `sync-blueprints.sh` (100 LoC) — rsync all stack blueprints to Newt
- `create-olm-clients.sh` (90 LoC) — Dagger-based OLM client creation

This drift is dangerous because:

- The 3 systems (Komodo + Pangolin + Infisical) are **not synchronised** — a new secret in `.infisical.env` doesn't auto-propagate to the Komodo procedure that references it; a new Pangolin resource in `pangolin.yaml` doesn't auto-register in Komodo; a new Komodo procedure in `komodo/procedures/*.toml` doesn't auto-deploy.
- The 4 known blockers from `DEPLOYMENT-STRATEGY.md` are un-fixed: (1) Newt-Pangolin version mismatch, (2) 3 manually-created Pangolin resources override the blueprints, (3) `PANGOLIN_API_KEY` returns 401, (4) `komodo-locket` sidecar `${INFISICAL_CLIENT_ID}` literal.
- The v0 IaC is 5 TypeScript files in `iac/komodo/` but the IaC should live at `iac/` (the root) per the 2026-06-29 v4-consolidation change.

This change **merges the 3 systems into a single TypeScript codebase** at `bonneagar/iac/` (Bun + TypeScript + hand-rolled `fetch()` for Komodo + Pangolin; `@infisical/sdk` for Infisical). The new IaC:

- Auto-discovers every stack from `bonneagar/stacks/*/compose.yaml` (the 91 stacks)
- Auto-derives the 30 "key" stacks from the 5-group model (infrastructure / data-engineering / agent-platform / language-model / user-facing-web / ci)
- Uses the **Pangolin Integrations API** (per-resource CRUD for daily syncs; blueprint import as an opt-in for bootstrap)
- Uses **Infisical's official SDK** (`@infisical/sdk`) for secret CRUD
- Fixes the 4 known blockers end-to-end
- Replaces the 3 bash scripts with TypeScript equivalents (kept the bash scripts for backward compat; they're deprecated)

## What Changes

### 1. The new `iac/` structure (15+ new TypeScript files)

```
bonneagar/iac/                              # The new IaC home (replaces iac/komodo/)
├── clients/                              # The 3 typed clients
│   ├── komodo-client.ts                   # Komodo RPC + REST API client (extends v0)
│   ├── pangolin-client.ts                 # Pangolin Integrations API client (extends v0 + 6 new methods)
│   └── infisical-client.ts                # Infisical REST API client (NEW; uses @infisical/sdk)
├── models/                                # TypeScript types
│   ├── komodo.ts                           # Server, Stack, Procedure, ResourceSync, Monitor, Alert, Variable, Schedule, ActionRecipient
│   ├── pangolin.ts                         # Site, Resource, Target, Blueprint, OlmClient
│   └── infisical.ts                        # Project, Environment, Folder, Secret, MachineIdentity
├── sources/                               # State declaration (the IaC "source of truth")
│   ├── discover-stacks.ts                  # Walks bonneagar/stacks/*/compose.yaml → typed Stack[]
│   ├── discover-resources.ts               # Walks bonneagar/stacks/*/pangolin.yaml → typed PangolinResource[]
│   ├── discover-secrets.ts                 # Walks bonneagar/stacks/*/secrets.env → typed InfisicalSecret[]
│   └── key-stacks.ts                       # The curated 30-stack list (5-group model filter)
├── commands/                              # The CLI commands
│   ├── plan.ts                             # Diff IaC-declared vs actual state (the 3 systems)
│   ├── deploy.ts                           # Deploy the key stacks end-to-end (Infisical → Komodo → Pangolin)
│   ├── sync-secrets.ts                     # Sync Infisical secrets
│   ├── sync-resources.ts                   # Sync Pangolin private resources (DELETE-then-CREATE the 3 manual ones)
│   ├── sync-procedures.ts                  # Sync Komodo procedures from bonneagar/komodo/procedures/*.toml
│   ├── sync-resource-syncs.ts              # Sync Komodo resource-syncs from bonneagar/komodo/resource-syncs/*.toml
│   ├── sync-monitors.ts                    # Sync Komodo monitors (HTTP health checks)
│   ├── sync-alerts.ts                      # Sync Komodo alerts (failure notifications)
│   ├── sync-variables.ts                   # Sync Komodo variables (cross-stack env vars)
│   ├── sync-schedules.ts                   # Sync Komodo schedules (cron jobs)
│   ├── sync-action-recipients.ts           # Sync Komodo ActionRecipients (Discord, email, Slack)
│   ├── sync-olm.ts                         # Sync Pangolin OLM clients
│   ├── bootstrap.ts                        # 1-command end-to-end (Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs)
│   ├── teardown.ts                         # Reverse of bootstrap
│   └── health.ts                           # Health check all 3 systems
├── config.ts                              # Single env loader
├── cli.ts                                  # bun run iac <cmd> entry point
├── diff.ts                                 # Deep-equal diff engine
├── auth.ts                                 # The 3 auth flows (Komodo login, Pangolin API key, Infisical machine identity)
├── README.md                              # The new IaC README
└── package.json                            # Already at bonneagar/package.json (the root)
```

### 2. The 9 per-resource CRUD methods on the new Pangolin client

The v0 had 4. The new has 9 (the 5 new ones are the Enterprise Edition Integrations API surface):

```typescript
// The 4 v0 methods (unchanged)
async listSites(): Promise<Site[]>                              // GET  /v1/org/{orgId}/sites
async listResources(): Promise<Resource[]>                      // GET  /v1/org/{orgId}/site-resources
async createSiteResource(body: Resource): Promise<Resource>      // POST /v1/org/{orgId}/site-resource
async deleteSiteResource(id: number): Promise<void>             // DELETE /v1/site-resource/{id}

// The 5 NEW methods (per the EE Integrations API OpenAPI spec)
async listOrganizations(): Promise<Org[]>                        // GET  /v1/orgs
async createOrganization(name: string): Promise<Org>            // POST /v1/orgs
async createSite(orgId: string, name: string): Promise<Site>     // POST /v1/org/{orgId}/site
async createOlmClient(orgId: string, body: OlmClient): Promise<OlmClient>  // POST /api/v1/integration/olm-client
async listOlmClients(orgId: string): Promise<OlmClient[]>       // GET  /api/v1/integration/olm-client
```

### 3. The 3 blueprint-import methods on the new Pangolin client

The blueprint import is a bulk endpoint — uploads a single YAML that creates N resources atomically. Faster than N individual API calls but less granular. Used as an **opt-in** for the bootstrap command:

```typescript
// The 3 BLUEPRINT methods (the bulk-import surface; per OLM curl example in olm-resources.blueprint.yaml)
async uploadBlueprint(blueprintYaml: string): Promise<Blueprint>     // POST   /api/v1/integration/blueprint
async listBlueprints(orgId: string): Promise<Blueprint[]>            // GET    /api/v1/integration/blueprint
async deleteBlueprint(orgId: string, id: number): Promise<void>      // DELETE /api/v1/integration/blueprint/{id}
```

### 4. The 9 new sync commands + 4 top-level commands (the 13 new CLI commands)

| Command | What it does | Systems |
|:--|:--|:--|
| `iac:plan` | Show diff between IaC-declared state and actual state | All 3 |
| `iac:deploy` | Deploy the 30 key stacks end-to-end | All 3 |
| `iac:sync:secrets` | Sync Infisical secrets from `secrets.env` refs | Infisical |
| `iac:sync:resources` | Sync Pangolin private resources (DELETE-then-CREATE the 3 manual ones) | Pangolin |
| `iac:sync:procedures` | Sync Komodo procedures from `komodo/procedures/*.toml` | Komodo |
| `iac:sync:resource-syncs` | Sync Komodo resource-syncs from `komodo/resource-syncs/*.toml` | Komodo |
| `iac:sync:monitors` | Sync Komodo monitors (HTTP health checks; opt-in) | Komodo |
| `iac:sync:alerts` | Sync Komodo alerts (failure notifications; opt-in) | Komodo |
| `iac:sync:variables` | Sync Komodo variables (cross-stack env vars) | Komodo |
| `iac:sync:schedules` | Sync Komodo schedules (cron jobs; opt-in) | Komodo |
| `iac:sync:action-recipients` | Sync Komodo ActionRecipients (Discord, email, Slack) | Komodo |
| `iac:sync:olm` | Sync Pangolin OLM clients (fixes the 2 manually-created OLM resources) | Pangolin |
| `iac:bootstrap` | The 1-command full bootstrap: Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs | All 3 |
| `iac:teardown` | Reverse of bootstrap (with `--force`) | All 3 |
| `iac:health` | Health check all 3 systems | All 3 |

### 5. The 4 blockers from `DEPLOYMENT-STRATEGY.md` that the new IaC fixes

| # | Blocker | IaC fix |
|--:|:--|:--|
| 1 | Newt 1.12.5 + Pangolin 1.18.4 incompatible | `iac:bootstrap` pins compatible versions on deploy |
| 2 | 3 manual Pangolin resources override the blueprints | `iac:sync:resources` DELETE-then-CREATE for the 3 hardcoded `niceId`s (komodo, calcom, infisical) |
| 3 | `PANGOLIN_API_KEY` returns 401 | `iac:auth:bootstrap` mints a new OIDC token via Pocket ID |
| 4 | `komodo-locket` sidecar `${INFISICAL_CLIENT_ID}` literal | `iac:auth:bootstrap` mints a new Infisical machine identity with `/komodo` access |

### 6. Update the root `bonneagar/package.json` with the new alias scripts

The current 4 alias scripts (`iac:deploy-stacks`, `iac:create-resources`, `iac:read-state`, `iac:bootstrap`) get replaced with the 15 new ones. The v0 4 are deprecated but kept as backward-compat aliases.

### 7. Migrate the 5 v0 `iac/komodo/*.ts` scripts to the new `iac/` structure

| v0 file (314 LoC total) | New home |
|:--|:--|
| `iac/komodo/config.ts` (23 LoC) | `iac/config.ts` (extended to 80 LoC with Infisical env vars) |
| `iac/komodo/komodo-rpc.ts` (202 LoC) | `iac/clients/komodo-client.ts` (extended to 350 LoC with the 9 new methods: Procedure, ResourceSync, Monitor, Alert, Variable, Schedule, ActionRecipient, Repos, Builder) |
| `iac/komodo/deploy-stacks.ts` (157 LoC) | `iac/commands/sync-procedures.ts` + `iac/commands/sync-resource-syncs.ts` (split into 2 commands; auto-derived from every `komodo/stacks/*.toml` + `komodo/resource-syncs/*.toml`) |
| `iac/komodo/create-resources.ts` (170 LoC) | `iac/clients/pangolin-client.ts` (extended to 350 LoC with the 9 methods + the 3 blueprint methods) + `iac/commands/sync-resources.ts` (auto-derived from every `pangolin.yaml`) |
| `iac/komodo/read-state.ts` (48 LoC) | `iac/commands/health.ts` (extended to 80 LoC; checks all 3 systems) |

## Impact

### Affected specs (3 total)

- MODIFIED `infrastructure-stacks` — +1 Requirement: the IaC at `bonneagar/iac/` is the single source of truth for Komodo + Infisical + Pangolin. The 5 hardcoded scripts are replaced.
- MODIFIED `indexing-and-cognition` — cross-reference the new IaC.
- NEW `bonneagar-iac-merge` — the new capability spec for the IaC.

### New files (~17)

```
bonnegar/iac/clients/komodo-client.ts
bonnegar/iac/clients/pangolin-client.ts
bonnegar/iac/clients/infisical-client.ts
bonnegar/iac/models/komodo.ts
bonnegar/iac/models/pangolin.ts
bonnegar/iac/models/infisical.ts
bonnegar/iac/sources/discover-stacks.ts
bonnegar/iac/sources/discover-resources.ts
bonnegar/iac/sources/discover-secrets.ts
bonnegar/iac/sources/key-stacks.ts
bonnegar/iac/commands/plan.ts
bonnegar/iac/commands/deploy.ts
bonnegar/iac/commands/sync-secrets.ts
bonnegar/iac/commands/sync-resources.ts
bonnegar/iac/commands/sync-procedures.ts
bonnegar/iac/commands/sync-resource-syncs.ts
bonnegar/iac/commands/sync-monitors.ts
bonnegar/iac/commands/sync-alerts.ts
bonnegar/iac/commands/sync-variables.ts
bonnegar/iac/commands/sync-schedules.ts
bonnegar/iac/commands/sync-action-recipients.ts
bonnegar/iac/commands/sync-olm.ts
bonnegar/iac/commands/bootstrap.ts
bonnegar/iac/commands/teardown.ts
bonnegar/iac/commands/health.ts
bonnegar/iac/config.ts
bonnegar/iac/cli.ts
bonnegar/iac/diff.ts
bonnegar/iac/auth.ts
bonnegar/iac/README.md
openspec/specs/bonneagar-iac-merge/spec.md
```

### Modified files

- `bonneagar/package.json` — add the 15 new alias scripts
- `openspec/specs/infrastructure-stacks/spec.md` — +1 Requirement
- `openspec/specs/indexing-and-cognition/spec.md` — cross-reference
- `openspec/project.md` — +1 capability row

### Deleted files

- `bonnegar/iac/komodo/{config,komodo-rpc,deploy-stacks,create-resources,read-state}.ts` (migrated to the new `iac/` structure)
- `bonnegar/iac/komodo/{package.json,tsconfig.json,bun.lock}` (the v0 IaC's manifests; the new IaC uses the root `bonnegar/package.json`)

### Affected CI

- `openspec validate 2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical --strict` must pass
- `bun run iac:health` must return 0 (all 3 systems healthy)
- `bun run iac:plan --dry-run` must not show unexpected diffs

## Non-Goals

- This change does **NOT** migrate the 3 bash scripts (`setup-pangolin-komodo.sh`, `sync-blueprints.sh`, `create-olm-clients.sh`) to TypeScript. They stay as legacy compatibility wrappers; the new TypeScript IaC is the primary path. A future change will deprecate the bash scripts.
- This change does **NOT** introduce Dagger. The `bonneagar/dagger/` TS submodule stays as-is.
- This change does **NOT** introduce the shared `kcg/base:latest` base image. The Dockerfiles keep their existing build approach.
- This change does **NOT** split `bonneagar/` out of the monorepo. It only prepares the structure.
- This change does **NOT** introduce a Web UI for the IaC. The Komodo Web UI already provides this.
- This change does **NOT** auto-deploy the bash setup script (e.g. `setup-pangolin-komodo.sh all`) — the user explicitly runs `iac:bootstrap` to do the same.

## Risk Assessment

- **Risk: the new IaC could overwrite the 3 manually-created Pangolin resources unexpectedly.** **Mitigation:** `iac:plan --dry-run` shows the diff first; `iac:sync:resources` requires `--force` flag to DELETE; the 3 hardcoded `niceId`s (komodo, calcom, infisical) are DELETEd then re-CREATEd, never untouched.
- **Risk: the IaC could expose secrets in dry-run output.** **Mitigation:** all secret values are redacted in the diff output; only the secret path + key are shown, never the value.
- **Risk: the new IaC could fail mid-deploy (e.g. Infisical succeeds but Komodo fails).** **Mitigation:** each sync command is idempotent + re-runnable; `iac:health` shows the current state; the user can re-run `iac:deploy` to retry.
- **Risk: the user might not have the `@infisical/sdk` package installed.** **Mitigation:** add to the root `bonneagar/package.json` + `bun install` is the first step in the deployment runbook.

## Validation

1. `bun install` succeeds (the `@infisical/sdk` is added)
2. `openspec validate 2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical --strict` passes
3. `bun run iac:health` returns 0 (Komodo + Pangolin + Infisical all healthy)
4. `bun run iac:plan --dry-run` shows the expected diff (the 30 key stacks detected; the 3 manual Pangolin resources flagged for DELETE+CREATE; the Infisical secrets ready to be created)
5. `bun run iac:bootstrap` end-to-end completes (Infisical → Pangolin → Komodo all synced)
6. `bun run iac:health` (post-deploy) confirms the 3 systems are consistent

## Estimated effort

- 15+ new TypeScript files + 4 spec deltas + 1 root manifest update
- ~4,200 LoC of TypeScript
- ~1-2 dev days for an experienced Bun + TypeScript + IaC engineer
