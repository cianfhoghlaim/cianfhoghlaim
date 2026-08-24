/**
 * CopilotKit v2 — the agent chat + generative UI runtime client.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change. The 5 consolidated web apps (`cianfhoghlaim`, `oideachais`,
 * `croilar`, `tuatha`, `game_showcase`) all import from this module
 * instead of installing CopilotKit independently.
 */

import { HttpAgent } from "@ag-ui/client";
import type { AgentSubscriber } from "@ag-ui/client";

/**
 * The canonical Cianfhoghlaim CopilotKit runtime URL.
 * Per the master plan, every frontend app talks to the SAME hono-api
 * gateway at `web/hono-api/src/routes/copilotkit/index.ts`.
 */
export const CIANFHOGHLAIM_RUNTIME_URL: string =
  (typeof process !== "undefined" && process.env?.CIANFHOGHLAIM_RUNTIME_URL) ||
  (typeof window !== "undefined" && (window as any).CIANFHOGHLAIM_RUNTIME_URL) ||
  "http://localhost:4000/copilotkit";

/**
 * Build the canonical AG-UI HttpAgent that all 5 web apps use to talk
 * to the hono-api gateway. Per the AG-UI spec, the agent exposes
 * Server-Sent Events (SSE) at `${runtime}/agui/sse`.
 */
export function createCianfhoghlaimAgent(): HttpAgent {
  return new HttpAgent({
    url: `${CIANFHOGHLAIM_RUNTIME_URL.replace(/\/$/, "")}/agui/sse`,
    threadId: `thread-${Date.now()}`,
  });
}

/**
 * Subscribe a callback to AG-UI events from the canonical runtime.
 * This is the type-safe entry point for the 5 web apps.
 */
export type CianfhoghlaimSubscriber = AgentSubscriber;

export type { HttpAgent, AgentSubscriber };
