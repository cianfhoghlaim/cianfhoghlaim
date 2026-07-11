# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Drift-remediation pass

The IaC at `bonneagar/iac/` SHALL expose a `iac:bootstrap`
command at the repo root via the cianfhoghlaim `package.json`
script `iac:bootstrap` (delegating to
`bun run --cwd bonneagar iac:bootstrap`).

#### Scenario: Root-level iac:bootstrap is callable

- **WHEN** a developer runs `bun run iac:bootstrap` from the
  cianfhoghlaim repo root
- **THEN** the IaC SHALL execute the 8-phase Pulumi →
  Infisical → Pangolin → Komodo → Newt → all syncs sequence
- **AND** the exit code SHALL be 0 on success

#### Scenario: iac:bootstrap supports --dry-run

- **WHEN** a developer runs `bun run iac:bootstrap --dry-run`
- **THEN** the IaC SHALL print the diff between the declared
  state and the actual state
- **AND** SHALL NOT mutate any remote system

### Requirement: preflight:arm-oci safety script

The repo SHALL provide a `bun run preflight:arm-oci` script
at `scripts/preflight-arm-oci.ts` that runs 4 checks before any
arm-oci stack deploy:

1. **Pangolin health** — `GET ${PANGOLIN_URL}/api/v1/` returns 200
2. **Komodo health** — `GET ${KOMODO_URL}/ping` returns 200
3. **Infisical health** — `GET ${INFISICAL_URL}/api/status` returns 200
4. **Process namespace isolation** — the opencode session PID
   MUST NOT share a PID namespace with any running container
   named `openchamber`, `openclaw`, `hermes`, `komodo`,
   `pangolin`, or `infisical`

#### Scenario: All 4 checks pass

- **WHEN** an opencode session runs `bun run preflight:arm-oci`
- **AND** Pangolin + Komodo + Infisical all return 200
- **AND** the opencode PID is in a distinct PID namespace
- **THEN** the script SHALL exit 0 with "ALL CHECKS PASSED"

#### Scenario: Pangolin is unreachable

- **WHEN** an opencode session runs `bun run preflight:arm-oci`
- **AND** Pangolin returns 5xx or times out
- **THEN** the script SHALL exit 1 with a clear error message
  identifying which check failed and how to remediate

#### Scenario: Opencode PID shares namespace with openchamber

- **WHEN** an opencode session runs `bun run preflight:arm-oci`
- **AND** the current PID is in the same PID namespace as a
  running openchamber container
- **THEN** the script SHALL exit 1 with the message
  "REFUSING TO DEPLOY: opencode PID <X> shares namespace with
  openchamber container <Y>; restart opencode outside the
  openchamber namespace first"
