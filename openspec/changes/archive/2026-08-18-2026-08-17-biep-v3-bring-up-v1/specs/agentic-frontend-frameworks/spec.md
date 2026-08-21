# agentic-frontend-frameworks

## ADDED Requirements

### Requirement: CopilotKit >= 1.67.1 pin

The 12 web apps under `web/apps/` that depend on CopilotKit SHALL
pin `@copilotkit/runtime >= 1.67.1` +
`@copilotkit/react-core >= 1.67.1` +
`@copilotkit/react-ui >= 1.67.1` (per the `agentic-frontend-frameworks`
spec).

The reason: per `CopilotKit issue #2946` (confirmed regression in
v1.50.1 where `useLazyToolRenderer` only processes `toolCalls[0]`)
+ `CopilotKit issue #3030` (Strands adapter required text
\nclose guard), the v1.50 series has 2 known regressions that are
fixed in v1.67.1 (verified via `CopilotKit v1.67.1 release notes`).

Additionally, `ag-ui-strands` MUST be upgraded alongside the
CopilotKit pin (per `ag-ui-strands` integration with CopilotKit).

#### Scenario: Pin is set in package.json

- **WHEN** `bun pm ls copilotkit --filter 'copilotkit'` runs in
  `web/apps/cianfhoghlaim-leaving-cert/`
- **THEN** the resolved versions are >= 1.67.1
- **AND** the same is true for `web/apps/cianfhoghlaim-web/`,
  `web/apps/oideachais/`, `web/apps/croilar-web/`,
  `web/apps/croilar-portal/`, `web/apps/tuatha-ui/`, etc.

#### Scenario: ag-ui-strands is upgraded

- **WHEN** `bun pm ls ag-ui-strands` runs
- **THEN** the resolved version is >= the version that ships with
  CopilotKit v1.67.1 (currently 0.0.3)

#### Scenario: CopilotKit useLazyToolRenderer renders all tool calls

- **GIVEN** an AG-UI agent emits multiple sequential `TOOL_CALL_*`
  events for the same assistant message
- **WHEN** the CopilotKit runtime processes the events
- **THEN** the runtime MUST render all tool calls (not just
  `toolCalls[0]` per the v1.50 regression)
- **AND** the chat UI shows all tool components side-by-side

### Requirement: `web/COPILOTKIT_PIN.md` canonical doc

The system SHALL maintain `web/COPILOTKIT_PIN.md` (canonical
reference) documenting:
- The 1.67.1 pin + the v1.50 regression context (per
  `CopilotKit issue #2946`)
- The `ag-ui-strands` upgrade requirement
- The Strands adapter `TEXT_MESSAGE_END` close-guard fix (per
  `CopilotKit issue #3030`)
- The recommended path to the v2 headless API (`@copilotkit/react-core/v2`)
  for new surfaces (per `CopilotKit v1.50 release announcement`)

#### Scenario: New developer consults the doc

- **WHEN** a developer is wiring a new CopilotKit surface
- **THEN** they MUST consult `web/COPILOTKIT_PIN.md` for the
  canonical pin + decision + 1.67.1 migration notes
- **AND** the doc covers the v1 → v2 migration path