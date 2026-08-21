# centralized-model-registry

## ADDED Requirements

### Requirement: Token-plan model entries in MODEL_REGISTRY

The MODEL_REGISTRY SHALL include entries for the 7 paid token-plan
models listed below. The registry file lives at
`meaisinfhoghlaim/models/model_registry.py`.

The entries are:
- `minimax-coding-plan/MiniMax-M3` (text_llm/default) — the MiniMax
  coding plan endpoint at `https://api.minimax.io/anthropic`
  (Anthropic-compatible)
- `qwen3-coder-next` (text_llm/token_plan_coding) — DashScope coding
  specialist
- `qwen3-coder-plus` (text_llm/token_plan_coding_strong) — DashScope
  coding + reasoning
- `qwen3-max-2026-01-23` (text_llm/token_plan_max) — DashScope
  flagship reasoning model
- `glm-5.1` (text_llm/token_plan_glm) — third-party via DashScope
- `kimi-k2.6` (text_llm/token_plan_kimi) — third-party via DashScope
- `mimo-v2.5` (text_llm/token_plan_mimo) — third-party via DashScope
- `deepseek-v4-flash` (text_llm/token_plan_deepseek) — third-party
  via DashScope

Each entry MUST include:
- `provider: openai` (for DashScope OpenAI-compatible endpoint)
- `base_url_env: DASHSCOPE_BASE_URL` (default
  `https://coding.dashscope.aliyuncs.com/v1`)
- `api_key_env: DASHSCOPE_API_KEY` (or `MINIMAX_API_KEY` for MiniMax)

Per the `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
change proposal.

Per the `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
change proposal. Each entry MUST include:
- `provider: "openai"` (for DashScope OpenAI-compatible endpoint)
- `base_url_env: "DASHSCOPE_BASE_URL"` (default `https://coding.dashscope.aliyuncs.com/v1`)
- `api_key_env: "DASHSCOPE_API_KEY"` (or `"MINIMAX_API_KEY"` for MiniMax)

#### Scenario: Token-plan model resolves via model_for

- **WHEN** `model_for("text_llm", "token_plan_coding")` is called
- **THEN** it returns `"qwen3-coder-next"`
- **AND** the BAML client can use this string as a model ID

#### Scenario: Token-plan secrets are hydrated

- **WHEN** `mise run secrets:init` runs
- **THEN** `MINIMAX_API_KEY` and `QWEN_DASHSCOPE_API_KEY` are populated
  in the dev-baile Infisical vault
- **AND** `.env` (hydrated by mise) exposes both keys

### Requirement: registry_audit covers token-plan hardcoded strings

The `mise run lint:registry` gate SHALL fail if any
`agents/`, `baml_src/`, `notebooks/`, `web/`, `orchestration/`,
`spaces/`, or `meaisinfhoghlaim/` file contains a hardcoded token-plan
model string that is not routed through `MODEL_REGISTRY`.

#### Scenario: Developer hardcodes a token-plan model

- **WHEN** a developer adds `model_name = "qwen3-coder-plus"` directly
  in a Python file (without using `model_for(...)`)
- **THEN** `mise run lint:registry` exits 1 with
  `path/to/file.py:<line>: 'qwen3-coder-plus' — route through MODEL_REGISTRY`