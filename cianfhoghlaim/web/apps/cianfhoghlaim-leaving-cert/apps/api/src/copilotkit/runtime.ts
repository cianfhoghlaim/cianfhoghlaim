// CopilotKit AG-UI runtime — Cianfhoghlaim OS
// Hono route mounted at /api/copilotkit.
// Streams AG-UI events to the SPA via SSE.
// The 8 NCCA subject specialists are registered as CopilotKit dispatch targets
// (the Brown Ajah per the Wheel of Time theming — see docs/BROWN_AJAH_THEMING.md).

import { Hono } from "hono";
import { streamAGUI } from "./agui_stream";
import { resolveSubjectTeam } from "./stage_router";

export const copilotkit = new Hono();

copilotkit.post("/", async (c) => {
  const url = new URL(c.req.url);
  const stage = (url.searchParams.get("stage") ?? "senior_cycle") as
    | "aistear"
    | "primary"
    | "junior_cycle"
    | "senior_cycle"
    | "tertiary";
  const subject = url.searchParams.get("subject") ?? "";
  const language = (url.searchParams.get("language") ?? "en") as "en" | "ga";

  const team = await resolveSubjectTeam(subject);
  return streamAGUI(c.req.raw, team, { stage, subject, language });
});

// GET endpoint for healthcheck
copilotkit.get("/health", (c) => c.json({ status: "ok" }));