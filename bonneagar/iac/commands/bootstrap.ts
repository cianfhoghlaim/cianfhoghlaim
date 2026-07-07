// bonneagar/iac/commands/bootstrap.ts — The 1-command full bootstrap
// Mirrors the 9-phase setup-pangolin-komodo.sh in TypeScript.

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { CLI_FLAGS } from "../cli.ts";
import { syncSecrets } from "./sync-secrets.ts";
import { syncResources } from "./sync-resources.ts";
import { syncProcedures } from "./sync-procedures.ts";
import { syncResourceSyncs } from "./sync-resource-syncs.ts";
import { syncVariables } from "./sync-variables.ts";
import { syncMonitors } from "./sync-monitors.ts";
import { syncAlerts } from "./sync-alerts.ts";
import { syncSchedules } from "./sync-schedules.ts";
import { syncActionRecipients } from "./sync-action-recipients.ts";
import { syncOlm } from "./sync-olm.ts";

export async function bootstrap() {
  logStep("iac:bootstrap — end-to-end (Pulumi → Infisical → Pangolin → Komodo → Newt → all syncs)");

  // Phase 1: Pulumi (TODO — calls bonneagar/pulumi/oci/deploy.ts)
  logStep("Phase 1: Pulumi (OCI / Cloudflare) — TODO");
  logWarn("Pulumi deploy not yet automated; run mise run pulumi:deploy manually");

  // Phase 2: Infisical vault sync
  logStep("Phase 2: Infisical secrets");
  await syncSecrets();

  // Phase 3: Pangolin (deploy + configure)
  logStep("Phase 3: Pangolin private resources");
  await syncResources();

  // Phase 4: Komodo Core (deploy) — TODO
  logStep("Phase 4: Komodo Core — TODO");
  logWarn("Komodo Core deploy not yet automated; run docker compose up -d manually");

  // Phase 5: Komodo Periphery (deploy on both hosts) — TODO
  logStep("Phase 5: Komodo Periphery — TODO");
  logWarn("Komodo Periphery deploy not yet automated");

  // Phase 6: Newt (Pangolin tunnel client) — TODO
  logStep("Phase 6: Newt (Pangolin tunnel client) — TODO");
  logWarn("Newt deploy not yet automated; pull the fosrl/newt image manually");

  // Phase 7: All sync commands
  logStep("Phase 7: All sync commands");
  await syncProcedures();
  await syncResourceSyncs();
  await syncVariables();
  if (CLI_FLAGS.withMonitors) await syncMonitors();
  if (CLI_FLAGS.withAlerts) await syncAlerts();
  if (CLI_FLAGS.withSchedules) await syncSchedules();
  await syncActionRecipients();
  await syncOlm();

  // Phase 8: Optional blueprint import
  if (CLI_FLAGS.withBlueprintImport) {
    logStep("Phase 8: Blueprint import (Pangolin bulk endpoint)");
    logWarn("--with-blueprint-import is not yet implemented; use the per-resource sync path for now");
  }

  logOk("iac:bootstrap complete");
}
