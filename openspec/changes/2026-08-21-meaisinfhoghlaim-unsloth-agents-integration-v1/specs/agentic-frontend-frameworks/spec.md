## MODIFIED Requirements

### Requirement: 4 web surfaces consume Unsloth Studio via litellm

The 4 cianfhoghlaim web surfaces (`tuatha-ui`, `ciandlithe-web`, `cianchosaint-web`, `croilar-portal`) SHALL consume Unsloth Studio via the litellm gateway at `http://localhost:4000/v1`. The web surfaces use the `local/unsloth/*` model names (NOT direct Unsloth Studio URLs).

#### Scenario: tuatha-ui queries via litellm

- **GIVEN** a user opens `https://tuatha.cianfhoghlaim.ie`
- **WHEN** they ask "what's on the 2018 LC Gaeilge paper 2?"
- **THEN** the BAML `GenerateGaeilgeSyllabus` function invokes litellm with `model=local/unsloth/qwen3.8-27b`
- **AND** litellm forwards the request to `http://host.docker.internal:8888/v1` (Unsloth Studio)
- **AND** the response streams back to the CopilotKit chat surface

### Requirement: CopilotKit v2 chat surface exposes 8 tools

The CopilotKit v2 chat surface SHALL expose the 8 new tools via the `tool_use` schema. Each invocation is streamed via the AG-UI event bridge to the Convex reactive state.

#### Scenario: User invokes `web_form_fill` via chat

- **GIVEN** the user is in the OpenChamber chat surface
- **WHEN** they say "Fill out the SEV pay form with these values: {form_data}"
- **THEN** the LLM emits a `tool_use` block calling `web_form_fill(url, fields)`
- **AND** the AG-UI bridge streams a `tool_call` event to the Convex reactive state
- **AND** OpenClaw executes the Playwright MCP call
- **AND** the screenshot + success status are returned as a `tool_result` event
- **AND** the Langfuse trace shows the full invocation chain

### Requirement: AG-UI event bridge + Convex reactive state

The system SHALL provide an AG-UI event bridge that streams per-tool results to a Convex reactive state. The 4 web surfaces subscribe to this state.

#### Scenario: Per-tool result streams via AG-UI

- **WHEN** a tool invocation completes on the OpenClaw side
- **THEN** the result is published to Convex via the AG-UI event bridge
- **AND** the active web surface re-renders to display the result
- **AND** the event includes the tool name, the inputs, the outputs, and the latency
