#!/usr/bin/env npx ts-node
/**
 * Setup script for OCI Infrastructure deployment
 *
 * This script:
 * 1. Saves Cloudflare credentials to 1Password
 * 2. Saves OCI server info to 1Password
 * 3. Updates DNS records via Pulumi
 *
 * Usage:
 *   bun run setup.ts save-cloudflare --token <token> --zone-id <zone-id>
 *   bun run setup.ts save-server --ip <ip>
 *   bun run setup.ts update-dns
 */

import { OnePasswordConnect, ItemBuilder, FullItem } from "@1password/connect";
import * as path from "path";
import * as fs from "fs";

// Configuration
const CONFIG = {
    // 1Password Connect (local instance via Komodo)
    opConnectHost: process.env.OP_CONNECT_HOST || "http://localhost:8080",
    opConnectToken: process.env.OP_CONNECT_TOKEN || "",
    opVault: process.env.OP_VAULT || "dev-baile",
    // Item names
    cloudflareItem: "cloudflare",
    serverOciItem: "server-oci",
    // Cloudflare
    cloudflareDomain: "cianfhoghlaim.ie",
};

// Read 1Password token from local file if not in env
function getOpToken(): string {
    if (CONFIG.opConnectToken) return CONFIG.opConnectToken;

    const tokenPath = path.join(__dirname, "..", "..", "pangolin", "pangolin-core", "config", "secrets", "op_token");
    if (fs.existsSync(tokenPath)) {
        return fs.readFileSync(tokenPath, "utf-8").trim();
    }
    throw new Error("OP_CONNECT_TOKEN not set and token file not found");
}

async function getOpClient() {
    const token = getOpToken();
    return OnePasswordConnect({
        serverURL: CONFIG.opConnectHost,
        token,
        keepAlive: false,
    });
}

/**
 * Get vault ID from vault name
 */
async function getVaultId(op: ReturnType<typeof OnePasswordConnect>, vaultName: string): Promise<string> {
    const vaults = await op.listVaults();
    const vault = vaults.find(v => v.name === vaultName);
    if (!vault || !vault.id) {
        throw new Error(`Vault "${vaultName}" not found. Available vaults: ${vaults.map(v => v.name).join(", ")}`);
    }
    return vault.id;
}

/**
 * Save Cloudflare credentials to 1Password
 */
async function saveCloudflareCredentials(apiToken: string, zoneId: string): Promise<void> {
    console.log("Saving Cloudflare credentials to 1Password...");

    const op = await getOpClient();
    const vaultId = await getVaultId(op, CONFIG.opVault);

    // Check if item exists
    let existingItem: FullItem | null = null;
    try {
        existingItem = await op.getItemByTitle(vaultId, CONFIG.cloudflareItem);
    } catch {
        // Item doesn't exist
    }

    if (existingItem) {
        // Update existing item
        existingItem.fields = existingItem.fields?.map(field => {
            if (field.label === "api_token") return { ...field, value: apiToken };
            if (field.label === "zone_id") return { ...field, value: zoneId };
            if (field.label === "domain") return { ...field, value: CONFIG.cloudflareDomain };
            return field;
        }) || [];

        // Add missing fields
        const fieldLabels = existingItem.fields?.map(f => f.label) || [];
        if (!fieldLabels.includes("api_token")) {
            existingItem.fields = [...(existingItem.fields || []), { label: "api_token", value: apiToken }];
        }
        if (!fieldLabels.includes("zone_id")) {
            existingItem.fields = [...(existingItem.fields || []), { label: "zone_id", value: zoneId }];
        }
        if (!fieldLabels.includes("domain")) {
            existingItem.fields = [...(existingItem.fields || []), { label: "domain", value: CONFIG.cloudflareDomain }];
        }

        await op.updateItem(vaultId, existingItem);
        console.log(`  Updated item "${CONFIG.cloudflareItem}" in vault "${CONFIG.opVault}"`);
    } else {
        // Create new item
        const newItem = new ItemBuilder()
            .setCategory("API_CREDENTIAL")
            .setTitle(CONFIG.cloudflareItem)
            .addField({ label: "api_token", value: apiToken, sectionName: "Credentials" })
            .addField({ label: "zone_id", value: zoneId, sectionName: "Credentials" })
            .addField({ label: "domain", value: CONFIG.cloudflareDomain, sectionName: "Credentials" })
            .build();

        await op.createItem(vaultId, newItem);
        console.log(`  Created item "${CONFIG.cloudflareItem}" in vault "${CONFIG.opVault}"`);
    }

    console.log("\nCloudflare credentials saved successfully!");
    console.log(`  Domain: ${CONFIG.cloudflareDomain}`);
    console.log(`  Zone ID: ${zoneId}`);
}

