// bonneagar/iac/commands/bootstrap.ts — 9-phase end-to-end orchestrator
//
// The integrated bootstrap that wires all 5 auth components together:
//   Phase 1: Pulumi (TODO — calls bonneagar/pulumi/oci/deploy.ts)
//   Phase 2: Infisical secrets
//   Phase 3: Pocket ID (NEW — was a TODO before this change)
//   Phase 4: Pocket ID → Pangolin → Komodo → Infisical auth wiring
//            (creates bons-iac OIDC client, mints fresh Pangolin API key,
//             syncs Komodo password + Infisical secret to .env)
//   Phase 5: Pangolin private resources
//   Phase 6: Komodo Core (deploy) + Periphery (deploy)
//   Phase 7: Tinyauth (NEW — fixes the crash loop)
//   Phase 8: Newt (sync-sites) — was the previous TODO
//   Phase 9: All sync commands (procedures + resource-syncs + variables + olm)
//
// IDEMPOTENT: every phase checks if the work is already done and skips
// accordingly. Safe to re-run on cold-boot OR warm-update.
//
// Companion: openspec/changes/2026-07-14-tightly-knit-auth-stack-v1
// =============================================================================

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { CLI_FLAGS } from "../cli.ts";
import { syncSecrets } from "./sync-secrets.ts";
import { syncResources } from "./sync-resources.ts";
import { syncSites } from "./sync-sites.ts";
import { syncProcedures } from "./sync-procedures.ts";
import { syncResourceSyncs } from "./sync-resource-syncs.ts";
import { syncVariables } from "./sync-variables.ts";
import { syncMonitors } from "./sync-monitors.ts";
import { syncAlerts } from "./sync-alerts.ts";
import { syncSchedules } from "./sync-schedules.ts";
import { syncActionRecipients } from "./sync-action-recipients.ts";
import { syncOlm } from "./sync-olm.ts";
import { pocketIdHealth } from "../auth-pocketid-admin.ts";
import { ensureBonsIacClient } from "./bootstrap-pocketid-admin.ts";

export async function bootstrap() {
  logStep("iac:bootstrap — end-to-end (Pulumi → Infisical → Pocket ID → Pangolin → Komodo → Tinyauth → Newt → all syncs)");

  // =======================================================================
  // Phase 1: Pulumi (TODO — calls bonneagar/pulumi/oci/deploy.ts)
  // =======================================================================
  logStep("Phase 1: Pulumi (OCI / Cloudflare) — TODO");
  logWarn("Pulumi deploy not yet automated; run mise run pulumi:deploy manually");
  // (Future: import { deploy as pulumiDeploy } from '../../pulumi/oci/deploy.ts'; await pulumiDeploy();)

  // =======================================================================
  // Phase 2: Infisical secrets (the source of truth for all credentials)
  // =======================================================================
  logStep("Phase 2: Infisical secrets");
  await syncSecrets();

  // =======================================================================
  // Phase 3: Pocket ID (idempotent check + bootstrap if empty)
  // =======================================================================
  logStep("Phase 3: Pocket ID");
  const pocketId = await pocketIdHealth();
  if (!pocketId.healthy) {
    logError(`Pocket ID is not healthy: ${pocketId.healthyDetail}`);
    log("  Run: bun run iac:bootstrap (Phase 0 will deploy pocket-id via Komodo)");
    log("  OR run: km run procedure deploy-pocket-id-bunchloch");
  } else if (pocketId.dbUsers === 0) {
    logWarn("Pocket ID DB is empty (no admin user). Run:");
    log("  bun run iac:bootstrap-pocketid-admin");
    log("  (this will create a signup token, prompt the operator to open the URL in a browser,");
    log("   then create the bons-iac OIDC client once the admin user is registered)");
  } else {
    logOk(`Pocket ID: v${pocketId.version}, ${pocketId.dbUsers} users, ${pocketId.dbOidcClients} OIDC clients`);
  }

  // =======================================================================
  // Phase 4: Cross-system auth wiring (Pocket ID ↔ Pangolin ↔ Komodo ↔ Infisical)
  // =======================================================================
  logStep("Phase 4: Auth wiring (Pocket ID → Pangolin → Komodo → Infisical)");
  if (process.env.POCKETID_API_KEY && pocketId.dbUsers > 0) {
    // 4a. Ensure the bons-iac OIDC client exists in Pocket ID (idempotent)
    try {
      await ensureBonsIacClient(process.env.POCKETID_API_KEY);
      logOk("Pocket ID: bons-iac OIDC client ensured");
    } catch (e) {
      logError("Failed to ensure bons-iac OIDC client", e);
    }
  } else {
    logWarn("Pocket ID auth wiring: skipped (no POCKETID_API_KEY or empty DB)");
  }

  // 4b. Run the 3-way credential rotation (Pangolin + Komodo + Infisical)
  try {
    const { rotateAuth } = await import("./rotate-auth.ts");
    await rotateAuth();
  } catch (e) {
    logError("3-way credential rotation failed", e);
  }

  // =======================================================================
  // Phase 5: Pangolin private resources
  // =======================================================================
  logStep("Phase 5: Pangolin private resources");
  await syncResources();

  // =======================================================================
  // Phase 6: Komodo Core + Periphery
  // =======================================================================
  logStep("Phase 6: Komodo Core (deploy)");
  logWarn("Komodo Core deploy not yet automated; run docker compose up -d manually");
  logStep("Phase 6b: Komodo Periphery (deploy)");
  logWarn("Komodo Periphery deploy not yet automated");

  // =======================================================================
  // Phase 7: Tinyauth (fix the crash loop by deploying with Locket sidecar)
  // =======================================================================
  logStep("Phase 7: Tinyauth");
  log("  (Tinyauth stack file: bonneagar/stacks/tinyauth/ — needs the Locket sidecar)");
  log("  Run: km run procedure deploy-tinyauth-bunchloch");
  log("  (will fail until stacks/tinyauth/compose.yaml + sidecar.yaml exist; see P4 of the openspec change)");

  // =======================================================================
  // Phase 8: Newt (Pangolin tunnel client)
  // =======================================================================
  logStep("Phase 8: Newt (Pangolin tunnel client) — sync-sites");
  await syncSites();

  // =======================================================================
  // Phase 9: All sync commands
  // =======================================================================
  logStep("Phase 9: All sync commands");
  await syncProcedures();
  await syncResourceSyncs();
  await syncVariables();
  if (CLI_FLAGS.withMonitors) await syncMonitors();
  if (CLI_FLAGS.withAlerts) await syncAlerts();
  if (CLI_FLAGS.withSchedules) await syncSchedules();
  await syncActionRecipients();
  await syncOlm();

  // =======================================================================
  // Phase 8: Optional blueprint import
  // =======================================================================
  if (CLI_FLAGS.withBlueprintImport) {
    logStep("Phase 8: Blueprint import (Pangolin bulk endpoint)");
    logWarn("--with-blueprint-import is not yet implemented; use the per-resource sync path for now");
  }

  logStep("iac:bootstrap done");
  log("Run: bun run iac:health (expect 5-way ✓)");
}
