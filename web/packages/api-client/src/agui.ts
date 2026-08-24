/**
 * AG-UI client — the Agent-User Interaction protocol.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change. The 5 consolidated web apps subscribe to AG-UI events from
 * the hono-api gateway (`web/hono-api/src/routes/agui/index.ts`) via
 * the canonical HttpAgent (see `./copilotkit.ts`).
 *
 * The AG-UI protocol supports:
 *   - Streaming chat tokens
 *   - Multimodality (files, images, audio, transcripts)
 *   - Generative UI (static + declarative)
 *   - Shared state (read-only & read-write)
 *   - Thinking steps
 *   - Frontend tool calls
 *   - Backend tool rendering
 *   - Interrupts (human in the loop)
 *   - Sub-agents and composition
 *   - Agent steering
 *   - Tool output streaming
 *   - Custom events
 *
 * Reference: https://docs.ag-ui.com/
 */

export {
  HttpAgent,
  EventType,
  type AgentSubscriber,
  type RunAgentInput,
  type Message,
  type ToolCall,
  type State,
} from "@ag-ui/client";

export { createCianfhoghlaimAgent, CIANFHOGHLAIM_RUNTIME_URL } from "./copilotkit";
