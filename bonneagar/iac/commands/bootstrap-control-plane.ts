// bonneagar/iac/commands/bootstrap-control-plane.ts — The operator's one-shot for the full 5-control-plane setup
//
// Runs the 8 phases in order (idempotent — each phase checks state and
// re-deploys only if needed):
//   1. locket binary (IaC use) — downloads to ~/.local/bin/locket
//   2. Pulumi IaC (provisions arm1-oci VM via OCI + saves Cloudflare creds to Infisical)
//   3. bundled stack deploy (stacks/control-plane/) — komodo + pangolin + pocket-id + tinyauth + infisical + locket
//   4. Infisical bootstrap (first admin + 8 machine identities via API-preferred / Chrome-MCP-fallback)
//   5. Pocket ID OIDC wire (creates komodo OIDC client in Pocket ID + wires Komodo + Pangolin)
//   6. Komodo Periphery (provisions the agent on the managed host)
//   7. Newt (provisions the Pangolin tunnel on the managed host)
//   8. health verify (7-way check — komodo + pangolin + infisical + newt + pocket-id + tinyauth)
//
// Usage:
//   bun run iac:bootstrap-control-plane --target=bunchloch
//   bun run iac:bootstrap-control-plane --target=arm1-oci
//   bun run iac:bootstrap-control-plane                 # default: detects from hostname
//
// Companion: openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1
// =============================================================================

import { execSync } from "node:child_process";
import { hostname } from "node:os";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { bootstrapLocketBinary } from "./bootstrap-locket-binary.ts";
import { bootstrapInfisical } from "./bootstrap-infisical.ts";
import { wirePocketIdAsOidc } from "./wire-pocketid-as-oidc.ts";
import { deployPeriphery } from "./deploy-periphery.ts";
import { deployNewt } from "./deploy-newt.ts";

interface BootstrapControlPlaneOpts {
  target?: "bunchloch" | "arm1-oci";
  connectAs?: string;
  hostDir?: string;
}

function getArg(name: string, args: string[]): string | undefined {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 ? args[idx + 1] : undefined;
}

export async function bootstrapControlPlane(opts?: BootstrapControlPlaneOpts): Promise<{ ts: string; target: string; results: Record<string, unknown> }> {
  const args = process.argv.slice(2);
  const target = (opts?.target ?? getArg("target", args) ?? (hostname() === "prod" ? "arm1-oci" : "bunchloch")) as "bunchloch" | "arm1-oci";
  const connectAs = opts?.connectAs ?? getArg("connect-as", args) ?? target;
  const hostDir = opts?.hostDir ?? getArg("host-dir", args) ?? join("/root", ".local", target === "arm1-oci" ? "newt" : "komodo_periphery");

  logStep(`iac:bootstrap-control-plane — target=${target} (8 phases)`);

  const results: Record<string, unknown> = {};

  // Phase 1: locket binary
  log("Phase 1: locket binary (IaC use)");
  try {
    results.locket = await bootstrapLocketBinary();
    logOk("Phase 1 complete: locket installed/verified");
  } catch (e) {
    logError(`Phase 1 failed: ${(e as Error).message}`);
    throw e;
  }

  // Phase 2: Pulumi IaC (only meaningful on arm1-oci; no-op on bunchloch)
  log("Phase 2: Pulumi IaC (provisions arm1-oci VM)");
  if (target === "arm1-oci") {
    try {
      execSync("bun run iac/pulumi/oci/deploy.ts up", { stdio: "inherit" });
      logOk("Phase 2 complete: arm1-oci VM provisioned");
    } catch (e) {
      logWarn(`Phase 2 failed (continuing): ${(e as Error).message}`);
    }
  } else {
    logOk("Phase 2 skipped: Pulumi IaC is a no-op on bunchloch (VM is already running)");
  }

  // Phase 3: bundled stack deploy
  log("Phase 3: bundled stack deploy (stacks/control-plane/)");
  try {
    const stackDir = join("/etc/komodo/control-plane");
    try {
      execSync(`cd ${stackDir} && docker compose up -d 2>&1 | tail -20`, { stdio: "inherit" });
      logOk("Phase 3 complete: control-plane stack deployed");
    } catch {
      logWarn("Phase 3 stack deploy failed (the stack may not exist on this host — falling back to the IaC's standard `stacks/` dirs)");
      // Fall back to the individual stack deploys
      for (const stack of ["infisical", "pangolin", "pocket-id", "tinyauth", "komodo"]) {
        try {
          execSync(`cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar/stacks/${stack} && docker compose up -d 2>&1 | tail -5`, { stdio: "inherit" });
        } catch {
          // ignore individual stack failures
        }
      }
    }
  } catch (e) {
    logWarn(`Phase 3 failed: ${(e as Error).message}`);
  }

  // Phase 4: Infisical bootstrap
  log("Phase 4: Infisical bootstrap (first admin + 8 machine identities)");
  try {
    results.infisical = await bootstrapInfisical({ useExistingCreds: true });
    logOk("Phase 4 complete: Infisical bootstrap verified/seeded");
  } catch (e) {
    logError(`Phase 4 failed: ${(e as Error).message}`);
    throw e;
  }

  // Phase 5: Pocket ID OIDC wire
  log("Phase 5: Pocket ID OIDC wire (komodo + Pangolin)");
  try {
    results.oidc = await wirePocketIdAsOidc();
    logOk("Phase 5 complete: Pocket ID wired as OIDC IdP for Komodo + Pangolin");
  } catch (e) {
    logWarn(`Phase 5 failed (continuing): ${(e as Error).message}`);
  }

  // Phase 6: Komodo Periphery
  log("Phase 6: Komodo Periphery (provisions the agent on the managed host)");
  try {
    results.periphery = await deployPeriphery({ connectAs, rootDirectory: hostDir });
    logOk("Phase 6 complete: Komodo Periphery rendered");
    log(`  operator: cd ${hostDir} && docker compose up -d`);
  } catch (e) {
    logWarn(`Phase 6 failed: ${(e as Error).message}`);
  }

  // Phase 7: Newt
  log("Phase 7: Newt (provisions the Pangolin tunnel on the managed host)");
  try {
    results.newt = await deployNewt({ host: connectAs, hostDir });
    logOk("Phase 7 complete: Newt rendered");
    log(`  operator: cd ${hostDir} && docker compose up -d`);
  } catch (e) {
    logWarn(`Phase 7 failed: ${(e as Error).message}`);
  }

  // Phase 8: health verify
  log("Phase 8: health verify (7-way)");
  try {
    execSync("cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar && bun run iac:health 2>&1 | tail -20", { stdio: "inherit" });
    logOk("Phase 8 complete: health check ran");
  } catch (e) {
    logWarn(`Phase 8 had issues: ${(e as Error).message}`);
  }

  return { ts: new Date().toISOString(), target, results };
}

function join(...parts: string[]): string {
  return parts.join("/");
}
