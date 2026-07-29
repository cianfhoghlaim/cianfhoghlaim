# Bonneagar IaC Merge Capability

## Purpose

`bonneagar-iac-merge` is a capability of the Cianfhoghlaim platform. It
defines the unified TypeScript IaC at `bonneagar/iac/` that orchestrates
the 3 systems (Komodo + Pangolin + Infisical) into a single codebase.

The corresponding source code lives at:

- `bonneagar/iac/clients/{komodo,pangolin,infisical}-client.ts` (the 3 typed clients)
- `bonneagar/iac/models/{komodo,pangolin,infisical}.ts` (the 19 typed models)
- `bonneagar/iac/sources/{discover-stacks,discover-resources,discover-secrets,key-stacks}.ts` (the 4 source-discoverers)
- `bonneagar/iac/commands/{plan,deploy,bootstrap,teardown,health}.ts` (the 5 top-level commands)
- `bonneagar/iac/commands/sync-{secrets,resources,procedures,resource-syncs,monitors,alerts,variables,schedules,action-recipients,olm}.ts` (the 10 sync commands)
- `bonneagar/iac/{config,cli,diff,auth,README}.ts/.md`

## Background

The v0 IaC was split across 3 disconnected sub-circuits: the 5 TypeScript
files at `iac/komodo/`, the 3 bash scripts at `scripts/`, and the 2 vault
scripts at the repo root. The 3 systems (Komodo + Pangolin + Infisical)
were not synchronised.

This change merges them into a single TypeScript codebase with 15 CLI
commands + 3 typed clients + 4 source-discoverers + 5 top-level commands.

The 3 typed clients use the official API surfaces:
- **Pangolin** — the Enterprise Edition **Integrations API** at `${PANGOLIN_URL}/v1` + `/api/v1/integration/...` (verified by `PANGOLIN_LICENCE=PER-...`)
- **Infisical** — the official `@infisical/sdk` npm package
- **Komodo** — raw `fetch()` against the Komodo RPC API (the `komodo_client` npm package has a `localStorage` browser-only bug)
## Requirements
### Requirement: 3 typed clients (Komodo + Pangolin + Infisical)

The system SHALL provide 3 typed clients at `bonneagar/iac/clients/` —
one per system. Each client uses the system's official API surface.

#### Scenario: KomodoClient has 18 methods

- **WHEN** a developer reads `clients/komodo-client.ts`
- **THEN** the `KomodoClient` class SHALL expose 18 methods:
  - The 3 v0 methods (`listServers`, `listStacks`, `listResourceSyncs`)
  - The 6 v0 upsert methods (`upsertServer`, `upsertStack`, `upsertResourceSync`, `login`, `read`, `write`, `execute`)
  - The 9 NEW methods (`listProcedures`, `upsertProcedure`, `listMonitors`, `upsertMonitor`, `listAlerts`, `upsertAlert`, `listVariables`, `upsertVariable`, `listSchedules`, `upsertSchedule`, `listActionRecipients`, `upsertActionRecipient`, `listRepos`, `upsertRepo`, `listBuilders`, `upsertBuilder`)

#### Scenario: PangolinClient has 12 methods

- **WHEN** a developer reads `clients/pangolin-client.ts`
- **THEN** the `PangolinClient` class SHALL expose 12 methods:
  - The 4 v0 methods (`listSites`, `listResources`, `createSiteResource`, `deleteSiteResource`)
  - The 5 NEW per-resource methods (`listOrganizations`, `createOrganization`, `createSite`, `createOlmClient`, `listOlmClients`)
  - The 3 NEW blueprint-import methods (`uploadBlueprint`, `listBlueprints`, `deleteBlueprint`)

#### Scenario: InfisicalClient has 10 methods

- **WHEN** a developer reads `clients/infisical-client.ts`
- **THEN** the `InfisicalClient` class SHALL expose 10 methods using the `@infisical/sdk`:
  `login`, `listProjects`, `createEnvironment`, `createFolder`, `listSecrets`,
  `createSecret`, `updateSecret`, `deleteSecret`, `createMachineIdentity`, `listMachineIdentities`

### Requirement: 4 source-discoverers

The system SHALL provide 4 source-discoverers at `bonneagar/iac/sources/`
that walk the stacks at `bonneagar/stacks/` and produce typed objects.

#### Scenario: discover-stacks walks every compose.yaml

- **WHEN** `sources/discover-stacks.ts` runs
- **THEN** it SHALL walk `bonneagar/stacks/*/compose.yaml`
- **AND** produce typed `Stack[]` (one per stack)
- **AND** each `Stack` SHALL have the 6-file GOLD_STANDARD check (passes if `compose.yaml` + `sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example` all exist)

#### Scenario: discover-resources walks every pangolin.yaml

- **WHEN** `sources/discover-resources.ts` runs
- **THEN** it SHALL walk `bonneagar/stacks/*/pangolin.yaml`
- **AND** produce typed `PangolinResource[]`
- **AND** filter out stacks whose `pangolin.yaml` is empty or commented-out

#### Scenario: discover-secrets walks every secrets.env

- **WHEN** `sources/discover-secrets.ts` runs
- **THEN** it SHALL walk `bonneagar/stacks/*/secrets.env`
- **AND** produce typed `InfisicalSecret[]` (one per `infisical://dev-baile/<stack>/<key>` ref)
- **AND** each `InfisicalSecret` SHALL have a `path` + `key` + `value` triplet (the value is redacted in diff output)

#### Scenario: key-stacks returns the key stacks subset

- **WHEN** `sources/key-stacks.ts` is queried
- **THEN** it SHALL return the names of the "key" stacks that the IaC deploys

