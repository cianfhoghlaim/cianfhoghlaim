# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: iac:sync:sites provisions newt sites via the Pangolin Integrations API

The system SHALL provide a `bun run iac:sync:sites` command that walks
`stacks/*/site.yaml` and provisions each newt site via the Pangolin
Integrations API (`POST /org/{orgId}/site`). The returned `newtId` +
`newtSecret` SHALL be written to local `~/.env` (under
`PANGOLIN_NEWT_<NAME>_ID` + `PANGOLIN_NEWT_<NAME>_SECRET`) AND to the
Infisical `dev-baile` vault (so other hosts can fetch via Locket).

The command SHALL be idempotent: re-running skips sites that already
exist (via `GET /org/{orgId}/site/{niceId}`) and does not re-issue
credentials.

The command SHALL be wired into `iac:bootstrap` Phase 6 (the missing
"newt deploy" step that was previously a TODO).

#### Scenario: new site is provisioned

- **GIVEN** `stacks/newt/site.yaml` declares `niceId: bunchloch-newt`
- **AND** the site does NOT exist in Pangolin
- **WHEN** `bun run iac:sync:sites` runs
- **THEN** the command POSTs to `/org/{orgId}/site` → gets back `{ id, newtId, newtSecret }`
- **AND** writes `PANGOLIN_NEWT_BUNCHLOCH_ID` + `PANGOLIN_NEWT_BUNCHLOCH_SECRET` to `~/.env`
- **AND** writes the same to Infisical `/pangolin/` (if Infisical auth is configured)
- **AND** the `deploy-newt-bunchloch-v2` procedure can now read the credentials via Locket

#### Scenario: existing site is skipped (idempotent)

- **GIVEN** the bunchloch-newt site already exists in Pangolin
- **WHEN** `bun run iac:sync:sites` runs
- **THEN** the command GETs `/org/{orgId}/site/bunchloch-newt` → finds the existing site
- **AND** does NOT POST a new site
- **AND** does NOT overwrite the existing credentials in `~/.env`
- **AND** logs `bunchloch-newt (already exists, id=<n>)`

#### Scenario: credentials are written to local .env

- **WHEN** `bun run iac:sync:sites` runs with a valid Pangolin API key
- **AND** Infisical auth is NOT configured
- **THEN** the command writes newtId + newtSecret ONLY to local `~/.env`
- **AND** logs a warning: `infisical: not configured — credentials will be written to local .env only`
- **AND** the procedure still succeeds (exit 0)

#### Scenario: iac:bootstrap Phase 6 calls iac:sync:sites

- **WHEN** `bun run iac:bootstrap` runs
- **THEN** Phase 6 (the "Newt (Pangolin tunnel client)" step) calls `await syncSites()`
- **AND** the bootstrap is no longer stuck at a TODO for the Newt step
