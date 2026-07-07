## MODIFIED Requirements

### Requirement: Infisical URI Format Conformance

The system SHALL require every `secrets.env` file under
`bonneagar/stacks/` to use the canonical `infisical://dev-baile/<service>/<key>`
URI format compatible with the Locket sidecar at runtime. Jinja template
syntax (`{{ infisical:///... }}`) SHALL NOT be used.

#### Scenario: Bunchloch local Infisical compose pins the 2026-07 release

- **GIVEN** `bonneagar/stacks/infisical/compose.yaml`
- **AND** Firecrawl-verified latest stable is `infisical/infisical:v0.161.12`
  (2026-07-03, confirmed via https://github.com/Infisical/infisical/releases)
- **WHEN** the file is read
- **THEN** the `backend` service SHALL declare
  `image: infisical/infisical:v0.161.12` (NOT `:latest`)
- **AND** the `db` service SHALL declare `image: postgres:16-alpine` (NOT
  `:14-alpine`; PostgreSQL 16 is upstream-recommended)
- **AND** the `redis` service SHALL declare `image: redis:7.4-alpine` (NOT
  `:alpine`)

#### Scenario: Consumer stacks (lakehouse, litellm, mlflow, unstract) secrets.env are Locket-compatible

- **GIVEN** all 4 consumer stack `secrets.env` files:
  `bonneagar/stacks/{lakehouse,litellm,mlflow,unstract}/secrets.env`
- **WHEN** each file is grepped for `{{ infisical:///`
- **THEN** zero matches SHALL be found
- **AND** every secret reference uses the `infisical://dev-baile/...`
  URI form
- **AND** the `unstract/secrets.env` SHALL declare at minimum 20 canonical
  `infisical://dev-baile/unstract/<key>` entries covering the full
  upstream 15-service env surface