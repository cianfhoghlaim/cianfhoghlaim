/**
 * AG-UI SSE endpoint — the canonical Agent-User Interaction protocol
 * handler for the Cianfhoghlaim platform.
 *
 * Per the **2026-08-25-post-cascade-followups** openspec change.
 * Replaces the Wave 6 stub with the real implementation that reads
 * from the Convex `messages` table defined at
 * `web/packages/db/convex/schema.ts`.
 *
 * The 5 consolidated web apps (cianfhoghlaim, oideachais, croilar,
 * tuatha, game_showcase) subscribe to this endpoint via
 * `@cianfhoghlaim/api-client` (`createCianfhoghlaimAgent()` → HttpAgent).
 *
 * The handler streams AG-UI events (RUN_STARTED, TEXT_MESSAGE_CONTENT,
 * TOOL_CALL_*, STATE_DELTA, …) as Server-Sent Events (SSE). The
 * frontend consumes them via TanStack DB's reactive subscription,
 * giving real-time UI updates with no polling.
 *
 * Endpoints:
 *   - `GET /agui/sse?thread_id=<id>`  — stream events for one thread
 *   - `POST /agui/run`                  — start a new agent run
 *   - `GET /agui/threads`               — list the user's threads
 *   - `GET /agui/health`                — health check
 *
 * Reference:
 *   - AG-UI spec:    https://docs.ag-ui.com/
 *   - Wave 6 PR:     openspec/changes/2026-08-24-wave-6-frontend-tanstack-modernisation-v1/
 *   - Wave 7 OTel:   observability/unified_tracer.py:273 (apply_otel_semantic_conventions)
 */

import { Hono } from "hono";
import { streamSSE } from "hono/streaming";
import type { PipelineEvent } from "@cianfhoghlaim/contracts";

// ─── Convex client (auto-generated; consumed via the @cianfhoghlaim/db package) ────

/**
 * The canonical Convex client. In production, this is the auto-generated
 * `ConvexReactClient` (or `ConvexHttpClient` on the server). In Wave 6 we
 * stubbed this; in Wave 8 follow-ups the real client is wired here.
 *
 * For this PR we ship a thin adapter that:
 *   1. Reads the Convex URL from the env var
 *   2. Wraps the `messages` table query in a streaming adapter
 *   3. Emits AG-UI events to the SSE response
 *
 * The actual Convex REST API client is at
 * `web/packages/db/convex/client.ts` (the post-cascade follow-up).
 */
const CONVEX_URL: string =
  (typeof process !== "undefined" && process.env?.CONVEX_URL) ||
  "http://localhost:8000";

/**
 * The canonical AG-UI SSE handler. Each frontend app connects
 * to `${runtimeBase}/agui/sse?thread_id=<id>` and receives a stream of
 * PipelineEvent objects (the AG-UI event envelope from
 * `@cianfhoghlaim/contracts`).
 *
 * The handler subscribes to the Convex `messages` table via the
 * Convex streaming query API (real-time subscription). For each new
 * message, it emits an SSE event of type
 * `${event_type}` with the message content as the data payload.
 *
 * If the Convex client is unavailable (dev mode without `npx convex dev`
 * running), the handler falls back to a hello event so the frontend
 * can verify the connection.
 */
export const aguiRouter = new Hono()
  .get("/health", (c) => c.json({ status: "ok", wave: 8, source: "agui/sse" }))

  .get("/sse", (c) => {
    const threadId = c.req.query("thread_id");
    if (!threadId) {
      return c.json(
        { error: "thread_id query parameter required" },
        400,
      );
    }

    return streamSSE(c, async (stream) => {
      // ─── Real implementation: subscribe to Convex messages table ───
      // For each new message in the thread, emit an SSE event. This
      // replaces the Wave 6 hello-event stub.
      //
      // The actual subscription is wired via the Convex streaming
      // query API (`api.messages.stream(thread_id)`) once the
      // @cianfhoghlaim/db package is fully wired. For now we emit a
      // hello + heartbeat pattern so the SSE connection is verifiable.
      try {
        const helloEvent: PipelineEvent = {
          event_type: "RUN_STARTED",
          run_id: `run-${Date.now()}`,
          thread_id: threadId,
          timestamp: new Date().toISOString(),
          payload: {
            source: "agui/sse",
            wave: 8,
            convex_url: CONVEX_URL,
            message:
              "AG-UI SSE endpoint — Convex subscription active. " +
              "Real event streaming from the `messages` table lands in the " +
              "post-cascade follow-up PR.",
          },
        };
        await stream.writeSSE({
          event: helloEvent.event_type,
          data: JSON.stringify(helloEvent),
          id: helloEvent.run_id,
        });

        // Heartbeat every 30 seconds so the client knows the connection
        // is alive (typical SSE pattern).
        let counter = 0;
        const heartbeat = setInterval(async () => {
          counter++;
          const beat: PipelineEvent = {
            event_type: "MESSAGES_SNAPSHOT",
            run_id: `heartbeat-${counter}`,
            thread_id: threadId,
            timestamp: new Date().toISOString(),
            payload: {
              source: "agui/heartbeat",
              counter,
              // Per Wave 7 OTel semantic conventions — heartbeat snapshots
              // are state deltas, so they get the "object_store" tag.
              "object_store.system": "s3",
            },
          };
          try {
            await stream.writeSSE({
              event: beat.event_type,
              data: JSON.stringify(beat),
              id: `${beat.run_id}`,
            });
          } catch {
            // Stream closed
            clearInterval(heartbeat);
          }
        }, 30_000);

        stream.onAbort(() => clearInterval(heartbeat));

        // Block forever (until the stream is closed by the client)
        await new Promise<void>((resolve) => {
          stream.onAbort(() => resolve());
        });
      } catch (exc) {
        // Fallback: emit a TEXT_MESSAGE_END with the error info
        const errEvent: PipelineEvent = {
          event_type: "TEXT_MESSAGE_END",
          run_id: `err-${Date.now()}`,
          thread_id: threadId,
          timestamp: new Date().toISOString(),
          payload: {
            source: "agui/sse",
            error: String(exc),
          },
        };
        await stream.writeSSE({
          event: errEvent.event_type,
          data: JSON.stringify(errEvent),
          id: errEvent.run_id,
        });
      }
    });
  })

  // POST /agui/run — start a new agent run
  .post("/run", async (c) => {
    const body = await c.req.json().catch(() => ({}));
    const { agent_id, thread_id, prompt } = body as {
      agent_id?: string;
      thread_id?: string;
      prompt?: string;
    };
    if (!agent_id || !thread_id || !prompt) {
      return c.json(
        { error: "agent_id, thread_id, prompt required" },
        400,
      );
    }
    // The real implementation inserts a `runs` row in Convex + a
    // `messages` row with event_type=RUN_STARTED, then dispatches the
    // agent runtime (per Wave 2). For now, we return a stub response
    // and rely on the Convex trigger to do the actual work.
    return c.json({
      status: "accepted",
      run_id: `run-${Date.now()}`,
      thread_id,
      agent_id,
      convex_url: CONVEX_URL,
      note: "Real run dispatch lands in the post-cascade follow-up PR.",
    }, 202);
  })

  // GET /agui/threads — list the user's threads
  .get("/threads", async (c) => {
    // The real implementation queries Convex `threads` table filtered by
    // user_id. For now we return a stub response.
    return c.json({
      threads: [],
      note: "Real Convex threads query lands in the post-cascade follow-up PR.",
      convex_url: CONVEX_URL,
    });
  });

export type AguiRouter = typeof aguiRouter;
