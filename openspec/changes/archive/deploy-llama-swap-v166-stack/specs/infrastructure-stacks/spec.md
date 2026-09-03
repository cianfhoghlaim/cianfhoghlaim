# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: llama-swap v166 stack

The system SHALL deploy a llama-swap v166 service at
`infrastructure/stacks/llama-swap/` per the 6-file GOLD_STANDARD
pattern (compose.yaml, sidecar.yaml, secrets.env, pangolin.yaml,
blueprint.yaml, .env.example). The service serves the 14 v4 Unsloth
GGUFs at `http://llama-swap:8080/v1/chat/completions`.

The service MUST mount `/models/unsloth/`, `/models/mlx-community/`,
and `/models/gguf/` from the stedding volume. It MUST be configured
for Apple Silicon (`LLAMA_ARG_NGL=99`).

#### Scenario: A developer runs the llama-swap service locally

- **GIVEN** the 14 v4 Unsloth GGUFs are downloaded to `/models/unsloth/`
- **WHEN** `mise run llama-swap:up` is run
- **THEN** the service starts and `curl http://localhost:8080/v1/models`
  returns 14+ model entries
- **AND** `mise run llama-swap:health` exits with code 0
