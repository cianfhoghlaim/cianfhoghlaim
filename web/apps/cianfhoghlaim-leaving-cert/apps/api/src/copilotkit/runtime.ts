// CopilotKit AG-UI runtime — Cianfhoghlaim OS
// Hono route mounted at /api/copilotkit.
// Streams AG-UI events to the SPA via SSE.
// The 14 CopilotKit actions (6 leaving-cert + 4 diagram + 2 3D-asset +
// 1 cross-subject + 1 SCR commentary) are registered as dispatch targets.
//
// Per openspec/changes/cianfhoghlaim-website-rewrite/proposal.md
// — wired to the apps/api/src/registry.ts (the 9 ADK agent definitions).

import { Hono } from "hono";
import { streamAGUI } from "./agui_stream";
import { AGENTS, getAgentById } from "../registry";
import { ALL_ACTIONS } from "./actions";

const copilotkitApp = new Hono();

const SUBJECT_SLUGS = [
  "mathematics", "applied_mathematics", "chemistry", "geography",
  "history", "english", "gaeilge", "computer_science",
] as const;
type SubjectSlug = typeof SUBJECT_SLUGS[number];

function isSubjectSlug(s: string): s is SubjectSlug {
  return (SUBJECT_SLUGS as readonly string[]).includes(s);
}

copilotkitApp.post("/", async (c) => {
  const url = new URL(c.req.url);
  const stage = (url.searchParams.get("stage") ?? "senior_cycle") as
    | "aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary";
  const subject = url.searchParams.get("subject") ?? "";
  const language = (url.searchParams.get("language") ?? "en") as "en" | "ga";

  // Resolve to a synthetic ADK team — for now, return a fake team for any
  // subject. The cianfhoghlaim operator agent (id="cianfhoghlaim") is the
  // default if the subject is unknown.
  const team: BuiltInAgentLike = isSubjectSlug(subject)
    ? makeSyntheticTeam(getAgentById(subject))
    : makeSyntheticTeam(getAgentById("cianfhoghlaim"));

  return streamAGUI(c.req.raw, team, { stage, subject, language }, ALL_ACTIONS);
});

copilotkitApp.get("/health", (c) => c.json({
  status: "ok",
  actions_registered: ALL_ACTIONS.length,
  action_names: ALL_ACTIONS.map((a) => a.name),
}));

// The /api/subjects endpoint moved to ../subjects — see apps/api/src/routers/subjects.ts

// Synthetic ADK team shape — wraps an AGENTS entry into a BuiltInAgent-compatible
// object for the SSE stream.
function makeSyntheticTeam(agent: typeof AGENTS[number]): BuiltInAgentLike {
  return {
    name: agent.id,
    description: agent.role,
    model: "minimax-m3",
    systemPrompt: agent.system_prompt,
  };
}

interface BuiltInAgentLike {
  name: string;
  description: string;
  model: string;
  systemPrompt: string;
}

export { copilotkitApp as copilotkit };