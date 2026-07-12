// bonneagar/iac/commands/sync-schedules.ts — Sync Komodo schedules (cron jobs)
// OPT-IN: requires --with-schedules flag

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

// The 5 cron jobs (per the proposal)
const SCHEDULES = [
  { name: "daily-komodo-backup", cron: "0 2 * * *", target_id: "backup-komodo" },
  { name: "hourly-cdc-sync", cron: "0 * * * *", target_id: "cdc-sync" },
  { name: "nightly-secret-rotation", cron: "0 3 * * *", target_id: "rotate-secrets" },
  { name: "weekly-stack-audit", cron: "0 4 * * 0", target_id: "iac-plan" },
  { name: "monthly-dr-test", cron: "0 5 1 * *", target_id: "dr-test" },
];

export async function syncSchedules() {
  logStep("sync-schedules (5 cron jobs)");
  if (!CLI_FLAGS.withSchedules) {
    logWarn("--with-schedules not set; skipping (schedules are opt-in)");
    return;
  }

  const client = await ensureKomodoAuth();
  log(`  discovered ${SCHEDULES.length} schedules`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would create ${SCHEDULES.length} schedules`);
    return;
  }

  for (const s of SCHEDULES) {
    try {
      await client.upsertSchedule({
        name: s.name,
        config: { cron: s.cron, target: { type: "Procedure", id: s.target_id } },
        tags: ["iac:synced"],
      });
      logOk(s.name);
    } catch (e) {
      logError(s.name, e);
    }
  }
}
