// =============================================================================
// SYNC DNS RECORDS ACTION
// =============================================================================
// Syncs DNS records to Cloudflare based on server IPs from Komodo.
// Run this after infrastructure changes or as pre-deploy validation.
//
// Usage:
//   km run action sync-dns-records --dryRun=true
//   km run action sync-dns-records --domain=cianfhoghlaim.ie
// =============================================================================

const dryRun = ARGS.dryRun || false;
const domain = ARGS.domain || "cianfhoghlaim.ie";

interface DnsRecord {
  name: string;
  type: "A" | "AAAA" | "CNAME";
  server: string; // Komodo server name to resolve IP from
  proxied?: boolean;
}

interface CloudflareDnsRecord {
  id: string;
  name: string;
  type: string;
  content: string;
  proxied: boolean;
}

// DNS records to manage - maps subdomains to Komodo servers
const DNS_RECORDS: DnsRecord[] = [
  // Core services on OCI
  { name: "komodo", type: "A", server: "arm1-oci", proxied: true },
  { name: "pangolin", type: "A", server: "arm1-oci", proxied: true },
  { name: "auth", type: "A", server: "arm1-oci", proxied: true },
  // Wildcard for Pangolin tunnels
  { name: "*", type: "A", server: "arm1-oci", proxied: true },
];

// Results tracking
const results: { record: string; action: string; status: string }[] = [];

// Get Cloudflare credentials from Komodo variables
const cfApiToken = await komodo.read("GetVariable", { name: "CLOUDFLARE_API_TOKEN" });
const cfZoneId = await komodo.read("GetVariable", { name: "CLOUDFLARE_ZONE_ID" });

if (!cfApiToken?.value || !cfZoneId?.value) {
  return {
    success: false,
    error: "Missing Cloudflare credentials. Set CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID variables in Komodo.",
  };
}

// Get server IPs from Komodo
const servers = await komodo.read("ListServers", {});
const serverIps: Record<string, string> = {};

for (const server of servers) {
  // Get server details to extract IP
  const details = await komodo.read("GetServer", { server: server.name });
  if (details?.config?.address) {
    // Extract IP from address (remove port if present)
    const ip = details.config.address.replace(/:\d+$/, "").replace(/^https?:\/\//, "");
    serverIps[server.name] = ip;
    console.log(`  Server ${server.name}: ${ip}`);
  }
}

// Fetch existing DNS records from Cloudflare
console.log("\nFetching existing DNS records from Cloudflare...");
const cfResponse = await fetch(
  `https://api.cloudflare.com/client/v4/zones/${cfZoneId.value}/dns_records`,
  {
    headers: {
      Authorization: `Bearer ${cfApiToken.value}`,
      "Content-Type": "application/json",
    },
  }
);

if (!cfResponse.ok) {
  const error = await cfResponse.text();
  return { success: false, error: `Cloudflare API error: ${cfResponse.status} - ${error}` };
}

const cfData = (await cfResponse.json()) as { result: CloudflareDnsRecord[] };
const existingRecords = cfData.result;
console.log(`  Found ${existingRecords.length} existing records`);

// Process each DNS record
console.log("\nSyncing DNS records...\n");

for (const record of DNS_RECORDS) {
  const ip = serverIps[record.server];
  if (!ip) {
    console.log(`  SKIP ${record.name}: Server ${record.server} not found or has no IP`);
    results.push({ record: record.name, action: "skip", status: `Server ${record.server} not found` });
    continue;
  }

  const fullName = record.name === "@" ? domain : `${record.name}.${domain}`;
  const existing = existingRecords.find((r) => r.name === fullName && r.type === record.type);

  if (existing) {
    if (existing.content === ip) {
      console.log(`  OK ${fullName} -> ${ip}`);
      results.push({ record: fullName, action: "none", status: "Already correct" });
    } else if (!dryRun) {
      // Update existing record
      const updateResponse = await fetch(
        `https://api.cloudflare.com/client/v4/zones/${cfZoneId.value}/dns_records/${existing.id}`,
        {
          method: "PATCH",
          headers: {
            Authorization: `Bearer ${cfApiToken.value}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            type: record.type,
            name: fullName,
            content: ip,
            proxied: record.proxied ?? false,
          }),
        }
      );
      if (updateResponse.ok) {
        console.log(`  UPDATE ${fullName}: ${existing.content} -> ${ip}`);
        results.push({ record: fullName, action: "update", status: "Updated" });
      } else {
        console.log(`  FAILED ${fullName}: Update failed`);
        results.push({ record: fullName, action: "update", status: "Failed" });
      }
    } else {
      console.log(`  WOULD UPDATE ${fullName}: ${existing.content} -> ${ip}`);
      results.push({ record: fullName, action: "update (dry-run)", status: `Would change to ${ip}` });
    }
  } else if (!dryRun) {
    // Create new record
    const createResponse = await fetch(
      `https://api.cloudflare.com/client/v4/zones/${cfZoneId.value}/dns_records`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${cfApiToken.value}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          type: record.type,
          name: fullName,
          content: ip,
          proxied: record.proxied ?? false,
          ttl: 1, // Auto
        }),
      }
    );
    if (createResponse.ok) {
      console.log(`  CREATE ${fullName} -> ${ip}`);
      results.push({ record: fullName, action: "create", status: "Created" });
    } else {
      console.log(`  FAILED ${fullName}: Create failed`);
      results.push({ record: fullName, action: "create", status: "Failed" });
    }
  } else {
    console.log(`  WOULD CREATE ${fullName} -> ${ip}`);
    results.push({ record: fullName, action: "create (dry-run)", status: `Would create with ${ip}` });
  }
}

return {
  success: true,
  dryRun,
  domain,
  totalRecords: DNS_RECORDS.length,
  results,
};
