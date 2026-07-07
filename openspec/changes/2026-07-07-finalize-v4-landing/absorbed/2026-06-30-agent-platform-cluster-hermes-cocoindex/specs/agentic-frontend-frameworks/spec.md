# `agentic-frontend-frameworks` capability spec — litellm-rewire delta

The agentic-frontend-frameworks capability spec governs the
4 agent UI surfaces (TanStack Start + CopilotKit + AG-UI +
marimo), the 5 surfaces in the `agent-platform` group
(Agno AgentOS, Google ADK, OpenClaw, OpenChamber, Cognee,
Graphiti, Letta), and the cross-cutting LLM provider chain
for each surface.

This delta rewires the OpenClaw and OpenChamber LLM provider
chains from the previous `opencode-go` primary +
`minimax-coding-plan` fallback model to the canonical
`litellm` chokepoint. The M3 plan (the user's new
`minimax-coding-plan` allocation) is now reached exclusively
through `litellm:4000`, with vendor-derisking handled
internally by the existing `litellm-minimax-vendor-derisking`
change.

## MODIFIED Requirements

### Requirement: OpenClaw routes LLM through LiteLLM

The system SHALL route all OpenClaw LLM calls through the
canonical `litellm` stack at `http://litellm:4000/v1`. The
`openclaw.json` `provider` block SHALL be rewritten to:
- `name: litellm`
- `base_url: http://litellm:4000/v1`
- `model: minimax-m3`
- `api_key_env: OPENAI_API_KEY` (resolves at runtime to
  `LITELLM_MASTER_KEY`)

The `fallback_chain` SHALL be set to `[]` (LiteLLM handles
fallback internally). The previous `opencode-go` primary +
`minimax-coding-plan` fallback chain SHALL be removed
entirely. The `OPENCODE_GO_BASE_URL` env var in `compose.yaml`
SHALL be removed; the `OPENAI_BASE_URL` env var in
`secrets.env` SHALL be set to `http://litellm:4000/v1`.

_(Previously: OpenClaw used `opencode-go` as the primary LLM
provider with `minimax-coding-plan/minimax-m3` as the
fallback chain. The `opencode-go` provider exposed
`OPENCODE_GO_BASE_URL=https://opencode.ai/zen/go/v1` as the
`OPENAI_BASE_URL`; the `OPENCODE_GO_API_KEY` was the single
key; `MINIMAX_API_KEY` was the fallback key.)_

#### Scenario: openclaw.json provider block is litellm-only

- **GIVEN** `bonneagar/stacks/openclaw/config/openclaw.json`
- **WHEN** the file is read
- **THEN** the `provider` block SHALL have
  `name: "litellm"`,
  `base_url: "http://litellm:4000/v1"`,
  `model: "minimax-m3"`,
  `api_key_env: "OPENAI_API_KEY"`
- **AND** the `fallback_chain` SHALL be `[]`
- **AND** the file SHALL NOT reference `opencode-go` or
  `OPENCODE_GO_BASE_URL`

#### Scenario: openclaw secrets.env references LITELLM_MASTER_KEY

- **GIVEN** `bonneagar/stacks/openclaw/secrets.env`
- **WHEN** the file is read
- **THEN** the `OPENAI_API_KEY` line SHALL be
  `OPENAI_API_KEY={{ infisical:///litellm/master_key }}`
- **AND** the `OPENAI_BASE_URL` line SHALL be
  `OPENAI_BASE_URL=http://litellm:4000/v1`
- **AND** the file SHALL NOT reference `OPENCODE_GO_API_KEY`
  or `MINIMAX_API_KEY`

#### Scenario: openclaw compose.yaml drops OPENCODE_GO_BASE_URL

- **GIVEN** `bonneagar/stacks/openclaw/compose.yaml`
- **WHEN** the file is read
- **THEN** the `environment:` block SHALL NOT contain
  `OPENCODE_GO_BASE_URL`
- **AND** the `OPENAI_BASE_URL` SHALL be injected at runtime
  via Locket from `secrets.env`

### Requirement: OpenChamber routes LLM through LiteLLM

The system SHALL route all OpenChamber LLM calls through the
canonical `litellm` stack. OpenChamber's bundled runtime
SHALL gain a 4th provider entry "litellm" with:
- `base_url: http://litellm:4000/v1`
- `models: [minimax-m3]`

The 3 hard-coded provider API keys (OpenAI, Anthropic,
minimax) SHALL be replaced by a single `OPENAI_API_KEY` that
resolves to `LITELLM_MASTER_KEY` via Locket. The
`OPENAI_BASE_URL` env var in `secrets.env` SHALL be set to
`http://litellm:4000/v1`.

_(Previously: OpenChamber's bundled `opencode-ai` runtime
had 3 hard-coded provider entries (OpenAI, Anthropic,
minimax) with 3 separate API keys. The user picked the
provider in the OpenChamber UI dropdown.)_

#### Scenario: openchamber secrets.env references LITELLM_MASTER_KEY

- **GIVEN** `bonneagar/stacks/openchamber/secrets.env`
- **WHEN** the file is read
- **THEN** the `OPENAI_API_KEY` line SHALL be
  `OPENAI_API_KEY={{ infisical:///litellm/master_key }}`
- **AND** the `OPENAI_BASE_URL` line SHALL be
  `OPENAI_BASE_URL=http://litellm:4000/v1`

#### Scenario: openchamber runtime has 4th litellm provider

- **GIVEN** the OpenChamber bundled `opencode-ai` runtime
  config at
  `bonneagar/stacks/openchamber/config/opencode-config.json`
  (or wherever the bundled runtime reads its config)
- **WHEN** the file is read
- **THEN** the `providers` array SHALL contain 4 entries:
  `openai`, `anthropic`, `minimax`, `litellm`
- **AND** the `litellm` entry SHALL have
  `base_url: "http://litellm:4000/v1"` and
  `models: ["minimax-m3"]`

## Cross-references

- [`openspec/changes/litellm-minimax-vendor-derisking/`](../litellm-minimax-vendor-derisking/)
- [`openspec/changes/add-openclaw-stack-and-channel-fanout/`](../add-openclaw-stack-and-channel-fanout/)
- [`openspec/changes/add-openchamber-stack-and-opencode-ui/`](../add-openchamber-stack-and-opencode-ui/)
- [`openspec/changes/2026-06-30-agent-platform-cluster-hermes-cocoindex/proposal.md`](../proposal.md)
