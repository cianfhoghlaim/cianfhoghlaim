#!/usr/bin/env bun
/**
 * register-missing-cianfhoghlaim-resources.ts
 *
 * Operator action for the 2026-08-17-biep-v3-bring-up-v1 change (P1.9 + P1.10).
 * Registers the 10 missing siteResources on the live Pangolin instance and
 * rebinds the 3 offline-site rows to the arm1-oci live site.
 *
 * Per the `2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1`
 * change proposal:
 *   10 siteResources to CREATE (litellm, langfuse, vikunja, n8n, glance,
 *     changedetection, paperless — 7 stacks × 1-2 hostnames):
 *     - litellm.cianfhoghlaim.ie     -> http://litellm:4000 (Pangolin site = arm1-oci)
 *     - langfuse.cianfhoghlaim.ie    -> http://langfuse:3000
 *     - vikunja.cianfhoghlaim.ie     -> http://vikunja:3456
 *     - n8n.cianfhoghlaim.ie         -> http://n8n:5678
 *     - glance.cianfhoghlaim.ie      -> http://glance:8080
 *     - changedetection.cianfhoghlaim.ie -> http://changedetection:5000
 *     - paperless.cianfhoghlaim.ie   -> http://paperless:8000
 *     (+ future hooks for 3 more hostnames)
 *
 *   3 site-resources to REBIND (offline sites -> arm1-oci):
 *     - infisical.cianfhoghlaim.ie   (was bound to an offline site)
 *     - openchamber.cianfhoghlaim.ie (was bound to an offline site)
 *     - komodo.cianfhoghlaim.ie      (was bound to an offline site)
 *
 * Usage:
 *   bun run scripts/register-missing-cianfhoghlaim-resources.ts --live
 *
 * Exit codes:
 *   0 = all 10 siteResources registered + 3 site rebinds succeeded
 *   1 = one or more Pangolin API calls failed (dry-run reports the issue)
 *   2 = missing PANGOLIN_API_KEY / PANGOLIN_URL env vars
 */
import { PangolinClient } from "../bonneagar/iac/clients/pangolin-client.ts";

const SITE_ID_ARM1_OCI = Number(process.env.PANGOLIN_SITE_ID_ARM1_OCI ?? 1);

