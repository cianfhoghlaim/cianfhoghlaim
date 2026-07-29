## ADDED Requirements

### Requirement: Pocket ID + Pangolin + Komodo OIDC wiring MUST be automatable via the bons IaC + the wire-pocketid-pangolin-komodo.sh script

The system SHALL provide a single one-shot automation that wires Pocket ID
as the OIDC identity provider for both Komodo (orchestrator) and
Pangolin (proxy) so non-technical operators do not need to manually
configure 4+ steps (Pocket ID OIDC client creation, Komodo OIDC config,
Pangolin IDP creation, Pangolin Resource IdP binding).

#### Scenario: Operator first deploys the cianfhoghlaim stack

- GIVEN the operator has populated the repo's .env with the
  required credentials (POCKETID_API_KEY, PANGOLIN_API_KEY, and
  optionally KOMODO_PASSWORD)
- WHEN the operator runs ./scripts/wire-pocketid-pangolin-komodo.sh
- THEN the script:
  - Creates (or finds) the komodo OIDC client in Pocket ID via
    POST /api/oidc/clients + POST /api/oidc/clients/{id}/secret
  - Updates Komodos OIDC config via POST /api/v1/set-core-config
  - Creates (or finds) the Pocket ID Identity Provider in Pangolin
    via POST /api/v1/idp
  - Writes the credentials to .env + (optionally) to the local
    Infisical vault at /komodo
  - Writes an audit record to /tmp/wire-pocketid-pangolin-komodo-{ts}.json
- AND the operator can verify the wiring by visiting
  https://komodo.cianfhoghlaim.ie and https://pangolin.cianfhoghlaim.ie

#### Scenario: Operator re-runs the script (idempotency)

- GIVEN the wiring is already in place
- WHEN the operator runs the script again
- THEN each step checks for existing state first and skips

#### Scenario: Operator wants to rotate the OIDC client secret

- WHEN the operator runs the script with --force
- THEN the script deletes the existing komodo OIDC client and creates a new one

### Requirement: Pocket ID OIDC clients are reconciled idempotently by the bash script + Pocket ID admin API (re-running is a no-op)

The system SHALL ensure that the wire-pocketid-pangolin-komodo.sh script
never creates duplicate OIDC clients in Pocket ID, never overwrites valid
Pangolin IdP configs, and never downgrades a working Komodo OIDC setup.

#### Scenario: Partial deployment (Komodo not yet up)

- WHEN the operator runs the script with --skip-komodo
- THEN the script skips Step 2 (Komodo OIDC config update) with a warning log
- AND still completes Steps 1, 3, 4, 5, 6 (Pocket ID + Pangolin + .env + audit)

#### Scenario: Partial deployment (Pangolin not yet up)

- WHEN the operator runs the script with --skip-pangolin
- THEN the script skips Step 3 (Pangolin IDP creation) with a warning log
- AND still completes Steps 1, 2, 4, 5, 6

#### Scenario: Script runs against a non-existent Komodo/Pangolin (DNS failure)

- WHEN the operator runs the script but Pocket ID / Pangolin / Komodo DNS resolution fails
- THEN the script logs the DNS failure and exits with a clear error code

#### Scenario: Pocket ID rejects the client_secret fetch (auth or permission issue)

- WHEN the Pocket ID admin API returns 401 or 403
- THEN the script logs the error and exits with code 1
