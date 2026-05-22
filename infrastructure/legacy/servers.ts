import { KomodoClient, Types } from "komodo_client";
import { OnePasswordConnect, OPConnect, FullItem } from "@infisical/connect";
import * as dotenv from "dotenv";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

// =============================================================================
// CONFIGURATION
// =============================================================================

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, "core", "compose.env") });

const KOMODO_URL = process.env.KOMODO_HOST || "https://komodo.local";
const INFISICAL_HOST = process.env.INFISICAL_HOST || "http://localhost:8080";
const INFISICAL_TOKEN_FILE = process.env.INFISICAL_TOKEN_FILE || "/etc/connect/token";

// Read token from file or environment
function getOPConnectToken(): string {
  // First check environment variable
  if (process.env.INFISICAL_TOKEN) {
    return process.env.INFISICAL_TOKEN;
  }
  // Then try to read from file
  try {
    return fs.readFileSync(INFISICAL_TOKEN_FILE, "utf-8").trim();
  } catch (err) {
    throw new Error(
      `Could not read Infisical token. Set INFISICAL_TOKEN env var or ensure ${INFISICAL_TOKEN_FILE} exists.`
    );
  }
}

// Infisical project and item references
const OP_VAULT = "dev-baile";
const OP_KOMODO_ITEM = "komodo";

// Server definitions - these map to Infisical secrets in dev-baile vault
// Each server has an item in Infisical with fields: hostname, ip, user
interface ServerDefinition {
  name: string;
  opItem: string; // Infisical secret name (e.g., "server-bunchloch")
  isCore: boolean;
  installPeriphery: boolean; // Whether to install periphery binary
  region?: string;
  os?: "linux" | "darwin"; // Operating system for architecture selection
}

const SERVER_DEFINITIONS: ServerDefinition[] = [
  // bunchloch (Mac) - Core only, locket for compose infisical:// refs, no periphery (v2-dev lacks apple build)
  { name: "bunchloch", opItem: "server-bunchloch", isCore: true, installPeriphery: false, region: "local", os: "darwin" },
  // Linux servers - periphery + locket
  { name: "security.hetzner", opItem: "server-hetzner", isCore: false, installPeriphery: true, region: "eu-central", os: "linux" },
  { name: "arm1.oci", opItem: "server-oci", isCore: false, installPeriphery: true, region: "eu-amsterdam", os: "linux" },
];

// =============================================================================
// INFISICAL CONNECT CLIENT
// =============================================================================

let opClient: OPConnect | null = null;

/**
 * Initialize the Infisical client.
 */
export function getOPClient(): OPConnect {
  if (!opClient) {
    const token = getOPConnectToken();
    opClient = OnePasswordConnect({
      serverURL: INFISICAL_HOST,
      token,
    });
  }
  return opClient;
}

/**
 * Get a field value from a Infisical secret.
 */
export function getFieldValue(item: FullItem, fieldLabel: string): string | undefined {
  const field = item.fields?.find(
    (f) => f.label?.toLowerCase() === fieldLabel.toLowerCase()
  );
  return field?.value;
}

/**
 * Retrieve Komodo credentials from Infisical.
 */
export async function getKomodoCredentials(): Promise<{
  username: string;
  password: string;
  passkey: string;
}> {
  const op = getOPClient();
  const vault = await op.getVaultByTitle(OP_VAULT);
  const item = await op.getItemByTitle(vault.id!, OP_KOMODO_ITEM);

  // Try multiple field name variations
  const username = getFieldValue(item, "username") ||
                   getFieldValue(item, "init_username");
  const password = getFieldValue(item, "password") ||
                   getFieldValue(item, "init_password") ||
                   getFieldValue(item, "credential");
  const passkey = getFieldValue(item, "passkey");

  if (!username || !password || !passkey) {
    // Debug: show available fields
    const availableFields = item.fields?.map(f => f.label).join(", ") || "none";
    throw new Error(
      `Missing required fields in Infisical secret '${OP_KOMODO_ITEM}'. ` +
        `Found fields: ${availableFields}. ` +
        `Need: username (or init_username), password (or init_password/credential), passkey`
    );
  }

  return { username, password, passkey };
}

/**
 * Retrieve server details from Infisical.
 */
