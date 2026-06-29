# `infrastructure-stacks` capability spec — bonneagar-iac-merge-komodo-pangolin-infisical delta

The `infrastructure-stacks` capability spec governs the 88
stacks at `bonneagar/stacks/` + the 6-file GOLD_STANDARD
pattern + the IaC TypeScript client at `bonneagar/iac/`.

This delta adds 1 Requirement: the IaC is the single source
of truth for the 3 systems (Komodo + Pangolin + Infisical).
The v0 5-script approach at `iac/komodo/` is replaced by the
new 15-file IaC at `iac/`.

## ADDED Requirements

### Requirement: IaC at `bonnegar/iac/` is the single source of truth

The system SHALL maintain a single TypeScript IaC at
`bonnegar/iac/` that orchestrates the 3 systems (Komodo +
Pangolin + Infisical). The 5 v0 scripts at
`iac/komodo/{config,komodo-rpc,deploy-stacks,create-resources,read-state}.ts`
SHALL be migrated to the new `iac/{clients,models,sources,commands}/`
structure (15+ new files).

#### Scenario: IaC structure is complete

- **WHEN** a developer lists `bonnegar/iac/`
- **THEN** the directory SHALL contain:
  - `clients/{komodo,pangolin,infisical}-client.ts`
  - `models/{komodo,pangolin,infisical}.ts`
  - `sources/{discover-stacks,discover-resources,discover-secrets,key-stacks}.ts`
  - `commands/{plan,deploy,bootstrap,teardown,health}.ts` + 11 sync commands
  - `config.ts`, `cli.ts`, `diff.ts`, `auth.ts`, `README.md`
- **AND** the `iac/komodo/` dir SHALL be removed

#### Scenario: IaC uses the Pangolin Integrations API

- **WHEN** `iac:sync:resources` runs
- **THEN** the script SHALL call the official Pangolin
  **Integrations API** at `${PANGOLIN_URL}/v1/...` (per the
  v0 `create-resources.ts` pattern) — verified by the
  `PANGOLIN_LICENCE=PER-...` env var confirming Enterprise
  Edition
- **AND** the script SHALL use the 9 per-resource CRUD
  methods (listSites, listResources, createSiteResource,
  deleteSiteResource, listOrganizations, createOrganization,
  createSite, createOlmClient, listOlmClients) + the 3
  blueprint-import methods (uploadBlueprint, listBlueprints,
  deleteBlueprint) as an opt-in

#### Scenario: IaC uses the Infisical SDK

- **WHEN** `iac:sync:secrets` runs
- **THEN** the script SHALL use the official `@infisical/sdk`
  npm package (not hand-rolled `fetch()`)
- **AND** the script SHALL use the 8 SDK methods (login,
  listProjects, createEnvironment, createFolder, listSecrets,
  createSecret, updateSecret, deleteSecret)

#### Scenario: IaC uses Komodo RPC directly (no npm package)

- **WHEN** `iac:sync:procedures` runs
- **THEN** the script SHALL use the Komodo RPC API directly
  via `fetch()` (per the v0 `komodoClient.ts` pattern; the
  `komodo_client` npm package has a `localStorage`
  browser-only bug)
- **AND** the script SHALL use the 18 new methods on the
  `KomodoClient` class (listProcedures, upsertProcedure,
  listMonitors, upsertMonitor, listAlerts, upsertAlert,
  listVariables, upsertVariable, listSchedules, upsertSchedule,
  listActionRecipients, upsertActionRecipient, listRepos,
  upsertRepo, listBuilders, upsertBuilder, + the 3 v0 methods)

#### Scenario: IaC fixes the 4 DEPLOYMENT-STRATEGY blockers

- **WHEN** `iac:bootstrap` runs
- **THEN** the script SHALL fix the 4 known blockers:
  - Blocker 1: pin compatible Newt + Pangolin versions on deploy
  - Blocker 2: DELETE-then-CREATE the 3 manually-created
    Pangolin resources (komodo, calcom, infisical)
  - Blocker 3: mint a new `PANGOLIN_API_KEY` via Pocket ID
    OIDC if the existing one returns 401
  - Blocker 4: mint a new Infisical machine identity with
    `/komodo` access if the sidecar `${INFISICAL_CLIENT_ID}`
    is a literal

#### Scenario: IaC supports 15 CLI commands

- **WHEN** the user runs `bun run iac <cmd>`
- **THEN** the CLI SHALL support the 15 commands: `plan`,
  `deploy`, `bootstrap`, `teardown`, `health`, `sync:secrets`,
  `sync:resources`, `sync:procedures`, `sync:resource-syncs`,
  `sync:monitors`, `sync:alerts`, `sync:variables`,
  `sync:schedules`, `sync:action-recipients`, `sync:olm`
- **AND** each command SHALL support `--dry-run`,
  `--force`, `--stack=<name>`, `--with-blueprint-import`,
  `--verbose` flags

## MODIFIED Requirements

*(None — the change only ADDS the new IaC Requirement; the
existing 6-file GOLD_STANDARD pattern + 88-stack inventory +
5-group model are unchanged.)*

## REMOVED Requirements

*(None.)*
