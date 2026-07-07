// bonneagar/iac/commands/health.ts — Health check all 3 systems

import { log, logStep, logOk, logError } from "../cli.ts";
import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";

export async function health() {
  logStep("Health check");
  let allOk = true;

  try {
    const komodo = await ensureKomodoAuth();
    const servers = await komodo.listServers();
    const stacks = await komodo.listStacks();
    logOk(`komodo: ${servers.length} servers, ${stacks.length} stacks`);
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
