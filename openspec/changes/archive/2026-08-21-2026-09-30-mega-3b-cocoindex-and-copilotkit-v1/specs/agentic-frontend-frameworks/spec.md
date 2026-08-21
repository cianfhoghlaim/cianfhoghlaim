## ADDED Requirements

### Requirement: CopilotKit v2.0 pin across both web apps

The system SHALL pin CopilotKit v2.0 across both web apps
(`web/apps/cianfhoghlaim` + `web/apps/cianfhoghlaim-mmo`).

The canonical pin is `@copilotkit/react-core/v2@^1.67.1` (per the
2026-08-17-biep-v3-bring-up-v1 change + this change's CK.1).

#### Scenario: Both web apps use the same CopilotKit pin

- **WHEN** `mise run lint:copilotkit-pin-version` runs
- **THEN** both web apps MUST use `@copilotkit/react-core/v2@^1.67.1`
- **AND** no web app MUST use the legacy `@copilotkit/react-core@^1.x` pin

### Requirement: 12 ADK agents registered as CopilotRuntime.agents

The system SHALL register the 12 ADK agents (per the
2026-08-26-mega-3a-baml-and-adk-v1 change) as
`CopilotRuntime.agents[name]` so the CopilotKit UI can route user
messages to any of the 12 agents.

#### Scenario: All 12 ADK agents are registered

- **GIVEN** the CopilotKit runtime at `web/apps/cianfhoghlaim/app.config.ts`
- **WHEN** the operator inspects the CopilotRuntime initialization
- **THEN** all 12 ADK agents MUST be registered
- **AND** each agent MUST have a corresponding route in
  `web/apps/cianfhoghlaim-web/src/routes/agents/<agent_name>/`

### Requirement: A2UI surface generator (1 generator, 8 surfaces)

The system SHALL provide a single A2UI surface generator at
`web/apps/cianfhoghlaim/components/_shared/A2UISurfaceGenerator.tsx`
that the 8 A2UI surfaces share.

The 8 surfaces are:
- Chart surface (statistics_agent)
- Graph surface (corpus_agent)
- Playback surface (research_agent)
- Lineage surface (curriculum_agent)
- Search surface (mcp_curriculum_agent)
- Subject grid surface (root_agent)
- Dashboard surface (curriculum_comparison_agent)
- Translator surface (translation_agent)

#### Scenario: All 8 surfaces share the canonical generator

- **WHEN** `mise run lint:a2ui-surface-coverage` runs
- **THEN** every A2UI surface MUST use the canonical
  `A2UISurfaceGenerator` (no hand-written `createSurface` calls)
- **AND** the lint returns `OK: 8/8 surfaces use the generator`

### Requirement: cianfhoghlaim-mmo CopilotKit v1.10 → v2.0 migration

The system SHALL migrate `web/apps/cianfhoghlaim-mmo` from
`@copilotkit/react-core@^1.10.0` to `@copilotkit/react-core/v2@^1.67.1`.

The migration includes:
- Update package.json
- Migrate v1.x API patterns to v2.x (createA2UIMessageRenderer + A2UIProvider)
- Update all imports (e.g., `from '@copilotkit/react-core'` →
  `from '@copilotkit/react-core/v2'`)
- Run `mise run turbo build` + the v2.x conformance tests

#### Scenario: cianfhoghlaim-mmo uses CopilotKit v2.0

- **WHEN** the operator inspects `web/apps/cianfhoghlaim-mmo/package.json`
- **THEN** the package MUST use `@copilotkit/react-core/v2@^1.67.1`
- **AND** no `@copilotkit/react-core@^1.x` MUST appear in the dependencies