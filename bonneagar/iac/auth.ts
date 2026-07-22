// bonneagar/iac/auth.ts — The 3 auth flows
// (a) komodoLogin: uses KOMODO_PASSWORD if set, else throws
// (b) pangolinLogin: uses PANGOLIN_API_KEY if set, else mints a new one via Pocket ID OIDC
// (c) infisicalLogin: uses INFISICAL_TOKEN if set, else mints a new machine identity

import { KomodoClient } from "./clients/komodo-client.ts";
import { PangolinClient } from "./clients/pangolin-client.ts";
import { InfisicalClient } from "./clients/infisical-client.ts";
import { pocketIdLogin } from "./auth-pocketid.ts";
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
  // 1. If we already have a working PANGOLIN_API_KEY, use it
  if (CONFIG.pangolinApiKey) {
    const client = new PangolinClient();
    try {
      await client.listResources();
      return client;
    } catch (e) {
      console.warn(`⚠ pangolin: PANGOLIN_API_KEY returned ${(e as Error).message}; re-mint required`);
    }
  }

  // 2. If Pocket ID OIDC client_credentials are configured, mint a fresh API key
  if (process.env.POCKETID_PANGOLIN_CLIENT_ID && process.env.POCKETID_PANGOLIN_CLIENT_SECRET) {
    try {
      const newApiKey = await pocketIdLogin();
      // Write the new key to .env for next time
      const envPath = process.env.ENV_PATH ?? join(import.meta.dir, "../../../.env");
      if (existsSync(envPath)) {
        const original = readFileSync(envPath, "utf8");
        const updated = upsertEnvVar(original, "PANGOLIN_API_KEY", newApiKey);
        writeFileSync(envPath, updated);
        console.log("✓ pangolin: wrote new PANGOLIN_API_KEY to .env");
      }
      // Use the new key in-memory (don't reload env)
      process.env.PANGOLIN_API_KEY = newApiKey;
      const client = new PangolinClient();
      await client.listResources();  // verify
      return client;
    } catch (e) {
      console.warn(`⚠ pangolin: Pocket ID login failed: ${(e as Error).message}`);
    }
  }

  // 3. Give up with a clear error message
  throw new Error(
    "PANGOLIN_API_KEY required and no Pocket ID OIDC client configured.\n" +
      "  Fix option A: run `bun run iac:rotate-auth` to mint a fresh key (requires POCKETID_PANGOLIN_CLIENT_ID + POCKETID_PANGOLIN_CLIENT_SECRET in env).\n" +
      "  Fix option B: manually mint an API key via the Pangolin dashboard and write it to .env as PANGOLIN_API_KEY=...\n" +
      "  Fix option C: configure Pocket ID OIDC client per PANGOLIN-SETUP.md Manual Step 1, then re-run `bun run iac:rotate-auth`.",
  );
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

// ---------------------------------------------------------------------------
// Helper: upsertEnvVar (shared with rotate-auth.ts to keep the .env write logic DRY)
// ---------------------------------------------------------------------------
function upsertEnvVar(content: string, key: string, value: string): string {
  const escaped = value.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n");
  const line = `${key}="${escaped}"`;
  const regex = new RegExp(`^${key}=.*$`, "m");
  if (regex.test(content)) {
    return content.replace(regex, line);
  }
  return content + "\n" + line;
}

// node:fs + node:path imports (added here so this file is self-contained)
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