### Requirement: 10 sync commands + 5 top-level commands

The system SHALL provide 15 CLI commands at `bonneagar/iac/commands/`. The
5 top-level commands (`plan`, `deploy`, `bootstrap`, `teardown`, `health`)
orchestrate the 10 sync commands.

#### Scenario: iac:deploy runs the 10 sync commands in order

- **WHEN** the user runs `bun run iac:deploy`
- **THEN** the script SHALL sequentially execute:
  1. `sync-secrets`
  2. `sync-procedures`
  3. `sync-resource-syncs`
  4. `sync-variables`
  5. `sync-resources`
  6. `sync-monitors` (opt-in via `--with-monitors`)
  7. `sync-alerts` (opt-in via `--with-alerts`)
  8. `sync-schedules` (opt-in via `--with-schedules`)
  9. `sync-action-recipients`
  10. `sync-olm`
- **AND** each step SHALL be idempotent + print a summary

#### Scenario: iac:plan is the diff viewer

- **WHEN** the user runs `bun run iac:plan --dry-run`
- **THEN** the script SHALL call all 10 sync commands in `--dry-run` mode
- **AND** print a side-by-side diff of what would change

#### Scenario: iac:bootstrap is the 1-command end-to-end

- **WHEN** the user runs `bun run iac:bootstrap`
- **THEN** the script SHALL execute the 9-phase bootstrap: Pulumi → Infisical → Pangolin → Komodo Core → Komodo Periphery → Newt → all 10 sync commands
- **AND** the `--with-blueprint-import` flag uses the Pangolin blueprint-import API for the initial Pangolin resource creation (bulk endpoint; faster than N individual API calls)

#### Scenario: iac:health returns 0/1 exit code

- **WHEN** the user runs `bun run iac:health`
- **THEN** the script SHALL check all 3 systems: Komodo `GET /health`, Pangolin `GET /api/health`, Infisical `GET /api/status`
- **AND** the script SHALL exit 0 if all 3 are healthy, exit 1 if any are unhealthy

### Requirement: Cross-repo sync convention

Every openspec change SHALL include a `cross-repo-sync.md` file
that lists the commit hashes + branches + ordered tasks needed
in each repo, when the change touches more than one of the 3
repos (cianfhoghlaim + bonneagar + leabharlann).

#### Scenario: A change touches cianfhoghlaim + bonneagar

- **WHEN** a developer creates a change that edits both repos
- **THEN** `openspec/changes/<id>/cross-repo-sync.md` SHALL exist
- **AND** it SHALL list the commit plan for each repo
- **AND** it SHALL be referenced from the change's `proposal.md`

#### Scenario: A change is single-repo

- **WHEN** a developer creates a change that only edits
  cianfhoghlaim
- **THEN** the `cross-repo-sync.md` file is OPTIONAL
- **AND** the proposal.md `## Dependencies` section SHALL
  declare `Affected repos: cianfhoghlaim` for clarity

### Requirement: iac:bootstrap at root

The IaC `iac:bootstrap` SHALL be reachable from the
cianfhoghlaim repo root via the `package.json` script
`iac:bootstrap`, delegating to `bun run --cwd bonneagar iac:bootstrap`.

#### Scenario: Root-level iac:bootstrap is callable

- **WHEN** a developer runs `bun run iac:bootstrap` from the
  cianfhoghlaim repo root
- **THEN** the IaC SHALL execute the bootstrap sequence
- **AND** the exit code SHALL be 0 on success

#### Scenario: iac:bootstrap supports --dry-run

- **WHEN** a developer runs `bun run iac:bootstrap --dry-run`
- **THEN** the IaC SHALL print the diff and SHALL NOT mutate
  any remote system

### Requirement: Dependencies field in proposal.md

Every openspec change's `proposal.md` SHALL include a
`## Dependencies` section that lists `Blocked by: <change-id>`
edges for topo ordering.

#### Scenario: A change depends on a not-yet-archived change

- **WHEN** a developer writes a new change that depends on a
  previously-authored change still in `openspec/changes/`
- **THEN** the new change's proposal.md SHALL declare
  `Blocked by: <change-id>` in its `## Dependencies` section
- **AND** the new change SHALL NOT be archived until the
  blocker is archived

#### Scenario: A change has no dependencies

- **WHEN** a developer writes a new change that has no
  ordering constraint
- **THEN** the proposal.md SHALL declare `Blocked by: none`
  in its `## Dependencies` section

### Requirement: Bonneagar subdirectory preservation

The `bonneagar/` subdirectory at the repo root SHALL contain the full
IaC: 88 Docker Compose stacks + the unified TypeScript IaC + the
Komodo resource-syncs + the Pangolin config + the audit scripts +
the IaC's own pyproject.toml.

#### Scenario: Bonneagar subdir is preserved across merges

- **WHEN** any future change touches IaC files
- **AND** the change is committed to the v7 main branch
- **THEN** the IaC files SHALL continue to live at `bonneagar/{iac,stacks,
  komodo,pangolin,...}/` paths
- **AND** the root `package.json` SHALL retain the `--cwd bonneagar`
  delegation in the `iac:*` scripts

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 88 stacks at `bonneagar/stacks/` + the 6-file GOLD_STANDARD pattern
- [`indexing-and-cognition`](../indexing-and-cognition/spec.md) — the cognify + indexing layers
- [`data-engineering-pipeline-documentation`](../data-engineering-pipeline-documentation/spec.md) — the 4 canonical ops dirs
- [`bonneagar-komodo-gitops`](../bonneagar-komodo-gitops/spec.md) — the resource-syncs layer that this IaC orchestrates

## Migrated from: *(none)*
