## ADDED Requirements

### Requirement: 5th-surface lock — no 6th surface without a separate openspec change

The system SHALL NOT add a 6th row to the 4 canonical surfaces table
without first opening a separate openspec change that explicitly amends
this requirement.

The current 5-surface table (per this spec's R-5Surface requirement) is
locked as of the archive date of
`2026-07-18-british-isles-portal-activation-v3`.

#### Scenario: A developer asks for a 6th surface

- **GIVEN** a developer asks "can I add a 6th surface to the table?"
- **WHEN** the openspec change is reviewed
- **THEN** the reviewer MUST reject any PR that adds a 6th row without a
  separate openspec change explicitly amending this requirement

### Requirement: 5th-surface activation marker

The system SHALL publish the 5th surface (`cianfhoghlaim-leaving-cert`)
to `portal.cianfhoghlaim.ie` via the `portal-cloudflare-r2` stack
(see `openspec/changes/2026-07-18-british-isles-portal-activation-v3/`).

The Pangolin resource binding SHALL live at
`bonneagar/pangolin/resources/portal.yaml`.

#### Scenario: portal.cianfhoghlaim.ie resolves

- **WHEN** the operator opens `https://portal.cianfhoghlaim.ie`
- **THEN** the British Isles map renders with Éire active
- **AND** at least 1 NCCA subject (Mathematics) shows the 6-section shell
- **AND** the CopilotKit sidebar is mounted with EN+GA

### Requirement: Pocket ID SSO as the 7th layer authentication provider

The system SHALL document Pocket ID OIDC as the canonical SSO provider
in the 7-layer agentic-frontend-framework stack spec. The 5 OIDC
audiences are documented in the `infrastructure-stacks` spec.

#### Scenario: A new agent surface is added

- **WHEN** a developer looks at the 7-layer stack spec
- **THEN** they see Pocket ID OIDC as the canonical SSO provider
- **AND** they see the 5 OIDC audiences
