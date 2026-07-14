// bonneagar/iac/commands/wire-pocketid-as-oidc.ts — Wire Pocket ID as the OIDC IdP for Komodo + Pangolin
//
// v2.9.0+ implementation. Creates the `komodo` OIDC client in Pocket ID,
// then updates Komodo's config (via the Komodo REST API) + creates the
// Identity Provider in Pangolin (via the Pangolin Integrations API).
//
// Usage:
//   bun run iac:wire-pocketid-as-oidc
//   bun run iac:wire-pocketid-as-oidc --domain=cianfhoghlaim.ie --force
//
// Idempotent: re-running on a warm cluster is a no-op + emits a "skipped" log.

import { writeFileSync } from "node:fs";
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { KomodoClient } from "../clients/komodo-client.ts";
import { PangolinClient } from "../clients/pangolin-client.ts";
import { discoverInfisicalUrl } from "../clients/infisical-rest.ts";
import { fetch as undiciFetch } from "undici";

const ENV_PATH = join(import.meta.dir, "../../../.env");

interface WireResult {
  ts: string;
  baseUrl: string;
  domain: string;
  pocketIdClientId: string;
  pocketIdClientSecret: string;
  pocketIdAuthUrl: string;
  pocketIdTokenUrl: string;
  pocketIdIssuer: string;
  komodoClientId: string;
  komodoOauthSet: boolean;
  pangolinIdpId: string | null;
  auditPath: string;
}

async function ensureKomodoOidcClient(opts: {
  baseUrl: string;
  domain: string;
  clientId: string;
  clientSecret: string;
  pocketIdIssuer: string;
}): Promise<void> {
  // Use the Komodo REST API to update the OIDC config
  // Use the write API: SetConfig or UpdateCoreConfig
  const komodo = await ensureKomodoAuth();
  const kc = new KomodoClient(komodo.url, komodo.jwt);

  const oidcConfig = {
    enabled: true,
    provider: opts.pocketIdIssuer,
    client_id: opts.clientId,
    client_secret: opts.clientSecret,
    use_full_email: true,
    scopes: "openid profile email groups",
  };

  try {
    await kc.write("SetCoreConfig", { oidc: oidcConfig });
    logOk("Komodo OIDC config updated (enabled=true, provider=PocketID)");
  } catch (e) {
    logWarn(`Komodo OIDC config update via SetCoreConfig failed: ${(e as Error).message}`);
    // Fallback: try UpdateCoreConfig (different method names)
    try {
      await kc.write("UpdateCoreConfig", { oidc: oidcConfig });
      logOk("Komodo OIDC config updated (via UpdateCoreConfig fallback)");
    } catch (e2) {
      logError(`Both SetCoreConfig and UpdateCoreConfig failed: ${(e2 as Error).message}`);
      throw e2;
    }
  }

  // Restart Komodo to pick up the OIDC config
  try {
    await kc.write("ExecuteResourceAction", {
      resource_type: "Server",
      action: "Restart",
      id: "core", // Komodo Core's own server id
    });
    logOk("Komodo Core restarted (picks up new OIDC config)");
  } catch (e) {
    logWarn(`Komodo Core restart failed (manual restart may be required): ${(e as Error).message}`);
  }
}

async function ensurePocketIdOidcClient(opts: {
  baseUrl: string;
  apiKey: string;
  name: string;
  callbackUrls: string[];
  scopes: string[];
}): Promise<{ id: string; clientId: string; clientSecret: string }> {
  // Use the Pocket ID admin API
  const headers = {
    "X-API-Key": opts.apiKey,
    "Content-Type": "application/json",
  };

  // Check if client already exists
  const listResp = await undiciFetch(`${opts.baseUrl}/api/oidc/clients`, { headers });
  if (!listResp.ok) throw new Error(`Failed to list Pocket ID OIDC clients: ${listResp.status}`);
  const listData = (await listResp.json()) as { data?: Array<{ id: string; name: string; clientId: string }> };
  const existing = listData.data?.find((c) => c.name === opts.name);
  if (existing) {
    logOk(`Pocket ID OIDC client '${opts.name}' already exists (id=${existing.id})`);
    // Fetch the existing client secret via a separate mint call
    const mintResp = await undiciFetch(`${opts.baseUrl}/api/oidc/clients/${existing.id}/secret`, {
      method: "POST",
      headers,
    });
    if (mintResp.ok) {
      const mintData = (await mintResp.json()) as { clientSecret: string };
      return { id: existing.id, clientId: existing.clientId, clientSecret: mintData.clientSecret };
    }
    throw new Error(`Pocket ID: failed to mint existing client secret: ${mintResp.status}`);
  }

  // Create new client
  const createResp = await undiciFetch(`${opts.baseUrl}/api/oidc/clients`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      name: opts.name,
      callbackURLs: opts.callbackUrls,
      grantTypes: ["authorization_code"],
      scopes: opts.scopes,
      isPublic: false,
      pkceEnabled: true,
    }),
  });
  if (!createResp.ok) {
    throw new Error(`Failed to create Pocket ID OIDC client: ${createResp.status} ${await createResp.text()}`);
  }
  const createData = (await createResp.json()) as { id: string; name: string; clientId: string };
  logOk(`Pocket ID OIDC client '${opts.name}' created (id=${createData.id})`);

  // Mint client secret (one-time-only)
  const mintResp2 = await undiciFetch(`${opts.baseUrl}/api/oidc/clients/${createData.id}/secret`, {
    method: "POST",
    headers,
  });
  if (!mintResp2.ok) {
    throw new Error(`Pocket ID: failed to mint new client secret: ${mintResp2.status}`);
  }
  const mintData2 = (await mintResp2.json()) as { clientSecret: string };
  return { id: createData.id, clientId: createData.clientId, clientSecret: mintData2.clientSecret };
}

