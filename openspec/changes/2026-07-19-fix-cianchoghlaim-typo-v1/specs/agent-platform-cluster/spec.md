## MODIFIED Requirements
### Requirement: Agent-platform containers join the cianfhoghlaim bridge network
The `openclaw` + `openchamber` containers in the agent-platform cluster SHALL join the bridge network `cianfhoghlaim` (NOT the legacy `cianfhoghlaim` typo).

#### Scenario: Compose files reference the correct network
- **WHEN** `bonneagar/stacks/openclaw/compose.yaml` and `bonneagar/stacks/openchamber/compose.yaml` declare the network
- **THEN** `networks.cianfhoghlaim.name: cianfhoghlaim` SHALL be set
- **AND** `networks: [cianfhoghlaim]` SHALL be on every service
