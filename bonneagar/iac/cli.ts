// bonneagar/iac/cli.ts — The `bun run iac <cmd>` entry point
// Uses Bun.argv for parsing. Supports --dry-run, --force, --stack=<name>,
// --with-blueprint-import, --with-monitors, --with-alerts, --with-schedules, --verbose.

import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "./auth.ts";

const args = process.argv.slice(2);
const flags = new Set<string>();
const flagValues: Record<string, string> = {};
for (const arg of args.slice(1)) {
  if (arg.startsWith("--")) {
    const [k, v] = arg.slice(2).split("=");
    if (v) flagValues[k] = v;
    else flags.add(k);
  }
}

export const CLI_FLAGS = {
  dryRun: flags.has("dry-run") || process.env.IAC_DRY_RUN === "true",
  force: flags.has("force"),
  verbose: flags.has("verbose") || process.env.IAC_VERBOSE === "true",
  withBlueprintImport: flags.has("with-blueprint-import"),
  withMonitors: flags.has("with-monitors"),
  withAlerts: flags.has("with-alerts"),
  withSchedules: flags.has("with-schedules"),
  stack: flagValues["stack"],
};

export function log(...args: unknown[]) {
  console.log(...args);
}
export function logStep(name: string) {
  log(`\n→ ${name}`);
}
export function logOk(name: string) {
  log(`  ✓ ${name}`);
}
export function logSkip(name: string, reason: string) {
  log(`  - skip ${name}: ${reason}`);
}
export function logWarn(msg: string) {
  log(`  ⚠ ${msg}`);
}
export function logError(msg: string, err?: unknown) {
  log(`  ✗ ${msg}`, err ?? "");
}

export async function dispatch(command: string) {
  log(`iac ${command} ${args.slice(1).join(" ")}`);
  switch (command) {
    case "plan": return (await import("./commands/plan.ts")).plan();
    case "deploy": return (await import("./commands/deploy.ts")).deploy();
    case "bootstrap": return (await import("./commands/bootstrap.ts")).bootstrap();
    case "teardown": return (await import("./commands/teardown.ts")).teardown();
    case "health": return (await import("./commands/health.ts")).health();
    case "sync:secrets": return (await import("./commands/sync-secrets.ts")).syncSecrets();
    case "sync:resources": return (await import("./commands/sync-resources.ts")).syncResources();
    case "sync:sites": return (await import("./commands/sync-sites.ts")).syncSites();
    case "sync:procedures": return (await import("./commands/sync-procedures.ts")).syncProcedures();
    case "sync:resource-syncs": return (await import("./commands/sync-resource-syncs.ts")).syncResourceSyncs();
    case "bootstrap-infisical": return (await import("./commands/bootstrap-infisical.ts")).bootstrapInfisical();
    case "bootstrap-pocketid-admin": return (await import("./commands/bootstrap-pocketid-admin.ts")).bootstrapPocketIdAdmin();
    case "bootstrap-pangolin-client": return (await import("./commands/bootstrap-pangolin-client.ts")).bootstrapPangolinClient();
    case "bootstrap-locket-binary": return (await import("./commands/bootstrap-locket-binary.ts")).bootstrapLocketBinary();
    case "bootstrap-control-plane": return (await import("./commands/bootstrap-control-plane.ts")).bootstrapControlPlane();
    case "wire-pocketid-as-oidc": return (await import("./commands/wire-pocketid-as-oidc.ts")).wirePocketIdAsOidc();
    case "deploy-periphery": return (await import("./commands/deploy-periphery.ts")).deployPeriphery();
    case "deploy-newt": return (await import("./commands/deploy-newt.ts")).deployNewt();
    case "rotate-auth": return (await import("./commands/rotate-auth.ts")).rotateAuth();
    case "sync:monitors": return (await import("./commands/sync-monitors.ts")).syncMonitors();
    case "sync:alerts": return (await import("./commands/sync-alerts.ts")).syncAlerts();
    case "sync:variables": return (await import("./commands/sync-variables.ts")).syncVariables();
    case "sync:schedules": return (await import("./commands/sync-schedules.ts")).syncSchedules();
    case "sync:action-recipients": return (await import("./commands/sync-action-recipients.ts")).syncActionRecipients();
    case "sync:olm": return (await import("./commands/sync-olm.ts")).syncOlm();
    case "sync:clients": return (await import("./commands/sync-clients.ts")).syncClients();
    default:
      logError(`unknown command: ${command}`);
      log(`Available commands: plan, deploy, bootstrap, teardown, health, sync:<target>, bootstrap-pangolin-client`);
      process.exit(1);
  }
}

if (import.meta.main) {
  const command = args[0];
  if (!command || command === "--help" || command === "-h") {
    log(`Usage: bun run iac <command> [flags]

Commands:
  plan                              Show diff between IaC-declared and actual state
  deploy                            Deploy the 30 key stacks end-to-end
  bootstrap                         1-command full bootstrap (Pulumi → Infisical → Pangolin → Komodo → Newt)
  teardown                          Reverse of bootstrap (requires --force)
  health                            Health check all 3 systems
  bootstrap-pocketid-admin          Idempotent: create the bons-iac + pangolin OIDC clients in Pocket ID
  bootstrap-pangolin-client         Idempotent: install pangolin CLI + mint a Pangolin client + render newt compose
  bootstrap-infisical               Idempotent: bootstrap the Infisical instance (first admin + 8 machine identities)
  bootstrap-control-plane           Idempotent: bootstrap the control plane (arm1-oci + bunchloch)
  bootstrap-locket-binary           Build the bons-locket-shim Docker image
  wire-pocketid-as-oidc             Wire Pocket ID as the OIDC IdP for Komodo + Pangolin
  deploy-periphery                  Deploy a Komodo Periphery agent
  deploy-newt                       Deploy a Newt Pangolin client
  rotate-auth                       Rotate Pangolin + Komodo + Infisical credentials (3-way)
  sync:secrets                       Sync Infisical secrets
  sync:resources                     Sync Pangolin private resources
  sync:sites                         Sync Pangolin sites
  sync:procedures                    Sync Komodo procedures
  sync:resource-syncs                Sync Komodo resource-syncs
  sync:monitors                      Sync Komodo monitors (opt-in)
  sync:alerts                        Sync Komodo alerts (opt-in)
  sync:variables                     Sync Komodo variables
  sync:schedules                     Sync Komodo schedules (opt-in)
  sync:action-recipients             Sync Komodo ActionRecipients
  sync:olm                           Sync Pangolin OLM clients
  sync:clients                       Sync Pangolin clients (user + machine)

Flags:
  --dry-run                          Don't mutate anything
  --force                            Skip confirmation prompts
  --verbose                          Verbose output
  --stack=<name>                     Limit to a single stack
  --host=<name>                      Limit to a single host (for bootstrap-pangolin-client)
  --type=<user|machine>              Client type (for bootstrap-pangolin-client)
  --expires-in=<seconds>             Client TTL (for bootstrap-pangolin-client; 0 = never)
  --skip-binary-install              Skip the pangolin CLI binary install (for bootstrap-pangolin-client)
  --with-blueprint-import            Use the Pangolin blueprint-import API (faster bootstrap)
  --with-monitors                    Also sync Komodo monitors
  --with-alerts                      Also sync Komodo alerts
  --with-schedules                   Also sync Komodo schedules
`);
    process.exit(0);
  }
  await dispatch(command);
}
