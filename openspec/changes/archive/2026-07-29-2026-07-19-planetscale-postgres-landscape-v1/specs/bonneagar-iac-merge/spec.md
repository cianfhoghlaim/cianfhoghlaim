# Spec Delta: bonneagar-iac-merge

## ADDED Requirements

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
