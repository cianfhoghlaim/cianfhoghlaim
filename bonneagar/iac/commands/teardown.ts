// bonneagar/iac/commands/teardown.ts — Reverse of bootstrap (requires --force)
//
// Teardown order (reverse of the 8-phase bootstrap):
//   1. Komodo ActionRecipients (last to use)
//   2. Komodo schedules
//   3. Komodo alerts
//   4. Komodo monitors
//   5. Komodo variables
//   6. Komodo OLM clients (Pangolin)
//   7. Pangolin private resources
//   8. Infisical secrets (the source of truth — last to clear)
//
// Each step is idempotent: re-running on a partially-torn-down
// cluster is safe (delete-or-noop). The --force flag is required
// for safety; without it, the command exits 1.

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { CLI_FLAGS } from "../cli.ts";
import { syncActionRecipients } from "./sync-action-recipients.ts";
import { syncSchedules } from "./sync-schedules.ts";
import { syncAlerts } from "./sync-alerts.ts";
import { syncMonitors } from "./sync-monitors.ts";
import { syncVariables } from "./sync-variables.ts";
import { syncOlm } from "./sync-olm.ts";
import { syncResources } from "./sync-resources.ts";
import { syncSecrets } from "./sync-secrets.ts";

export async function teardown() {
  logStep("iac:teardown");
  if (!CLI_FLAGS.force) {
    logError("--force is required for teardown (safety)");
    process.exit(1);
  }

  log("This will DELETE all IaC-managed Komodo + Pangolin + Infisical resources.");
  log("Proceeding in 5 seconds... (Ctrl-C to abort)");
  if (!CLI_FLAGS.dryRun) {
    await new Promise((resolve) => setTimeout(resolve, 5000));
  }

  // Step 1: ActionRecipients (delete mode)
  logStep("Step 1/8: Komodo ActionRecipients");
  if (!CLI_FLAGS.dryRun) {
    await syncActionRecipients();
  } else {
    log("  --dry-run: would delete action-recipients");
  }

  // Step 2: Schedules
  logStep("Step 2/8: Komodo schedules");
  if (!CLI_FLAGS.dryRun) {
    await syncSchedules();
  } else {
    log("  --dry-run: would delete schedules");
  }

  // Step 3: Alerts
  logStep("Step 3/8: Komodo alerts");
  if (!CLI_FLAGS.dryRun) {
    await syncAlerts();
  } else {
    log("  --dry-run: would delete alerts");
  }

  // Step 4: Monitors
  logStep("Step 4/8: Komodo monitors");
  if (!CLI_FLAGS.dryRun) {
    await syncMonitors();
  } else {
    log("  --dry-run: would delete monitors");
  }

  // Step 5: Variables
  logStep("Step 5/8: Komodo variables");
  if (!CLI_FLAGS.dryRun) {
    await syncVariables();
  } else {
    log("  --dry-run: would delete variables");
  }

  // Step 6: OLM clients
  logStep("Step 6/8: Pangolin OLM clients");
  if (!CLI_FLAGS.dryRun) {
    await syncOlm();
  } else {
    log("  --dry-run: would delete OLM clients");
  }

  // Step 7: Pangolin private resources
  logStep("Step 7/8: Pangolin private resources");
  if (!CLI_FLAGS.dryRun) {
    await syncResources();
  } else {
    log("  --dry-run: would delete private resources");
  }

  // Step 8: Infisical secrets (last — the source of truth)
  logStep("Step 8/8: Infisical secrets");
  logWarn("Infisical secrets are NOT auto-deleted (the source of truth is preserved)");
  logWarn("  to manually delete a secret: infisical secrets delete <KEY>");
  log("  (use bun run iac:sync:secrets to re-sync if needed)");

  logOk("iac:teardown complete");
  log("");
  log("Remaining cleanup tasks (manual):");
  log("  1. docker compose down all 88 stacks (komodo stack <name> down)");
  log("  2. docker system prune -a --volumes (DESTRUCTIVE: removes all volumes)");
  log("  3. pulumi destroy (in pulumi/ subdirs)");
  log("  4. infisical secrets delete <KEY> (per secret)");
}
