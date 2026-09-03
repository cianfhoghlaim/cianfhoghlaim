# tanstack-ai-agui-integration Specification

## Purpose

Formalize the TanStack AI + AG-UI compliance + Convex +
CopilotKit integration for the consolidated `web/` apps. The
integration MUST comply with the TanStack AI AG-UI compliance
post (https://tanstack.com/blog/ag-ui-compliance) and the AG-UI
protocol spec (https://docs.ag-ui.com).

The system is added by the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
openspec change (Phase Q).

## ADDED Requirements

### Requirement: The TanStack AI client SHALL be AG-UI compliant

The system SHALL provide a TanStack AI client at
`web/apps/oideachais/src/lib/tanstack-ai-client.ts` that uses
the canonical `chat()` + `chatParamsFromRequest()` +
`toServerSentEventsResponse()` pattern.

#### Scenario: A new chat endpoint is added per subject

- **WHEN** a developer adds a new chat endpoint at
  `web/apps/oideachais/routes/api/chat/$subjectId.ts`
- **THEN** the endpoint MUST use the canonical pattern:
```typescript
import { chat, chatParamsFromRequest, toServerSentEventsResponse } from '@tanstack/ai'
import { openaiText } from '@tanstack/ai-openai/adapters'

export async function POST(req: Request) {
  const params = await chatParamsFromRequest(req)
  const stream = chat({
    adapter: openaiText('minimax-m3'),
    messages: params.messages,
    threadId: params.threadId,
    tools: serverTools,
  })
  return toServerSentEventsResponse(stream)
}
```
- **AND** the model MUST be resolved via `MODEL_REGISTRY`,
  never hardcoded

### Requirement: The Convex client MUST integrate with TanStack Query

The system MUST provide a Convex client at
`web/apps/oideachais/src/lib/convex-client.ts` that uses the
canonical pattern from
https://docs.convex.dev/quickstart/tanstack-start.

#### Scenario: A route uses Convex data

- **WHEN** a developer writes a route at
  `web/apps/oideachais/routes/lc/<subject>/$topicId.tsx`
- **THEN** the route MUST use `useSuspenseQuery(api.queries.get)` to
  fetch Convex data
- **AND** the route MUST use `useChat({ adapter: openaiText('minimax-m3') })`
  to render the CopilotKit chat

### Requirement: CopilotKit actions MUST route through AG-UI protocol

The system MUST use CopilotKit v2 + AG-UI protocol per
https://docs.copilotkit.ai/concepts/generative-ui-overview:

- Components as Tools: register React components as frontend
  tools
- Tool Call Rendering: render backend tool calls as custom UI
  cards
- State Rendering: subscribe to agent state and re-render
- Reasoning: render model reasoning as a message type
- A2UI: render declarative UI from the agent
- MCP Apps: embed UI from MCP servers

#### Scenario: A per-subject CopilotKit action is generated

- **WHEN** the codegen pipeline emits a new CopilotKit action for
  `mathematics_lc`
- **THEN** the action MUST live at
  `web/hono-api/src/routes/copilotkit/lc/mathematics.ts`
- **AND** MUST use the canonical `useCopilotAction` pattern
- **AND** MUST be bound to the per-subject BAML function