export async function getServerDetails(opItemName: string): Promise<{
  ip: string;
  user: string;
  hostname?: string;
}> {
  const op = getOPClient();
  const vault = await op.getVaultByTitle(OP_VAULT);
  const item = await op.getItemByTitle(vault.id!, opItemName);

  const ip = getFieldValue(item, "ip") || getFieldValue(item, "address");
  const user = getFieldValue(item, "user") || getFieldValue(item, "username") || "root";
  const hostname = getFieldValue(item, "hostname");

  if (!ip) {
    throw new Error(
      `Missing 'ip' or 'address' field in Infisical secret '${opItemName}'`
    );
  }

  return { ip, user, hostname };
}

// =============================================================================
// KOMODO CLIENT
// =============================================================================

/**
 * Login to Komodo using credentials from Infisical and create an API key.
 */
export async function loginAndCreateApiKey(
  apiKeyName: string = "cli-automation",
  expires: number = 0
): Promise<{ key: string; secret: string; komodo: ReturnType<typeof KomodoClient> }> {
  const { username, password } = await getKomodoCredentials();

  console.log(`Logging in to Komodo at ${KOMODO_URL} as ${username}...`);

  // Step 1: Login with username/password to get JWT
  const loginResponse = await fetch(`${KOMODO_URL}/auth/LoginLocalUser`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!loginResponse.ok) {
    const error = await loginResponse.text();
    throw new Error(`Login failed: ${loginResponse.status} - ${error}`);
  }

  const { jwt, user_id } = (await loginResponse.json()) as Types.JwtResponse;
  console.log(`Login successful. User ID: ${user_id}`);

  // Step 2: Initialize client with JWT
  const komodo = KomodoClient(KOMODO_URL, { type: "jwt", params: { jwt } });

  // Step 3: Create API key
  console.log(`Creating API key "${apiKeyName}"...`);
  const { key, secret } = await komodo.user("CreateApiKey", {
    name: apiKeyName,
    expires,
  });

  console.log("API key created successfully!");
  console.log(`  Key:    ${key}`);
  console.log(`  Secret: ${secret}`);
  console.log(
    "\nIMPORTANT: Save these credentials - the secret cannot be retrieved later."
  );

  return { key, secret, komodo };
}

/**
 * Login to Komodo using credentials from Infisical (JWT only, no API key).
 */
export async function loginToKomodo(): Promise<ReturnType<typeof KomodoClient>> {
  const { username, password } = await getKomodoCredentials();

  console.log(`Logging in to Komodo at ${KOMODO_URL} as ${username}...`);

  const loginResponse = await fetch(`${KOMODO_URL}/auth/LoginLocalUser`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!loginResponse.ok) {
    const error = await loginResponse.text();
    throw new Error(`Login failed: ${loginResponse.status} - ${error}`);
  }

  const { jwt } = (await loginResponse.json()) as Types.JwtResponse;
  return KomodoClient(KOMODO_URL, { type: "jwt", params: { jwt } });
}

/**
 * Initialize a Komodo client using API key credentials.
 */
export function createKomodoClient(key: string, secret: string) {
  return KomodoClient(KOMODO_URL, {
    type: "api-key",
    params: { key, secret },
  });
}

// =============================================================================
// SERVER MANAGEMENT
// =============================================================================

/**
 * List all servers from Komodo.
 */
export async function listServers(
  komodo: ReturnType<typeof KomodoClient>
): Promise<Types.ServerListItem[]> {
  const servers = await komodo.read("ListServers", {});
  console.log(`Found ${servers.length} servers`);
  return servers;
}

/**
 * Check if a server exists in Komodo by name.
 */
export async function serverExists(
  komodo: ReturnType<typeof KomodoClient>,
  name: string
): Promise<boolean> {
  const servers = await komodo.read("ListServers", {});
  return servers.some((s) => s.name === name);
}

/**
 * Create a server in Komodo for outbound periphery connection.
 * Returns the server config including the passkey.
 */
export async function createServer(
  komodo: ReturnType<typeof KomodoClient>,
  name: string,
  options: {
    region?: string;
    enabled?: boolean;
  } = {}
): Promise<Types.Server> {
  const { passkey } = await getKomodoCredentials();

  console.log(`Creating server '${name}' in Komodo...`);

  const server = await komodo.write("CreateServer", {
    name,
    config: {
      // For outbound mode, address is not used - periphery connects to core
      address: "",
      enabled: options.enabled ?? true,
      region: options.region,
      // Use the shared passkey from Infisical
      passkey,
      // Enable monitoring
      stats_monitoring: true,
      auto_prune: true,
      send_unreachable_alerts: true,
      send_version_mismatch_alerts: true,
    },
  });

  console.log(`  Server created: ${server.name} (id: ${server._id?.$oid})`);
  return server;
}

