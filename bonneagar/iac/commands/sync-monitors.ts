// bonneagar/iac/commands/sync-monitors.ts — Sync Komodo monitors (HTTP health checks)
// OPT-IN: requires --with-monitors flag

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { discoverResources } from "../sources/discover-resources.ts";
import { CLI_FLAGS } from "../cli.ts";

export async function syncMonitors() {
  logStep("sync-monitors (HTTP health checks for every Pangolin-routed stack)");
  if (!CLI_FLAGS.withMonitors) {
    logWarn("--with-monitors not set; skipping (monitors are opt-in)");
    return;
  }

  const client = await ensureKomodoAuth();
  const resources = discoverResources();
  log(`  discovered ${resources.length} resources`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would create ${resources.length} monitors`);
    return;
  }

  for (const r of resources) {
    try {
      await client.upsertMonitor({
        name: `health-check-${r.niceId}`,
        config: {
          resource_type: "Server",
          resource_id: "all",
          http_check: {
            url: `https://${r.subdomain}.cianfhoghlaim.ie/api/health`,
            method: "GET",
            interval_secs: 60,
          },
        },
        tags: ["iac:synced"],
      });
      logOk(`health-check-${r.niceId}`);
    } catch (e) {
      logError(`health-check-${r.niceId}`, e);
    }
  }
}
