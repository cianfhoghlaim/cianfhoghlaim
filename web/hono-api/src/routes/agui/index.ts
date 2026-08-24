/**
 * AG-UI SSE endpoint — the canonical Agent-User Interaction protocol
 * handler for the Cianfhoghlaim platform.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change. The 5 consolidated web apps (cianfhoghlaim, oideachais,
 * croilar, tuatha, game_showcase) all subscribe to this endpoint via
 * `@cianfhoghlaim/api-client` (`createCianfhoghlaimAgent()` → HttpAgent).
 *
 * The handler streams AG-UI events (RUN_STARTED, TEXT_MESSAGE_CONTENT,
 * TOOL_CALL_*, STATE_DELTA, …) as Server-Sent Events (SSE). The
 * frontend consumes them via TanStack DB's reactive subscription,
 * giving real-time UI updates with no polling.
 *
 * Reference:
 *   - AG-UI spec:    https://docs.ag-ui.com/
 *   - Wave 6 spec:   openspec/changes/2026-08-24-wave-6-frontend-tanstack-modernisation-v1/
 */

import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import type { PipelineEvent } from "@cianfhoghlaim/contracts";

/**
 * The single canonical AG-UI SSE handler. Each frontend app connects
 * to `${runtimeBase}/agui/sse` and receives a stream of PipelineEvent
 * objects (the AG-UI event envelope from `@cianfhoghlaim/contracts`).
 */
export const aguiRouter = new Hono().get("/sse", (c) => {
  return streamSSE(c, async (stream) => {
    // Wave 6 stub: emit a hello event so the frontend can verify the
    // connection. The real implementation (per Wave 6 follow-up) will
    // stream events from the Convex agent table + the CocoIndex DAG.
    const helloEvent: PipelineEvent = {
      event_type: "RUN_STARTED",
      run_id: `run-${Date.now()}`,
      thread_id: c.req.query("thread_id") ?? `thread-${Date.now()}`,
      timestamp: new Date().toISOString(),
      payload: {
        source: "agui/sse",
        wave: 6,
        message: "Cianfhoghlaim AG-UI SSE endpoint — Wave 6 stub",
      },
    };
    await stream.writeSSE({
      event: helloEvent.event_type,
      data: JSON.stringify(helloEvent),
      id: helloEvent.run_id,
    });
    await stream.sleep(1000);

    const readyEvent: PipelineEvent = {
      ...helloEvent,
      event_type: "TEXT_MESSAGE_END",
      payload: {
        ...helloEvent.payload,
        message: "AG-UI endpoint is ready. Real event streaming lands in Wave 6 follow-up.",
      },
    };
    await stream.writeSSE({
      event: readyEvent.event_type,
      data: JSON.stringify(readyEvent),
      id: `${readyEvent.run_id}-ready`,
    });
  });
});

export type AguiRouter = typeof aguiRouter;
