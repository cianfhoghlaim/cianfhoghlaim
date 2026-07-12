// bonneagar/iac/commands/sync-alerts.ts — Sync Komodo alerts (failure notifications)
// OPT-IN: requires --with-alerts flag

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

// The 4 critical failure paths (per the proposal)
const ALERTS = [
  { name: "komodo-deploy-failed", level: "CRITICAL" as const, target_type: "Procedure" as const, target_id: "deploy-stack" },
  { name: "komodo-backup-failed", level: "WARNING" as const, target_type: "Procedure" as const, target_id: "backup-komodo" },
  { name: "host-down", level: "CRITICAL" as const, target_type: "Server" as const, target_id: "all" },
  { name: "monitor-failing", level: "WARNING" as const, target_type: "Monitor" as const, target_id: "all" },
];

export async function syncAlerts() {
  logStep("sync-alerts (4 critical failure paths)");
  if (!CLI_FLAGS.withAlerts) {
    logWarn("--with-alerts not set; skipping (alerts are opt-in)");
    return;
  }

  const client = await ensureKomodoAuth();
  log(`  discovered ${ALERTS.length} alert paths`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would create ${ALERTS.length} alerts`);
    return;
  }

  for (const a of ALERTS) {
    try {
      await client.upsertAlert({
        name: a.name,
        config: {
          target: { type: a.target_type as any, id: a.target_id },
          level: a.level,
          recipients: ["discord"],
        },
        tags: ["iac:synced"],
      });
      logOk(a.name);
    } catch (e) {
      logError(a.name, e);
    }
  }
}
