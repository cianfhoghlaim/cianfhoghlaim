// bonneagar/iac/auth.ts — The 3 auth flows
// (a) komodoLogin: uses KOMODO_PASSWORD if set, else throws
// (b) pangolinLogin: uses PANGOLIN_API_KEY if set, else mints a new one via Pocket ID OIDC
// (c) infisicalLogin: uses INFISICAL_TOKEN if set, else mints a new machine identity

import { KomodoClient } from "./clients/komodo-client.ts";
import { PangolinClient } from "./clients/pangolin-client.ts";
import { InfisicalClient } from "./clients/infisical-client.ts";
import { CONFIG } from "./config.ts";

export async function ensureKomodoAuth(): Promise<KomodoClient> {
  if (CONFIG.komodoJwt) {
    return new KomodoClient();
  }
  if (CONFIG.komodoPassword) {
    const client = new KomodoClient();
    await client.login("ciansedai", CONFIG.komodoPassword);
    console.log("✓ komodo: logged in via KOMODO_PASSWORD");
    return client;
  }
  // TODO: komodo-recover.sh flow (docker exec into komodo-ferretdb to reset the password)
  throw new Error("KOMODO_JWT or KOMODO_PASSWORD required");
}

export async function ensurePangolinAuth(): Promise<PangolinClient> {
  if (CONFIG.pangolinApiKey) {
    const client = new PangolinClient();
    // Verify the key works (fixes blocker #3)
    try {
      await client.listResources();
      return client;
    } catch (e) {
      console.warn(`⚠ pangolin: PANGOLIN_API_KEY returned ${(e as Error).message}; re-mint required`);
    }
  }
  // TODO: Pocket ID OIDC client_credentials flow
  // For now, throw with a helpful error
  throw new Error("PANGOLIN_API_KEY required (or implement Pocket ID OIDC client_credentials flow)");
}

export async function ensureInfisicalAuth(): Promise<InfisicalClient> {
  if (CONFIG.infisicalToken || (CONFIG.infisicalClientId && CONFIG.infisicalClientSecret)) {
    const client = new InfisicalClient();
    // Smoke test
    try {
      await client.listProjects();
      return client;
    } catch (e) {
      console.warn(`⚠ infisical: auth returned ${(e as Error).message}`);
    }
  }
  throw new Error("INFISICAL_TOKEN or INFISICAL_CLIENT_ID+INFISICAL_CLIENT_SECRET required");
}
