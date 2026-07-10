# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: Auto-archive procedure gates on 3 health endpoints returning 200

The system SHALL provide an `archive-agent-platform-cluster-arm1-oci`
Komodo procedure that archives the 5 openspec changes closing the
agent-platform-cluster deployment — but ONLY WHEN all 3 health
endpoints return 200:

- `https://hermes.cianfhoghlaim.ie/api/health` (must return 200)
- `https://openclaw.cianfhoghlaim.ie/api/health` (must return 200)
- `https://openchamber.cianfhoghlaim.ie/api/health` (must return 200)

The 5 changes to archive (in any order, all idempotent):

1. `2026-07-13-backfill-server-id-on-12-procedures`
2. `2026-07-13-arm-oci-deploy-preflight-hard-gate-v1`
3. `2026-07-13-agent-platform-cluster-arm1-oci-bootstrap-procedure-v1`
4. `2026-07-13-archive-agent-platform-cluster-arm1-oci-automation-v1` (self)
5. `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow`

The procedure SHALL emit a JSON artifact at
`/tmp/agent-platform-cluster/archived-on-<utc-ts>.json` containing the
timestamp + the 5 archived change IDs.

#### Scenario: all 3 endpoints return 200

- **WHEN** `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200
- **AND** `curl https://openclaw.cianfhoghlaim.ie/api/health` returns 200
- **AND** `curl https://openchamber.cianfhoghlaim.ie/api/health` returns 200
- **THEN** the procedure runs `openspec archive --yes` on the 5 changes
  (idempotent — `|| true` so already-archived is treated as success)
- **AND** the JSON artifact is written to `/tmp/agent-platform-cluster/archived-on-<ts>.json`

#### Scenario: any endpoint returns non-200

- **WHEN** ANY of the 3 endpoints returns non-200
- **THEN** the procedure aborts at Stage 1
- **AND** no archive commands run
- **AND** the JSON artifact is NOT emitted

#### Scenario: archive commands are idempotent

- **WHEN** an already-archived change is re-archived
- **THEN** `openspec archive` exits 0 (not an error)
- **AND** the procedure reports success
- **AND** the JSON artifact IS emitted (with the timestamp of the current run)