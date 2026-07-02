// Stage router — resolves the right NCCA subject team for a given subject.
// Lazy-imports the canonical ADK SequentialAgent "team" from
// cianfhoghlaim/agents/tuatha/subject_router.py via
// `../../../agents/tuatha/subject_router`.
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
  const { make_subject_team } = await import(
    /* @vite-ignore */ "../../../agents/tuatha/subject_router" as string
  ).catch(async () => {
    return {
      make_subject_team: () => null,
    };
  });

  if (typeof make_subject_team !== "function") {
    throw new Error(
      `Subject team '${subject}' is not available. Did you start the ADK runtime?`,
    );
  }
  const team = (make_subject_team as (s: SubjectSlug) => BuiltInAgent | null)(subject);
  if (team === null || team === undefined) {
    throw new Error(
      `Subject team '${subject}' is not available. Did you start the ADK runtime?`,
    );
  }
  return team;
}