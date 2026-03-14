import { OnePasswordConnect, OPConnect, FullItem } from "@1password/connect";
import * as dotenv from "dotenv";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

// =============================================================================
// CONFIGURATION
// =============================================================================

const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, ".env") });

const OP_CONNECT_HOST = process.env.OP_CONNECT_HOST || "http://localhost:8080";
const OP_CONNECT_TOKEN_FILE = process.env.OP_CONNECT_TOKEN_FILE || "./croí/op/connect_token";

// 1Password vault and item references
const OP_VAULT = "dev-baile";
const OP_CLOUDFLARE_ITEM = "cloudflare";

// DNS records to manage
interface DnsRecord {
  name: string;
  type: "A" | "AAAA" | "CNAME";
  content: string;
  proxied?: boolean;
  ttl?: number;
}

// Server IP definitions from 1Password
interface ServerIp {
  name: string;
  opItem: string;
}

const SERVERS: ServerIp[] = [
  { name: "arm1.oci", opItem: "server-oci" },
];

// DNS records to create/update
const DNS_RECORDS: DnsRecord[] = [
  // Main domain services on arm1.oci
  { name: "komodo", type: "A", content: "SERVER:arm1.oci", proxied: false },
  { name: "pangolin", type: "A", content: "SERVER:arm1.oci", proxied: false },
  { name: "auth", type: "A", content: "SERVER:arm1.oci", proxied: false },
  { name: "tinyauth", type: "A", content: "SERVER:arm1.oci", proxied: false },
  // Wildcard for Pangolin tunnels
  { name: "*", type: "A", content: "SERVER:arm1.oci", proxied: false },
];

// =============================================================================
// 1PASSWORD CONNECT CLIENT
// =============================================================================

function getOPConnectToken(): string {
  if (process.env.OP_CONNECT_TOKEN) {
    return process.env.OP_CONNECT_TOKEN;
  }
  try {
    return fs.readFileSync(OP_CONNECT_TOKEN_FILE, "utf-8").trim();
  } catch (err) {
    throw new Error(
      `Could not read 1Password Connect token. Set OP_CONNECT_TOKEN env var or ensure ${OP_CONNECT_TOKEN_FILE} exists.`
    );
  }
}

let opClient: OPConnect | null = null;

function getOPClient(): OPConnect {
  if (!opClient) {
    const token = getOPConnectToken();
    opClient = OnePasswordConnect({
      serverURL: OP_CONNECT_HOST,
      token,
    });
  }
  return opClient;
}

function getFieldValue(item: FullItem, fieldLabel: string): string | undefined {
  const field = item.fields?.find(
    (f) => f.label?.toLowerCase() === fieldLabel.toLowerCase()
  );
  return field?.value;
}

// =============================================================================
// CLOUDFLARE API
// =============================================================================

interface CloudflareCredentials {
  apiToken: string;
  zoneId: string;
}

async function getCloudflareCredentials(): Promise<CloudflareCredentials> {
  const op = getOPClient();
  const vault = await op.getVaultByTitle(OP_VAULT);
  const item = await op.getItemByTitle(vault.id!, OP_CLOUDFLARE_ITEM);

  const apiToken = getFieldValue(item, "api_token") || getFieldValue(item, "token");
  const zoneId = getFieldValue(item, "zone_id") || getFieldValue(item, "cianfhoghlaim_zone_id");

  if (!apiToken || !zoneId) {
    const availableFields = item.fields?.map(f => f.label).join(", ") || "none";
    throw new Error(
      `Missing required fields in 1Password item '${OP_CLOUDFLARE_ITEM}'. ` +
      `Found fields: ${availableFields}. ` +
      `Need: api_token (or token), zone_id`
    );
  }

  return { apiToken, zoneId };
}

async function getServerIp(serverName: string): Promise<string> {
  const server = SERVERS.find(s => s.name === serverName);
  if (!server) {
    throw new Error(`Unknown server: ${serverName}`);
  }

  const op = getOPClient();
  const vault = await op.getVaultByTitle(OP_VAULT);
  const item = await op.getItemByTitle(vault.id!, server.opItem);

  const ip = getFieldValue(item, "ip") || getFieldValue(item, "address");
  if (!ip) {
    throw new Error(`No IP found for server ${serverName} in 1Password item ${server.opItem}`);
  }

  return ip;
}

interface CloudflareDnsRecord {
  id: string;
  name: string;
  type: string;
  content: string;
  proxied: boolean;
  ttl: number;
}

