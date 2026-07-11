// bonneagar/iac/commands/health.ts — 5-way health check
//
// Checks all 5 auth surfaces in the bons IaC:
//   1. Komodo     — the GitOps orchestrator
//   2. Pangolin   — the identity-aware reverse proxy + WireGuard server (gerbil)
//   3. Infisical  — the secrets source of truth
//   4. Newt       — the WireGuard client(s) on bunchloch + arm1-oci
//   5. Pocket ID  — the OIDC identity provider (admin SSO for Pangolin + newt creds)
//
// Plus a 6th: Tinyauth (the ForwardAuth middleware that fronts Pangolin).
//
// Exits 0 only if all 6 are healthy.

import { log, logStep, logOk, logError } from "../cli.ts";
import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";
import { pocketIdHealth } from "../auth-pocketid-admin.ts";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);

const TINYAUTH_URL = process.env.TINYAUTH_URL ?? "http://tinyauth.cianfhoghlaim.ie";
const TINYAUTH_HEALTH_PATH = process.env.TINYAUTH_HEALTH_PATH ?? "/api/health";

export async function health() {
  logStep("Health check (5-way: komodo + pangolin + infisical + newt + pocket-id + tinyauth)");
  let allOk = true;

  // 1. Komodo
  try {
    const komodo = await ensureKomodoAuth();
    const servers = await komodo.listServers();
    const stacks = await komodo.listStacks();
    logOk(`komodo: ${servers.length} servers, ${stacks.length} stacks`);
  } catch (e) {
    logError("komodo", e);
    allOk = false;
  }

  // 2. Pangolin
  try {
    const pangolin = await ensurePangolinAuth();
    const h = await pangolin.health();
    if (h.healthy) logOk(`pangolin: ${h.detail}`);
    else { logError("pangolin", h.detail); allOk = false; }
  } catch (e) {
    logError("pangolin", e);
    allOk = false;
  }

  // 3. Infisical
  try {
    const infisical = await ensureInfisicalAuth();
    const h = await infisical.health();
    if (h.healthy) logOk(`infisical: ${h.detail}`);
    else { logError("infisical", h.detail); allOk = false; }
  } catch (e) {
    logError("infisical", e);
    allOk = false;
  }

  // 4. Newt (bunchloch) — WireGuard handshake + version
  try {
    // 4a. Container exists + is Up?
    const psOut = (await execAsync("docker ps --filter name=bunchloch-newt --format '{{.Status}}'")).stdout.trim();
    if (!psOut.includes("Up")) {
      logError(`newt (bunchloch): container NOT Up (status: ${psOut || "absent"}); run: km run procedure deploy-newt-bunchloch-v2`);
      allOk = false;
    } else {
      logOk(`newt (bunchloch): container Up (${psOut})`);

      // 4b. newt binary version (only if container is Up)
      try {
        const versionOut = (await execAsync("docker exec bunchloch-newt -- newt --version 2>&1")).stdout.trim();
        const versionMatch = versionOut.match(/(\d+\.\d+\.\d+)/);
        const version = versionMatch ? versionMatch[1] : "unknown";
        if (version === "1.14.0") {
          logOk(`newt (bunchloch): version ${version} (matches IMAGE pin)`);
        } else {
          logError(`newt (bunchloch): version ${version} MISMATCH (expected 1.14.0)`);
          allOk = false;
        }
      } catch (e) {
        logError(`newt (bunchloch): version check failed: ${(e as Error).message.slice(0, 100)}`);
        allOk = false;
      }

      // 4c. WireGuard tunnel handshake (only if container is Up)
      try {
        const wgOut = (await execAsync("docker exec bunchloch-newt -- wg show 2>&1")).stdout.trim();
        if (wgOut.includes("latest handshake")) {
          const handshakeLine = wgOut.split("\n").find((l) => l.includes("latest handshake"));
          logOk(`newt (bunchloch): WireGuard tunnel LIVE (${handshakeLine?.trim()})`);
        } else {
          logError(`newt (bunchloch): NO WireGuard handshake yet (tunnel not established)`);
          allOk = false;
        }
      } catch (e) {
        logError(`newt (bunchloch): wg show failed: ${(e as Error).message.slice(0, 100)}`);
        allOk = false;
      }
    }
  } catch (e) {
    logError("newt (bunchloch)", e);
    allOk = false;
  }

  // 5. Pocket ID (NEW)
  try {
    const pid = await pocketIdHealth();
    if (pid.healthy && pid.dbUsers > 0) {
      logOk(`pocket-id: v${pid.version}, ${pid.dbUsers} users, ${pid.dbOidcClients} OIDC clients, signup=${pid.signupEnabled ? "on" : "off"}`);
    } else if (pid.healthy && pid.dbUsers === 0) {
      logError(`pocket-id: v${pid.version} but DB is empty (run: bun run iac:bootstrap-pocketid-admin)`);
      allOk = false;
    } else {
      logError(`pocket-id: ${pid.healthyDetail}`);
      allOk = false;
    }
  } catch (e) {
    logError("pocket-id", e);
    allOk = false;
  }

  // 6. Tinyauth (ForwardAuth middleware)
  try {
    const r = await fetch(`${TINYAUTH_URL}${TINYAUTH_HEALTH_PATH}`, { signal: AbortSignal.timeout(5000) });
    if (r.ok) {
      logOk(`tinyauth: ${TINYAUTH_URL} returned ${r.status}`);
    } else {
      logError(`tinyauth: ${TINYAUTH_URL} returned ${r.status}`);
      allOk = false;
    }
  } catch (e) {
    logError("tinyauth", e);
    allOk = false;
  }

  finish(allOk);
}

function finish(allOk: boolean): never {
  process.exit(allOk ? 0 : 1);
}
