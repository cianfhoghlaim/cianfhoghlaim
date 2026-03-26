// =============================================================================
// SETUP PANGOLIN SITE ACTION
// =============================================================================
// Creates a Pangolin site and deploys Newt on a remote server.
// Run this when adding a new site to the Pangolin network.
//
// Usage:
//   km run action setup-pangolin-site --server=arm1-oci --siteName=arm1-oci
//   km run action setup-pangolin-site --server=cax41-hetzner --dryRun=true
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

interface SiteDefaults {
  exitNodeId: number;
  subnet: string;
  newtId: string;
  newtSecret: string;
}

interface PangolinSite {
  siteId: number;
  name: string;
  niceId: string;
  type: string;
  online: boolean;
}

// Get Pangolin API key from Komodo variables
const pangolinApiKey = await komodo.read("GetVariable", { name: "PANGOLIN_API_KEY" });

if (!pangolinApiKey?.value) {
  return {
    success: false,
    error: "Missing PANGOLIN_API_KEY variable in Komodo. Create an API key in Pangolin UI first.",
  };
}

// Verify server exists in Komodo
const servers = await komodo.read("ListServers", {});
const targetServer = servers.find((s) => s.name === serverName);

if (!targetServer) {
  return {
    success: false,
    error: `Server '${serverName}' not found in Komodo. Available: ${servers.map((s) => s.name).join(", ")}`,
  };
}

console.log(`Setting up Pangolin site '${siteName}' on server '${serverName}'...`);

// Helper to make Pangolin API calls via the server
async function pangolinApi<T>(method: string, endpoint: string, body?: object): Promise<T> {
  const curlCmd = body
    ? `docker exec pangolin curl -s 'http://localhost:3003/v1${endpoint}' -X ${method} -H 'Authorization: Bearer ${pangolinApiKey.value}' -H 'Content-Type: application/json' -d '${JSON.stringify(body)}'`
    : `docker exec pangolin curl -s 'http://localhost:3003/v1${endpoint}' -H 'Authorization: Bearer ${pangolinApiKey.value}'`;

  // Execute via Komodo on the Pangolin host server (arm1-oci typically)
  const result = await komodo.execute("RunCommand", {
    server: "arm1-oci", // Pangolin runs on OCI
    command: curlCmd,
  });

  if (!result.success) {
    throw new Error(`Pangolin API call failed: ${result.stderr || "Unknown error"}`);
  }

  try {
    const data = JSON.parse(result.stdout || "{}");
    if (data.error) {
      throw new Error(data.message || "Pangolin API error");
    }
    return data.data as T;
  } catch (e) {
    throw new Error(`Invalid Pangolin API response: ${result.stdout}`);
  }
}

// Check for existing sites
console.log("\nChecking for existing sites...");
let existingSite: PangolinSite | undefined;

try {
  const sites = await pangolinApi<{ sites: PangolinSite[] }>("GET", `/org/${pangolinOrg}/sites`);
  existingSite = sites.sites?.find((s) => s.name === siteName);

  if (existingSite) {
    console.log(`  Site '${siteName}' already exists (ID: ${existingSite.siteId})`);
    console.log(`  Status: ${existingSite.online ? "Online" : "Offline"}`);
  }
} catch (err) {
  console.log(`  Could not list sites: ${(err as Error).message}`);
}

let newtId: string;
let newtSecret: string;

if (!existingSite) {
  // Get site defaults (includes new Newt credentials)
  console.log("\nGetting site defaults...");
  const defaults = await pangolinApi<SiteDefaults>("GET", `/org/${pangolinOrg}/pick-site-defaults`);

  newtId = defaults.newtId;
  newtSecret = defaults.newtSecret;

  console.log(`  Exit Node ID: ${defaults.exitNodeId}`);
  console.log(`  Subnet: ${defaults.subnet}`);
  console.log(`  Newt ID: ${newtId}`);

  if (!dryRun) {
    // Create the site
    console.log("\nCreating site...");
    const site = await pangolinApi<PangolinSite>("PUT", `/org/${pangolinOrg}/site`, {
      name: siteName,
      type: "newt",
      exitNodeId: defaults.exitNodeId,
      subnet: defaults.subnet,
      newtId: defaults.newtId,
      secret: defaults.newtSecret,
    });
    console.log(`  Site created (ID: ${site.siteId})`);
  } else {
    console.log("\n[DRY-RUN] Would create site with above defaults");
  }
} else {
  // Site exists - get fresh credentials for redeployment
  console.log("\nGetting fresh Newt credentials for existing site...");
  const defaults = await pangolinApi<SiteDefaults>("GET", `/org/${pangolinOrg}/pick-site-defaults`);
  newtId = defaults.newtId;
  newtSecret = defaults.newtSecret;
  console.log(`  WARNING: Using new credentials - site may need recreation in Pangolin UI`);
}

// Generate Newt compose file
const composeContent = `---
# =============================================================================
# NEWT - Pangolin Site Connector
# =============================================================================
# Site: ${siteName}
# Generated by: setup-pangolin-site action

services:
  newt:
    image: fosrl/newt:latest
    container_name: newt
    restart: unless-stopped
    environment:
      NEWT_ID: "${newtId}"
      NEWT_SECRET: "${newtSecret}"
      PANGOLIN_ENDPOINT: "https://pangolin.cianfhoghlaim.ie"
      DOCKER_SOCKET: "/var/run/docker.sock"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - pangolin
    cap_add:
      - NET_ADMIN
    labels:
      komodo.skip: "true"

networks:
  pangolin:
    external: true
`;

if (!dryRun) {
  console.log("\nDeploying Newt on server...");

  // Create directory and write compose file
  await komodo.execute("RunCommand", {
    server: serverName,
    command: `sudo mkdir -p /opt/newt`,
  });

  await komodo.execute("RunCommand", {
    server: serverName,
    command: `sudo tee /opt/newt/docker-compose.yaml > /dev/null << 'NEWTEOF'
${composeContent}
NEWTEOF`,
  });

  // Ensure pangolin network exists
  await komodo.execute("RunCommand", {
    server: serverName,
    command: `docker network create pangolin 2>/dev/null || true`,
  });

  // Start Newt
  await komodo.execute("RunCommand", {
    server: serverName,
    command: `cd /opt/newt && sudo docker compose up -d`,
  });

  console.log("  Newt deployed. Waiting for connection...");

  // Wait and check logs
  await new Promise((resolve) => setTimeout(resolve, 10000));

  const logsResult = await komodo.execute("RunCommand", {
    server: serverName,
    command: `docker logs newt 2>&1 | tail -5`,
  });

  console.log("\nNewt logs:");
  console.log(logsResult.stdout);

  if (logsResult.stdout?.includes("Tunnel connection to server established")) {
    console.log("\nNewt connected successfully!");
  } else {
    console.log("\nNewt may still be connecting. Check logs with: docker logs newt");
  }
} else {
  console.log("\n[DRY-RUN] Would deploy Newt with compose file:");
  console.log(composeContent);
}

return {
  success: true,
  dryRun,
  server: serverName,
  siteName,
  newtId,
  newtSecret: dryRun ? "[hidden]" : newtSecret,
  existingSite: !!existingSite,
};
