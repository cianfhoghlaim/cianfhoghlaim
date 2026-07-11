# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: Bootstrap procedure composes 7 stages into one km invocation

The system SHALL provide an `agent-platform-cluster-arm1-oci-bootstrap`
Komodo procedure that brings up the agent platform on arm1-oci via a
single `km run procedure` invocation. The procedure SHALL compose 7
stages:

1. **pre-reqs** — Check 9 environment variables exist
   (INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET, INFISICAL_PROJECT_ID,
   DOCKER_REGISTRY_TOKEN, OPENCODE_AUTH_TOKEN, MCP_CURATOR_AUTH_TOKEN,
   LANE_POOL_STORAGE_S3_BUCKET, LANE_POOL_STORAGE_S3_ACCESS_KEY,
   LANE_POOL_STORAGE_S3_SECRET_KEY) AND check the arm1-oci resource
   ceiling (CPU ≤ 85%, MEM ≤ 90%).
2. **parallel-image-builds** — Run 3 Komodo `Build` resources in
   parallel (`openchamber-arm1-oci` + `openclaw-arm1-oci` +
   `hermes-arm1-oci`).
3. **iac-bootstrap** — Invoke `pnpm tsx bonneagar/iac/commands/bootstrap.ts arm1-oci`.
4. **omnibus-deploy** — Invoke `deploy-agent-platform-cluster-arm1-oci`
   (the preflight-gated omnibus from Improvement 3).
5. **health-checks** — Curl `https://{hermes,openclaw,openchamber}.cianfhoghlaim.ie/api/health`
   (all 3 MUST return 200).
6. **emit-artifact** — Write
   `/tmp/agent-platform-cluster/arm-oci-<utc-ts>.json` containing the
   resolved cluster fingerprint (URLs + image tags).
7. **validate** — Run `bun run validate-stacks`.

#### Scenario: All 3 builds succeed in parallel

- **WHEN** all 3 image builds (`openchamber-arm1-oci` + `openclaw-arm1-oci` + `hermes-arm1-oci`) complete with exit 0
- **THEN** `iac-bootstrap` proceeds
- **AND** the omnibus runs (with preflight gating Stage 4)
- **AND** the 3 health endpoints are probed
- **AND** the JSON artifact is written

#### Scenario: 1 build fails

- **WHEN** at least 1 of the 3 builds returns non-zero
- **THEN** `iac-bootstrap` is skipped
- **AND** the omnibus is skipped
- **AND** no curl probes run
- **AND** the JSON artifact is NOT emitted

#### Scenario: Omnibus preflight fails

- **WHEN** the omnibus preflight (Stage 0 of `deploy-agent-platform-cluster-arm1-oci`) returns non-zero
- **THEN** the 3 health checks are skipped
- **AND** the JSON artifact is NOT emitted
- **AND** the procedure reports the preflight failure reason (the captured `/tmp/preflight-reports/arm-oci/<ts>.md` path)