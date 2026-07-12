// bonneagar/iac/commands/sync-variables.ts — Sync Komodo variables

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

// The 12 cross-stack env vars (per the proposal)
const CROSS_STACK_VARS = [
  "KOMODO_PASSWORD",
  "KOMODO_JWT",
  "PANGOLIN_API_KEY",
  "PANGOLIN_ORG_ID",
  "PANGOLIN_LICENCE",
  "INFISICAL_TOKEN",
  "INFISICAL_CLIENT_ID",
  "INFISICAL_CLIENT_SECRET",
  "INFISICAL_PROJECT_ID",
  "INFISICAL_ENVIRONMENT",
  "LOCKET_TOKEN",
  "GIT_BRANCH",
];

export async function syncVariables() {
  logStep("sync-variables");
  log(`  discovered ${CROSS_STACK_VARS.length} cross-stack env vars`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would sync ${CROSS_STACK_VARS.length} variables`);
    return;
  }

  const client = await ensureKomodoAuth();
  for (const name of CROSS_STACK_VARS) {
    try {
      const value = process.env[name] ?? "";
      await client.upsertVariable({ name, value, is_secret: true });
      logOk(`${name}`);
    } catch (e) {
      logError(name, e);
    }
  }
}