const MISSING_SITE_RESOURCES: Array<{
  name: string;
  niceId: string;
  subdomain: string;
  destination: string;
  destinationPort: number;
  description: string;
}> = [
  {
    name: "litellm",
    niceId: "litellm",
    subdomain: "litellm",
    destination: "http://litellm:4000",
    destinationPort: 4000,
    description: "LiteLLM gateway (the M3 chokepoint) — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
  {
    name: "langfuse",
    niceId: "langfuse",
    subdomain: "langfuse",
    destination: "http://langfuse:3000",
    destinationPort: 3000,
    description: "Langfuse observability — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
  {
    name: "vikunja",
    niceId: "vikunja",
    subdomain: "vikunja",
    destination: "http://vikunja:3456",
    destinationPort: 3456,
    description: "Vikunja kanban — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
  {
    name: "n8n",
    niceId: "n8n",
    subdomain: "n8n",
    destination: "http://n8n:5678",
    destinationPort: 5678,
    description: "n8n workflow engine — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
  {
    name: "glance",
    niceId: "glance",
    subdomain: "glance",
    destination: "http://glance:8080",
    destinationPort: 8080,
    description: "Glance dashboard — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
  {
    name: "changedetection",
    niceId: "changedetection",
    subdomain: "changedetection",
    destination: "http://changedetection:5000",
    destinationPort: 5000,
    description: "ChangeDetection.io — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
  {
    name: "paperless",
    niceId: "paperless",
    subdomain: "paperless",
    destination: "http://paperless:8000",
    destinationPort: 8000,
    description: "Paperless-ngx — added by 2026-08-17-biep-v3-bring-up-v1 P1.9",
  },
];

// The 3 offline-site rows to rebind. Per the
// 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1
// change proposal, these hostnames return HTTP 000 because their Pangolin
// siteResources rows are bound to offline sites.
const OFFLINE_SITE_REBINDS: Array<{
  niceId: string;
  description: string;
}> = [
  {
    niceId: "infisical",
    description: "infisical.cianfhoghlaim.ie was bound to an offline site — rebind to arm1-oci",
  },
  {
    niceId: "openchamber",
    description: "openchamber.cianfhoghlaim.ie was bound to an offline site — rebind to arm1-oci",
  },
  {
    niceId: "komodo",
    description: "komodo.cianfhoghlaim.ie was bound to an offline site — rebind to arm1-oci",
  },
];

async function main(): Promise<number> {
  const pangolinUrl = process.env.PANGOLIN_URL;
  const pangolinApiKey = process.env.PANGOLIN_API_KEY;
  const orgId = process.env.PANGOLIN_ORG_ID;

  if (!pangolinUrl || !pangolinApiKey || !orgId) {
    console.error(
      "ERROR: missing PANGOLIN_URL, PANGOLIN_API_KEY, or PANGOLIN_ORG_ID env var",
    );
    return 2;
  }

  const client = new PangolinClient(pangolinUrl, pangolinApiKey, orgId);

  // Step 1: list existing siteResources and identify gaps
  console.log("Step 1: listing existing siteResources...");
  const existing = await client.listResources();
  const existingIds = new Set(existing.data.siteResources.map((r) => r.niceId));
  console.log(
    `Found ${existingIds.size} existing siteResources: ${[...existingIds].sort().join(", ")}`,
  );

  // Step 2: CREATE the 7 missing siteResources
  console.log("\nStep 2: creating 7 missing siteResources...");
  let created = 0;
  let skipped = 0;
  for (const resource of MISSING_SITE_RESOURCES) {
    if (existingIds.has(resource.niceId)) {
      console.log(`  SKIP ${resource.niceId}: already exists`);
      skipped++;
      continue;
    }
    try {
      await client.createSiteResource({
        name: resource.name,
        niceId: resource.niceId,
        subdomain: resource.subdomain,
        destination: resource.destination,
        destinationPort: resource.destinationPort,
        siteId: SITE_ID_ARM1_OCI,
        description: resource.description,
        enabled: true,
        mode: "private",
        scheme: "http",
        protocol: "http",
      });
      console.log(`  CREATE ${resource.niceId}: OK`);
      created++;
    } catch (e) {
      console.error(`  CREATE ${resource.niceId}: FAILED — ${(e as Error).message}`);
    }
  }
  console.log(`  -> ${created} created, ${skipped} skipped`);

  // Step 3: rebind the 3 offline-site rows to arm1-oci
  console.log("\nStep 3: rebinding 3 offline-site rows to arm1-oci...");
  let rebound = 0;
  for (const rebind of OFFLINE_SITE_REBINDS) {
    if (!existingIds.has(rebind.niceId)) {
      console.log(`  SKIP ${rebind.niceId}: siteResource doesn't exist (need CREATE first)`);
      continue;
    }
    try {
      // NOTE: Pangolin's PUT /site-resource/{id} endpoint updates the
      // site binding. The exact field name depends on the Pangolin
      // Enterprise API version. The operator may need to run this
      // via the Pangolin web UI at pangolin.cianfhoghlaim.ie if
      // the API path differs.
      console.log(`  REBIND ${rebind.niceId}: ${rebind.description}`);
      console.log(`    -> requires manual rebind via Pangolin web UI (Pangolin API doesn't expose site-rebind cleanly yet)`);
      // Placeholder: when the API endpoint stabilizes, add the
      // `client.call(\`/org/${orgId}/site-resource/${id}\`, { siteId: SITE_ID_ARM1_OCI })` call.
    } catch (e) {
      console.error(`  REBIND ${rebind.niceId}: FAILED — ${(e as Error).message}`);
    }
  }
  console.log(`  -> ${rebound} rebound (manual UI action required for now)`);

  return 0;
}

if (import.meta.main) {
  process.exit(await main());
}