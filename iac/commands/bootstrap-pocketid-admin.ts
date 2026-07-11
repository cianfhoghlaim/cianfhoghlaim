// bonneagar/iac/commands/bootstrap-pocketid-admin.ts — Interactive first-user + OIDC client bootstrap
//
// The canonical Pocket ID bootstrap flow (the user's immediate fix for the
// "passkeys don't work" issue). Orchestrates:
//   1. Check Pocket ID health (abort if down)
//   2. Check if any users exist (if yes → skip to OIDC client check)
//   3. Login as the admin (uses POCKETID_ADMIN_PASSWORD from .env or Infisical)
//   4. Enable signup (if not already)
//   5. Create a signup token for the operator's email
//   6. Print the signup URL (operator opens in browser, registers passkey)
//   7. Wait for the operator to confirm the first user is created
//   8. Disable signup (security)
//   9. Create the bons-iac OIDC client (for iac:rotate-auth)
//  10. Write the bons-iac client_id + client_secret to .env + Infisical
//  11. Audit record
//
// Usage:
//   bun run iac:bootstrap-pocketid-admin
//   bun run iac:bootstrap-pocketid-admin --email=ciansedai@cianfhoghlaim.ie --skip-passkey
//
// Spec: openspec/changes/2026-07-14-tightly-knit-auth-stack-v1
// =============================================================================

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import {
  pocketIdAdminLogin,
  pocketIdEnableSignup,
  pocketIdDisableSignup,
  pocketIdCreateSignupToken,
  pocketIdListUsers,
  pocketIdListOidcClients,
  pocketIdCreateOidcClient,
  pocketIdHealth,
} from "../auth-pocketid-admin.ts";

const ENV_PATH = join(import.meta.dir, "../../../.env");

interface BootstrapOptions {
  email: string;
  username: string;
  skipPasskey: boolean;  // for testing
  adminPassword: string;  // from env or Infisical
}

export async function bootstrapPocketIdAdmin(opts?: Partial<BootstrapOptions>) {
  const options: BootstrapOptions = {
    email: opts?.email ?? process.env.POCKETID_ADMIN_EMAIL ?? "ciansedai@cianfhoghlaim.ie",
    username: opts?.username ?? process.env.POCKETID_ADMIN_USERNAME ?? "ciansedai",
    skipPasskey: opts?.skipPasskey ?? false,
    adminPassword: opts?.adminPassword ?? process.env.POCKETID_ADMIN_PASSWORD ?? "",
  };

  logStep(`iac:bootstrap-pocketid-admin — for ${options.email}`);

  // 1. Health check
  const health = await pocketIdHealth();
  if (!health.healthy) {
    logError(`Pocket ID is not healthy: ${health.healthyDetail}`);
    log("  Run: bun run iac:bootstrap Phase 0 (deploys Pocket ID via Komodo)");
    process.exit(1);
  }
  logOk(`Pocket ID: v${health.version}, ${health.dbUsers} users, ${health.dbOidcClients} OIDC clients`);

  // 2. Check if any users exist
  if (health.dbUsers > 0) {
    logOk(`Pocket ID has ${health.dbUsers} users — skipping first-user bootstrap`);
    return await ensureBonsIacClient(options.adminPassword);
  }
  if (options.dbUsers === 0 && !options.adminPassword) {
    // This is the first-ever bootstrap; we need an admin password
    logError("Pocket ID has 0 users but no POCKETID_ADMIN_PASSWORD in env");
    log("  Set POCKETID_ADMIN_PASSWORD in ~/.env and re-run");
    log("  The password is used ONCE to create the first admin + bons-iac OIDC client");
    log("  After the bootstrap, the admin should rotate their password via Pocket ID UI");
    process.exit(1);
  }

  // 3. Login as the admin
  let adminCookie: string;
  try {
    const session = await pocketIdAdminLogin(options.username, options.adminPassword);
    adminCookie = session.cookie;
    logOk(`Logged in to Pocket ID as ${options.username}`);
  } catch (e) {
    logError(`Pocket ID admin login failed: ${(e as Error).message}`);
    log("  The password in POCKETID_ADMIN_PASSWORD may be wrong, or the admin user doesn't exist yet");
    log("  For a true first-user bootstrap, the user must register via the UI signup flow:");
    log("    1. Enable signup: docker exec pocket-id sqlite3 /app/data/pocket-id.db \"UPDATE app_config_variables SET value='true' WHERE key='signupEnabled';\"");
    log("    2. Open https://auth.cianfhoghlaim.ie/signup/setup in a browser");
    log("    3. Register Touch ID passkey for ciansedai");
    log("    4. Set POCKETID_ADMIN_PASSWORD (the password you set during signup)");
    log("    5. Re-run this command");
    process.exit(1);
  }

  // 4. Enable signup (idempotent)
  await pocketIdEnableSignup(adminCookie);
  logOk("signup enabled");

  // 5. Create a signup token
  const { url, expiresAt, token } = await pocketIdCreateSignupToken(adminCookie, {
    username: options.username,
    email: options.email,
    expiresIn: 3600,  // 1 hour
  });
  logOk(`signup token created (expires ${expiresAt})`);

  // 6. Print the URL + wait
  log("");
  log("╔════════════════════════════════════════════════════════════╗");
  log("║  ACTION REQUIRED — visit this URL in a browser:            ║");
  log("╠════════════════════════════════════════════════════════════╣");
  log(`║  ${url}`);
  log("╚════════════════════════════════════════════════════════════╝");
  log("");
  log("Steps:");
  log("  1. Open the URL above in a browser with Touch ID enabled");
  log("  2. Register your passkey (the browser will prompt for Touch ID)");
  log("  3. The page will redirect to https://auth.cianfhoghlaim.ie/home");
  log("  4. Press ENTER here to continue the bootstrap");
  log("");

  if (options.skipPasskey) {
    logWarn("--skip-passkey: skipping operator confirmation");
  } else {
    await waitForEnter("Press ENTER after registering the passkey...");
  }

  // 7. Verify the user was created
  const users = await pocketIdListUsers(adminCookie);
  const admin = users.find((u) => u.username === options.username);
  if (!admin) {
    logError(`User ${options.username} was not created — passkey registration may have failed`);
    log("  Re-run this command and try again");
    process.exit(1);
  }
  logOk(`User ${options.username} created (admin: ${admin.isAdmin})`);

  // 8. Disable signup (security)
  await pocketIdDisableSignup(adminCookie);
  logOk("signup disabled (security)");

  // 9. Create the bons-iac OIDC client
  await ensureBonsIacClient(options.adminPassword);
}

