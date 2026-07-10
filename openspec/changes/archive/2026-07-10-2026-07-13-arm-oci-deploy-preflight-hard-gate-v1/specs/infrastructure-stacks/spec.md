# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: preflight:arm-oci hard-gates arm1-oci cluster deployment

The system SHALL require the `preflight:arm-oci` safety gate to exit 0
before any ClusterDeployment procedure on `arm1-oci` proceeds past
Stage 0. The preflight report (`--emit-md` output) SHALL be captured
to `/tmp/preflight-reports/arm-oci/<utc-timestamp>.md` for every
deploy attempt (success or failure).

The omnibus `deploy-agent-platform-cluster-arm1-oci` MUST set
`require_success = true` on its Stage 0 `preflight` RunShellCommand so
that a non-zero preflight exit code aborts the omnibus before Stage 1
(control-plane foundation).

The `--skip=preflight` flag SHALL be rejected (exit code 2) on any
arm1-oci cluster procedure; preflight is a mandatory first step.

#### Scenario: preflight exits 0 — omnibus proceeds

- **WHEN** `bun run preflight:arm-oci --strict --emit-md` exits 0
- **THEN** the omnibus proceeds to Stage 1 (control-plane foundation)
- **AND** the captured report exists at `/tmp/preflight-reports/arm-oci/<utc-ts>.md`
- **AND** the report ends with `PASS` or `ALL CHECKS PASSED`

#### Scenario: preflight exits non-zero — omnibus aborts at Stage 0

- **WHEN** `bun run preflight:arm-oci --strict --emit-md` exits non-zero
- **THEN** the omnibus aborts at Stage 0
- **AND** no Stage 1+ execution is attempted
- **AND** the captured report retains the failure cause (e.g.
  `Pangolin unreachable`, `Komodo unreachable`, `Infisical unreachable`,
  `process-namespace conflict`)
- **AND** the operator sees the report path in the Komodo log

#### Scenario: --skip=preflight is rejected

- **WHEN** `km run procedure deploy-agent-platform-cluster-arm1-oci -- --skip=preflight` runs
- **THEN** the procedure exits with code 2
- **AND** the operator sees the message "preflight is a mandatory first step; --skip=preflight is rejected"
- **AND** no Stage 0+ execution is attempted