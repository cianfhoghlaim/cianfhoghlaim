// bonneagar/iac/commands/health.ts — Health check all 3 systems

import { log, logStep, logOk, logError } from "../cli.ts";
import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";

// v5: the 3 GitOps resource-syncs the IaC registers + monitors.
// Any drift from this list fails the health check (drift = stale state).
const EXPECTED_RESOURCE_SYNCS = [
  "arm1-oci",        // control-plane stacks + procedures
  "bunchloch",       // workload-plane stacks + procedures
  "cross-cutting",   // 4 cross-host prerequisites (pangolin-first, komodo-core, infisical-first, locket-deploy)
];

export async function health() {
  logStep("Health check");
  let allOk = true;

  try {
    const komodo = await ensureKomodoAuth();
    const servers = await komodo.listServers();
    const stacks = await komodo.listStacks();

    // v5: add the resource-sync check (the GitOps contract).
    // The 3 resource-syncs must be registered + managed, otherwise
    // Komodo isn't doing its GitOps job (procedures are state mutations,
    // not the canonical sync).
    const resourceSyncs = await komodo.listResourceSyncs();
    const syncNames = new Set(resourceSyncs.map((s: { name: string }) => s.name));
    const missing = EXPECTED_RESOURCE_SYNCS.filter((n) => !syncNames.has(n));
    const syncDetail = missing.length === 0
      ? `${EXPECTED_RESOURCE_SYNCS.length}/${EXPECTED_RESOURCE_SYNCS.length} synced`
      : `MISSING: ${missing.join(", ")}`;
    logOk(`komodo: ${servers.length} servers, ${stacks.length} stacks, ${syncDetail}`);
    if (missing.length > 0) allOk = false;
  } catch (e) {
    logError("komodo", e);
    allOk = false;
  }

  try {
    const pangolin = await ensurePangolinAuth();
    const h = await pangolin.health();
    if (h.healthy) logOk(`pangolin: ${h.detail}`);
    else { logError("pangolin", h.detail); allOk = false; }
  } catch (e) {
    logError("pangolin", e);
    allOk = false;
  }

  try {
    const infisical = await ensureInfisicalAuth();
    const h = await infisical.health();
    if (h.healthy) logOk(`infisical: ${h.detail}`);
    else { logError("infisical", h.detail); allOk = false; }
  } catch (e) {
    logError("infisical", e);
    allOk = false;
  }

  process.exit(allOk ? 0 : 1);
}
