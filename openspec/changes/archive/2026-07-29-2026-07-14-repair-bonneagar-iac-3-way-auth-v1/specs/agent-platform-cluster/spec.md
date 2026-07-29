# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: iac:rotate-auth mints fresh Pangolin + Komodo + Infisical credentials via Pocket ID OIDC

The system SHALL provide a `bun run iac:rotate-auth` command that
auto-rotates the 3 critical IaC credentials via the Pocket ID OIDC
`client_credentials` flow. The rotation is idempotent and emits a JSON
audit record.

The command:
1. Discovers Pocket ID's `.well-known/openid-configuration`
2. POSTs to Pocket ID's `/oidc/token` with `grant_type=client_credentials`
3. Receives an `access_token` (JWT)
4. POSTs to Pangolin's form-login endpoint to exchange the JWT for a Pangolin session cookie
5. Mints a fresh Pangolin API key via `PUT /org/{orgId}/api-key` → writes to `PANGOLIN_API_KEY` in `~/.env`
6. Reads `KOMODO_PASSWORD` from Infisical (using the universal auth client) → writes to `~/.env`
7. Reads the `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET` from the Infisical vault → writes to `~/.env`
8. Emits a JSON audit record to `/tmp/auth-rotation-{ts}.json`

The command SHALL be wired into `iac:auth.ts` to replace the existing
`// TODO: Pocket ID OIDC client_credentials flow` placeholder.

#### Scenario: rotation succeeds

- **GIVEN** the Pocket ID OIDC client is configured (client_id + client_secret in `~/.env`)
- **AND** the Infisical universal auth client is functional
- **WHEN** `bun run iac:rotate-auth` runs
- **THEN** all 3 credentials are written to `~/.env` (PANGOLIN_API_KEY, KOMODO_PASSWORD, INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET)
- **AND** a JSON audit record is emitted to `/tmp/auth-rotation-{ts}.json`
- **AND** the procedure exits 0

#### Scenario: rotation fails (Pocket ID unreachable)

- **WHEN** the Pocket ID endpoint returns 503 (unreachable)
- **THEN** the command exits 1
- **AND** the existing credentials in `~/.env` are NOT modified
- **AND** a JSON audit record is emitted to `/tmp/auth-rotation-failed-{ts}.json` with the failure reason

#### Scenario: rotated credentials are used by iac:sync:sites

- **WHEN** `bun run iac:rotate-auth` has just succeeded
- **AND** `bun run iac:sync:sites` runs immediately afterward
- **THEN** the `iac:sync:sites` command uses the freshly-minted `PANGOLIN_API_KEY`
- **AND** the Pangolin Integrations API call succeeds (no 401)
- **AND** the bunchloch-newt site is provisioned + credentials written
