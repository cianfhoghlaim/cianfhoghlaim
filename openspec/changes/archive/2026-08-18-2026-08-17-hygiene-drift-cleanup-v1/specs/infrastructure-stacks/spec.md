# infrastructure-stacks

## ADDED Requirements

### Requirement: Locket version invariant

The system SHALL fail `mise run lint:locket-version` if any
`compose.yaml` file in `bonneagar/stacks/**/` references
`bpbradley/locket:infisical` at a version < v0.18.0.

The reason: per the `2026-08-15-bonneagar-infra-remediation-v2`
change, the upstream `locket v0.17.3` image ships snake_case field
names while the Infisical v0.161+ REST API requires camelCase
(`projectId`, `secretPath`, `secretType`); the upstream sidecar
422s on every call. The workaround is the
`bonneagar/locket-shim/cianfhoghlaim-locket-shim.py` 295-line Python
script, which is the canonical sidecar until `locket v0.18.0-rc.1`
ships the camelCase fix.

This lint gate ensures that operators don't accidentally roll back
to the broken upstream image, and tracks when the upstream fix
lands so we can retire the shim.

#### Scenario: A new stack adds `locket:infisical` at < v0.18.0

- **WHEN** `cd bonneagar/stacks/newstack && compose up -d` brings up a
  container with `bpbradley/locket:infisical:v0.17.3`
- **THEN** `mise run lint:locket-version` exits 1 with a finding like
  `bonneagar/stacks/newstack/compose.yaml:<line>: locket:infisical v0.17.3 is < v0.18.0 (camelCase fix) — substitute the shim image at ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0`
- **AND** the operator MUST either (a) upgrade to >= v0.18.0, or (b) substitute `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0`

#### Scenario: A stack uses the shim image

- **GIVEN** `bonneagar/stacks/openclaw/compose.yaml` references
  `ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0`
- **WHEN** `mise run lint:locket-version` runs
- **THEN** the lint exits 0 (the shim is exempt from the version check)

#### Scenario: The upstream ships the camelCase fix

- **WHEN** `bpbradley/locket:infisical:v0.18.0` is published with the
  camelCase Infisical v0.161+ field names
- **THEN** `mise run lint:locket-version` continues to pass (any
  version >= v0.18.0 is accepted)
- **AND** the shim retirement becomes a forward-seed (Mega-5 candidate)