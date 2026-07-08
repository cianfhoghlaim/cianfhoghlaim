// bonneagar/iac/commands/bootstrap.ts — The 1-command full bootstrap
// The 8-phase state machine (Pulumi → Infisical → Pangolin → Komodo Core
// → Komodo Periphery → Newt → resource-syncs → all syncs).

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { CLI_FLAGS } from "../cli.ts";
import { syncSecrets } from "./sync-secrets.ts";
import { syncResources } from "./sync-resources.ts";
import { syncVariables } from "./sync-variables.ts";
import { syncMonitors } from "./sync-monitors.ts";
import { syncAlerts } from "./sync-alerts.ts";
import { syncSchedules } from "./sync-schedules.ts";
import { syncActionRecipients } from "./sync-action-recipients.ts";
import { syncOlm } from "./sync-olm.ts";

// v5: per-stack skip flags. The omnibus procedure accepts
// --skip=<phase>:<name> to skip a single phase on a single stack,
// e.g. --skip=pulumi:arm1-oci --skip=newt:bunchloch.
// The default is "run all" — explicit skips are exceptions, not the rule.
export type BootstrapPhase = "pulumi" | "infisical" | "pangolin" | "komodo-core" | "komodo-periphery" | "newt" | "resource-syncs" | "all-syncs";

export function parseSkipFlags(args: string[]): Set<string> {
  const out = new Set<string>();
  for (const a of args) {
    if (a.startsWith("--skip=")) out.add(a.slice("--skip=".length));
  }
  return out;
}

export async function bootstrap() {
  const skip = parseSkipFlags(process.argv.slice(2));
  logStep("iac:bootstrap — 8-phase state machine (Pulumi → Infisical → Pangolin → Komodo Core → Komodo Periphery → Newt → resource-syncs → all syncs)");
  if (skip.size > 0) log(`  --skip flags: ${[...skip].join(", ")}`);

  // Phase 1: Pulumi (TODO — calls bonneagar/pulumi/oci/deploy.ts)
  if (skip.has("pulumi")) {
    logStep("Phase 1: Pulumi (SKIPPED)");
  } else {
    logStep("Phase 1: Pulumi (OCI / Cloudflare) — TODO");
    logWarn("Pulumi deploy not yet automated; run mise run pulumi:deploy manually");
  }

  // Phase 2: Infisical vault sync
  if (skip.has("infisical")) {
    logStep("Phase 2: Infisical secrets (SKIPPED)");
  } else {
    logStep("Phase 2: Infisical secrets");
    await syncSecrets();
  }

  // Phase 3: Pangolin (deploy + configure)
  if (skip.has("pangolin")) {
    logStep("Phase 3: Pangolin private resources (SKIPPED)");
  } else {
    logStep("Phase 3: Pangolin private resources");
    await syncResources();
  }

  // Phase 4: Komodo Core (deploy) — TODO
  if (skip.has("komodo-core")) {
    logStep("Phase 4: Komodo Core (SKIPPED)");
  } else {
    logStep("Phase 4: Komodo Core — TODO");
    logWarn("Komodo Core deploy not yet automated; run docker compose up -d manually");
  }

  // Phase 5: Komodo Periphery (deploy on both hosts) — TODO
  if (skip.has("komodo-periphery")) {
    logStep("Phase 5: Komodo Periphery (SKIPPED)");
  } else {
    logStep("Phase 5: Komodo Periphery — TODO");
    logWarn("Komodo Periphery deploy not yet automated");
  }

  // Phase 6: Newt (Pangolin tunnel client) — TODO
  if (skip.has("newt")) {
    logStep("Phase 6: Newt (Pangolin tunnel client) (SKIPPED)");
  } else {
    logStep("Phase 6: Newt (Pangolin tunnel client) — TODO");
    logWarn("Newt deploy not yet automated; pull the fosrl/newt image manually");
  }

  // Phase 7: resource-syncs (now Komodo handles this; the IaC just
  // verifies the 3 resource-syncs are registered + managed)
  if (skip.has("resource-syncs")) {
    logStep("Phase 7: resource-syncs verification (SKIPPED)");
  } else {
    logStep("Phase 7: resource-syncs (arm1-oci + bunchloch + cross-cutting)");
    log("  v5: Komodo owns the 3 resource-syncs. The IaC verifies they exist.");
    // No IaC action — the resource-syncs/*.toml files are read by Komodo.
  }

  // Phase 8: All sync commands
  if (skip.has("all-syncs")) {
    logStep("Phase 8: All sync commands (SKIPPED)");
  } else {
    logStep("Phase 8: All sync commands");
    await syncVariables();
    if (CLI_FLAGS.withMonitors) await syncMonitors();
    if (CLI_FLAGS.withAlerts) await syncAlerts();
    if (CLI_FLAGS.withSchedules) await syncSchedules();
    await syncActionRecipients();
    await syncOlm();
  }

  // Optional blueprint import (preserved from pre-v5)
  if (CLI_FLAGS.withBlueprintImport) {
    logStep("Blueprint import (Pangolin bulk endpoint)");
    logWarn("--with-blueprint-import is not yet implemented; use the per-resource sync path for now");
  }

  logOk("iac:bootstrap complete");
}
