## ADDED Requirements

### Requirement: Token-plan API endpoints are registered routing targets

The registry and the secrets template SHALL register the two flat-rate
token-plan API surfaces as first-class routing targets:

- **MiniMax coding plan** — OpenAI-compatible endpoint
  `https://api.minimax.io/v1` and Anthropic-compatible endpoint
  `https://api.minimax.io/anthropic`, authenticated by `MINIMAX_API_KEY`
  (vault ref `infisical://dev-baile/minimax/api_key`); the
  `minimax-m3` entry (`text_llm/default`) MUST carry this endpoint
  metadata.
- **Qwen token plan (Qwen Cloud, served via DashScope)** —
  OpenAI-compatible endpoint `https://coding.dashscope.aliyuncs.com/v1`
  and Anthropic-compatible endpoint
  `https://coding.dashscope.aliyuncs.com/apps/anthropic`, authenticated by
  `DASHSCOPE_API_KEY` (vault ref `infisical://dev-baile/qwen/api_key`).
  The registry MUST include at minimum `qwen3.7-plus`
  (role `token_plan_primary`) and `qwen3-coder-next`
  (role `token_plan_coding`).

The base URL MUST be environment-driven (`MINIMAX_BASE_URL`,
`DASHSCOPE_BASE_URL` in `.infisical.env`) so that switching between the
coding-plan endpoint and the international console endpoint
(`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`) is a one-line
template change. `opencode.json` providers MUST consume these env vars
(the `minimax` provider uses `https://api.minimax.io/anthropic`; the
`qwen` provider reads `{env:DASHSCOPE_BASE_URL}`). No model site MAY
hardcode a token-plan URL that bypasses the env-var indirection.

#### Scenario: Agent resolves the default text LLM

- **WHEN** an agent or BAML client resolves `model_for("text_llm", "default")`
- **THEN** the registry SHALL return `minimax-m3`
- **AND** the resolved endpoint metadata SHALL point at
  `https://api.minimax.io/v1` (OpenAI-compatible) and
  `https://api.minimax.io/anthropic` (Anthropic-compatible)
- **AND** authentication SHALL use `MINIMAX_API_KEY` from the hydrated
  environment

#### Scenario: Secondary token-plan model for cross-checking

- **WHEN** a pipeline requests `model_for("text_llm", "token_plan_primary")`
- **THEN** the registry SHALL return `qwen3.7-plus`
- **AND** the resolved base URL SHALL equal the current
  `DASHSCOPE_BASE_URL` value

#### Scenario: Missing token-plan key fails explicitly

- **WHEN** `DASHSCOPE_API_KEY` is absent from the hydrated environment
- **AND** a client attempts to use a `qwen` token-plan model
- **THEN** the client SHALL raise an explicit missing-secret error
  naming `DASHSCOPE_API_KEY`
- **AND** SHALL NOT silently fall back to a different paid provider
