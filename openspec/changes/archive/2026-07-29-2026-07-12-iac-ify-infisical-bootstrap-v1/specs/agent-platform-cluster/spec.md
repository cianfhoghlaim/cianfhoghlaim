# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: iac:bootstrap-infisical drives the first-admin + machine-identity flow

The system SHALL provide a `bun run iac:bootstrap-infisical` command
that:

1. Checks Infisical health (`https://infisical.cianfhoghlaim.ie/api/status`)
2. If the Infisical vault has **no admin user** (DB row count of `users == 0`):
   - Uses Chrome MCP (the `chrome_*` tools in the agent runtime) to drive the browser through the `/signup/setup` wizard at `https://infisical.cianfhoghlaim.ie/signup/setup`
   - Fills the email + password + display name fields, clicks submit, waits for the success redirect
   - Creates the first admin user without any operator click-throughs
3. After admin login (or if an admin already exists), the command:
   - Calls `POST /api/v1/auth/machine-identities` to create a `bons-iac` machine identity with the Admin role
   - Idempotent: skips creation if the identity already exists
   - Calls `POST /api/v1/auth/machine-identities/{id}/client-secrets` to mint a Universal Auth client secret
   - Writes `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` + `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET` to local `~/.env`
4. Verifies the 8 required machine identities are seeded:
   `bons-iac` + `pocket-id` + `komodo` + `pangolin` + `tinyauth` + `openclaw` + `openchamber` + `hermes`
5. Creates any missing identity (the bons IaC owns the seed list)
6. Emits a JSON audit record to `/tmp/infisical-bootstrap-{ts}.json`

The command MUST be idempotent: re-running on a warm cluster skips
the already-done steps.

#### Scenario: cold-boot (no admin exists)

- **GIVEN** the Infisical vault has 0 admin users (e.g. right after `komodo/stacks/infisical-arm1-oci.toml` is deployed for the first time)
- **WHEN** `bun run iac:bootstrap-infisical` runs
- **THEN** Chrome MCP opens `https://infisical.cianfhoghlaim.ie/signup/setup` in a browser session
- **AND** fills the email + password + display name fields automatically
- **AND** submits the form
- **AND** waits for the success redirect to `/login`
- **AND** the `bons-iac` machine identity is created via the admin API
- **AND** the Universal Auth client secret is written to `~/.env`
- **AND** the audit record is written to `/tmp/infisical-bootstrap-{ts}.json`

#### Scenario: warm-boot (admin already exists)

- **GIVEN** the Infisical vault already has at least 1 admin user
- **AND** `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` + `_SECRET` are in env
- **WHEN** `bun run iac:bootstrap-infisical` runs
- **THEN** Chrome MCP is NOT invoked
- **AND** the command skips the first-admin flow
- **AND** verifies the `bons-iac` machine identity exists (creates if missing)
- **AND** verifies all 8 required identities exist (creates any missing)
- **AND** the audit record is written

#### Scenario: missing machine identity is seeded

- **GIVEN** the Infisical vault is healthy and has the `bons-iac` identity
- **AND** the `hermes` machine identity does NOT exist
- **WHEN** `bun run iac:bootstrap-infisical` runs
- **THEN** the command calls `POST /api/v1/auth/machine-identities` with `{name: "hermes"}` + the Admin role
- **AND** logs `✓ created machine identity: hermes (id=<uuid>)`
- **AND** continues to the next identity (does not abort)
- **AND** all 8 identities exist at the end

### Requirement: deploy-infisical-arm1-oci Komodo procedure replaces the undocumented raw docker run

The system SHALL provide a `komodo/procedures/deploy-infisical-arm1-oci.toml`
Komodo procedure that deploys Infisical on arm1-oci via the bons IaC.
The procedure MUST have these 6 stages (in order):

1. **preflight** — verify Docker is present, env vars are hydrated, the `infisical` docker volume doesn't already exist (idempotency check)
2. **image-pullable** — `docker manifest inspect infisical/infisical:latest` (the canonical pin)
3. **stack-deploy** — `cd /etc/komodo/infisical && docker compose up -d`
4. **health** — poll `https://infisical.cianfhoghlaim.ie/api/status` until 200 (max 90s)
5. **bootstrap** — `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar && bun run iac:bootstrap-infisical` (the IaC does the first-admin + machine-identity work)
6. **audit** — write JSON to `/tmp/infisical-bootstrap-{ts}.json` containing image, version, oidc_issuer, machine identity count

