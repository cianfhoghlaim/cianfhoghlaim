## MODIFIED Requirements
### Requirement: Locket tmpfs volume name
The Locket shared tmpfs volume SHALL be named `cianfhoghlaim_locket_secrets` (NOT the legacy `cianfhoghlaim_locket_secrets` typo).

#### Scenario: All Compose stacks reference the correct name
- **WHEN** any stack under `bonneagar/stacks/*/compose*.yaml` mounts the Locket tmpfs volume
- **THEN** the mount ref SHALL be `cianfhoghlaim_locket_secrets:/run/secrets/locket:ro`
- **AND** the external volume declaration SHALL be `cianfhoghlaim_locket_secrets: { external: true }`

### Requirement: Primary dev/control-plane Docker bridge network
The shared bridge network SHALL be named `cianfhoghlaim`.

#### Scenario: All Compose stacks join the correctly-named network
- **WHEN** a Compose stack at `bonneagar/stacks/<name>/compose.yaml` declares the primary bridge network
- **THEN** `networks.cianfhoghlaim.name: cianfhoghlaim` SHALL be set
- **AND** `networks: [cianfhoghlaim]` SHALL appear on every service that needs internal mesh access
