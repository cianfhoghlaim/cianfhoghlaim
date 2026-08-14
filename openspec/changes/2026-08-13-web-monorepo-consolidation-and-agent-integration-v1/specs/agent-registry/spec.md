# agent-registry Specification

## ADDED Requirements

### Requirement: every agent SHALL have a web integration binding

Every agent in `agents/agent_registry.py:AGENT_REGISTRY` MUST
have a `web_integration` field that names the web app(s) the
agent is bound to (via CopilotKit actions or AG-UI streaming).

The `web_integration` field MUST be one of:

- A single app name (`"oideachais"`, `"croilar"`,
  `"oideachais-dashboard"`, `"cianfhoghlaim"`)
- A list of app names
- The literal string `"none"` (for agents with no web binding,
  e.g. headless data-pipeline agents)

For per-subject binding (e.g. the
`mathematics_lc_agent` is bound to a specific subject's
web route), the field SHALL be a JSON object with `app` and
`route` keys.

The field MUST be validated by `mise run lint:agent-registry`.

#### Scenario: New agent is added to the fleet

- **WHEN** a developer adds a new agent to
  `agents/agent_registry.py:AGENT_REGISTRY`
- **THEN** the agent entry MUST include a `web_integration` field
- **AND** if the agent is bound to a web app, the binding MUST
  be reflected in the corresponding `apps/<app>/AGENTS.md` file
- **AND** if the agent has CopilotKit actions, the actions MUST
  live at `web/hono-api/src/routes/copilotkit/<app>.ts`

#### Scenario: image_generation_agent is added (Phase L)

- **GIVEN** the `image_generation_agent` consumes the 5
  `image_gen` MODEL_REGISTRY entries
- **WHEN** the agent entry is added to
  `agents/agent_registry.py:AGENT_REGISTRY`
- **THEN** the `web_integration` field MUST specify the
  per-subject binding
- **AND** the CopilotKit actions MUST live at
  `web/hono-api/src/routes/copilotkit/image-gen/$subjectId.ts`

#### Scenario: A per-subject agent is added (Phase U)

- **GIVEN** a per-subject agent (e.g. `mathematics_lc_agent`)
  is added to `agents/agent_registry.py:AGENT_REGISTRY`
- **THEN** the `web_integration` field MUST name:
  - `app: "cianfhoghlaim"` (the central homepage app)
  - `route: "/<stage>/<subject>"` (the per-subject web route)
- **AND** the agent MUST be dispatchable from the homepage chat
- **AND** the agent MUST be registered against the per-subject
  Convex schema
