## MODIFIED Requirements

### Requirement: Each agent vertex has an unsloth-serve fallback provider

The 3 agent-platform vertices (Hermes, OpenClaw, OpenChamber) SHALL each register a 2nd provider pointing at the unsloth-serve API at `http://unsloth:8889/v1`, in addition to the existing LiteLLM M3 chokepoint.

#### Scenario: Hermes routes to unsloth-serve when UNSLOTH_PROVIDER=true

- **GIVEN** the unsloth-serve stack is running on bunchloch
- **WHEN** `UNSLOTH_PROVIDER=true` is set in `bonneagar/stacks/hermes/config/hermes.yaml`
- **THEN** the Hermes container entrypoint invokes `unsloth start hermes --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL`
- **AND** the 3 hermes channels (telegram/discord/webchat) route inference through the unsloth-serve API
- **AND** langfuse spans the hermes chat sessions with `provider=unsloth` tag

#### Scenario: OpenClaw adds unsloth provider block

- **WHEN** `bonneagar/stacks/openclaw/config/openclaw.json` is updated
- **THEN** the unsloth provider block appears with `baseUrl: http://unsloth:8889`, `api: "anthropic-messages"`, and 3 models (Qwen3.8-27B + DeepSeek-V4-Pro + Kimi-K2.7-Code)
- **AND** the existing 6 channels (telegram/slack/discord/whatsapp/webchat/ms-teams) continue to work via the existing litellm provider
- **AND** operators can switch between providers via the openclaw TUI

#### Scenario: OpenCode adds unsloth-studio custom provider

- **WHEN** `opencode.json` is updated with the unsloth-studio provider block
- **THEN** `type: "openai-compatible"` + `baseURL: http://unsloth:8889/v1/` + 4 models appear in the provider picker
- **AND** the agent dispatch table adds a fallback rule: if M3 plan returns `429 rate_limit_exceeded`, retry on unsloth-studio
- **AND** the fallback is visible in `/model` of the OpenChamber UI

### Requirement: M3 chokepoint aliases have unsloth fallback chain

The 5 M3 chokepoint aliases (`kimi-k2.6`, `glm-5.1`, `minimax-m2.5`, `mimo-v2.5`, `deepseek-v4-flash`) and the `vision`/`text`/`coding` aliases SHALL each declare an unsloth-served local model as a fallback when the upstream is rate-limited or unreachable.

#### Scenario: vision alias falls back to unsloth-serve

- **GIVEN** the litellm config is updated
- **WHEN** a request is made to the `vision` alias and the opencode-go upstream returns 429
- **THEN** litellm retries the request against `local/unsloth/qwen3-vl-8b` (unsloth-serve)
- **AND** the secondary fallback chain is `local/vision/qwen3-vl-8b` (llama-swap) then `gemini/gemini-2.5-pro`
- **AND** every fallback attempt is logged to langfuse with `fallback_chain_index` metadata
