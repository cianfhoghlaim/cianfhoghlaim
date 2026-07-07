// bonneagar/iac/commands/plan.ts — Diff IaC-declared vs actual state

import { log, logStep, logOk, logError } from "../cli.ts";
import { discoverStacks, discoverResources, discoverSecrets } from "../sources/index.ts";
import { getKeyStacks } from "../sources/key-stacks.ts";
import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

export async function plan() {
  logStep("Plan — diff IaC-declared vs actual");

  // IaC-declared
  const stacks = discoverStacks();
  const resources = discoverResources();
  const secrets = discoverSecrets();
  const keyStacks = getKeyStacks();

  log(`\n  IaC-declared:`);
  log(`    Stacks discovered:        ${stacks.length}`);
  log(`    Key stacks (5-group):     ${keyStacks.length}`);
  log(`    Pangolin resources:       ${resources.length}`);
  log(`    Infisical secrets:        ${secrets.length}`);

  // Actual (from each system)
  try {
    const komodo = await ensureKomodoAuth();
    const actualServers = await komodo.listServers();
    const actualStacks = await komodo.listStacks();
    const actualProcedures = await komodo.listProcedures();
    log(`\n  Actual state:`);
    log(`    Komodo servers:           ${actualServers.length}`);
    log(`    Komodo stacks:            ${actualStacks.length}`);
    log(`    Komodo procedures:        ${actualProcedures.length}`);
  } catch (e) {
    logError("komodo state", e);
  }

  try {
    const pangolin = await ensurePangolinAuth();
    const { data } = await pangolin.listResources();
    log(`    Pangolin resources:       ${data.siteResources.length}`);
  } catch (e) {
    logError("pangolin state", e);
  }

  try {
    const infisical = await ensureInfisicalAuth();
    const projects = await infisical.listProjects();
    log(`    Infisical projects:       ${projects.length}`);
  } catch (e) {
    logError("infisical state", e);
  }

  if (CLI_FLAGS.dryRun) log(`\n  (--dry-run: no mutations performed)`);
}