async function listDnsRecords(creds: CloudflareCredentials): Promise<CloudflareDnsRecord[]> {
  const response = await fetch(
    `https://api.cloudflare.com/client/v4/zones/${creds.zoneId}/dns_records`,
    {
      headers: {
        Authorization: `Bearer ${creds.apiToken}`,
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to list DNS records: ${response.status} - ${error}`);
  }

  const data = await response.json() as { result: CloudflareDnsRecord[] };
  return data.result;
}

async function createDnsRecord(
  creds: CloudflareCredentials,
  record: DnsRecord,
  domain: string
): Promise<CloudflareDnsRecord> {
  const fullName = record.name === "@" ? domain : `${record.name}.${domain}`;

  const response = await fetch(
    `https://api.cloudflare.com/client/v4/zones/${creds.zoneId}/dns_records`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${creds.apiToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: record.type,
        name: fullName,
        content: record.content,
        proxied: record.proxied ?? false,
        ttl: record.ttl ?? 1, // 1 = auto
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to create DNS record ${fullName}: ${response.status} - ${error}`);
  }

  const data = await response.json() as { result: CloudflareDnsRecord };
  return data.result;
}

async function updateDnsRecord(
  creds: CloudflareCredentials,
  recordId: string,
  record: DnsRecord,
  domain: string
): Promise<CloudflareDnsRecord> {
  const fullName = record.name === "@" ? domain : `${record.name}.${domain}`;

  const response = await fetch(
    `https://api.cloudflare.com/client/v4/zones/${creds.zoneId}/dns_records/${recordId}`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${creds.apiToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: record.type,
        name: fullName,
        content: record.content,
        proxied: record.proxied ?? false,
        ttl: record.ttl ?? 1,
      }),
    }
  );

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to update DNS record ${fullName}: ${response.status} - ${error}`);
  }

  const data = await response.json() as { result: CloudflareDnsRecord };
  return data.result;
}

// =============================================================================
// MAIN FUNCTIONS
// =============================================================================

async function syncDnsRecords(): Promise<void> {
  console.log("=== Syncing DNS Records to Cloudflare ===\n");

  // Get Cloudflare credentials
  console.log("Fetching Cloudflare credentials from 1Password...");
  const creds = await getCloudflareCredentials();
  console.log("  ✓ Credentials retrieved\n");

  // Resolve server IPs
  console.log("Resolving server IPs from 1Password...");
  const serverIps: Record<string, string> = {};
  for (const server of SERVERS) {
    const ip = await getServerIp(server.name);
    serverIps[server.name] = ip;
    console.log(`  ✓ ${server.name}: ${ip}`);
  }
  console.log();

  // Get existing DNS records
  console.log("Fetching existing DNS records from Cloudflare...");
  const existingRecords = await listDnsRecords(creds);
  console.log(`  Found ${existingRecords.length} existing records\n`);

  // Domain (extracted from first record or use default)
  const domain = "cianfhoghlaim.ie";

  // Process each DNS record
  console.log("Syncing DNS records...\n");
  for (const record of DNS_RECORDS) {
    // Resolve server reference to IP
    let content = record.content;
    if (content.startsWith("SERVER:")) {
      const serverName = content.substring(7);
      const ip = serverIps[serverName];
      if (!ip) {
        console.log(`  ✗ ${record.name}: Unknown server ${serverName}`);
        continue;
      }
      content = ip;
    }

    const fullName = record.name === "@" ? domain : `${record.name}.${domain}`;
    const resolvedRecord = { ...record, content };

    // Check if record exists
    const existing = existingRecords.find(
      (r) => r.name === fullName && r.type === record.type
    );

    if (existing) {
      if (existing.content === content) {
        console.log(`  ✓ ${fullName} (${record.type}): Already correct → ${content}`);
      } else {
        console.log(`  ↻ ${fullName} (${record.type}): Updating ${existing.content} → ${content}`);
        await updateDnsRecord(creds, existing.id, resolvedRecord, domain);
      }
    } else {
      console.log(`  + ${fullName} (${record.type}): Creating → ${content}`);
      await createDnsRecord(creds, resolvedRecord, domain);
    }
  }

  console.log("\n=== DNS Sync Complete ===");
}

async function listRecords(): Promise<void> {
  console.log("=== Listing DNS Records ===\n");

  const creds = await getCloudflareCredentials();
  const records = await listDnsRecords(creds);

  console.log(`Found ${records.length} DNS records:\n`);
  for (const record of records.sort((a, b) => a.name.localeCompare(b.name))) {
    const proxied = record.proxied ? " (proxied)" : "";
    console.log(`  ${record.name} (${record.type}): ${record.content}${proxied}`);
  }
}

async function checkIps(): Promise<void> {
  console.log("=== Checking Server IPs ===\n");

  for (const server of SERVERS) {
    try {
      const ip = await getServerIp(server.name);
      console.log(`  ✓ ${server.name}: ${ip}`);
    } catch (err) {
      console.log(`  ✗ ${server.name}: ${(err as Error).message}`);
    }
  }
}

// =============================================================================
// CLI
// =============================================================================

const commands: Record<string, () => Promise<void>> = {
  sync: syncDnsRecords,
  list: listRecords,
  "check-ips": checkIps,
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const command = process.argv[2] || "sync";

  if (command === "help" || command === "--help") {
    console.log("Usage: bun run cloudflare-dns.ts <command>\n");
    console.log("Commands:");
    console.log("  sync       - Sync DNS records to Cloudflare (default)");
    console.log("  list       - List existing DNS records");
    console.log("  check-ips  - Check server IPs from 1Password");
    console.log("  help       - Show this help message");
    process.exit(0);
  }

  const fn = commands[command];
  if (!fn) {
    console.error(`Unknown command: ${command}`);
    console.error("Run 'bun run cloudflare-dns.ts help' for available commands");
    process.exit(1);
  }

  fn()
    .then(() => process.exit(0))
    .catch((err) => {
      console.error("Error:", err.message);
      process.exit(1);
    });
}
