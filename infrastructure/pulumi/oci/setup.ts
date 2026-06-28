#!/usr/bin/env npx ts-node
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
 */

import { InfisicalSDK } from "@infisical/sdk";
import * as path from "path";
import * as fs from "fs";

// Configuration
const CONFIG = {
    // Infisical
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
    infisicalEnvironment: process.env.INFISICAL_ENVIRONMENT || "prod",
    infisicalUrl: process.env.INFISICAL_URL || "http://localhost:8081",
    // Cloudflare
    cloudflareDomain: "cianfhoghlaim.ie",
};

let _client: InfisicalSDK | null = null;
async function getInfisicalClient(): Promise<InfisicalSDK> {
    if (_client) return _client;
    
    if (!CONFIG.infisicalClientId || !CONFIG.infisicalClientSecret) {
        throw new Error("INFISICAL_CLIENT_ID or INFISICAL_CLIENT_SECRET not set in environment");
    }

    _client = new InfisicalSDK({ siteUrl: CONFIG.infisicalUrl });
    
    await _client.auth().universalAuth.login({
        clientId: CONFIG.infisicalClientId,
        clientSecret: CONFIG.infisicalClientSecret
    });
    
    return _client;
}

/**
 * Save Cloudflare credentials to Infisical
 */
async function saveCloudflareCredentials(apiToken: string, zoneId: string): Promise<void> {
    console.log("Saving Cloudflare credentials to Infisical...");

    const client = await getInfisicalClient();

    const secrets = [
        { name: "CLOUDFLARE_API_TOKEN", value: apiToken },
        { name: "CLOUDFLARE_ZONE_ID", value: zoneId },
        { name: "CLOUDFLARE_DOMAIN", value: CONFIG.cloudflareDomain }
    ];

    for (const secret of secrets) {
        try {
            await client.secrets().createSecret(secret.name, {
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                secretPath: "/",
                secretValue: secret.value
            });
        } catch {
            await client.secrets().updateSecret(secret.name, {
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                secretPath: "/",
                secretValue: secret.value
            });
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

    const client = await getInfisicalClient();

    const secretsToSave = [
        { name: "SERVER_PUBLIC_IP", value: ip },
        { name: "SERVER_USER", value: user },
        { name: "SERVER_HOSTNAME", value: "arm1.oci" }
    ];

    for (const secret of secretsToSave) {
        try {
            await client.secrets().createSecret(secret.name, {
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                secretPath: "/",
                secretValue: secret.value
            });
        } catch {
            await client.secrets().updateSecret(secret.name, {
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                secretPath: "/",
                secretValue: secret.value
            });
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
    const client = await getInfisicalClient();
    
    try {
        const apiTokenSecret = await client.secrets().getSecret({
            secretName: "CLOUDFLARE_API_TOKEN",
            projectId: CONFIG.infisicalProjectId,
            environment: CONFIG.infisicalEnvironment,
            secretPath: "/"
        });
        
        const zoneIdSecret = await client.secrets().getSecret({
            secretName: "CLOUDFLARE_ZONE_ID",
            projectId: CONFIG.infisicalProjectId,
            environment: CONFIG.infisicalEnvironment,
            secretPath: "/"
        });
        
        return { apiToken: apiTokenSecret.secretValue, zoneId: zoneIdSecret.secretValue };
    } catch (e) {
        throw new Error("Cloudflare credentials not found in Infisical");
    }
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

    const client = await getInfisicalClient();

    // Cloudflare
    try {
        const cfApi = await client.secrets().getSecret({ secretName: "CLOUDFLARE_API_TOKEN", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" });
        const cfZone = await client.secrets().getSecret({ secretName: "CLOUDFLARE_ZONE_ID", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" });
        const cfDomain = await client.secrets().getSecret({ secretName: "CLOUDFLARE_DOMAIN", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" });
        
        console.log("Cloudflare:");
        console.log(`  api_token: ${cfApi.secretValue.slice(0, 10)}...`);
        console.log(`  zone_id: ${cfZone.secretValue}`);
        console.log(`  domain: ${cfDomain.secretValue}`);
    } catch {
        console.log("Cloudflare: Not configured");
    }

    console.log();

    // Server
    try {
        const serverIp = await client.secrets().getSecret({ secretName: "SERVER_PUBLIC_IP", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" });
        const serverUser = await client.secrets().getSecret({ secretName: "SERVER_USER", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" });
        const serverHost = await client.secrets().getSecret({ secretName: "SERVER_HOSTNAME", projectId: CONFIG.infisicalProjectId, environment: CONFIG.infisicalEnvironment, secretPath: "/" });
        
        console.log("Server (arm1.oci):");
        console.log(`  ip: ${serverIp.secretValue}`);
        console.log(`  user: ${serverUser.secretValue}`);
        console.log(`  hostname: ${serverHost.secretValue}`);
    } catch {
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
            const user = getArg("user") || "ubuntu";
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
            console.log("  INFISICAL_CLIENT_ID     - Infisical Client ID");
            console.log("  INFISICAL_CLIENT_SECRET - Infisical Client Secret (or reads from local file)");
            console.log("  INFISICAL_PROJECT_ID    - Infisical Project ID");
            console.log("  INFISICAL_ENVIRONMENT   - Infisical Environment (default: prod)");
            process.exit(1);
    }
}

main()
    .then(() => process.exit(0))
    .catch((err) => {
        console.error("Error:", err.message);
        process.exit(1);
    });