/**
 * Register all defined servers in Komodo.
 * Skips servers that already exist.
 */
export async function registerAllServers(
  komodo: ReturnType<typeof KomodoClient>
): Promise<void> {
  console.log("\n=== Registering Servers in Komodo ===\n");

  const existingServers = await komodo.read("ListServers", {});
  const existingNames = new Set(existingServers.map((s) => s.name));

  for (const def of SERVER_DEFINITIONS) {
    if (existingNames.has(def.name)) {
      console.log(`  ✓ Server '${def.name}' already exists, skipping`);
      continue;
    }

    try {
      await createServer(komodo, def.name, { region: def.region });
      console.log(`  ✓ Server '${def.name}' registered successfully`);
    } catch (err) {
      console.error(`  ✗ Failed to register '${def.name}':`, (err as Error).message);
    }
  }

  console.log("\n=== Server Registration Complete ===\n");
}

// =============================================================================
// ANSIBLE INVENTORY GENERATION
// =============================================================================

/**
 * Generate Ansible inventory YAML with infisical:// references for IPs.
 * This allows Ansible to resolve IPs from Infisical at runtime via Locket.
 */
export async function generateAnsibleInventory(): Promise<string> {
  console.log("\n=== Generating Ansible Inventory ===\n");

  const coreHosts: string[] = [];
  const peripheryHosts: string[] = [];
  const locketOnlyHosts: string[] = [];
  const hostVars: Record<string, { ansible_host: string; ansible_user?: string; os?: string }> = {};

  for (const def of SERVER_DEFINITIONS) {
    // Get actual IP from Infisical - Ansible needs real IPs for SSH connectivity
    // (infisical:// refs are for Locket to inject secrets at runtime, not for Ansible inventory)
    try {
      const details = await getServerDetails(def.opItem);
      hostVars[def.name] = {
        ansible_host: details.ip,
        os: def.os,
      };
      if (details.user !== "ubuntu") {
        hostVars[def.name].ansible_user = details.user;
      }
      const peripheryFlag = def.installPeriphery ? "periphery+locket" : "locket only";
      console.log(`  ✓ ${def.name}: ${details.ip} (user: ${details.user}, ${peripheryFlag})`);
    } catch (err) {
      console.error(`  ✗ ${def.name}: Could not fetch details - ${(err as Error).message}`);
      throw err;
    }

    if (def.isCore) {
      coreHosts.push(def.name);
    }

    if (def.installPeriphery) {
      peripheryHosts.push(def.name);
    } else {
      locketOnlyHosts.push(def.name);
    }
  }

  // Generate YAML
  const inventory = `---
# =============================================================================
# KOMODO INVENTORY (Auto-generated)
# =============================================================================
# Generated by: bun run servers.ts generate-inventory
# =============================================================================

all:
  hosts:
${Object.entries(hostVars)
  .map(
    ([name, vars]) => `    ${name}:
      ansible_host: "${vars.ansible_host}"${
        vars.ansible_user ? `\n      ansible_user: ${vars.ansible_user}` : ""
      }${
        vars.os === "darwin" ? `\n      ansible_become: false  # macOS doesn't need sudo for locket install` : ""
      }`
  )
  .join("\n")}

  vars:
    ansible_user: ubuntu
    ansible_ssh_private_key_file: /root/.ssh/id_ed25519

    # Periphery version (use specific version, not "latest")
    periphery_version: "2.0.0-dev-90"

    # Periphery configuration (outbound mode)
    periphery_core_address: "wss://komodo.local"
    periphery_mode: outbound
    periphery_server_enabled: false
    periphery_passkey_op_ref: "infisical://${OP_VAULT}/${OP_KOMODO_ITEM}/passkey"

    # Locket configuration
    locket_enabled: true
    locket_provider: infisical
    locket_infisical_host: "http://connect.internal:8080"

  children:
    # All hosts that get locket installed (for infisical:// refs in compose files)
    locket:
      hosts:
${[...peripheryHosts, ...locketOnlyHosts].map((h) => `        ${h}:`).join("\n")}

    # Hosts that get periphery + locket (Linux servers managed by Komodo)
    komodo:
      vars:
        periphery_agent_secrets:
          - name: "PERIPHERY_PASSKEYS"
            value: "{{ periphery_passkey_op_ref }}"
          - name: "INFISICAL_HOST"
            value: "{{ locket_infisical_host }}"
      hosts:
${peripheryHosts.map((h) => `        ${h}:`).join("\n")}

    # Core hosts (for reference - Komodo Core runs here)
    core:
      hosts:
${coreHosts.map((h) => `        ${h}:`).join("\n")}

    # Locket-only hosts (no periphery - e.g., macOS)
    locket_only:
      hosts:
${locketOnlyHosts.map((h) => `        ${h}:`).join("\n")}
`;

  return inventory;
}

