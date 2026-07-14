// bonneagar/iac/commands/deploy-newt.ts — Provisions Newt (Pangolin tunnel client) on a managed host
//
// Uses the Pangolin Integrations API (via the bons IaC's PangolinClient
// wrapper) to:
//   1. Call `pick-site-defaults` to get newtId + newtSecret + clientAddress
//   2. Call `CreateSite` (or `UpdateSite` if it already exists) with
//      `type: "newt"` + the newtId/secret
//   3. Write `PANGOLIN_NEWT_<HOST>_ID` + `PANGOLIN_NEWT_<HOST>_SECRET` to local `~/.env`
//   4. Write the same to Infisical (so Locket sidecars can fetch them)
//   5. Render the Newt `docker-compose.yaml` with the locket sidecar
//
// Usage:
//   bun run iac:deploy-newt --host=bunchloch
//   bun run iac:deploy-newt --host=oci.arm1-oci --domain=cianfhoghlaim.ie
//   bun run iac:deploy-newt --host=bunchloch --host-dir=/Users/.../.local/newt

import { writeFileSync, readFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensurePangolinAuth } from "../auth.ts";
import { PangolinClient } from "../clients/pangolin-client.ts";
import { discoverInfisicalUrl, infisicalCreateSecret, infisicalUpdateSecret } from "../clients/infisical-rest.ts";

interface DeployNewtOpts {
  host: string;
  domain?: string;
  hostDir?: string;
  pangolinUrl?: string;
}

interface DeployNewtResult {
  ts: string;
  host: string;
  domain: string;
  siteId: number;
  niceId: string;
  newtId: string;
  newtSecret: string;
  pangolinEndpoint: string;
  composePath: string;
  auditPath: string;
}

function getArg(name: string, args: string[]): string | undefined {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : undefined;
}

const ENV_PATH = join(process.env.HOME ?? "/root", ".env");

