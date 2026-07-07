# `bonneagar-iac-merge` capability spec — leabharlann-email-inbox-pipeline delta

`bonneagar-iac-merge` is a NEW capability of the Cianfhoghlaim
platform. This document is the change-side delta file; the
canonical home for the capability spec is
`openspec/specs/bonneagar-iac-merge/spec.md`.

The corresponding source code lives at:

- `bonnegar/iac/clients/{komodo,pangolin,infisical}-client.ts`
  (the 3 typed clients)
- `bonnegar/iac/models/{komodo,pangolin,infisical}.ts`
  (the 9 + 5 + 5 = 19 typed models)
- `bonnegar/iac/sources/{discover-stacks,discover-resources,discover-secrets,key-stacks}.ts`
  (the 4 source-discoverers)
- `bonnegar/iac/commands/{plan,deploy,bootstrap,teardown,health}.ts`
  (the 5 top-level commands)
- `bonnegar/iac/commands/sync-{secrets,resources,procedures,resource-syncs,monitors,alerts,variables,schedules,action-recipients,olm}.ts`
  (the 10 sync commands)
- `bonnegar/iac/{config,cli,diff,auth,README}.ts/.md`
  (the supporting infra)

## ADDED Requirements

### Requirement: 3 typed clients (Komodo + Pangolin + Infisical)

The system SHALL provide 3 typed clients at
`bonnegar/iac/clients/` — one per system. Each client uses
the system's official API surface (Pangolin uses the
Integrations API at `${PANGOLIN_URL}/v1` + `/api/v1/integration/...`;
Infisical uses the `@infisical/sdk` npm package; Komodo uses
raw `fetch()` against the RPC API).

#### Scenario: KomodoClient has 18 methods

- **WHEN** a developer reads `clients/komodo-client.ts`
- **THEN** the `KomodoClient` class SHALL expose 18 methods:
  - The 3 v0 methods (`listServers`, `listStacks`,
    `listResourceSyncs`)
  - The 6 v0 upsert methods (`upsertServer`, `upsertStack`,
    `upsertResourceSync`, `login`, `read`, `write`,
    `execute`)
  - The 9 NEW methods (`listProcedures`, `upsertProcedure`,
    `listMonitors`, `upsertMonitor`, `listAlerts`,
    `upsertAlert`, `listVariables`, `upsertVariable`,
    `listSchedules`, `upsertSchedule`,
    `listActionRecipients`, `upsertActionRecipient`,
    `listRepos`, `upsertRepo`, `listBuilders`,
    `upsertBuilder`)

#### Scenario: PangolinClient has 12 methods

- **WHEN** a developer reads `clients/pangolin-client.ts`
- **THEN** the `PangolinClient` class SHALL expose 12 methods:
  - The 4 v0 methods (`listSites`, `listResources`,
    `createSiteResource`, `deleteSiteResource`)
  - The 5 NEW per-resource methods (`listOrganizations`,
    `createOrganization`, `createSite`, `createOlmClient`,
    `listOlmClients`)
  - The 3 NEW blueprint-import methods (`uploadBlueprint`,
    `listBlueprints`, `deleteBlueprint`)

#### Scenario: InfisicalClient has 10 methods

- **WHEN** a developer reads `clients/infisical-client.ts`
- **THEN** the `InfisicalClient` class SHALL expose 10
  methods using the `@infisical/sdk`:
  - `login`, `listProjects`, `createEnvironment`,
    `createFolder`, `listSecrets`, `createSecret`,
    `updateSecret`, `deleteSecret`, `createMachineIdentity`,
    `listMachineIdentities`

### Requirement: 4 source-discoverers

The system SHALL provide 4 source-discoverers at
`bonnegar/iac/sources/` that walk the 91 stacks at
`bonnegar/stacks/` and produce typed objects.

#### Scenario: discover-stacks walks every `compose.yaml`

- **WHEN** `sources/discover-stacks.ts` runs
- **THEN** it SHALL walk `bonnegar/stacks/*/compose.yaml`
- **AND** produce typed `Stack[]` (one per stack, 91 total)
- **AND** each `Stack` SHALL have the 6-file GOLD_STANDARD
  check (passes if `compose.yaml` + `sidecar.yaml` +
  `secrets.env` + `pangolin.yaml` + `blueprint.yaml` +
  `.env.example` all exist)

#### Scenario: discover-resources walks every `pangolin.yaml`

