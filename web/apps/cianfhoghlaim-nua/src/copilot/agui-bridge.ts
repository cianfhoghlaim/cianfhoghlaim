/**
 * AG-UI SSE bridge for the consolidated cianfhoghlaim-nua app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
 * (Phase 3 §B.9). Connects the client-side CopilotKit runtime to
 * the canonical Hono AG-UI SSE endpoint at /api/agui/sse.
 *
 * Lifted + simplified from web/hono-api/src/routes/agui/index.ts.
 */

export const AGUI_SSE_URL =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8787/api/agui/sse`
    : "http://localhost:8787/api/agui/sse";

export interface AGUIEvent {
  type:
    | "RUN_STARTED"
    | "TEXT_MESSAGE_CONTENT"
    | "TOOL_CALL_START"
    | "TOOL_CALL_ARGS"
    | "TOOL_CALL_END"
    | "TOOL_CALL_RESULT"
    | "STATE_DELTA"
    | "RUN_FINISHED"
    | "RUN_ERROR";
  data: Record<string, unknown>;
}

export function createAGUIEventSource(agent: string, threadId: string): EventSource {
  const url = new URL(AGUI_SSE_URL);
  url.searchParams.set("agent", agent);
  url.searchParams.set("thread_id", threadId);
  return new EventSource(url.toString());
}
