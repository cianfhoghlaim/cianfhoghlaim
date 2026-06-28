// Pangolin IaC — Create/update private resources via the Pangolin Integrations API.
// https://docs.pangolin.net/manage/integration-api
//
// The integration API is at ${PANGOLIN_URL}/v1 (not /api/v1 which is the
// dashboard API). Endpoints follow the OpenAPI spec emitted by the
// running Pangolin server at /app/config/openapi.yaml.

import { CONFIG } from "./config.ts";

interface PangolinResource {
  name: string;
  niceId: string;
  subdomain: string;
  destination: string;
  destinationPort: number;
  siteId: number;
  description?: string;
  mode?: "http" | "host" | "cidr";
  scheme?: "http" | "https";
}

const RESOURCES: PangolinResource[] = [
  {
    name: "Komodo Core",
    niceId: "komodo",
    subdomain: "komodo",
    destination: "komodo-core",
    destinationPort: 9120,
    siteId: 1, // bunchloch (mbp)
    description: "Komodo Core orchestration engine",
  },
  {
    name: "Cal.com (cal-diy)",
    niceId: "calcom",
    subdomain: "calcom",
    destination: "calcom-web",
    destinationPort: 3000,
    siteId: 2, // arm1-oci
    description: "Cal.com (cal-diy) — scheduling UI",
  },
  {
    name: "Infisical Vault",
    niceId: "infisical",
    subdomain: "infisical",
    destination: "infisical-backend",
    destinationPort: 8080,
    siteId: 2, // arm1-oci
    description: "Self-hosted Infisical secret vault",
  },
];

// ============================================================================
// Pangolin RPC client
// ============================================================================

class PangolinRpc {
  constructor(
    private base: string = CONFIG.pangolinApiBase,
    private apiKey: string = CONFIG.pangolinApiKey,
    private orgId: string = CONFIG.pangolinOrgId,
  ) {}

  private async call<T>(path: string, body: unknown = {}): Promise<T> {
    const r = await fetch(`${this.base}${path}`, {
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

  private async callGet<T>(path: string): Promise<T> {
    const r = await fetch(`${this.base}${path}`, {
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`pangolin GET ${path} failed: ${r.status} ${text}`);
    }
    return r.json() as Promise<T>;
  }

  async listSites() {
    return this.callGet<{ data: { sites: any[] } }>(`/org/${this.orgId}/sites`);
  }

  async listResources() {
    return this.callGet<{ data: { siteResources: any[] } }>(
      `/org/${this.orgId}/site-resources`,
    );
  }

  async createSiteResource(body: Record<string, unknown>) {
    return this.call(`/org/${this.orgId}/site-resource`, body);
  }

  async deleteSiteResource(id: number) {
    const r = await fetch(`${this.base}/site-resource/${id}`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${this.apiKey}` },
    });
    if (!r.ok) throw new Error(`delete ${id} failed: ${r.status} ${await r.text()}`);
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
  const { data } = await pangolin.listResources();
  const existing = data.siteResources;
  console.log(`  found ${existing.length} existing resources`);

  for (const r of RESOURCES) {
    console.log(`→ ${r.subdomain}.cianfhoghlaim.ie → ${r.destination}:${r.destinationPort}`);

    // Find existing match by fullDomain
    const fullDomain = `${r.subdomain}.cianfhoghlaim.ie`;
    const found = existing.find((e: any) => e.fullDomain === fullDomain);

    const body = {
      name: r.name,
      niceId: r.niceId,
      mode: r.mode ?? "http",
      scheme: r.scheme ?? "https",
      siteId: r.siteId,
      domainId: "cianfhoghlaim",
      subdomain: r.subdomain,
      destination: r.destination,
      destinationPort: r.destinationPort,
      enabled: true,
      userIds: [],
      roleIds: [],
      clientIds: [],
    };

    try {
      if (found) {
        console.log(`  - already exists (id=${found.siteResourceId}); leaving alone (no PATCH endpoint)`);
        continue;
      }
      console.log("  - creating");
      const res = await pangolin.createSiteResource(body);
      console.log(`  ✓ siteResourceId=${(res as any).data.siteResourceId}`);
    } catch (e) {
      console.error(`  ! failed: ${(e as Error).message}`);
    }
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
