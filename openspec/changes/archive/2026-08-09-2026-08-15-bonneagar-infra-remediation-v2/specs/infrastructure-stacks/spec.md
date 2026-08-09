# Delta: `infrastructure-stacks`

## ADDED Requirements

### Requirement: `stacks/newt-arm1-oci/` follows the 6-file GOLD_STANDARD

The system SHALL add `bonneagar/stacks/newt-arm1-oci/` as a new stack
with the 6 GOLD_STANDARD files. The stack SHALL be a control-plane
resource that wires the newt WireGuard tunnel client to the Pangolin
mesh on arm1-oci.

#### Scenario: Stack-doctor passes the new stack

- **WHEN** `bun run stack-doctor` runs against `bonneagar/stacks/newt-arm1-oci/`
- **THEN** the gate SHALL pass with `newt-arm1-oci` declared as
  `host:arm1-oci`, `tier:control-plane`, `type:wireguard-tunnel`
- **AND** the `sidecar.yaml` SHALL use the `bons-locker-shim:infisical-0.2.0`
  image (per the `locket-shim` stack convention)
- **AND** the `secrets.env` SHALL have 2
  `infisical://dev-baile/pangolin/clients/arm1-oci/...` URIs
- **AND** the `pangolin.yaml` SHALL declare the no-op sentinel (newt is
  outbound-only)
- **AND** the `blueprint.yaml` SHALL declare the no-op sentinel
- **AND** the `.env.example` SHALL document every env var

### Requirement: `deploy:full` extends to 10 phases (was 8)

The system SHALL extend the `deploy:full` orchestrator to 10 phases by
inserting 3 NEW phases (iac-auth-rotate, pocketid-oidc-wire,
pangolin-client-install) between the existing preflight (1) and
control-plane-up (formerly 2). The orchestrator SHALL also combine
dagster-materialize + dagster-sensor-health-gate into a single phase
10 to keep the total at 10 phases.

#### Scenario: Operator runs the 10-phase orchestrator

- **WHEN** the operator runs `mise run deploy:full`
- **THEN** the orchestrator SHALL execute all 10 phases in order:
  (1) preflight-arm-oci, (2) iac-auth-rotate, (3) pocketid-oidc-wire,
  (4) pangolin-client-install, (5) control-plane-up, (6) lakehouse-up,
  (7) data-stacks-up, (8) ocr-backends-up, (9) agent-surfaces-up,
  (10) dagster-materialize-and-sensor-health-gate
- **AND** the resumable checkpoint at
  `~/.cianfhoghlaim/deploy-state.json` SHALL track each phase's
  `pending` / `running` / `success` / `failed` status
- **AND** `--phase=N` SHALL run only phase N

## MODIFIED Requirements

None.

## REMOVED Requirements

None.
