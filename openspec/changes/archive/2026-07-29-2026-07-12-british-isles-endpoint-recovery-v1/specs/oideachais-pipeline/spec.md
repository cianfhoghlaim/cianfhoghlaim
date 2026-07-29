## ADDED Requirements

### Requirement: Canonical endpoint_recovery helper

The cianfhoghlaim-pipeline capability MUST expose the
`dlt/common/endpoint_recovery` helper as the canonical entry point
for every DLT source's outbound network call. The helper MUST be
importable from `cianfhoghlaim.dlt.common.endpoint_recovery` and
MUST be the only place the British Isles + EU + Commonwealth + EU
nations + Americas DLT sources are permitted to call out to live
endpoints.

#### Scenario: A new EU nation source uses the helper

- **WHEN** a developer adds a new EU nation DLT source
- **THEN** the source MUST call
  `from cianfhoghlaim.dlt.common.endpoint_recovery import endpoint_recovery`
- **AND** the source MUST route every outbound HTTP request through
  `endpoint_recovery.fetch(...)`
- **AND** the source MUST NOT import `requests` or `httpx` directly
