// =============================================================================
// SETUP PANGOLIN SITE ACTION
// =============================================================================
const dryRun = ARGS.dryRun || false;
const serverName = ARGS.server || "";
const siteName = ARGS.siteName || serverName;
const pangolinOrg = ARGS.org || "cianfhoghlaim";

if (!serverName) {
  return {
    success: false,
    error: "Missing required --server argument. Specify a Komodo server name.",
  };
}

import { InfisicalSDK } from "@infisical/sdk";

const client = new InfisicalSDK({
    siteUrl: process.env.INFISICAL_URL || "http://localhost:8081"
});
await client.auth().universalAuth.login({
    clientId: process.env.INFISICAL_CLIENT_ID || "",
    clientSecret: process.env.INFISICAL_CLIENT_SECRET || ""
});

const pangolinApiKeySecret = await client.secrets().getSecret({
    secretName: "PANGOLIN_API_KEY",
    projectId: process.env.INFISICAL_PROJECT_ID || "",
    environment: process.env.INFISICAL_ENVIRONMENT || "prod",
    secretPath: "/pangolin"
});
const pangolinApiKey = { value: pangolinApiKeySecret.secretValue };

if (!pangolinApiKey?.value) {
  return {
    success: false,
    error: "Missing PANGOLIN_API_KEY variable in Komodo. Create an API key in Pangolin UI first.",
  };
}

const servers = await komodo.read("ListServers", {});
