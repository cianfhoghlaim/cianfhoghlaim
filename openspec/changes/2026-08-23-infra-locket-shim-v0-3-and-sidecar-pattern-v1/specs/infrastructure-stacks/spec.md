## ADDED Requirements

### Requirement: locket-rotate-task

The dev environment SHALL expose a `devops:locket:rotate` task that
triggers a Locket secret rotation via the sidecar's `/rotate` endpoint.

#### Scenario: locket:rotate calls the sidecar

- **WHEN** `mise run devops:locket:rotate` runs
- **THEN** the command MUST invoke `POST /rotate` on the Locket sidecar
- **AND** the command MUST exit 0 on success or 1 on failure

### Requirement: locket-audit-task

The dev environment SHALL expose a `devops:locket:audit` task that
queries the `locket_audit.scrapes` table and emits the last 100
secret fetches per service.

#### Scenario: locket:audit returns recent fetches

- **WHEN** `mise run devops:locket:audit` runs
- **THEN** the command MUST query the audit table
- **AND** the output MUST include ≥ 1 row per active service
- **AND** the command MUST exit 0