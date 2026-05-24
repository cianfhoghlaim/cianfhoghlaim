import { InfisicalSDK } from "@infisical/sdk";

const CONFIG = {
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
    infisicalUrl: process.env.INFISICAL_URL || "http://localhost:8081",
};

async function main() {
    const client = new InfisicalSDK({ siteUrl: CONFIG.infisicalUrl });
    await client.auth().universalAuth.login({
        clientId: CONFIG.infisicalClientId,
        clientSecret: CONFIG.infisicalClientSecret
    });

    try {
        console.log("Creating dev-baile environment...");
        await client.environments().create({
            projectId: CONFIG.infisicalProjectId,
            slug: "dev-baile",
            name: "Dev Baile"
        });
        console.log("Created environment.");
    } catch(e) {
        console.log("Failed to create env:", e.message);
    }
}
main().catch(console.error);