The procedure MUST NOT use raw `ssh arm1-oci` (that pattern is what
this change is explicitly replacing).

#### Scenario: cold deploy

- **WHEN** `km run procedure deploy-infisical-arm1-oci` runs against a fresh arm1-oci
- **THEN** stage 1 (preflight) passes
- **AND** stage 3 (stack-deploy) creates the `infisical` container
- **AND** stage 4 (health) returns 200 from `/api/status` within 90s
- **AND** stage 5 (bootstrap) creates the first admin via Chrome MCP + the bons-iac machine identity
- **AND** stage 6 (audit) writes the JSON record
- **AND** the procedure completes within 5 minutes

#### Scenario: warm deploy (re-run)

- **WHEN** `km run procedure deploy-infisical-arm1-oci` runs against an arm1-oci with Infisical already deployed
- **THEN** stage 1 (preflight) detects the existing volume + skips it
- **AND** stage 4 (health) returns 200 immediately
- **AND** stage 5 (bootstrap) sees an admin already exists + skips to the machine identity check
- **AND** the procedure completes within 1 minute

### Requirement: infisical-first Komodo procedure is HTTP-only (no ssh)

The system SHALL provide a `komodo/procedures/infisical-first.toml`
Komodo procedure that verifies the Infisical vault is healthy + the
8 required machine identities are seeded. The procedure MUST use only
HTTP-based checks (no raw `ssh arm1-oci` — that pattern is what this
change is explicitly replacing).

#### Scenario: vault + identities all healthy

- **WHEN** `km run procedure infisical-first` runs
- **THEN** stage 1 (`vault-reachable`) does `HttpCheck` against `https://infisical.cianfhoghlaim.ie/api/status` (expected 200)
- **AND** stage 2 (`dev-baile-project`) does an HTTP GET against `/api/v3/projects/f3cff583-b74b-4804-b9d3-db8b68885236` with the `bons-iac` machine identity's token (expected 200 + `"name":"dev-baile"` in the response)
- **AND** stage 3 (`machine-identities-seeded`) loops over the 8 required names and does an HTTP GET against `/api/v3/projects/{id}/identity-machine-identities` to verify each exists
- **AND** the procedure reports `OK: infisical-first` at the end

#### Scenario: any identity is missing

- **GIVEN** the 8 identities are seeded EXCEPT `hermes`
- **WHEN** `km run procedure infisical-first` runs
- **THEN** stage 3 (`machine-identities-seeded`) detects the missing identity
- **AND** aborts with `ERROR: machine identity hermes not seeded (run: bun run iac:bootstrap-infisical)`

### Requirement: Pocket ID + Tinyauth + Infisical are part of the cross-cutting prereq order (with deploy-infisical-arm1-oci added)

The system SHALL add `deploy-infisical-arm1-oci` to the bons cross-cutting
prereq order at position **#3.5** (after `infisical-first`, before
`locket-deploy`, since Locket needs Infisical to be alive AND seeded
with machine identities for the Locket sidecars to authenticate).

#### Scenario: Komodo pulls the resource-sync

- **GIVEN** the bons cross-cutting resource-sync at `komodo/resource-syncs/cross-cutting.toml`
- **WHEN** Komodo pulls the file
- **THEN** the order is:
  1. `pangolin-first`
  2. `komodo-core`
  3. `infisical-first` (existing — HTTP checks only)
  4. **`deploy-infisical-arm1-oci` (NEW — only runs if no Infisical container exists on arm1-oci)**
  5. `locket-deploy`
  6. `deploy-pocket-id-bunchloch`
  7. `deploy-tinyauth-bunchloch`
  8. `deploy-pocket-id-arm1-oci`
  9. `deploy-pangolin-newt-arm1-oci`
  10. `deploy-newt-bunchloch-v2`
- **AND** the resource-sync comment SHALL be updated to reflect "10 cross-host prerequisite procedures" (not "9" as it currently says)

## MODIFIED Requirements

### Requirement: iac:bootstrap orchestrates all 5 auth components as a single tightly-integrated system (now 6 — adds Infisical first-admin)

The system SHALL provide a `bun run iac:bootstrap` command that
orchestrates all **6** auth components (Pulumi → **Infisical first-admin** →
Pocket ID → Pangolin → Komodo → Tinyauth → Newt → sync) as a single,
idempotent end-to-end flow. Each phase MUST check the current state
and (re)deploy as needed.

