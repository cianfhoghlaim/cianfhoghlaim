# `agentic-frontend-frameworks` capability spec — openchamber delta

The agentic-frontend-frameworks capability spec governs the
agentic web frontends in the Cianfhoghlaim monorepo — the
TanStack Start + CopilotKit + AG-UI + Convex + Hono + oRPC +
Cloudflare + BAML / Pydantic AI / Agno / Google ADK stack.

This delta adds the openchamber OpenCode UI as a sibling agent
UI surface alongside the CopilotKit-based AG-UI chat surfaces
and the marimo notebook dashboards.

## ADDED Requirements

### Requirement: openchamber as Bundled-Mode Agent UI
The system SHALL expose a browser-based OpenCode UI at `openchamber.cianfhoghlaim.ie` that bundles the `opencode-ai` runtime inside its own container.

#### Scenario: User reaches the OpenChamber UI
- **WHEN** a Pocket ID-authenticated user navigates to `https://openchamber.cianfhoghlaim.ie`
- **THEN** the OpenChamber React UI SHALL load (Bun-served, 18+ themes available)
- **AND** the bundled `opencode-ai` runtime SHALL respond to a sample prompt within 5 seconds

#### Scenario: OpenChamber session state persists
- **WHEN** a user closes the browser and re-opens `openchamber.cianfhoghlaim.ie` later
- **THEN** the previous chat sessions SHALL be available from the `openchamber-state` named volume
- **AND** the session list SHALL be searchable by topic or date

#### Scenario: Theme selection persists
- **WHEN** a user selects the `cianchoghlaim-dark` theme
- **THEN** the theme SHALL persist across sessions (stored in `openchamber-state`)
- **AND** a new visitor SHALL see the theme the user previously chose

### Requirement: openchamber Shares the LLM Provider Set with the Agent Fleet
The system SHALL configure openchamber with the same LLM providers that the rest of the meaisínfhoghlaim agent fleet uses (OpenAI, Anthropic, minimax-compatible).

#### Scenario: minimax is the default provider in OpenChamber
- **WHEN** the OpenChamber UI starts
- **THEN** `MINIMAX_API_KEY` SHALL be the default LLM key (matching the `litellm-minimax-vendor-derisking` change's primary path)
- **AND** OpenAI and Anthropic SHALL be selectable in the UI's provider picker

#### Scenario: Switching providers is a UI action
- **WHEN** a user picks a different provider in the UI
- **THEN** the next chat prompt SHALL use the picked provider's key
- **AND** no container restart SHALL be required

### Requirement: openchamber Does Not Replace the CopilotKit AG-UI Surface
The system SHALL keep OpenChamber as a **separate** UI from the CopilotKit AG-UI chat surface that ships with the TanStack Start apps (e.g. `oideachais.cianfhoghlaim.ie`).

#### Scenario: Two distinct chat surfaces
- **WHEN** a user wants to interact with the 12-agent meaisínfhoghlaim fleet
- **THEN** the user MAY use the TanStack Start AG-UI chat (e.g. on `oideachais.cianfhoghlaim.ie`)
- **AND** the user MAY use the OpenChamber OpenCode UI (on `openchamber.cianfhoghlaim.ie`)
- **AND** the two surfaces SHALL share the same LLM providers but maintain independent session state

#### Scenario: OpenChamber is for code-agent work
- **WHEN** a user wants to run an OpenCode CLI session (multi-file edits, agent loop, file system access)
- **THEN** the user SHALL use `openchamber.cianfhoghlaim.ie`
- **AND** the TanStack Start AG-UI chat SHALL NOT be the recommended surface for code-agent work

### Requirement: openchamber Is the Primary UI for the LiteLLM Dev Loop
The system SHALL document openchamber as the recommended UI for the LiteLLM provider-development loop (the same workflow the `litellm-minimax-vendor-derisking` change uses).

#### Scenario: Operator debugs a LiteLLM fallback
- **WHEN** an operator wants to debug a fallback chain issue
- **THEN** the operator SHALL open `openchamber.cianfhoghlaim.ie` and select the `litellm` provider
- **AND** the operator SHALL see the response from the fallback chain in the OpenChamber session history
- **AND** the Langfuse trace SHALL be cross-linked from the session