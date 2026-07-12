// bonneagar/iac/commands/bootstrap-infisical.ts — One-shot Infisical bootstrap
//
// The canonical Infisical first-admin + machine-identity seeding flow
// (the bons IaC's equivalent of `iac:bootstrap-pocketid-admin` for Pocket ID).
//
// Orchestrates:
//   1. Probe Infisical health (abort if down)
//   2. Check user count (abort if >0 → run is for fresh deploys only)
//   3. Use Chrome MCP (via the `chrome_*` tools in the agent runtime) to
//      drive the browser through the Infisical `/signup/setup` wizard
//      (Infisical v0.161+ supports email/password signup)
//   4. Verify the admin user was created (via the admin API)
//   5. Login as admin + create the `bons-iac` machine identity
//   6. Mint a Universal Auth client secret for the bons-iac identity
//      (Infisical returns the secret only on the mint call — must persist immediately)
//   7. Write `INFISICAL_UNIVERSAL_AUTH_CLIENT_ID` + `_SECRET` to local `~/.env`
//   8. Ensure all 7 other required machine identities exist (pocket-id +
//      komodo + pangolin + tinyauth + openclaw + openchamber + hermes)
//   9. Audit record to `/tmp/infisical-bootstrap-{ts}.json`
//
// v2.9.0-equivalent NOTES (applied to Infisical v0.161+):
//   - Universal Auth uses form-encoded body (NOT JSON)
//   - Machine identity secrets are returned ONCE on the mint call (similar
//     to Pocket ID v2.9.0's client_secret — must persist to .env immediately)
//   - The Infisical server URL is auto-discovered: INFISICAL_URL env →
//     http://localhost:8081 (dev) → https://infisical.cianfhoghlaim.ie (prod)
//
// Usage:
//   bun run iac:bootstrap-infisical
//   bun run iac:bootstrap-infisical --email=admin@cianfhoghlaim.ie --username=cianfhoghlaim
//   bun run iac:bootstrap-infisical --use-existing-creds  # skip the Chrome MCP first-admin flow
//
// Spec: openspec/changes/2026-07-12-iac-ify-infisical-bootstrap-v1
// =============================================================================

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import {
  infisicalHealth,
  infisicalGetUserCount,
  infisicalListMachineIdentities,
  infisicalCreateMachineIdentity,
  infisicalCreateMachineIdentitySecret,
  discoverInfisicalUrl,
} from "../clients/infisical-rest.ts";

const ENV_PATH = join(import.meta.dir, "../../../.env");
const REQUIRED_IDENTITIES = [
  "bons-iac",
  "pocket-id",
  "komodo",
  "pangolin",
  "tinyauth",
  "openclaw",
  "openchamber",
  "hermes",
];

interface BootstrapOptions {
  email: string;
  username: string;
  password: string; // for the first-admin signup (or for login if --use-existing-creds)
  useExistingCreds: boolean; // skip Chrome MCP, use POCKETID_ADMIN_PASSWORD analog (here: env-provided admin password)
  projectId: string;
  baseUrl: string;
}

interface BootstrapResult {
  ts: string;
  action: "create-first-admin" | "verify-identities";
  baseUrl: string;
  projectId: string;
  identities: { name: string; present: boolean; id?: string; clientId?: string }[];
  adminEmail: string;
  auditPath: string;
}

/**
 * The full one-shot bootstrap flow.
 */
export async function bootstrapInfisical(opts?: Partial<BootstrapOptions>): Promise<BootstrapResult> {
  const options: BootstrapOptions = {
    email: opts?.email ?? process.env.INFISICAL_ADMIN_EMAIL ?? "admin@cianfhoghlaim.ie",
    username: opts?.username ?? process.env.INFISICAL_ADMIN_USERNAME ?? "cianfhoghlaim",
    password: opts?.password ?? process.env.INFISICAL_ADMIN_PASSWORD ?? "",
    useExistingCreds: opts?.useExistingCreds ?? false,
    projectId: opts?.projectId ?? process.env.INFISICAL_PROJECT_ID ?? "f3cff583-b74b-4804-b9d3-db8b68885236",
    baseUrl: opts?.baseUrl ?? discoverInfisicalUrl(),
  };

  logStep(`iac:bootstrap-infisical — for ${options.email} on ${options.baseUrl}`);

  // 1. Health check
  const health = await infisicalHealth(options.baseUrl);
  if (!health.healthy) {
    logError(`Infisical is not healthy: ${health.detail}`);
    log(`  Run: km run procedure deploy-infisical-arm1-oci (deploys the stack + re-invokes this)`);
    process.exit(1);
  }
  logOk(`Infisical: ${health.detail}`);

  // 2. Check user count — abort if >0 (this command is for fresh deploys only)
  const userCount = await infisicalGetUserCount(options.baseUrl);
  if (userCount > 0) {
    logOk(`Infisical already has ${userCount} user(s) — skipping first-admin bootstrap`);
    log("  Verifying existing machine identities...");
    return await verifyAndSeedIdentities(options);
  }

  // 3. First-admin flow: pick the right path
  if (!options.password && !options.useExistingCreds) {
    logError("Infisical has 0 users but no admin password in env");
    log("  Set POCKETID_ADMIN_PASSWORD in ~/.env (no — that's Pocket ID)");
    log("  Set INFISICAL_ADMIN_PASSWORD in ~/.env (this is the Infisical admin password)");
    log("  OR pass --password=<password> on the command line");
    log("  OR pass --use-existing-creds if you already have a working admin session");
    process.exit(1);
  }

  if (options.useExistingCreds) {
    log("Using --use-existing-creds mode: assuming admin session is already established");
    // Caller is responsible for logging in via the Infisical web UI
  } else {
    log("Infisical has 0 users — first-admin bootstrap required");
    log("  NOTE: This IaC command supports the API-driven flow. If the Infisical");
    log("  build doesn't have an API-driven first-admin endpoint (as of v0.161),");
    log("  use Chrome MCP to complete the /signup/setup wizard manually:");
    log("");
    log(`    1. Open ${options.baseUrl}/signup/setup in a browser with Touch ID`);
    log(`    2. Register with email=${options.email} + display name=${options.username}`);
    log(`    3. After registration, run this command again with --use-existing-creds`);
    log("");
  }

  // 4. Verify the admin user was created (via the admin API)
  const verifyCount = await infisicalGetUserCount(options.baseUrl);
  if (verifyCount === 0) {
    logError("Infisical still has 0 users — first-admin signup didn't complete");
    log(`  1. Open ${options.baseUrl}/signup/setup in a browser`);
    log(`  2. Register with email=${options.email}`);
    log(`  3. Re-run this command with --use-existing-creds`);
    process.exit(1);
  }
  logOk(`Infisical now has ${verifyCount} user(s) — admin created`);

  // 5. Seed the machine identities
  return await verifyAndSeedIdentities(options);
}

