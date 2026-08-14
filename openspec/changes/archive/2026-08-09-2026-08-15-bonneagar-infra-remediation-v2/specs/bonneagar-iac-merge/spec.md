# Delta: `bonneagar-iac-merge`

## ADDED Requirements

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

## MODIFIED Requirements

None.

## REMOVED Requirements

None.
