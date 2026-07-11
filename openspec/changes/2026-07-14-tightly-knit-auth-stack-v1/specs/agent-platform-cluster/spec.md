# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: iac:bootstrap orchestrates all 5 auth components as a single tightly-integrated system

The system SHALL provide a `bun run iac:bootstrap` command that
orchestrates all 5 auth components (Pulumi → Infisical → Pocket ID →
Pangolin → Komodo → Tinyauth → Newt → sync) as a single, idempotent
end-to-end flow. Each phase checks the current state and (re)deploys as
needed.

Pocket ID + Tinyauth SHALL be first-class systems in the IaC (not
manually configured outside the bons). The bootstrap SHALL include a
new `iac:bootstrap-pocketid-admin` subcommand that creates the first
admin user + the bons-iac OIDC client via the Pocket ID admin API
(only the operator's browser-passkey-registration is manual).

The system SHALL also provide `iac:health` that does a 6-way check
(added Pocket ID + Tinyauth on top of the previous 4-way check of
Komodo + Pangolin + Infisical + Newt). Each check SHALL report a clear
actionable error message.

#### Scenario: iac:bootstrap runs end-to-end on cold-boot

- **WHEN** the bons host has no Pocket ID, no Tinyauth, no newt containers
- **THEN** `iac:bootstrap` orchestrates all 9 phases in order:
  1. Pulumi (TODO)
  2. Infisical secrets
  3. Pocket ID deploy + health check (via `km run procedure deploy-pocket-id-bunchloch`)
  4. Auth wiring (creates bons-iac OIDC client via admin API; mints Pangolin API key via OIDC client_credentials)
  5. Pangolin private resources
  6. Komodo Core + Periphery
  7. Tinyauth deploy + health check (via `km run procedure deploy-tinyauth-bunchloch`)
  8. Newt (sync-sites)
  9. All sync commands
- **AND** the bootstrap is idempotent: re-running on a warm cluster skips
  the already-done phases.

#### Scenario: iac:bootstrap-pocketid-admin is run after a DB wipe

- **GIVEN** the Pocket ID DB has 0 users (e.g. after a wipe)
- **AND** `POCKETID_ADMIN_PASSWORD` is in env
- **WHEN** `bun run iac:bootstrap-pocketid-admin` runs
- **THEN** the command:
  1. Logs in to Pocket ID as admin (uses `POCKETID_ADMIN_PASSWORD`)
  2. Enables signup
  3. Creates a signup token (1-hour expiry)
  4. Prints the signup URL to stdout (operator opens in browser)
  5. Waits for operator to press ENTER
  6. Verifies the user was created (via the admin API)
  7. Disables signup (security)
  8. Creates the bons-iac OIDC client (with `client_credentials` grant)
  9. Writes `POCKETID_CLIENT_ID` + `POCKETID_CLIENT_SECRET` to `~/.env`
  10. Emits a JSON audit record to `/tmp/pocketid-bootstrap-{ts}.json`
- **AND** the operator's next `bun run iac:health` exits 0 for the
  Pocket ID + tinyauth checks.

#### Scenario: iac:health returns 6-way actionable errors

- **WHEN** the user runs `bun run iac:health` with a broken auth state
- **THEN** the command reports the state of each of the 6 surfaces:
  - `komodo`: count of servers + stacks (or auth error)
  - `pangolin`: `{"healthy": true|false, "detail": "..."}`
  - `infisical`: `{"healthy": true|false, "detail": "..."}`
  - `newt (bunchloch)`: container status + version + WireGuard handshake
  - `pocket-id`: v{version}, {dbUsers} users, {dbOidcClients} OIDC clients, signup=on|off
  - `tinyauth`: HTTP status of `/api/health`
- **AND** if Pocket ID DB is empty, the message is actionable:
  `pocket-id: v2.9.0 but DB is empty (run: bun run iac:bootstrap-pocketid-admin)`
- **AND** if Tinyauth container is NOT Up:
  `tinyauth: http://tinyauth.cianfhoghlaim.ie returned {status_code}`

#### Scenario: Pocket ID + Tinyauth are part of the cross-cutting prereq order

- **GIVEN** the bons cross-cutting prereq order
- **WHEN** Komodo pulls the resource-sync
- **THEN** the order is:
  1. `pangolin-first`
  2. `komodo-core`
  3. `infisical-first`
  4. `locket-deploy`
  5. `deploy-pocket-id-bunchloch` (NEW in this change)
  6. `deploy-tinyauth-bunchloch` (NEW in this change)
  7. `deploy-pocket-id-arm1-oci` (NEW in this change; migration target)
  8. `deploy-pangolin-newt-arm1-oci`
  9. `deploy-newt-bunchloch-v2`
- **AND** the operator can run any one of them in any order (each is
  idempotent and health-checks its own state)
