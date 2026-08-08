## ADDED Requirements

### Requirement: Bria Fibo Enabled for Celtic Mythology Asset Generation

The system SHALL have `local/image/fibo: true` in `deployment-choice.yaml`
once the Familiar Dynamic NFT System change is archived.

#### Scenario: Fibo server running in dev
- **WHEN** the user invokes `mise run cic:stack-doctor`
- **THEN** the `fibo-server` stack SHALL pass the 6-file GOLD_STANDARD validation

#### Scenario: Mythology agent invokes Fibo
- **WHEN** the user invokes `celtic_mythology_agent` with "Generate an image of Cúchulainn in the warp spasm in La Tène style"
- **THEN** the agent invokes Fibo via the LiteLLM gateway with the JSON-native Celtic asset prompt