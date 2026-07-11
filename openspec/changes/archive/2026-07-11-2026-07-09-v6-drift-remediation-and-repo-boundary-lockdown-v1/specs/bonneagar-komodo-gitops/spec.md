## ADDED Requirements

### Requirement: Pre-flight gate before resource-sync apply

The 3 Komodo resource-syncs MUST NOT be applied without first
running `bun run preflight:arm-oci`. The resource-syncs are
arm1-oci.toml, bunchloch.toml, and cross-cutting.toml.

#### Scenario: Resource-sync apply attempted without preflight

- **WHEN** an agent runs `iac:bootstrap` (which registers the
  3 resource-syncs) without first running
  `bun run preflight:arm-oci`
- **THEN** the IaC SHALL refuse with exit 1 and the message
  "REFUSING TO APPLY: run `bun run preflight:arm-oci` first"

#### Scenario: Resource-sync apply with preflight green

- **WHEN** an agent runs `bun run preflight:arm-oci` and it
  exits 0
- **AND** then runs `iac:bootstrap`
- **THEN** the resource-syncs SHALL be applied normally