import { InfisicalClient } from "@infisical/sdk";
import * as fs from "fs";
import * as path from "path";

// Define the core setup configuration
const CONFIG = {
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
    infisicalEnvironment: process.env.INFISICAL_ENVIRONMENT || "prod",
    infisicalUrl: process.env.INFISICAL_URL || "http://localhost:8081",
};

async function main() {
    if (!CONFIG.infisicalClientId || !CONFIG.infisicalClientSecret || !CONFIG.infisicalProjectId) {
        console.error("Missing required Infisical environment variables.");
        console.error("Please ensure INFISICAL_CLIENT_ID, INFISICAL_CLIENT_SECRET, and INFISICAL_PROJECT_ID are set.");
        process.exit(1);
    }

    console.log("Initializing Infisical Client...");
    const client = new InfisicalClient({
        clientId: CONFIG.infisicalClientId,
        clientSecret: CONFIG.infisicalClientSecret,
        siteUrl: CONFIG.infisicalUrl
    });

    const pathsToCreate = ["/komodo", "/pangolin", "/infrastructure", "/oideachais"];

    console.log("Setting up folder structure...");
    for (const p of pathsToCreate) {
        try {
            await client.createFolder({
                environment: CONFIG.infisicalEnvironment,
                projectId: CONFIG.infisicalProjectId,
                path: "/",
                folderName: p.replace("/", "")
            });
            console.log(`  Created folder: ${p}`);
        } catch (e: any) {
            if (e.message?.includes("already exists")) {
                console.log(`  Folder already exists: ${p}`);
            } else {
                console.log(`  Ensured folder path: ${p}`);
            }
        }
    }

    // Load local secrets if available for seeding
    const envLocalPath = path.join(__dirname, ".env.local");
    let secretsToSeed: Array<{name: string, value: string, path: string}> = [];

    if (fs.existsSync(envLocalPath)) {
        console.log("Found .env.local, parsing secrets to seed...");
        const envContent = fs.readFileSync(envLocalPath, "utf-8");
        envContent.split("\n").forEach(line => {
            if (line.trim() && !line.startsWith("#")) {
                const [key, ...valParts] = line.split("=");
                const value = valParts.join("=").replace(/['"]/g, "");
                
                let targetPath = "/infrastructure";
                if (key.startsWith("NEWT_") || key.startsWith("PANGOLIN_")) targetPath = "/pangolin";
                if (key.startsWith("KOMODO_") || key.startsWith("PERIPHERY_")) targetPath = "/komodo";

                secretsToSeed.push({ name: key, value, path: targetPath });
            }
        });
    } else {
        console.log("No .env.local found. Using default placeholder seeds.");
        secretsToSeed = [
            { name: "PERIPHERY_ONBOARDING_KEY", value: "change-me", path: "/komodo" },
            { name: "NEWT_ID", value: "change-me", path: "/pangolin" },
            { name: "NEWT_SECRET", value: "change-me", path: "/pangolin" },
            { name: "PANGOLIN_API_KEY", value: "change-me", path: "/pangolin" },
        ];
        console.log("Hint: Create a .env.local file in scripts/ with KEY=VALUE to automatically seed them.");
    }

    console.log("Seeding secrets into Vault...");
    for (const secret of secretsToSeed) {
        try {
            await client.createSecret({
                secretName: secret.name,
                secretValue: secret.value,
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                path: secret.path
            });
            console.log(`  Created: ${secret.path}/${secret.name}`);
        } catch (e: any) {
            await client.updateSecret({
                secretName: secret.name,
                secretValue: secret.value,
                projectId: CONFIG.infisicalProjectId,
                environment: CONFIG.infisicalEnvironment,
                path: secret.path
            });
            console.log(`  Updated: ${secret.path}/${secret.name}`);
        }
    }

    console.log("\nVault successfully initialized and seeded!");
}

main().catch(console.error);
