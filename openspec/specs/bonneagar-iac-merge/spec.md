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

### Requirement: PlanetScale Postgres Centralisation (bonneagar-iac-merge)

The system SHALL treat PlanetScale PostgreSQL as the canonical managed remote DB in the IaC subtree at `bonneagar/`. The Locket-side secret loader at `bonneagar/iac/auth-pocketid.ts` SHALL be extended with a sibling `bonneagar/iac/planetscale-postgres.ts` that resolves PlanetScale credentials from Infisical.

#### Scenario: Phase B wires Locket secret for Lakekeeper

- **GIVEN** the Phase B change ships
- **WHEN** `locket exec -- docker compose up -d` runs for `lakekeeper`
- **THEN** Locket SHALL inject `LAKEKEEPER__PG_DATABASE_URL_WRITE` from `infisical://dev-baile/lakekeeper/database_url`
- **AND** the connection SHALL use `?sslmode=verify-full` (per the umbrella spec R6)

#### Scenario: Operator adds a new stack with PlanetScale PG

- **GIVEN** a new stack is added to `bonneagar/stacks/<new-stack>/`
- **WHEN** the operator chooses PlanetScale PG per the decision tree (R1)
- **THEN** they SHALL register the `infisical://dev-baile/<new-stack>/database_url` secret in the `.infisical.env` template
- **AND** the compose.yaml SHALL mount the Locket sidecar (per the canonical pattern)

### Requirement: PangolinClient has 20 methods (was 16) + the client-mgmt surface

The system SHALL extend `PangolinClient` to 20 methods. The 4 NEW
methods on the `/api/v1/integration/clients/...` surface SHALL be
`listClients`, `getClient`, `createClient`, `deleteClient`. Each
method SHALL use the same Bearer-auth + POST/GET/DELETE pattern as
the existing 16 methods.

#### Scenario: Calling `pc.listClients()` returns the typed client list

- **WHEN** a developer invokes `await pc.listClients()`
- **THEN** the response SHALL be
  `{ data: { clients: PangolinClientCert[] } }` where each
  `PangolinClientCert` has `id` (number), `name` (string),
  `clientId` (string), `organizationId` (string), `endpoint`
  (string), `type` (`"user" | "machine"`), `expiresAt?` (ISO 8601
  string), `createdAt` (ISO 8601 string), `siteIds?` (number[])

#### Scenario: Calling `pc.createClient()` mints a new client

- **WHEN** a developer invokes
  `await pc.createClient({ name, endpoint, type, expiresIn, siteIds? })`
- **THEN** the request SHALL be `POST /api/v1/integration/clients`
  with a JSON body containing the 5 fields
- **AND** the response SHALL be
  `{ data: { id, clientId, secret } }`
- **AND** the `secret` field SHALL be write-only (returned once on
  create; never on subsequent `listClients()` or `getClient()` calls)

### Requirement: `iac:bootstrap-pangolin-client` installs the Pangolin CLI + newt container via Integrations API

The system SHALL provide a new `iac:bootstrap-pangolin-client` command
that: (a) installs the Pangolin CLI binary on the local machine via
`curl -fsSL https://static.pangolin.net/get-cli.sh | bash`, (b) calls
the new `pc.listClients()` + `pc.createClient()` methods to mint a
user-or-machine client, (c) writes the client credentials to `.env` +
Infisical under `/pangolin/clients/`, (d) renders the newt
`docker-compose.yaml` for the target host.

#### Scenario: Operator runs the command for the Oracle arm1-oci host

- **WHEN** the operator runs
  `bun run iac:bootstrap-pangolin-client --host=arm1-oci --type=machine`
- **THEN** the command SHALL:
  (1) install the pangolin binary at `/usr/local/bin/pangolin` (idempotent)
  (2) call `pc.createClient({ name: "arm1-oci", endpoint, type: "machine", expiresIn: 0 })`
  (3) write `PANGOLIN_CLIENT_arm1_oci_ID` + `_SECRET` to `.env` + Infisical under `/pangolin/clients/arm1-oci/`
  (4) render `/etc/komodo/sruth/bonneagar/stacks/newt-arm1-oci/docker-compose.yaml`
  (5) emit an audit record to `/tmp/pangolin-client-bootstrap-{ts}.json`

#### Scenario: Operator runs the command for the operator-laptop bunchloch host

- **WHEN** the operator runs
  `bun run iac:bootstrap-pangolin-client --host=bunchloch --type=user`
- **THEN** the command SHALL mint a user client the operator can use
  to log into the native `Pangolin.app` on the Mac
- **AND** the command SHALL NOT install the pangolin binary (already
  present at `/Applications/Pangolin.app`)
- **AND** the command SHALL print
  `pangolin login --id {clientId} --secret {secret} --endpoint https://pangolin.cianfhoghlaim.ie`

### Requirement: `iac:load-env.ts` auto-loads the repo-root `.env`

The system SHALL provide a `iac:load-env.ts` module that explicitly
loads the repo-root `.env` file into `process.env`. The IaC scripts
run from `bonneagar/iac/`, but bun's built-in `.env` auto-load only
looks for `.env` in the working directory.

#### Scenario: IaC script is invoked from `bonneagar/iac/`

- **WHEN** the operator runs `cd bonneagar/iac && bun run cli.ts health`
- **THEN** the `load-env.ts` side-effect import SHALL walk up from
  `process.cwd()` looking for `.env`
- **AND** the first `.env` file found SHALL be loaded into `process.env`
- **AND** existing shell env vars SHALL NOT be overwritten (shell
  takes precedence over `.env`)
- **AND** `CONFIG.pangolinApiKey` SHALL now be set from the `.env`
  file even when bun runs from a sub-directory

### Requirement: `iac:rotate-auth` correctly extracts the API key string (bug fix)

The system SHALL fix the `iac:rotate-auth` bug where the Pangolin
rotation wrote the whole `PocketIdAdminKey` object to `PANGOLIN_API_KEY`
instead of just the `.apiKey` string.

#### Scenario: Operator runs `iac:rotate-auth` with Pocket ID OIDC credentials

- **WHEN** the operator runs `bun run iac:rotate-auth`
- **THEN** the Pangolin rotation SHALL write `newApiKey.apiKey` (a
  string) to `PANGOLIN_API_KEY`
- **AND** the audit record at `/tmp/auth-rotation-{ts}.json` SHALL
  include `apiKeyId`, `lastChars`, `name`, `createdAt` metadata

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) — the 88 stacks at `bonneagar/stacks/` + the 6-file GOLD_STANDARD pattern
- [`indexing-and-cognition`](../indexing-and-cognition/spec.md) — the cognify + indexing layers
- [`data-engineering-pipeline-documentation`](../data-engineering-pipeline-documentation/spec.md) — the 4 canonical ops dirs
- [`bonneagar-komodo-gitops`](../bonneagar-komodo-gitops/spec.md) — the resource-syncs layer that this IaC orchestrates

## Migrated from: *(none)*
