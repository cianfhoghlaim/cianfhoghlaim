## MODIFIED Requirements

### Requirement: Pangolin hostnames use `*.cianfhoghlaim.ie`

The system SHALL require all Pangolin router hostnames under
`bonnegar/stacks/cianfhoghlaim/pangolin.yaml` to use the
`*.cianfhoghlaim.ie` namespace (not `*.oideachais.cianfhoghlaim.ie`).

#### Scenario: All 5 router hostnames updated

- **WHEN** `grep "hostname:" bonnegar/stacks/cianfhoghlaim/pangolin.yaml` runs
- **THEN** every hostname SHALL be of the form `*.cianfhoghlaim.ie`
  (e.g. `web.cianfhoghlaim.ie`, `api.cianfhoghlaim.ie`, `dagster.cianfhoghlaim.ie`,
  `agents.cianfhoghlaim.ie`, `adk-agents.cianfhoghlaim.ie`)
- **AND** zero hostnames SHALL be of the form `*.oideachais.cianfhoghlaim.ie`

#### Scenario: CORS middleware renamed

- **WHEN** `grep "cors" bonnegar/stacks/cianfhoghlaim/pangolin.yaml` runs
- **THEN** the CORS middleware SHALL be named `cianfhoghlaim-cors`
  (not `oideachais-cors`)