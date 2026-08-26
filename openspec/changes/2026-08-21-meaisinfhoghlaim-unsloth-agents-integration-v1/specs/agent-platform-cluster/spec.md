## MODIFIED Requirements

### Requirement: Unsloth Studio is a primary LLM provider for the 3 agent vertices

The 3 agent-platform vertices (Hermes, OpenClaw, OpenChamber) SHALL each register Unsloth Studio as a primary LLM provider (after the M3 chokepoint). The canonical base URL is `http://host.docker.internal:8888/v1` for internal Docker traffic and `https://unsloth.cianfhoghlaim.ie/v1` for external traffic (via Pangolin private resource).

#### Scenario: Hermes routes to Unsloth Studio when UNSLOTH_PROVIDER=true

- **GIVEN** the Unsloth Studio is running on the bunchloch host
- **WHEN** `UNSLOTH_PROVIDER=true` is set in `bonneagar/stacks/hermes/secrets.env`
- **THEN** the Hermes container entrypoint invokes `unsloth start hermes --model unsloth/Qwen3.8-27B-GGUF:UD-Q4_K_XL`
- **AND** the 3 hermes channels (telegram/discord/webchat) route inference to the Unsloth Studio

#### Scenario: OpenClaw adds unsloth provider block

- **WHEN** `bonneagar/stacks/openclaw/config/openclaw.json` is updated
- **THEN** the `fallback_chain` block contains an unsloth entry with `baseUrl: http://host.docker.internal:8888`

#### Scenario: OpenCode adds unsloth-studio custom provider

- **WHEN** `opencode.json` is updated with the unsloth-studio provider block
- **THEN** `baseURL: http://host.docker.internal:8888/v1/` (internal) OR `https://unsloth.cianfhoghlaim.ie/v1/` (public)

### Requirement: 8 new tools wired via the tool_use schema

The system SHALL provide 8 canonical tools wired via the `tool_use` schema (4 OCR + 1 HTR + 1 alignment + 1 schema extract + 1 form fill / bash execute / eval orchestrator). The tools are dispatched via Hermes (API + channels) + OpenClaw (consumer gateway).

#### Scenario: 8 tools registered in tool_use schema

- **GIVEN** the 8 tools implemented at `agents/meaisinfhoghlaim/tools/`
- **WHEN** the operator runs `python3 -c "from agents.meaisinfhoghlaim.tools import TOOL_REGISTRY; print(len(TOOL_REGISTRY))"`
- **THEN** the output is `8`
- **AND** each tool has a `backend`, `inputs`, and `outputs` schema
