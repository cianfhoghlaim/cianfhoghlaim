## ADDED Requirements

### Requirement: PocketID IdP MUST be bound to every Pangolin Resource (4th manual step) — wired by wire-pocketid-resource-idp.sh

The system SHALL ensure that the PocketID Identity Provider (created in
step 3 by wire-pocketid-pangolin-komodo.sh) is bound to every Pangolin
Resource (site) so that users in Pocket ID can access the Resource.

#### Scenario: Operator runs wire-pocketid-resource-idp.sh --all

- **WHEN** the operator runs `wire-pocketid-resource-idp.sh --all`
- **THEN** the script:
  - Lists all Resources in the org via `GET /api/v1/site-resources`
  - For each Resource, calls `POST /v1/org/{orgId}/site-resource/{id}/idp`
    with the PocketID IdP id
  - Logs success/failure per Resource
  - Writes an audit record

#### Scenario: Operator runs wire-pocketid-resource-idp.sh --resource=mlflow.cianfhoghlaim.ie

- **WHEN** the operator specifies a single Resource
- **THEN** the script binds the PocketID IdP only to that Resource

#### Scenario: A Resource already has the PocketID IdP bound

- **WHEN** the operator runs the script multiple times
- **THEN** the script detects the existing binding (via the Pangolin
  Resource IdPs list) and skips the duplicate
- **OR** the script logs a warning that the IdP is already bound

### Requirement: Komodo + Periphery MUST be self-configured from the get-go (5th manual step) — wired by bootstrap-komodo-periphery.sh

The system SHALL ensure that when a new Komodo + Periphery deployment is
started, the auto-derive workflow runs and Periphery self-registers with
Pangolin + auto-derives its API key from Pocket ID.

#### Scenario: Operator runs bootstrap-komodo-periphery.sh after Komodo + Periphery are deployed

- **WHEN** the operator runs `bootstrap-komodo-periphery.sh`
- **THEN** the script:
  1. Mints a fresh Pangolin API key (via Pocket ID OIDC client_credentials)
  2. Self-registers Periphery with Pangolin (Newt protocol: POST /api/v1/newt)
  3. Wipes stale credentials from .env
  4. Verifies reachability of Komodo + Pangolin
  5. Writes an audit record to /tmp/bootstrap-komodo-periphery-{ts}.json

#### Scenario: PocketID secret rotation via cron

- **WHEN** the cron job `rotate-pocketid-secrets.sh` runs (default: 3am on the 1st of every 3rd month)
- **THEN** the script:
  1. Fetches a fresh secret via Pocket ID admin API (X-API-Key auth)
  2. Mints a fresh Pangolin API key (7-day TTL)
  3. Updates .env atomically
  4. Writes an audit record to /tmp/pocketid-rotation-{ts}.json
  5. Exits 0 on success or 1 on failure (with the failure logged)
