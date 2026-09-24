/**
 * CopilotKit + AG-UI runtime — Cianfhoghlaim Oideachais
 *
 * Per the 2026-09-24-web-agentic-deep-refactor-v1 change. The runtime
 * exposes 2 routes:
 * - POST /api/copilotkit      — streams AG-UI events from the stage team
 * - GET  /api/copilotkit/health — healthcheck
 *
 * The actions.ts in this same dir defines the 13 + 14 canonical
 * CopilotKit actions. This runtime is the AG-UI transport that the
 * actions ride on.
 */
import { Hono } from "hono";
import { streamAGUI } from "./agui_stream";
import { resolveStageTeam } from "./stage_router";
import { ALL_ACTIONS, type Tool } from "./actions";

export const copilotkit = new Hono();

// POST /api/copilotkit?stage=...&subject=...&language=...
copilotkit.post("/", async (c) => {
  const url = new URL(c.req.url);
  const stage = (url.searchParams.get("stage") ?? "senior_cycle") as
    | "aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary";
  const subject = url.searchParams.get("subject") ?? "";
  const language = (url.searchParams.get("language") ?? "en") as "en" | "ga";

  const team = await resolveStageTeam(stage);
  return streamAGUI(c.req.raw, team, { stage, subject, language });
});

// GET /api/copilotkit/actions — the 13 + 14 canonical action definitions
// (per the 2026-09-24-web-agentic-deep-refactor-v1 change)
copilotkit.get("/actions", (c) => {
  return c.json({
    actions: ALL_ACTIONS.map((a: Tool) => ({
      name: a.name,
      description: a.description,
      parameters: a.parameters,
    })),
    count: ALL_ACTIONS.length,
  });
});

// GET /api/copilotkit/health — healthcheck
copilotkit.get("/health", (c) => c.json({ status: "ok" }));
