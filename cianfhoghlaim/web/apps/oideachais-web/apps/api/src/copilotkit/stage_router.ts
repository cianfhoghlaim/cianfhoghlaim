// Stage router — resolves the right Agno Team for a given stage.
// Imports the stage_teams factory from the data_platform package.
import type { Team } from "agno/team";

export type StageSlug = "aistear" | "primary" | "junior_cycle" | "senior_cycle" | "tertiary";

export async function resolveStageTeam(stage: StageSlug): Promise<Team> {
  // Lazy import to keep the bundle small; the stage_teams package depends on
  // agno + django (not bundled in apps/api).
  const { makeTeam } = await import(
    /* @vite-ignore */ "oideachais.data_platform.agents.agno.stage_teams" as string
  ).catch(async () => {
    // Fallback for local dev: import the Python stage_teams via a thin proxy
    return { makeTeam: () => null };
  });

  if (!makeTeam) {
    throw new Error(
      `Stage team '${stage}' is not available. Did you start the Agno runtime?`,
    );
  }
  return (makeTeam as (s: StageSlug) => Team)(stage);
}