/**
 * Write the generated inventory to a file.
 */
export async function writeAnsibleInventory(outputPath?: string): Promise<void> {
  const inventory = await generateAnsibleInventory();
  const targetPath =
    outputPath ||
    path.join(__dirname, "..", "automation", "ansible", "inventory", "komodo-generated.yml");

  fs.writeFileSync(targetPath, inventory, "utf-8");
  console.log(`\nInventory written to: ${targetPath}`);
}

// =============================================================================
// FULL SETUP WORKFLOW
// =============================================================================

/**
 * Complete setup workflow:
 * 1. Login to Komodo using Infisical credentials
 * 2. Register all servers in Komodo
 * 3. Generate Ansible inventory with infisical:// references
 */
export async function setup(): Promise<void> {
  console.log("╔════════════════════════════════════════════════════════════╗");
  console.log("║          KOMODO + INFISICAL AUTOMATED SETUP                ║");
  console.log("╚════════════════════════════════════════════════════════════╝\n");

  // Step 1: Login to Komodo
  console.log("Step 1: Connecting to Komodo...");
  const komodo = await loginToKomodo();
  console.log("  ✓ Connected to Komodo\n");

  // Step 2: Register servers
  console.log("Step 2: Registering servers...");
  await registerAllServers(komodo);

  // Step 3: Generate inventory
  console.log("Step 3: Generating Ansible inventory...");
  await writeAnsibleInventory();

  console.log("\n╔════════════════════════════════════════════════════════════╗");
  console.log("║                    SETUP COMPLETE                          ║");
  console.log("╚════════════════════════════════════════════════════════════╝");
  console.log("\nNext steps:");
  console.log("  1. Start Komodo Core: infisical export -i compose.env | docker compose up -d");
  console.log("  2. Deploy periphery: ansible-playbook -i inventory/komodo-generated.yml playbooks/periphery.yml");
}

// =============================================================================
// CLI
// =============================================================================

const commands: Record<string, () => Promise<void>> = {
  setup: setup,
  "register-servers": async () => {
    const komodo = await loginToKomodo();
    await registerAllServers(komodo);
  },
  "generate-inventory": async () => {
    await writeAnsibleInventory();
  },
  "list-servers": async () => {
    const komodo = await loginToKomodo();
    const servers = await listServers(komodo);
    servers.forEach((s) => {
      console.log(`  - ${s.name} (id: ${s.id})`);
    });
  },
  "create-api-key": async () => {
    await loginAndCreateApiKey();
  },
  "test-infisical": async () => {
    console.log("Testing Infisical...");
    const creds = await getKomodoCredentials();
    console.log(`  ✓ Retrieved Komodo credentials (username: ${creds.username})`);

    for (const def of SERVER_DEFINITIONS) {
      try {
        const details = await getServerDetails(def.opItem);
        console.log(`  ✓ ${def.name}: ${details.ip} (user: ${details.user})`);
      } catch (err) {
        console.error(`  ✗ ${def.name}: ${(err as Error).message}`);
      }
    }
  },
};

// Run if executed directly
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const command = process.argv[2] || "setup";

  if (command === "help" || command === "--help") {
    console.log("Usage: bun run servers.ts <command>\n");
    console.log("Commands:");
    console.log("  setup              - Full setup: register servers + generate inventory");
    console.log("  register-servers   - Register all servers in Komodo");
    console.log("  generate-inventory - Generate Ansible inventory with infisical:// refs");
    console.log("  list-servers       - List all servers in Komodo");
    console.log("  create-api-key     - Create a new API key");
    console.log("  test-infisical     - Test Infisical connectivity");
    console.log("  help               - Show this help message");
    process.exit(0);
  }

  const fn = commands[command];
  if (!fn) {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'bun run servers.ts help' for available commands");
    process.exit(1);
  }

  fn()
    .then(() => process.exit(0))
    .catch((err) => {
      console.error("Error:", err.message);
      process.exit(1);
    });
}