/**
 * Save server info to 1Password (matches servers.ts expectations)
 */
async function saveServerInfo(ip: string, user: string = "ubuntu"): Promise<void> {
    console.log("Saving server info to 1Password...");

    const op = await getOpClient();
    const vaultId = await getVaultId(op, CONFIG.opVault);

    // Check if item exists
    let existingItem: FullItem | null = null;
    try {
        existingItem = await op.getItemByTitle(vaultId, CONFIG.serverOciItem);
    } catch {
        // Item doesn't exist
    }

    if (existingItem) {
        // Update existing item
        existingItem.fields = existingItem.fields?.map(field => {
            if (field.label === "ip") return { ...field, value: ip };
            if (field.label === "user") return { ...field, value: user };
            if (field.label === "hostname") return { ...field, value: "arm1.oci" };
            return field;
        }) || [];

        await op.updateItem(vaultId, existingItem);
        console.log(`  Updated item "${CONFIG.serverOciItem}" in vault "${CONFIG.opVault}"`);
    } else {
        // Create new item
        const newItem = new ItemBuilder()
            .setCategory("SERVER")
            .setTitle(CONFIG.serverOciItem)
            .addField({ label: "ip", value: ip, sectionName: "Infrastructure" })
            .addField({ label: "user", value: user, sectionName: "Infrastructure" })
            .addField({ label: "hostname", value: "arm1.oci", sectionName: "Infrastructure" })
            .build();

        await op.createItem(vaultId, newItem);
        console.log(`  Created item "${CONFIG.serverOciItem}" in vault "${CONFIG.opVault}"`);
    }

    console.log("\nServer info saved successfully!");
    console.log(`  IP: ${ip}`);
    console.log(`  User: ${user}`);
}

/**
 * Get Cloudflare credentials from 1Password
 */
async function getCloudflareCredentials(): Promise<{ apiToken: string; zoneId: string }> {
    const op = await getOpClient();
    const vaultId = await getVaultId(op, CONFIG.opVault);
    const item = await op.getItemByTitle(vaultId, CONFIG.cloudflareItem);

    const apiToken = item.fields?.find(f => f.label === "api_token")?.value;
    const zoneId = item.fields?.find(f => f.label === "zone_id")?.value;

    if (!apiToken || !zoneId) {
        throw new Error("Cloudflare credentials not found in 1Password");
    }

    return { apiToken, zoneId };
}

/**
 * Update DNS records using Pulumi
 */
async function updateDns(): Promise<void> {
    console.log("Updating DNS records...");

    // Get credentials from 1Password
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
 * Show current configuration from 1Password
 */
async function showConfig(): Promise<void> {
    console.log("Current configuration from 1Password:\n");

    const op = await getOpClient();
    const vaultId = await getVaultId(op, CONFIG.opVault);

    // Cloudflare
    try {
        const cfItem = await op.getItemByTitle(vaultId, CONFIG.cloudflareItem);
        console.log("Cloudflare:");
        cfItem.fields?.forEach(f => {
            if (f.label === "api_token") {
                console.log(`  ${f.label}: ${f.value?.slice(0, 10)}...`);
            } else {
                console.log(`  ${f.label}: ${f.value}`);
            }
        });
    } catch {
        console.log("Cloudflare: Not configured");
    }

    console.log();

    // Server
    try {
        const serverItem = await op.getItemByTitle(vaultId, CONFIG.serverOciItem);
        console.log("Server (arm1.oci):");
        serverItem.fields?.forEach(f => {
            console.log(`  ${f.label}: ${f.value}`);
        });
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
            console.log("  OP_CONNECT_HOST  - 1Password Connect URL (default: http://localhost:8080)");
            console.log("  OP_CONNECT_TOKEN - 1Password Connect token (or reads from local file)");
            console.log("  OP_VAULT         - 1Password vault name (default: dev-baile)");
            process.exit(1);
    }
}

main()
    .then(() => process.exit(0))
    .catch((err) => {
        console.error("Error:", err.message);
        process.exit(1);
    });
