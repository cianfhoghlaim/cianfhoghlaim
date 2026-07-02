// Stage router — resolves the right NCCA subject team for a given subject.
// Lazy-imports the canonical ADK LlmAgent from cianfhoghlaim/agents/tuatha/agents/.
//
// Per the Brown Ajah theming (docs/BROWN_AJAH_THEMING.md), the 8 NCCA
// subject specialists are the 8 Brown Ajah members; the orchestrator
// (the Amyrlin Seat) routes to the right Brown Ajah based on the URL param.

import type { BuiltInAgent } from "@copilotkit/runtime";

export type SubjectSlug =
  | "mathematics"
  | "applied_mathematics"
  | "chemistry"
  | "geography"
  | "history"
  | "english"
  | "gaeilge"
  | "computer_science";

export async function resolveSubjectTeam(subject: SubjectSlug): Promise<BuiltInAgent> {
  // Lazy import to keep the bundle small; the agents package depends on
  // google.adk + langfuse + letta (not bundled in apps/api).
  const { makeSubjectAgent } = await import(
    /* @vite-ignore */ "cianfhoghlaim/agents/tuatha/agents/subject_router" as string
  ).catch(async () => {
    // Fallback for local dev: return a stub
    return {
      makeSubjectAgent: () => null,
    };
  });

  if (!makeSubjectAgent) {
    throw new Error(
      `Subject team '${subject}' is not available. Did you start the ADK runtime?`,
    );
  }
  return (makeSubjectAgent as (s: SubjectSlug) => BuiltInAgent)(subject);
}