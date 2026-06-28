// Komodo IaC Configuration
// Reads secrets from the root .env (hydrated by mise hooks) or process env.

function envOr(key: string, fallback: string): string {
  return process.env[key] ?? fallback;
}

export const CONFIG = {
  // Komodo Core
  komodoUrl: envOr("KOMODO_URL", "http://localhost:9120"),
  komodoJwt: envOr("KOMODO_JWT", ""),

  // Pangolin
  pangolinUrl: envOr("PANGOLIN_URL", "https://pangolin.cianfhoghlaim.ie"),
  pangolinApiBase: envOr("PANGOLIN_API_BASE", "https://pangolin.cianfhoghlaim.ie/v1"),
  pangolinApiKey: envOr("PANGOLIN_API_KEY", ""),
  pangolinOrgId: envOr("PANGOLIN_ORG_ID", "cianfhoghlaim"),

  // Git provider for resource-syncs
  gitProvider: envOr("GIT_PROVIDER", "forgejo.cianfhoghlaim.ie"),
  gitRepo: envOr("GIT_REPO", "kings_college_galway"),
  gitBranch: envOr("GIT_BRANCH", "main"),
};
