// CopilotKit AG-UI runtime — Cianfhoghlaim OS
// Hono route mounted at /api/copilotkit.
// Streams AG-UI events to the SPA via SSE.
// The 14 CopilotKit actions (6 leaving-cert + 4 diagram + 2 3D-asset +
// 1 cross-subject + 1 SCR commentary) are registered as dispatch targets.

import { Hono } from "hono";
import { streamAGUI } from "./agui_stream";
import { resolveSubjectTeam } from "./stage_router";
import { ALL_ACTIONS } from "./actions";

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
  return streamAGUI(c.req.raw, team, { stage, subject, language }, ALL_ACTIONS);
});

copilotkit.get("/health", (c) => c.json({
  status: "ok",
  actions_registered: ALL_ACTIONS.length,
  action_names: ALL_ACTIONS.map((a) => a.name),
}));