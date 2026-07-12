// bonneagar/iac/clients/infisical-client.ts — High-level Infisical client (uses infisical-rest.ts)
//
// Bypasses the buggy @infisical/sdk v5.0.2. Promotes the working direct-REST
// pattern from the legacy `fetchInfisicalSecret` function in
// `iac/commands/rotate-auth.ts` into a proper client.
//
// Backwards-compat shim: this file keeps the original class-based API
// (`InfisicalClient`) but delegates everything to the new REST helpers.

import {
  infisicalLogin,
  infisicalListProjects,
  infisicalGetProject,
  infisicalListSecrets,
  infisicalGetSecret,
  infisicalCreateSecret,
  infisicalUpdateSecret,
  infisicalDeleteSecret,
  infisicalListMachineIdentities,
  infisicalCreateMachineIdentity,
  infisicalCreateMachineIdentitySecret,
  infisicalHealth,
  infisicalGetUserCount,
  discoverInfisicalUrl,
} from "./infisical-rest.ts";

import type {
  InfisicalProject,
  InfisicalSecret,
  InfisicalMachineIdentity,
  InfisicalAuth,
} from "./infisical-rest.ts";

// Re-export for backwards compat with anything that imported these types
// from this file (vs the new infisical-rest.ts).
export type { InfisicalProject, InfisicalSecret, InfisicalMachineIdentity, InfisicalAuth };

// ---------------------------------------------------------------------------
// Class wrapper (legacy API — kept for backwards compat)
// ---------------------------------------------------------------------------

export class InfisicalClient {
  private baseUrl: string;
  private auth: InfisicalAuth;

  constructor(opts?: { baseUrl?: string; auth?: InfisicalAuth }) {
    this.baseUrl = opts?.baseUrl ?? discoverInfisicalUrl();
    this.auth = opts?.auth ?? {
      clientId: process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_ID ?? "",
      clientSecret: process.env.INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET ?? "",
    };
  }

  async login(): Promise<string> {
    const t = await infisicalLogin(this.baseUrl, this.auth);
    return t.accessToken;
  }

  listProjects = infisicalListProjects;
  getProject = infisicalGetProject;
  listSecrets = infisicalListSecrets;
  getSecret = infisicalGetSecret;
  createSecret = infisicalCreateSecret;
  updateSecret = infisicalUpdateSecret;
  deleteSecret = infisicalDeleteSecret;
  listMachineIdentities = infisicalListMachineIdentities;
  createMachineIdentity = infisicalCreateMachineIdentity;
  createMachineIdentitySecret = infisicalCreateMachineIdentitySecret;
  health = infisicalHealth;
  getUserCount = infisicalGetUserCount;
}

// ---------------------------------------------------------------------------
// Auth check helper (used by iac:health + iac:bootstrap)
// ---------------------------------------------------------------------------

/**
 * Verify the current Infisical auth works AND report which machine identities
 * are seeded. Returns a report structure for the iac:health 7-way check.
 */
export async function infisicalAuthReport(baseUrl: string = discoverInfisicalUrl()): Promise<{
  healthy: boolean;
  detail: string;
  identities: { name: string; present: boolean; id?: string }[];
  url: string;
}> {
  const requiredIdentities = [
    "bons-iac",
    "pocket-id",
    "komodo",
    "pangolin",
    "tinyauth",
    "openclaw",
    "openchamber",
    "hermes",
  ];

  try {
    const health = await infisicalHealth(baseUrl);
    if (!health.healthy) {
      return { healthy: false, detail: health.detail, identities: [], url: baseUrl };
    }
    const projectId = process.env.INFISICAL_PROJECT_ID ?? "f3cff583-b74b-4804-b9d3-db8b68885236";
    const present = await infisicalListMachineIdentities(projectId, baseUrl);
    const presentNames = new Set(present.map((i) => i.name));
    const identities = requiredIdentities.map((name) => ({
      name,
      present: presentNames.has(name),
      id: present.find((i) => i.name === name)?.id,
    }));
    const missing = identities.filter((i) => !i.present).map((i) => i.name);
    return {
      healthy: missing.length === 0,
      detail: missing.length === 0
        ? `infisical: ${present.length} machine identities seeded (${requiredIdentities.length} required)`
        : `infisical: missing machine identities: ${missing.join(", ")} (run: bun run iac:bootstrap-infisical)`,
      identities,
      url: baseUrl,
    };
  } catch (e) {
    return {
      healthy: false,
      detail: `infisical auth check failed: ${(e as Error).message}`,
      identities: [],
      url: baseUrl,
    };
  }
}
