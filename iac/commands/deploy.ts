// bonneagar/iac/commands/deploy.ts — The deploy command (10 sync commands in order)

import { log, logStep, logOk } from "../cli.ts";
import { syncSecrets } from "./sync-secrets.ts";
import { syncProcedures } from "./sync-procedures.ts";
import { syncResourceSyncs } from "./sync-resource-syncs.ts";
import { syncVariables } from "./sync-variables.ts";
import { syncResources } from "./sync-resources.ts";
import { syncMonitors } from "./sync-monitors.ts";
import { syncAlerts } from "./sync-alerts.ts";
import { syncSchedules } from "./sync-schedules.ts";
import { syncActionRecipients } from "./sync-action-recipients.ts";
import { syncOlm } from "./sync-olm.ts";
import { CLI_FLAGS } from "../cli.ts";

export async function deploy() {
  logStep("iac:deploy — 10 sync commands in order");
  await syncSecrets();
  await syncProcedures();
  await syncResourceSyncs();
  await syncVariables();
  await syncResources();
  if (CLI_FLAGS.withMonitors) await syncMonitors();
  if (CLI_FLAGS.withAlerts) await syncAlerts();
  if (CLI_FLAGS.withSchedules) await syncSchedules();
  await syncActionRecipients();
  await syncOlm();
  logOk("iac:deploy complete");
}
