// bonneagar/iac/commands/sync-olm.ts — Sync Pangolin OLM clients
// (OLM = Org Lifecycle Manager; the Enterprise Edition TCP-tunnel feature)

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensurePangolinAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

// The OLM clients (per the v0 olm-resources.blueprint.yaml; the 2 manually-created)
const OLM_CLIENTS = [
  { name: "arm1-oci-olm", siteId: 2 },
  { name: "cax41-hetzner-olm", siteId: 2 },
];

export async function syncOlm() {
  logStep("sync-olm");
  const client = await ensurePangolinAuth();
  log(`  discovered ${OLM_CLIENTS.length} OLM clients`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would create ${OLM_CLIENTS.length} OLM clients`);
    return;
  }

  for (const o of OLM_CLIENTS) {
    try {
      await client.createOlmClient({ ...o });
      logOk(o.name);
    } catch (e) {
      // Probably already exists — that's fine
      logWarn(`${o.name} (probably exists): ${(e as Error).message.slice(0, 80)}`);
    }
  }
}