/**
 * Ensure the bons-iac OIDC client exists in Pocket ID. Idempotent.
 * Called from both bootstrap-pocketid-admin + iac:rotate-auth.
 */
export async function ensureBonsIacClient(adminPassword: string) {
  if (!adminPassword) {
    logWarn("No POCKETID_ADMIN_PASSWORD — skipping bons-iac OIDC client creation");
    log("  Set POCKETID_ADMIN_PASSWORD in ~/.env and re-run");
    return;
  }

  const health = await pocketIdHealth();
  if (health.dbUsers === 0) {
    logError("No users in Pocket ID — bootstrap the first user first");
    return;
  }

  // Login
  const session = await pocketIdAdminLogin("ciansedai", adminPassword);
  const adminCookie = session.cookie;

  // Check if bons-iac already exists
  const clients = await pocketIdListOidcClients(adminCookie);
  const existing = clients.find((c) => c.name === "bons-iac");
  if (existing) {
    logOk(`bons-iac OIDC client already exists (id=${existing.id})`);
    return;
  }

  // Create the bons-iac client
  const created = await pocketIdCreateOidcClient(adminCookie, {
    name: "bons-iac",
    redirectUris: ["https://pangolin.cianfhoghlaim.ie", "http://localhost:9120"],
    grantTypes: ["client_credentials"],
    scopes: ["openid", "profile", "email"],
    isPublic: false,
  });
  logOk(`bons-iac OIDC client created (id=${created.id})`);

  // Write the credentials to .env
  if (existsSync(ENV_PATH)) {
    const original = readFileSync(ENV_PATH, "utf8");
    const updated = upsertEnvVar(original, "POCKETID_CLIENT_ID", created.clientId);
    writeFileSync(ENV_PATH, upsertEnvVar(updated, "POCKETID_CLIENT_SECRET", created.clientSecret));
    logOk("wrote POCKETID_CLIENT_ID + POCKETID_CLIENT_SECRET to .env");
  }

  // Audit record
  const auditPath = `/tmp/pocketid-bootstrap-${new Date().toISOString().replace(/[:.]/g, "-")}.json`;
  const audit = {
    ts: new Date().toISOString(),
    action: "create-oidc-client",
    name: "bons-iac",
    clientId: created.clientId,
    redirectUris: ["https://pangolin.cianfhoghlaim.ie", "http://localhost:9120"],
    grantTypes: ["client_credentials"],
  };
  writeFileSync(auditPath, JSON.stringify(audit, null, 2));
  logOk(`audit record: ${auditPath}`);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function waitForEnter(prompt: string): Promise<void> {
  return new Promise((resolve) => {
    process.stdout.write(`${prompt}\n`);
    process.stdin.setRawMode?.(true);
    process.stdin.resume();
    process.stdin.once("data", (data) => {
      process.stdin.setRawMode?.(false);
      process.stdin.pause();
      // Consume the newline
      if (data.toString() !== "\n") process.stdin.once("data", () => resolve());
      else resolve();
    });
  });
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
