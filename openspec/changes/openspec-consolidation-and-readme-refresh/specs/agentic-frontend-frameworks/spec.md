## ADDED Requirements

The `agentic-frontend-frameworks` capability is renamed from
`frontend-frameworks` (and the old `agent-frameworks` spec is merged
into it) and shrunk to a thin capability pointer at the relevant
skills. The full Requirements + Scenarios are in the canonical spec at
`openspec/specs/agentic-frontend-frameworks/spec.md`.

### Requirement: File-based routing

The system SHALL use TanStack Start's file-based routing for the
oideachais web app and the croilar apps.

#### Scenario: Routes are auto-generated

- **WHEN** a file `oideachais/web/apps/web/src/routes/curriculum.tsx` is added
- **THEN** the route `/curriculum` is auto-generated

### Requirement: Server functions

The system SHALL use TanStack Start server functions for all data
fetching and agent calls.

#### Scenario: Type-safe server function

- **WHEN** a server function `getCurriculum(subject: string)` is
  called from the client with `subject="ga101"`
- **THEN** the function executes on the server with type safety

### Requirement: Agent UI streaming

The system SHALL stream agent responses to the client using the AG-UI
protocol.

#### Scenario: AG-UI streaming

- **WHEN** an agent generates a response
- **THEN** the response is streamed to the client via AG-UI
