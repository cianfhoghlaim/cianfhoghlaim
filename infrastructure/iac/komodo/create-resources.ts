// Pangolin IaC — Create/update private resources via the Pangolin Integrations API.
// https://docs.pangolin.net/manage/integration-api

import { CONFIG } from "./config.ts";

interface PangolinResource {
  orgId: string;
  siteId: string;
  name: string;
  subdomain: string;
  destination: string;
  destinationPort: number;
  // Optional: fullDomain override
  fullDomain?: string;
  // Optional: description
  description?: string;
}

const RESOURCES: PangolinResource[] = [
  {
    orgId: "cianfhoghlaim",
    siteId: "bunchloch", // mbp newt site
    name: "Komodo Core",
    subdomain: "komodo",
    destination: "komodo-core:9120",
    destinationPort: 9120,
    description: "Komodo Core orchestration engine (mbp)",
  },
  {
    orgId: "cianfhoghlaim",
    siteId: "arm1-oci", // arm1-oci site (uses gerbil for routing)
    name: "Cal.com (cal-diy)",
    subdomain: "calcom",
    destination: "calcom-web:3000",
    destinationPort: 3000,
    description: "Cal.com (cal-diy build) — scheduling UI",
  },
  {
    orgId: "cianfhoghlaim",
    siteId: "arm1-oci",
    name: "Infisical Vault",
    subdomain: "infisical",
    destination: "infisical-backend:8080",
    destinationPort: 8080,
    description: "Self-hosted Infisical secret vault",
  },
];

// ============================================================================
// Pangolin RPC client (bare-metal fetch wrapper)
// ============================================================================

class PangolinRpc {
  constructor(
    private url: string = CONFIG.pangolinUrl,
    private apiKey: string = CONFIG.pangolinApiKey,
  ) {}

  private async call<T>(path: string, body: unknown = {}): Promise<T> {
    const r = await fetch(`${this.url}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`pangolin ${path} failed: ${r.status} ${text}`);
    }
    return r.json() as Promise<T>;
  }

  // ----- Sites / Resources -----
  async listSites() {
    return this.call<unknown[]>(`/api/v1/orgs/${RESOURCES[0]?.orgId ?? "default"}/sites`);
  }

  async listResources(orgId: string) {
    return this.call<unknown[]>(`/api/v1/orgs/${orgId}/resources`);
  }

  async createResource(orgId: string, siteId: string, body: Record<string, unknown>) {
    return this.call(`/api/v1/orgs/${orgId}/sites/${siteId}/resources`, body);
  }

  async updateResource(orgId: string, resourceId: string, body: Record<string, unknown>) {
    return this.call(`/api/v1/orgs/${orgId}/resources/${resourceId}`, body);
  }
}

// ============================================================================
// Main
// ============================================================================

async function main() {
  if (!CONFIG.pangolinApiKey) {
    console.error("PANGOLIN_API_KEY not set. Get one from Pangolin UI → Settings → API Keys");
    process.exit(1);
  }

  const pangolin = new PangolinRpc();

  console.log("→ Listing existing resources");
  let existing: any[] = [];
  try {
    existing = await pangolin.listResources(RESOURCES[0].orgId);
  } catch (e) {
    console.log("  (could not list — site/org may not exist yet)");
  }

  for (const r of RESOURCES) {
    console.log(`→ ${r.subdomain}.cianfhoghlaim.ie → ${r.destination}:${r.destinationPort}`);
    const found = existing.find((e: any) => e.subdomain === r.subdomain);

    const body = {
      name: r.name,
      subdomain: r.subdomain,
      description: r.description ?? "",
      destination: r.destination,
      destinationPort: r.destinationPort,
      protocol: "tcp",
      // For HTTP services, the newt will proxy the request to the destination.
      http: true,
      enabled: true,
    };

    try {
      if (found) {
        console.log(`  - already exists (id=${found.id}); updating`);
        await pangolin.updateResource(r.orgId, found.id, body);
      } else {
        console.log("  - creating");
        await pangolin.createResource(r.orgId, r.siteId, body);
      }
    } catch (e) {
      console.error(`  ! failed: ${(e as Error).message}`);
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
