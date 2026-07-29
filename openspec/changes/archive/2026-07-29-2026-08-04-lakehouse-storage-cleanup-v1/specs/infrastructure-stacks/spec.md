## MODIFIED Requirements

### Requirement: lakehouse stack is the canonical home for Nimtable + Olake + LanceDB Viewer

The system SHALL require the canonical `bonnegar/stacks/lakehouse/`
stack to be the single home for the Nimtable + Olake + LanceDB Viewer
services. The 3 standalone IaC stacks (`olake`, `nimtable`,
`lancedb-viewer`) SHALL be deleted.

#### Scenario: 3 services respond 200 OK

- **WHEN** `docker compose -f bonnegar/stacks/lakehouse/compose.yaml up -d` runs
- **THEN** `curl -s http://localhost:3018/api/v1/health` SHALL return
  200 OK (Nimtable)
- **AND** `curl -s http://localhost:3901/v1/databases` SHALL return
  200 OK (Olake)
- **AND** `curl -s http://localhost:8081/health` SHALL return
  200 OK (LanceDB Viewer)

#### Scenario: 3 standalone stacks deleted

- **WHEN** `ls bonnegar/stacks/olake/ bonnegar/stacks/nimtable/ bonnegar/stacks/lancedb-viewer/`
  runs
- **THEN** none of the 3 directories SHALL exist
- **AND** `grep -r "olake\|nimtable\|lancedb-viewer" bonnegar/ --include="*.toml"
  --include="*.yaml"` returns 0 matches

#### Scenario: 1-row round-trip works

- **WHEN** a test row is written to Nimtable + queried via Olake +
  embedded in LanceDB
- **THEN** the same row SHALL be retrievable via all 3 services