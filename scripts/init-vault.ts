import { InfisicalSDK } from "@infisical/sdk";
import * as fs from "fs";
import * as path from "path";

const CONFIG = {
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
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

    const envLocalPath = path.join(process.cwd(), ".env");
    const infisicalEnvPath = path.join(process.cwd(), ".infisical.env");
    
    // Load local actual values
    let localEnv: Record<string, string> = {};
    if (fs.existsSync(envLocalPath)) {
        console.log(`Found .env at ${envLocalPath}, reading values...`);
        const envContent = fs.readFileSync(envLocalPath, "utf-8");
        envContent.split("\n").forEach(line => {
            if (line.trim() && !line.startsWith("#")) {
                const [key, ...valParts] = line.split("=");
                if (!valParts.length) return;
                localEnv[key.trim()] = valParts.join("=").replace(/['"]/g, "").trim();
            }
        });
    } else {
        console.log("No .env found, using process.env");
        localEnv = process.env as Record<string, string>;
    }

    // Load mappings from .infisical.env
    let secretsToSeed: Array<{env: string, path: string, name: string, value: string}> = [];
    const foldersToCreate: Set<string> = new Set();
    const envsFound: Set<string> = new Set();

    if (fs.existsSync(infisicalEnvPath)) {
        console.log(`Found .infisical.env at ${infisicalEnvPath}, parsing mappings...`);
        const templateContent = fs.readFileSync(infisicalEnvPath, "utf-8");
        templateContent.split("\n").forEach(line => {
            const match = line.match(/^([A-Z0-9_]+)=.*?infisical:\/\/([^\/]+)\/(.*?)\/([^\/]+)$/i);
            if (match) {
                const [_, envKey, targetEnv, targetPath, targetName] = match;
                if (localEnv[envKey]) {
                    const fullPath = "/" + targetPath;
                    secretsToSeed.push({
                        env: targetEnv,
                        path: fullPath,
                        name: targetName,
                        value: localEnv[envKey]
                    });
                    foldersToCreate.add(`${targetEnv}:${fullPath}`);
                    envsFound.add(targetEnv);
                }
            }
        });
    }

    console.log("Setting up folder structure...");
    for (const folderKey of Array.from(foldersToCreate)) {
        const [environment, p] = folderKey.split(":");
        try {
            await client.folders().create({
                environment: environment,
                projectId: CONFIG.infisicalProjectId,
                path: "/",
                name: p.replace("/", "")
            });
            console.log(`  Created folder: ${p} in ${environment}`);
        } catch (e: any) {
            if (e.message?.includes("already exists") || e.message?.includes("Folder already exists") || e.message?.includes("already") || e.message?.includes("400")) {
                console.log(`  Folder already exists: ${p} in ${environment}`);
            } else {
                console.log(`  Failed to create folder ${p} in ${environment}:`, e.message);
            }
        }
    }

    console.log(`Seeding ${secretsToSeed.length} secrets into Vault...`);
    for (const secret of secretsToSeed) {
        try {
            await client.secrets().createSecret(secret.name, {
                projectId: CONFIG.infisicalProjectId,
                environment: secret.env,
                secretPath: secret.path,
                secretValue: secret.value
            });
            console.log(`  Created: [${secret.env}] ${secret.path}/${secret.name}`);
        } catch (e: any) {
            try {
                await client.secrets().updateSecret(secret.name, {
                    projectId: CONFIG.infisicalProjectId,
                    environment: secret.env,
                    secretPath: secret.path,
                    secretValue: secret.value
                });
                console.log(`  Updated: [${secret.env}] ${secret.path}/${secret.name}`);
            } catch (err: any) {
                console.log(`  Failed to process [${secret.env}] ${secret.path}/${secret.name}:`, err.message);
            }
        }
    }

    console.log("\nVault successfully synchronized with local .env!");
}

main().catch(console.error);
