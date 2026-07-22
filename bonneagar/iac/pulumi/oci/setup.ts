#!/usr/bin/env bun
/**
 * Setup script for OCI Infrastructure deployment
 *
 * This script:
 * 1. Saves Cloudflare credentials to Infisical
 * 2. Saves OCI server info to Infisical
 * 3. Updates DNS records via Pulumi
 *
 * Usage:
 *   bun run setup.ts save-cloudflare --token <token> --zone-id <zone-id>
 *   bun run setup.ts save-server --ip <ip>
 *   bun run setup.ts update-dns
 *   bun run setup.ts show
 *
 * v2.9.0+: Uses iac/clients/infisical-rest.ts (direct REST) instead of the
 * buggy @infisical/sdk v5.0.2. The REST client uses form-encoded body
 * for /api/v1/auth/universal-auth/login (the SDK was sending JSON, which
 * the server rejects).
 */

import {
  infisicalCreateSecret,
  infisicalGetSecret,
  discoverInfisicalUrl,
} from "../clients/infisical-rest.ts";

const CONFIG = {
  // Infisical
  infisicalClientId: process.env.INFISICAL_CLIENT_ID ?? "",
  infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET ?? "",
  infisicalProjectId: process.env.INFISICAL_PROJECT_ID ?? "",
  infisicalEnvironment: process.env.INFISICAL_ENVIRONMENT ?? "prod",
  infisicalUrl: process.env.INFISICAL_URL ?? discoverInfisicalUrl(),
  // Cloudflare
  cloudflareDomain: "cianfhoghlaim.ie",
};

/**
 * Save Cloudflare credentials to Infisical
 */
async function saveCloudflareCredentials(apiToken: string, zoneId: string): Promise<void> {
  console.log("Saving Cloudflare credentials to Infisical...");

  const secrets = [
    { name: "CLOUDFLARE_API_TOKEN", value: apiToken },
    { name: "CLOUDFLARE_ZONE_ID", value: zoneId },
    { name: "CLOUDFLARE_DOMAIN", value: CONFIG.cloudflareDomain },
  ];

  for (const secret of secrets) {
    // Idempotent: try create, fall back to update on 404/409
    try {
      await infisicalCreateSecret(
        {
          projectId: CONFIG.infisicalProjectId,
          environment: CONFIG.infisicalEnvironment,
          key: secret.name,
          value: secret.value,
          path: "/",
          type: "shared",
        },
        CONFIG.infisicalUrl,
      );
    } catch (e) {
      // 404 = "not found" should not happen on create, but 409 "already exists"
      // means we need to update instead. Use update path either way.
      const { infisicalUpdateSecret } = await import("../clients/infisical-rest.ts");
      await infisicalUpdateSecret(
        {
          projectId: CONFIG.infisicalProjectId,
          environment: CONFIG.infisicalEnvironment,
          key: secret.name,
          value: secret.value,
          path: "/",
        },
        CONFIG.infisicalUrl,
      );
    }
  }

  console.log("\nCloudflare credentials saved successfully!");
  console.log(`  Domain: ${CONFIG.cloudflareDomain}`);
  console.log(`  Zone ID: ${zoneId}`);
}

/**
 * Save server info to Infisical
 */
async function saveServerInfo(ip: string, user: string = "ubuntu"): Promise<void> {
  console.log("Saving server info to Infisical...");

  const secretsToSave = [
    { name: "SERVER_PUBLIC_IP", value: ip },
    { name: "SERVER_USER", value: user },
    { name: "SERVER_HOSTNAME", value: "arm1.oci" },
  ];

  for (const secret of secretsToSave) {
    try {
      await infisicalCreateSecret(
        {
          projectId: CONFIG.infisicalProjectId,
          environment: CONFIG.infisicalEnvironment,
          key: secret.name,
          value: secret.value,
          path: "/",
          type: "shared",
        },
        CONFIG.infisicalUrl,
      );
    } catch {
      const { infisicalUpdateSecret } = await import("../clients/infisical-rest.ts");
      await infisicalUpdateSecret(
        {
          projectId: CONFIG.infisicalProjectId,
          environment: CONFIG.infisicalEnvironment,
          key: secret.name,
          value: secret.value,
          path: "/",
        },
        CONFIG.infisicalUrl,
      );
    }
  }

  console.log("\nServer info saved successfully!");
  console.log(`  IP: ${ip}`);
  console.log(`  User: ${user}`);
}

/**
 * Get Cloudflare credentials from Infisical
 */
async function getCloudflareCredentials(): Promise<{ apiToken: string; zoneId: string }> {
  const apiTokenSecret = await infisicalGetSecret(
    {
      secretName: "CLOUDFLARE_API_TOKEN",
      projectId: CONFIG.infisicalProjectId,
      environment: CONFIG.infisicalEnvironment,
      secretPath: "/",
    },
    CONFIG.infisicalUrl,
  );
  if (!apiTokenSecret) throw new Error("CLOUDFLARE_API_TOKEN not found in Infisical");

  const zoneIdSecret = await infisicalGetSecret(
    {
      secretName: "CLOUDFLARE_ZONE_ID",
      projectId: CONFIG.infisicalProjectId,
      environment: CONFIG.infisicalEnvironment,
      secretPath: "/",
    },
    CONFIG.infisicalUrl,
  );
  if (!zoneIdSecret) throw new Error("CLOUDFLARE_ZONE_ID not found in Infisical");

  return { apiToken: apiTokenSecret.value, zoneId: zoneIdSecret.value };
}