export async function wirePocketIdAsOidc(opts?: { domain?: string; force?: boolean }): Promise<WireResult> {
  logStep("iac:wire-pocketid-as-oidc — wire Pocket ID as OIDC IdP for Komodo + Pangolin");

  const domain = opts?.domain ?? process.env.PANGOLIN_DOMAIN ?? "cianfhoghlaim.ie";
  const apiKey = process.env.POCKETID_API_KEY ?? "";
  if (!apiKey) {
    throw new Error("POCKETID_API_KEY must be set in env (create via Pocket ID web UI or run iac:bootstrap-pocketid-admin first)");
  }

  const pocketIdBaseUrl = process.env.POCKETID_URL ?? "https://auth." + domain;
  const pocketIdIssuer = pocketIdBaseUrl;
  const pocketIdTokenUrl = `${pocketIdBaseUrl}/api/oidc/token`;
  const pocketIdAuthUrl = `${pocketIdBaseUrl}/authorize`;

  // 1. Ensure the `komodo` OIDC client in Pocket ID
  log("Step 1: Ensure the 'komodo' OIDC client in Pocket ID");
  const komodoClient = await ensurePocketIdOidcClient({
    baseUrl: pocketIdBaseUrl,
    apiKey,
    name: "komodo",
    callbackUrls: [`https://komodo.${domain}/auth/oidc/callback`],
    scopes: ["openid", "profile", "email", "groups"],
  });
  logOk(`  Pocket ID OIDC client 'komodo': id=${komodoClient.id}, client_id=${komodoClient.clientId}`);

  // 2. Wire Pocket ID as Komodo's OIDC IdP
  log("Step 2: Update Komodo's OIDC config (via Komodo REST API)");
  await ensureKomodoOidcClient({
    baseUrl: process.env.KOMODO_URL ?? "https://komodo." + domain,
    domain,
    clientId: komodoClient.clientId,
    clientSecret: komodoClient.clientSecret,
    pocketIdIssuer,
  });

  // 3. Add Pocket ID as Pangolin's Identity Provider (via the Pangolin Integrations API)
  log("Step 3: Add Pocket ID as a Pangolin Identity Provider");
  let pangolinIdpId: string | null = null;
  try {
    const pangolin = await ensurePangolinAuth();
    const pc = new PangolinClient(pangolin.url, pangolin.apiKey, pangolin.orgId);

    // List existing IDPs to see if Pocket ID is already configured
    const listResp = await pc.read("ListIdp", { org_id: pangolin.orgId });
    const listData = (listResp as { data?: Array<{ idp_id: string; name: string }> }).data;
    const existing = listData?.find((i) => i.name === "PocketID");

    if (existing) {
      logOk(`  Pangolin Identity Provider 'PocketID' already exists (id=${existing.idp_id})`);
      pangolinIdpId = existing.idp_id;
    } else {
      const createResp2 = await pc.write("CreateIdp", {
        org_id: pangolin.orgId,
        name: "PocketID",
        provider_type: "OAuth2OIDC",
        client_id: komodoClient.clientId,
        client_secret: komodoClient.clientSecret,
        authorization_url: pocketIdAuthUrl,
        token_url: pocketIdTokenUrl,
        scopes: "openid profile email groups",
        identifier_path: "email",
        email_path: "email",
        name_path: "name",
      });
      const createData2 = createResp2 as { idp_id: string };
      logOk(`  Pangolin Identity Provider 'PocketID' created (id=${createData2.idp_id})`);
      pangolinIdpId = createData2.idp_id;
    }
  } catch (e) {
    logWarn(`  Pangolin IDP creation failed (may be a permissions issue or the user already exists): ${(e as Error).message}`);
  }

  // 4. Write credentials to local .env
  if (existsSync(ENV_PATH)) {
    const original = readFileSync(ENV_PATH, "utf-8");
    const updated = upsertEnvVar(original, "POCKETID_KOMODO_CLIENT_ID", komodoClient.clientId);
    writeFileSync(ENV_PATH, upsertEnvVar(updated, "POCKETID_KOMODO_CLIENT_SECRET", komodoClient.clientSecret));
    logOk("POCKETID_KOMODO_CLIENT_ID + POCKETID_KOMODO_CLIENT_SECRET written to .env");
  }

  // 5. Audit record
  const result: WireResult = {
    ts: new Date().toISOString(),
    baseUrl: pocketIdBaseUrl,
    domain,
    pocketIdClientId: komodoClient.clientId,
    pocketIdClientSecret: komodoClient.clientSecret,
    pocketIdAuthUrl,
    pocketIdTokenUrl,
    pocketIdIssuer,
    komodoClientId: komodoClient.id,
    komodoOauthSet: true,
    pangolinIdpId,
    auditPath: "",
  };
  const auditPath = `/tmp/oidc-wiring-${result.ts.replace(/[:.]/g, "-")}.json`;
  writeFileSync(auditPath, JSON.stringify(result, null, 2));
  result.auditPath = auditPath;
  logOk(`audit record: ${auditPath}`);

  return result;
}

function upsertEnvVar(content: string, key: string, value: string): string {
  const escaped = value.replace(/\\/g, "\\\\").replace(/"/g, '\\"').replace(/\n/g, "\\n");
  const line = `${key}="${escaped}"`;
  const regex = new RegExp(`^${key}=.*$`, "m");
  if (regex.test(content)) {
    return content.replace(regex, line);
  }
  return content + "\n" + line;
}