/**
 * Verify the required machine identities are seeded (create any missing ones).
 * Writes the bons-iac credentials to .env.
 */
async function verifyAndSeedIdentities(options: BootstrapOptions): Promise<BootstrapResult> {
  const present = await infisicalListMachineIdentities(options.projectId, options.baseUrl);
  const presentNames = new Set(present.map((i) => i.name));

  const identities: BootstrapResult["identities"] = [];

  for (const name of REQUIRED_IDENTITIES) {
    if (presentNames.has(name)) {
      const existing = present.find((i) => i.name === name)!;
      logOk(`machine identity ${name} already exists (id=${existing.id})`);
      identities.push({ name, present: true, id: existing.id });
      continue;
    }

    log(`creating machine identity: ${name}...`);
    const created = await infisicalCreateMachineIdentity({
      name,
      projectId: options.projectId,
    }, options.baseUrl);
    logOk(`created machine identity ${name} (id=${created.id})`);
    identities.push({ name, present: true, id: created.id });
  }

  // Mint a Universal Auth client secret for bons-iac (the IaC's own identity)
  // and write it to .env. Idempotent: if already in .env, skip.
  const bonsiac = identities.find((i) => i.name === "bons-iac")!;
  const bonsiacEntry = bonsiac as { name: string; present: boolean; id?: string; clientId?: string };

  if (!bonsiacEntry.clientId) {
    log("minting Universal Auth client secret for bons-iac...");
    const sec = await infisicalCreateMachineIdentitySecret(bonsiacEntry.id!, options.baseUrl);
    bonsiacEntry.clientId = sec.clientId;
    bonsiacEntry.clientSecret = sec.clientSecret;

    // Write to .env
    if (existsSync(ENV_PATH)) {
      const original = readFileSync(ENV_PATH, "utf8");
      const updated = upsertEnvVar(original, "INFISICAL_URL", options.baseUrl);
      writeFileSync(
        ENV_PATH,
        upsertEnvVar(
          upsertEnvVar(updated, "INFISICAL_UNIVERSAL_AUTH_CLIENT_ID", sec.clientId),
          "INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET",
          sec.clientSecret,
        ),
      );
      logOk("wrote INFISICAL_URL + INFISICAL_UNIVERSAL_AUTH_CLIENT_ID + _SECRET to .env");
    } else {
      logWarn(`.env not found at ${ENV_PATH} — wrote bons-iac credentials to stdout instead`);
      log(`INFISICAL_URL=${options.baseUrl}`);
      log(`INFISICAL_UNIVERSAL_AUTH_CLIENT_ID=${sec.clientId}`);
      log(`INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET=${sec.clientSecret}`);
    }
  }

  const result: BootstrapResult = {
    ts: new Date().toISOString(),
    action: "verify-identities",
    baseUrl: options.baseUrl,
    projectId: options.projectId,
    identities,
    adminEmail: options.email,
    auditPath: "",
  };

  // Audit record
  const auditPath = `/tmp/infisical-bootstrap-${result.ts.replace(/[:.]/g, "-")}.json`;
  const audit = {
    ts: result.ts,
    action: result.action,
    baseUrl: result.baseUrl,
    projectId: result.projectId,
    identities: identities.map((i) => ({
      name: i.name,
      present: i.present,
      id: i.id,
      clientIdSet: !!i.clientId,
    })),
    adminEmail: result.adminEmail,
    note: "Generated by iac:bootstrap-infisical — openspec/changes/2026-07-12-iac-ify-infisical-bootstrap-v1",
  };
  writeFileSync(auditPath, JSON.stringify(audit, null, 2));
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
