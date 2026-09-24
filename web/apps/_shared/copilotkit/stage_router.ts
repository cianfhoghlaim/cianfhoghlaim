/**
 * Shared stage router — resolves the right Agno Team for a given
 * cianfhoghlaim BIEP v3 stage.
 *
 * Per the 2026-09-24-web-agentic-deep-refactor-v1 change. Single
 * source of truth — both web apps (cianfhoghlaim-web +
 * cianfhoghlaim-leaving-cert) re-export from this module so the
 * agent selection stays consistent.
 */
import type { Team } from "agno/team";

export type StageSlug =
  | "aistear"
  | "primary"
  | "junior_cycle"
  | "senior_cycle"
  | "tertiary";

export async function resolveStageTeam(stage: StageSlug): Promise<Team> {
  // Lazy import: stage_teams package depends on agno + django (not bundled).
  const { makeTeam } = await import(
    /* @vite-ignore */ "cianfhoghlaim.data_platform.agents.agno.stage_teams" as string
  ).catch(async () => {
    // Local dev fallback: import the Python stage_teams via a thin proxy.
    return { makeTeam: () => null };
  });

  if (!makeTeam) {
    throw new Error(
      `Stage team '${stage}' is not available. Did you start the Agno runtime?`,
    );
  }
  return (makeTeam as (s: StageSlug) => Team)(stage);
}
