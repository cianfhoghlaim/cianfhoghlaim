## ADDED Requirements

### Requirement: LLM Serving Layer Skill Currency

The system SHALL keep the LLM serving skill files (litellm, unsloth,
llama-swap) in sync with the installed package versions and Docker
image tags used by the Bonneagar compose stacks. Drift detection is
tested via automated pytest assertions.

#### Scenario: litellm skill version matches installed library

- **WHEN** any developer runs `uv run pytest tests/llm_serving/`
- **THEN** `uv pip show litellm` reports a 1.x version
- **AND** `.agents/skills/litellm/SKILL.md` documents the same major version

#### Scenario: litellm config registers ≥ 30 models

- **WHEN** `bonneagar/stacks/litellm/config/config.yaml` exists
- **THEN** it lists ≥ 30 `model_name:` entries
- **AND** all `local/*` models route through `http://llama-swap:8080/v1`

#### Scenario: Llama-swap skill exists

- **WHEN** any developer runs `uv run pytest tests/llm_serving/`
- **THEN** `.agents/skills/llama-swap/SKILL.md` exists
- **AND** documents the GPU-vs-CPU reality (Docker Desktop on macOS has
  no Metal GPU passthrough, so `:cpu` image + `LLAMA_ARG_NGL=0` is the
  only working config inside Docker)

#### Scenario: BAML clients default to minimax-m3

- **WHEN** any developer runs `uv run pytest tests/llm_serving/`
- **THEN** `baml_src/clients.baml` has more `model "minimax-m3"` entries
  than any other model string
- **AND** the BAML clients reference published litellm aliases (the
  `local/vision/*` and `local/unsloth/*` aliases match litellm config)
