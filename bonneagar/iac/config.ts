// bonneagar/iac/config.ts — single env loader
// Reads all env vars needed by the IaC (Komodo + Pangolin + Infisical).
// Supports `mise` directory hooks (the .env is auto-hydrated by mise on cd).

function envOr(key: string, fallback: string): string {
  return process.env[key] ?? fallback;
}

function envRequired(key: string): string {
  const v = process.env[key];
  if (!v) {
    throw new Error(`Missing required env var: ${key}`);
  }
  return v;
}

export const CONFIG = {
  // Komodo Core
  komodoUrl: envOr("KOMODO_URL", "http://localhost:9120"),
  komodoJwt: envOr("KOMODO_JWT", ""),
  komodoPassword: envOr("KOMODO_PASSWORD", ""),

  // Pangolin (Enterprise Edition — Integrations API at /v1/...)
  pangolinUrl: envOr("PANGOLIN_URL", "https://pangolin.cianfhoghlaim.ie"),
  pangolinApiBase: envOr("PANGOLIN_API_BASE", "https://pangolin.cianfhoghlaim.ie/v1"),
  pangolinApiKey: envOr("PANGOLIN_API_KEY", ""),
  pangolinOrgId: envOr("PANGOLIN_ORG_ID", "cianfhoghlaim"),
  pangolinLicence: envOr("PANGOLIN_LICENCE", ""),

  // Infisical
  infisicalUrl: envOr("INFISICAL_URL", "https://infisical.cianfhoghlaim.ie"),
  infisicalToken: envOr("INFISICAL_TOKEN", ""),
  infisicalClientId: envOr("INFISICAL_CLIENT_ID", ""),
  infisicalClientSecret: envOr("INFISICAL_CLIENT_SECRET", ""),
  infisicalProjectId: envOr("INFISICAL_PROJECT_ID", ""),
  infisicalEnvironment: envOr("INFISICAL_ENVIRONMENT", "dev-baile"),

  // Locket (used by the sidecar pattern, not by the IaC directly)
  locketToken: envOr("LOCKET_TOKEN", ""),

  // Git provider for resource-syncs
  gitProvider: envOr("GIT_PROVIDER", "forgejo.cianfhoghlaim.ie"),
  gitRepo: envOr("GIT_REPO", "kings_college_galway"),
  gitBranch: envOr("GIT_BRANCH", "main"),

  // Crossover flags
  dryRun: envOr("IAC_DRY_RUN", "false") === "true",
  verbose: envOr("IAC_VERBOSE", "false") === "true",
};

export function requireKomodoAuth(): { jwt: string } | { password: string } {
  if (CONFIG.komodoJwt) return { jwt: CONFIG.komodoJwt };
  if (CONFIG.komodoPassword) return { password: CONFIG.komodoPassword };
  throw new Error("KOMODO_JWT or KOMODO_PASSWORD required");
}

export function requirePangolinAuth(): { apiKey: string } {
  if (!CONFIG.pangolinApiKey) {
    throw new Error("PANGOLIN_API_KEY required");
  }
  return { apiKey: CONFIG.pangolinApiKey };
}

export function requireInfisicalAuth(): { token: string } | { clientId: string; clientSecret: string } {
  if (CONFIG.infisicalToken) return { token: CONFIG.infisicalToken };
  if (CONFIG.infisicalClientId && CONFIG.infisicalClientSecret) {
    return { clientId: CONFIG.infisicalClientId, clientSecret: CONFIG.infisicalClientSecret };
  }
  throw new Error("INFISICAL_TOKEN or INFISICAL_CLIENT_ID+CLIENT_SECRET required");
}