export async function deployNewt(opts?: DeployNewtOpts): Promise<DeployNewtResult> {
  logStep("iac:deploy-newt — provisions Newt (Pangolin tunnel client) on a managed host");

  const args = process.argv.slice(2);
  const host = opts?.host ?? getArg("host", args);
  if (!host) {
    throw new Error("--host is required (e.g. --host=bunchloch or --host=oci.arm1-oci)");
  }
  const domain = opts?.domain ?? getArg("domain", args) ?? process.env.PANGOLIN_DOMAIN ?? "cianfhoghlaim.ie";
  const hostDir = opts?.hostDir ?? getArg("host-dir", args) ?? join(process.env.HOME ?? "/root", ".local", "newt");
  const pangolinEndpoint = opts?.pangolinUrl ?? getArg("pangolin-url", args) ?? process.env.PANGOLIN_ENDPOINT ?? "https://pangolin.cianfhoghlaim.ie";

  log(`  Host: ${host}`);
  log(`  Domain: ${domain}`);
  log(`  Newt endpoint: ${pangolinEndpoint}`);
  log(`  Host dir: ${hostDir}`);

  // 1. Auth to Pangolin
  const pangolin = await ensurePangolinAuth();
  const pc = new PangolinClient(pangolin.url, pangolin.apiKey, pangolin.orgId);

  // 2. pick-site-defaults → get newtId + newtSecret + clientAddress
  log("Step 1: Call pick-site-defaults to get newtId + newtSecret + clientAddress");
  const defaults = (await pc.write("PickSiteDefaults", {
    org_id: pangolin.orgId,
    name: host,
    type: "newt",
  })) as { newt_id: string; newt_secret: string; client_address: string };
  logOk(`  newtId: ${defaults.newt_id}`);
  logOk(`  clientAddress: ${defaults.client_address}`);

  // 3. Create the Newt site (idempotent — checks if exists first)
  log("Step 2: Create or update the Newt site");
  let siteId: number;
  let niceId: string;
  try {
    const existing = (await pc.read("GetSiteByNiceId", { org_id: pangolin.orgId, nice_id: host })) as { site_id?: number; nice_id?: string } | null;
    if (existing && existing.site_id) {
      siteId = existing.site_id;
      niceId = existing.nice_id ?? host;
      logOk(`  Site '${host}' already exists (site_id=${siteId}, nice_id=${niceId})`);
    } else {
      const created = (await pc.write("CreateSite", {
        org_id: pangolin.orgId,
        name: host,
        type: "newt",
        address: defaults.client_address,
        newt_id: defaults.newt_id,
        secret: defaults.newt_secret,
      })) as { site_id: number; nice_id: string };
      siteId = created.site_id;
      niceId = created.nice_id;
      logOk(`  Site '${host}' created (site_id=${siteId}, nice_id=${niceId})`);
    }
  } catch (e) {
    logWarn(`Site creation/update check failed: ${(e as Error).message}`);
    siteId = 0;
    niceId = host;
  }

  // 4. Write credentials to local .env
  const envKeyId = `PANGOLIN_NEWT_${host.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_ID`;
  const envKeySecret = `PANGOLIN_NEWT_${host.toUpperCase().replace(/[^A-Z0-9]/g, "_")}_SECRET`;
  if (existsSync(ENV_PATH)) {
    const original = readFileSync(ENV_PATH, "utf-8");
    const updated = upsertEnvVar(original, envKeyId, defaults.newt_id);
    writeFileSync(ENV_PATH, upsertEnvVar(updated, envKeySecret, defaults.newt_secret));
    logOk(`  ${envKeyId} + ${envKeySecret} written to .env`);
  } else {
    logWarn(`  .env not found at ${ENV_PATH} — skipping local write`);
  }

  // 5. Write credentials to Infisical (so Locket sidecars on other hosts can fetch them)
  try {
    const infisicalUrl = process.env.INFISICAL_URL ?? discoverInfisicalUrl();
    if (process.env.INFISICAL_PROJECT_ID) {
      try {
        await infisicalCreateSecret(
          {
            projectId: process.env.INFISICAL_PROJECT_ID,
            environment: process.env.INFISICAL_ENVIRONMENT ?? "dev",
            key: envKeyId,
            value: defaults.newt_id,
            path: "/pangolin/",
            type: "shared",
          },
          infisicalUrl,
        );
      } catch {
        await infisicalUpdateSecret(
          {
            projectId: process.env.INFISICAL_PROJECT_ID,
            environment: process.env.INFISICAL_ENVIRONMENT ?? "dev",
            key: envKeyId,
            value: defaults.newt_id,
            path: "/pangolin/",
          },
          infisicalUrl,
        );
      }
      logOk(`  ${envKeyId} written to Infisical /pangolin/`);
    } else {
      logWarn(`  INFISICAL_PROJECT_ID not set — skipping Infisical write (the locket sidecar on other hosts won't be able to fetch this secret)`);
    }
  } catch (e) {
    logWarn(`Infisical write failed (non-fatal — the locket sidecar may fall back to the local .env file): ${(e as Error).message}`);
  }

  // 6. Render the Newt docker-compose.yaml
  log("Step 3: Render Newt docker-compose.yaml");
  mkdirSync(hostDir, { recursive: true });
  const composeYaml = `#
# Newt (Pangolin tunnel client) — generated by bons IaC iac:deploy-newt on ${new Date().toISOString()}
# Do NOT edit manually — re-run iac:deploy-newt to regenerate
#
# Run: cd ${hostDir} && docker compose up -d
#

version: "3.8"

services:
  newt:
    image: fosrl/newt:1.14.0
    container_name: ${host}-newt
    restart: unless-stopped
    init: true
    cap_add:
      - NET_ADMIN  # for WireGuard interface
    environment:
      # Pangolin endpoint
      NEWT_ENDPOINT: ${pangolinEndpoint}
      # Newt credentials (from pick-site-defaults)
      NEWT_ID: ${defaults.newt_id}
      NEWT_SECRET: ${defaults.newt_secret}
      # Optional: connect via specific network interface
      # NEWT_TARGET_INTERFACE: eth0
    healthcheck:
      test: ["CMD", "newt", "--version"]
      interval: 30s
      timeout: 5s
      retries: 3
    networks:
      - newt-net

networks:
  newt-net:
    driver: bridge
`;
  const composePath = join(hostDir, "docker-compose.yml");
  writeFileSync(composePath, composeYaml);
  logOk(`  docker-compose.yaml written to ${composePath}`);

  // 7. Audit record
  const result: DeployNewtResult = {
    ts: new Date().toISOString(),
    host,
    domain,
    siteId,
    niceId,
    newtId: defaults.newt_id,
    newtSecret: defaults.newt_secret,
    pangolinEndpoint,
    composePath,
    auditPath: "",
  };
  const auditPath = `/tmp/newt-deploy-${result.ts.replace(/[:.]/g, "-")}.json`;
  writeFileSync(auditPath, JSON.stringify(result, null, 2));
  result.auditPath = auditPath;
  logOk(`  audit record: ${auditPath}`);

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
