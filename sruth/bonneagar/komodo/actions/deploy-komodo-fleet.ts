import { InfisicalSDK } from "@infisical/sdk";

const limit = ARGS.limit || "";
const dryRun = ARGS.dryRun || false;
const tags = ARGS.tags || "";

const CONFIG = {
    infisicalClientId: process.env.INFISICAL_CLIENT_ID || "",
    infisicalClientSecret: process.env.INFISICAL_CLIENT_SECRET || "",
    infisicalProjectId: process.env.INFISICAL_PROJECT_ID || "",
    infisicalEnvironment: process.env.INFISICAL_ENVIRONMENT || "prod",
    infisicalUrl: process.env.INFISICAL_URL || "http://localhost:8081"
};

console.log("=".repeat(60));
console.log("DEPLOY KOMODO FLEET (Infisical + Ansible)");
console.log("=".repeat(60));

if (!CONFIG.infisicalClientId || !CONFIG.infisicalClientSecret) {
    throw new Error("Missing INFISICAL_CLIENT_ID or INFISICAL_CLIENT_SECRET environment variables.");
}

console.log("Authenticating with Infisical...");
const client = new InfisicalSDK({ siteUrl: CONFIG.infisicalUrl });

await client.auth().universalAuth.login({
    clientId: CONFIG.infisicalClientId,
    clientSecret: CONFIG.infisicalClientSecret
});

// Fetch critical secrets needed for Ansible context if needed
const peripheryKeySecret = await client.secrets().getSecret({
    secretName: "PERIPHERY_ONBOARDING_KEY",
    projectId: CONFIG.infisicalProjectId,
    environment: CONFIG.infisicalEnvironment,
    secretPath: "/komodo"
});
const peripheryKey = peripheryKeySecret.secretValue;
console.log("Successfully retrieved PERIPHERY_ONBOARDING_KEY from Infisical vault.");

// Trigger the existing run-ansible-playbook flow
console.log("\nTriggering Core Playbook...");
const coreResult = await komodo.execute("RunAction", {
    name: "run-ansible-playbook",
    args: {
        playbook: "komodo.yml",
        limit: limit || "arm1-oci,macbook",
        tags,
        dryRun,
        extraVars: `periphery_onboarding_key=${peripheryKey}`
    }
});
if (!coreResult.success) throw new Error("Core playbook failed.");

console.log("\nTriggering Periphery Playbook...");
const peripheryResult = await komodo.execute("RunAction", {
    name: "run-ansible-playbook",
    args: {
        playbook: "periphery.yml",
        limit: limit || "arm1-oci,macbook",
        tags,
        dryRun,
        extraVars: `periphery_onboarding_key=${peripheryKey}`
    }
});
if (!peripheryResult.success) throw new Error("Periphery playbook failed.");

console.log("\nKomodo fleet successfully deployed and sidecars synced to Infisical.");
return { success: true };