/**
 * Update DNS records using Pulumi
 */
async function updateDns(): Promise<void> {
  console.log("Updating DNS records...");

  // Get credentials from Infisical
  const { apiToken, zoneId } = await getCloudflareCredentials();

  // Set environment variables for Pulumi
  process.env.CLOUDFLARE_API_TOKEN = apiToken;
  process.env.CLOUDFLARE_ZONE_ID = zoneId;

  console.log(`  Cloudflare Zone ID: ${zoneId}`);
  console.log("  Running Pulumi to update DNS...");

  // Import and run the deploy up command
  const { execSync } = await import("child_process");
  execSync("bun run up", {
    cwd: __dirname,
    stdio: "inherit",
    env: {
      ...process.env,
      CLOUDFLARE_API_TOKEN: apiToken,
      CLOUDFLARE_ZONE_ID: zoneId,
    },
  });
}

/**
 * Show current configuration from Infisical
 */
async function showConfig(): Promise<void> {
  console.log("Current configuration from Infisical:\n");

  // Cloudflare
  const cfApi = await infisicalGetSecret(
    { secretName: "CLOUDFLARE_API_TOKEN", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" },
    CONFIG.infisicalUrl,
  );
  const cfZone = await infisicalGetSecret(
    { secretName: "CLOUDFLARE_ZONE_ID", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" },
    CONFIG.infisicalUrl,
  );
  const cfDomain = await infisicalGetSecret(
    { secretName: "CLOUDFLARE_DOMAIN", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" },
    CONFIG.infisicalUrl,
  );

  if (cfApi && cfZone && cfDomain) {
    console.log("Cloudflare:");
    console.log(`  api_token: ${cfApi.value.slice(0, 10)}...`);
    console.log(`  zone_id: ${cfZone.value}`);
    console.log(`  domain: ${cfDomain.value}`);
  } else {
    console.log("Cloudflare: Not configured");
  }

  console.log();

  // Server
  const serverIp = await infisicalGetSecret(
    { secretName: "SERVER_PUBLIC_IP", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" },
    CONFIG.infisicalUrl,
  );
  const serverUser = await infisicalGetSecret(
    { secretName: "SERVER_USER", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" },
    CONFIG.infisicalUrl,
  );
  const serverHost = await infisicalGetSecret(
    { secretName: "SERVER_HOSTNAME", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" },
    CONFIG.infisicalUrl,
  );

  if (serverIp && serverUser && serverHost) {
    console.log("Server (arm1.oci):");
    console.log(`  ip: ${serverIp.value}`);
    console.log(`  user: ${serverUser.value}`);
    console.log(`  hostname: ${serverHost.value}`);
  } else {
    console.log("Server: Not configured");
  }
}

// CLI handling
const command = process.argv[2];
const args = process.argv.slice(3);

function getArg(name: string): string | undefined {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : undefined;
}

async function main() {
  if (!CONFIG.infisicalClientId || !CONFIG.infisicalClientSecret) {
    throw new Error(
      "INFISICAL_CLIENT_ID and INFISICAL_CLIENT_SECRET must be set in environment",
    );
  }
  if (!CONFIG.infisicalProjectId) {
    throw new Error("INFISICAL_PROJECT_ID must be set in environment");
  }

  switch (command) {
    case "save-cloudflare": {
      const token = getArg("token");
      const zoneId = getArg("zone-id");
      if (!token || !zoneId) {
        console.error("Usage: setup.ts save-cloudflare --token <token> --zone-id <zone-id>");
        process.exit(1);
      }
      await saveCloudflareCredentials(token, zoneId);
      break;
    }

    case "save-server": {
      const ip = getArg("ip");
      const user = getArg("user") ?? "ubuntu";
      if (!ip) {
        console.error("Usage: setup.ts save-server --ip <ip> [--user <user>]");
        process.exit(1);
      }
      await saveServerInfo(ip, user);
      break;
    }

    case "update-dns": {
      await updateDns();
      break;
    }

    case "show": {
      await showConfig();
      break;
    }

    default:
      console.log("OCI Infrastructure Setup Script\n");
      console.log("Usage: bun run setup.ts <command>\n");
      console.log("Commands:");
      console.log("  save-cloudflare --token <token> --zone-id <zone-id>  Save Cloudflare credentials");
      console.log("  save-server --ip <ip> [--user <user>]                Save server info");
      console.log("  update-dns                                           Update DNS using stored credentials");
      console.log("  show                                                 Show current configuration");
      console.log("\nEnvironment:");
      console.log("  INFISICAL_URL            - Infisical URL (default: http://localhost:8081)");
      console.log("  INFISICAL_CLIENT_ID      - Infisical Client ID");
      console.log("  INFISICAL_CLIENT_SECRET  - Infisical Client Secret");
      console.log("  INFISICAL_PROJECT_ID     - Infisical Project ID");
      console.log("  INFISICAL_ENVIRONMENT    - Infisical Environment (default: prod)");
      process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((err) => {
    console.error("Error:", err.message);
    process.exit(1);
  });
