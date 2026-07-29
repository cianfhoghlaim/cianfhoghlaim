# Spec Delta — agent-platform-cluster

This delta adds 3 new requirements to the existing
`agent-platform-cluster` capability. Existing requirements are
preserved unchanged.

## ADDED Requirements

### Requirement: Bundling procedure `deploy-agent-fleet-bunchloch`

The system SHALL provide a Komodo procedure
`deploy-agent-fleet-bunchloch.toml` at
`bonneagar/komodo/procedures/` that bundles the 12 main
agents + the 8 NCCA subject agents + the 3 educational agents
into a single 4-stage omnibus:

- **Stage 1**: pre-reqs (cross-cutting prerequisites)
- **Stage 2**: DeployStack 8 supporting stacks (lakehouse + litellm + langfuse + mlflow + cognee + graphiti + lancedb + falkordb)
- **Stage 3**: DeployStack 3 agent surfaces (hermes + openclaw + openchamber)
- **Stage 4**: health verify (12 agents reachable, 8 NCCA agents reachable, 3 educational agents reachable)

The procedure SHALL accept `--skip=<stage>` flags like the
existing `deploy-agent-platform-cluster-bunchloch` omnibus.

#### Scenario: `deploy-agent-fleet-bunchloch` completes all 4 stages

- **GIVEN** the 8 supporting stacks are deployed (lakehouse + litellm + langfuse + mlflow + cognee + graphiti + lancedb + falkordb)
- **WHEN** `km run procedure deploy-agent-fleet-bunchloch`
- **THEN** the 3 agent surfaces SHALL be deployed (hermes + openclaw + openchamber)
- **AND** the 12 main agents SHALL be reachable via `AGENT_REGISTRY`
- **AND** the 8 NCCA subject agents SHALL be reachable via `agents.tuatha.<slug>_agent`
- **AND** the 3 educational agents SHALL be reachable via `agents.meaisinfhoghlaim.educational.<slug>_agent`

#### Scenario: `--skip=` flag accepts per-stage names

- **GIVEN** the operator wants to skip the agent surfaces (already deployed)
- **WHEN** `km run procedure deploy-agent-fleet-bunchloch --skip=stage3`
- **THEN** Stages 1, 2, 4 SHALL run
- **AND** Stage 3 SHALL be skipped
- **AND** the procedure SHALL exit 0

### Requirement: Bundling procedure `deploy-agent-fleet-arm1-oci`

The system SHALL provide a Komodo procedure
`deploy-agent-fleet-arm1-oci.toml` at
`bonneagar/komodo/procedures/` that mirrors the bunchloch
procedure but adapted for `arm1-oci` (the 6-stage omnibus with
`preflight:arm-oci`):

- **Stage 1**: pre-reqs (`preflight:arm-oci` + cross-cutting prerequisites)
- **Stage 2**: control-plane foundation (pangolin + langfuse + observability)
- **Stage 3**: 8 supporting stacks (lakehouse + litellm + mlflow + cognee + graphiti + lancedb + falkordb + mlflow)
- **Stage 4**: 3 agent surfaces (hermes + openclaw + openchamber)
- **Stage 5**: Pangolin routes (12 agents + 8 NCCA + 3 educational)
- **Stage 6**: health verify

The procedure SHALL have `server_id = "arm1-oci"` at the top
of the file (the cross-host dispatch convention from the
`2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`
change).

#### Scenario: `deploy-agent-fleet-arm1-oci` runs `preflight:arm-oci` as Stage 1

- **GIVEN** the arm1-oci host is reachable
- **WHEN** `km run procedure deploy-agent-fleet-arm1-oci`
- **THEN** Stage 1 SHALL run `preflight:arm-oci` first
- **AND** if `preflight:arm-oci` returns ALL CHECKS PASSED,
  Stages 2-6 SHALL proceed
- **AND** if `preflight:arm-oci` reports any failure, the
  procedure SHALL exit with a non-zero status

#### Scenario: `deploy-agent-fleet-arm1-oci` has `server_id = "arm1-oci"`

- **GIVEN** `bonneagar/komodo/procedures/deploy-agent-fleet-arm1-oci.toml`
- **WHEN** `head -1 deploy-agent-fleet-arm1-oci.toml`
- **THEN** the output SHALL be `server_id = "arm1-oci"`

### Requirement: Operator runbooks `agent-fleet-*-2026-08.md`

The system SHALL provide 2 operator runbooks at
`bonneagar/deploy-runbooks/`:

- `agent-fleet-bunchloch-2026-08.md` — the operator's
  quick-start for bunchloch (the `bun run deploy-agent-fleet-bunchloch`
  5-command sequence)
- `agent-fleet-arm1-oci-2026-08.md` — the operator's
  quick-start for arm1-oci (the `bun run deploy-agent-fleet-arm1-oci`
  6-command sequence with WARP + Locket)

Each runbook SHALL include:

- Pre-flight checks (the 4 outputs the operator must verify)
- Bundled procedure invocation (the 1 `km run` command)
- Post-archive verification (the 3 health endpoints)
- Rollback (the 1 `km run procedure rollback` command)

#### Scenario: `agent-fleet-bunchloch-2026-08.md` runbook exists

- **GIVEN** `bonneagar/deploy-runbooks/agent-fleet-bunchloch-2026-08.md`
- **WHEN** tested against the current bunchloch state
- **THEN** the runbook's 5-command sequence SHALL result in
  all 12 + 8 + 3 agents being reachable within 10 min

#### Scenario: `agent-fleet-arm1-oci-2026-08.md` runbook exists

- **GIVEN** `bonneagar/deploy-runbooks/agent-fleet-arm1-oci-2026-08.md`
- **WHEN** tested against the current arm1-oci state
- **THEN** the runbook's 6-command sequence SHALL result in
  all 12 + 8 + 3 agents being reachable via `*.cianfhoghlaim.ie`
  within 15 min
- **AND** the 3 health endpoints SHALL return 200:
  - `https://hermes.cianfhoghlaim.ie/api/health`
  - `https://openclaw.cianfhoghlaim.ie/api/health`
  - `https://openchamber.cianfhoghlaim.ie/api/health`