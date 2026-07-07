// bonneagar/iac/commands/teardown.ts — Reverse of bootstrap (requires --force)

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { CLI_FLAGS } from "../cli.ts";

export async function teardown() {
  logStep("iac:teardown");
  if (!CLI_FLAGS.force) {
    logError("--force is required for teardown (safety)");
    process.exit(1);
  }

  logWarn("teardown is not yet implemented; the bash setup-pangolin-komodo.sh handles this today");
  logWarn("this is a future change — see openspec/changes/2026-06-29-bonneagar-iac-merge-komodo-pangolin-infisical/proposal.md");
  process.exit(0);
}