The orchestrator MUST include an explicit Infisical-bootstrap phase
(Phase 2.5) that invokes `iac:bootstrap-infisical` BEFORE the Pocket
ID phase (Phase 3). The Pocket ID bootstrap depends on Infisical being
alive (for the Pocket ID bootstrap script to write `POCKETID_API_KEY`
to Infisical).

Pocket ID + Tinyauth SHALL be first-class systems in the IaC (not
manually configured outside the bons). The bootstrap SHALL include a
new `iac:bootstrap-pocketid-admin` subcommand that creates the first
admin user + the bons-iac OIDC client via the Pocket ID admin API
(only the operator's browser-passkey-registration is manual).

The system SHALL also provide `iac:health` that does a **7-way** check
(added Pocket ID + Tinyauth on top of the previous 4-way check of
Komodo + Pangolin + Infisical + Newt + the new machine-identities-seeded
check). Each check SHALL report a clear actionable error message.

#### Scenario: iac:bootstrap runs end-to-end on cold-boot (updated order)

- **WHEN** the bons host has no Infisical, no Pocket ID, no Tinyauth containers
- **THEN** `iac:bootstrap` orchestrates all 10 phases in order:
  1. Pulumi (TODO)
  2. Infisical secrets (mount the `dev-baile` project into the local filesystem)
  2.5. **Infisical bootstrap (NEW — invokes `iac:bootstrap-infisical` which does the first-admin via Chrome MCP)**
  3. Pocket ID deploy + health check
  4. Auth wiring (creates bons-iac OIDC client via admin API; mints Pangolin API key via OIDC client_credentials)
  5. Pangolin private resources
  6. Komodo Core + Periphery
  7. Tinyauth deploy + health check
  8. Newt (sync-sites)
  9. All sync commands
- **AND** the bootstrap is idempotent: re-running on a warm cluster skips
  the already-done phases.
- **AND** Phase 2.5 (Infisical bootstrap) creates the bons-iac machine identity that's needed for Phase 4 (Pangolin API key mint) and Phase 9 (sync commands)

#### Scenario: iac:health returns 7-way actionable errors (now includes Infisical)

- **WHEN** the user runs `bun run iac:health` with a broken auth state
- **THEN** the command reports the state of each of the **7** surfaces (was 6):
  - `komodo`
  - `pangolin`
  - **`infisical` (updated to use the API not local SQLite)**
  - `newt (bunchloch)`
  - `pocket-id`
  - `tinyauth`
  - **`machine-identities-seeded` (NEW — reports count of `bons-iac` + 7 surface identities that exist)**
- **AND** if Pocket ID DB is empty, the message is actionable:
  `pocket-id: v2.9.0 but DB is empty (run: bun run iac:bootstrap-pocketid-admin)`
- **AND** if Tinyauth container is NOT Up:
  `tinyauth: http://tinyauth.cianfhoghlaim.ie returned {status_code}`
- **AND** if the bons-iac machine identity is missing:
  `infisical: bons-iac identity missing (run: bun run iac:bootstrap-infisical)`

## REMOVED Requirements

### Requirement: infisical-first Komodo procedure uses ssh arm1-oci (REMOVED)

**Reason**: The previous procedure called `ssh arm1-oci '<curl command>'` which cannot run from a CI agent, dagger workflow, or remote operator laptop. It also bypasses the bons IaC's secrets + state management entirely. Replaced by the HTTP-only checks (no SSH) + the new `deploy-infisical-arm1-oci` procedure (which uses Komodo's stack runner, not raw SSH).

**Migration**: Any operator who was running `km run procedure infisical-first` as the deployment mechanism MUST migrate to `km run procedure deploy-infisical-arm1-oci` (the new procedure). The old `infisical-first` procedure is rewritten to be a health check only (HTTP checks for vault + project + identities) — it no longer deploys anything.

### Requirement: iac:rotate-auth uses inline fetchInfisicalSecret (REMOVED)

**Reason**: The previous rotate-auth had its own private `fetchInfisicalSecret` function that duplicated the Infisical client logic (with a bug — JSON body when the server wants form-encoded). Promoted to the canonical `iac/clients/infisical-rest.ts` helper that the rotate-auth command now imports.

**Migration**: Any code that imported `fetchInfisicalSecret` from `iac/commands/rotate-auth.ts` MUST import it from `iac/clients/infisical-rest.ts` instead.
