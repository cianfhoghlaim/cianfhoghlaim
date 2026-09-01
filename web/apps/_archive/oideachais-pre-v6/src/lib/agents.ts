// apps/web/src/lib/agents.ts
// Per openspec/changes/cianfhoghlaim-website-rewrite/specs/.../spec.md
// Requirement R3. The 9 ADK agent functions that the chat surface calls.

import { getAgentById, getSystemPrompt, type AgentDef } from "./registry";

/**
 * Get the 9 ADK agent system prompts. These are the canonical
 * instructions the chat surface uses when dispatching to each agent.
 */
export function getAgentSystemPrompt(agentId: string): string | null {
  const validIds = [
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
    "cianfhoghlaim",
  ] as const;
  if (!validIds.includes(agentId as (typeof validIds)[number])) return null;
  return getSystemPrompt(getAgentById(agentId as (typeof validIds)[number]));
}

/**
 * Get the 9 ADK agent tools. Each tool is wired to the corresponding
 * baml.qpack_{subject}.baml schema + the cocoindex subject embeddings +
 * the dlt ncca_root_pdfs.py extraction.
 */
export function getAgentTools(agentId: string): string[] | null {
  const agent = getAgentById(agentId as Parameters<typeof getAgentById>[0]);
  return agent?.tools ?? null;
}

/**
 * List all 9 ADK agents. Used by the chat surface + the global
 * CopilotKit provider to populate the agent selection menu.
 */
export function listAllAgents(): AgentDef[] {
  const { AGENTS } = require("./registry");
  return AGENTS;
}

/**
 * Map a subject slug to its ADK agent ID. The 8 NCCA subjects
 * map 1:1 to their agent IDs.
 */
export function subjectToAgentId(subject: string): string | null {
  const map: Record<string, string> = {
    mathematics: "mathematics",
    applied_mathematics: "applied_mathematics",
    chemistry: "chemistry",
    geography: "geography",
    history: "history",
    english: "english",
    gaeilge: "gaeilge",
    computer_science: "computer_science",
  };
  return map[subject] ?? null;
}