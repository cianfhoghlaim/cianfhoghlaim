// bonneagar/iac/commands/health.ts — Health check all 4 surfaces:
//   1. komodo     — the GitOps orchestrator
//   2. pangolin   — the identity-aware reverse proxy + WireGuard server (gerbil)
//   3. infisical  — the secrets source of truth
//   4. newt       — the WireGuard client(s) that bridge the operator-laptop
//                   (bunchloch) + the arm1-oci control plane into the mesh
//
// Exits 0 only if all 4 are healthy.

import { log, logStep, logOk, logError } from "../cli.ts";
import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);

export async function health() {
  logStep("Health check (4-way: komodo + pangolin + infisical + newt)");
  let allOk = true;

  try {
    const komodo = await ensureKomodoAuth();
    const servers = await komodo.listServers();
    const stacks = await komodo.listStacks();
    logOk(`komodo: ${servers.length} servers, ${stacks.length} stacks`);
  } catch (e) {
    logError("komodo", e);
    allOk = false;
  }

  try {
    const pangolin = await ensurePangolinAuth();
    const h = await pangolin.health();
    if (h.healthy) logOk(`pangolin: ${h.detail}`);
    else { logError("pangolin", h.detail); allOk = false; }
  } catch (e) {
    logError("pangolin", e);
    allOk = false;
  }

  try {
    const infisical = await ensureInfisicalAuth();
    const h = await infisical.health();
    if (h.healthy) logOk(`infisical: ${h.detail}`);
    else { logError("infisical", h.detail); allOk = false; }
  } catch (e) {
    logError("infisical", e);
    allOk = false;
  }

  // -----------------------------------------------------------------------
  // Newt WireGuard status (bunchloch operator-laptop side)
  // -----------------------------------------------------------------------
  // Checks the 3 newt health conditions:
  //   a. bunchloch-newt container is Up
  //   b. newt binary version is 1.14.0 (the v1.13.0 → v1.14.0 bump)
  //   c. WireGuard tunnel has a recent handshake (proves the mesh is live)
  //
  // The arm1-oci-side newt is checked by `deploy-pangolin-newt-arm1-oci`
  // Stage 4 (it's a separate procedure because the host is different).
  // -----------------------------------------------------------------------
  try {
    const psOut = (await execAsync("docker ps --filter name=bunchloch-newt --format '{{.Status}}'")).stdout.trim();
    if (psOut.includes("Up")) {
      logOk(`newt (bunchloch): container Up (${psOut})`);
    } else {
      logError(`newt (bunchloch): container NOT Up (status: ${psOut || "absent"})`);
      allOk = false;
      return finish(allOk);
    }

    const versionOut = (await execAsync("docker exec bunchloch-newt -- newt --version 2>&1")).stdout.trim();
    const versionMatch = versionOut.match(/(\d+\.\d+\.\d+)/);
    const version = versionMatch ? versionMatch[1] : "unknown";
    if (version === "1.14.0") {
      logOk(`newt (bunchloch): version ${version} (matches IMAGE pin)`);
    } else {
      logError(`newt (bunchloch): version ${version} MISMATCH (expected 1.14.0)`);
      allOk = false;
    }

    const wgOut = (await execAsync("docker exec bunchloch-newt -- wg show 2>&1")).stdout.trim();
    if (wgOut.includes("latest handshake")) {
      const handshakeLine = wgOut.split("\n").find((l) => l.includes("latest handshake"));
      logOk(`newt (bunchloch): WireGuard tunnel LIVE (${handshakeLine?.trim()})`);
    } else {
      logError(`newt (bunchloch): NO WireGuard handshake yet (tunnel not established)`);
      allOk = false;
    }
  } catch (e) {
    logError("newt (bunchloch)", e);
    allOk = false;
  }

  finish(allOk);
}

function finish(allOk: boolean): never {
  process.exit(allOk ? 0 : 1);
}