- **WHEN** `sources/discover-resources.ts` runs
- **THEN** it SHALL walk `bonnegar/stacks/*/pangolin.yaml`
- **AND** produce typed `PangolinResource[]` (one per
  Pangolin-routed stack, ~30 total — the 5-group model)
- **AND** filter out stacks whose `pangolin.yaml` is
  empty/commented-out

#### Scenario: discover-secrets walks every `secrets.env`

- **WHEN** `sources/discover-secrets.ts` runs
- **THEN** it SHALL walk `bonnegar/stacks/*/secrets.env`
- **AND** produce typed `InfisicalSecret[]` (one per
  `infisical://dev-baile/<stack>/<key>` ref, ~200+ total)
- **AND** each `InfisicalSecret` SHALL have a `path` + `key`
  + `value` triplet (the value is redacted in diff output)

#### Scenario: key-stacks returns the 30 "key" stacks

- **WHEN** `sources/key-stacks.ts` is queried
- **THEN** it SHALL return the names of the 30 "key" stacks
  that the IaC deploys (the 5-group model minus duplicates:
  9 infrastructure + 12 data-engineering + 7 agent-platform
  + 6 language-model + 6 user-facing-web + 1 ci = 41, minus
  ~11 duplicates = ~30 unique)

### Requirement: 10 sync commands + 5 top-level commands

The system SHALL provide 15 CLI commands at
`bonnegar/iac/commands/`. The 5 top-level commands
(`plan`, `deploy`, `bootstrap`, `teardown`, `health`)
orchestrate the 10 sync commands.

#### Scenario: `iac:deploy` runs the 10 sync commands in order

- **WHEN** the user runs `bun run iac:deploy`
- **THEN** the script SHALL sequentially execute:
  1. `sync-secrets` — Infisical secrets from `secrets.env` refs
  2. `sync-procedures` — Komodo procedures from `*.toml`
  3. `sync-resource-syncs` — Komodo resource-syncs from `*.toml`
  4. `sync-variables` — Komodo variables (cross-stack env vars)
  5. `sync-resources` — Pangolin private resources (DELETE-then-CREATE the 3 manual ones)
  6. `sync-monitors` — Komodo monitors (opt-in via `--with-monitors`)
  7. `sync-alerts` — Komodo alerts (opt-in via `--with-alerts`)
  8. `sync-schedules` — Komodo schedules (opt-in via `--with-schedules`)
  9. `sync-action-recipients` — Komodo ActionRecipients
  10. `sync-olm` — Pangolin OLM clients
- **AND** each step SHALL be idempotent + print a summary

#### Scenario: `iac:plan` is the diff viewer

- **WHEN** the user runs `bun run iac:plan --dry-run`
- **THEN** the script SHALL call all 10 sync commands in
  `--dry-run` mode
- **AND** print a side-by-side diff: "would create 12
  Infisical secrets, update 3 secrets, create 5 Pangolin
  resources, delete 2 manual resources, create 1
  Komodo procedure, etc."

#### Scenario: `iac:bootstrap` is the 1-command end-to-end

- **WHEN** the user runs `bun run iac:bootstrap`
- **THEN** the script SHALL execute the 9-phase bootstrap
  that the v0 `setup-pangolin-komodo.sh` does, in TypeScript:
  1. Pulumi (OCI / Cloudflare)
  2. Infisical (vault sync)
  3. Pangolin (deploy + configure)
  4. Komodo Core (deploy)
  5. Komodo Periphery (deploy on both hosts)
  6. Newt (Pangolin tunnel client on mbp)
  7. All 10 sync commands (from `iac:deploy`)
- **AND** the `--with-blueprint-import` flag uses the
  Pangolin blueprint-import API for the initial Pangolin
  resource creation (bulk endpoint; faster than N
  individual API calls)

#### Scenario: `iac:health` returns 0/1 exit code

- **WHEN** the user runs `bun run iac:health`
- **THEN** the script SHALL check all 3 systems:
  - Komodo `GET /health` (200 = healthy)
  - Pangolin `GET /api/health` (200 = healthy)
  - Infisical `GET /api/status` (200 = healthy)
- **AND** the script SHALL exit 0 if all 3 are healthy
- **AND** the script SHALL exit 1 if any are unhealthy

## MODIFIED Requirements

*(None — this is a NEW capability.)*

## REMOVED Requirements

*(None.)*
