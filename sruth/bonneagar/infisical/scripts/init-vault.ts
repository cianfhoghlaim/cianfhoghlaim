import { InfisicalSDK } from "@infisical/sdk";
import * as fs from "fs";
import * as path from "path";

const CONFIG = {
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
    infisicalEnvironment: process.env.INFISICAL_ENVIRONMENT || "prod",
    infisicalUrl: process.env.INFISICAL_URL || "http://localhost:8081",
};

async function main() {
    let missing = [];
    if (!CONFIG.infisicalClientId) missing.push("INFISICAL_CLIENT_ID");
    if (!CONFIG.infisicalClientSecret) missing.push("INFISICAL_CLIENT_SECRET");
    if (!CONFIG.infisicalProjectId) missing.push("INFISICAL_PROJECT_ID");

    if (missing.length > 0) {
        console.error("Missing required Infisical environment variables:");
        missing.forEach(m => console.error(`  - ${m}`));
        console.error("\nPlease add them to your .env file.");
        process.exit(1);
    }

    console.log("Initializing Infisical Client...");
    const client = new InfisicalSDK({
        siteUrl: CONFIG.infisicalUrl
    });

    console.log("Authenticating...");
    await client.auth().universalAuth.login({
        clientId: CONFIG.infisicalClientId,
        clientSecret: CONFIG.infisicalClientSecret
    });

    const pathsToCreate = ["/komodo", "/pangolin", "/infrastructure", "/oideachais"];

    console.log("Setting up folder structure...");
    for (const p of pathsToCreate) {
        try {
            await client.folders().create({
                environment: CONFIG.infisicalEnvironment,
                projectId: CONFIG.infisicalProjectId,
                path: "/",
                name: p.replace("/", "")
            });
            console.log(`  Created folder: ${p}`);
        } catch (e: any) {
            if (e.message?.includes("already exists") || e.message?.includes("Folder already exists")) {
                console.log(`  Folder already exists: ${p}`);
            } else {
                console.log(`  Failed to create folder ${p}:`, e.message);
            }
        }
    }

    const envLocalPath = path.join(process.cwd(), ".env");
    let secretsToSeed: Array<{name: string, value: string, path: string}> = [];

    if (fs.existsSync(envLocalPath)) {
        console.log(`Found .env at ${envLocalPath}, parsing secrets to seed...`);
        const envContent = fs.readFileSync(envLocalPath, "utf-8");
        envContent.split("\n").forEach(line => {
            if (line.trim() && !line.startsWith("#")) {
                const [key, ...valParts] = line.split("=");
                if (!valParts.length) return;
                
                const value = valParts.join("=").replace(/['"]/g, "");
                
                let targetPath = "/infrastructure";
                if (key.startsWith("NEWT_") || key.startsWith("PANGOLIN_")) targetPath = "/pangolin";
                if (key.startsWith("KOMODO_") || key.startsWith("PERIPHERY_")) targetPath = "/komodo";
                if (key === "LOGFIRE_TOKEN" || key === "FIRECRAWL_API_KEY" || key.startsWith("LLM_") || key.startsWith("LANGFUSE_")) targetPath = "/oideachais";

                // Don't push infisical identity to the vault itself
                if (!key.startsWith("INFISICAL_")) {
                    secretsToSeed.push({ name: key, value, path: targetPath });
                }
            }
        });
    }

    // Always ensure these basic ones exist even if not in .env
    const defaults = [
        { name: "PERIPHERY_ONBOARDING_KEY", value: "change-me", path: "/komodo" },
        { name: "NEWT_ID", value: "change-me", path: "/pangolin" },
        { name: "NEWT_SECRET", value: "change-me", path: "/pangolin" },
        { name: "PANGOLIN_API_KEY", value: "change-me", path: "/pangolin" },
    ];

    for (const def of defaults) {
        if (!secretsToSeed.find(s => s.name === def.name)) {
            secretsToSeed.push(def);
        }
    }

    console.log(`Seeding ${secretsToSeed.length} secrets into Vault...`);
    for (const secret of secretsToSeed) {
        try {
            await client.secrets().createSecret(secret.name, {
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                secretPath: secret.path,
                secretValue: secret.value
            });
            console.log(`  Created: ${secret.path}/${secret.name}`);
        } catch (e: any) {
            try {
                await client.secrets().updateSecret(secret.name, {
                    projectId: CONFIG.infisicalProjectId,
                    environment: CONFIG.infisicalEnvironment,
                    secretPath: secret.path,
                    secretValue: secret.value
                });
                console.log(`  Updated: ${secret.path}/${secret.name}`);
            } catch (err: any) {
                console.log(`  Failed to process ${secret.path}/${secret.name}:`, err.message);
            }
        }
    }

    console.log("\nVault successfully initialized and seeded!");
}

main().catch(console.error);
