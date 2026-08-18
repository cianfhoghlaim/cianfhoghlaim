// bonneagar/iac/commands/health.ts — 14-way health check
//
// Checks all 14 surfaces in the bons IaC:
//   1. Komodo     — the GitOps orchestrator
//   2. Pangolin   — the identity-aware reverse proxy + WireGuard server (gerbil)
//   3. Infisical  — the secrets source of truth
//   4. Newt       — the WireGuard client(s) on bunchloch + arm1-oci
//   5. Pocket ID  — the OIDC identity provider (admin SSO for Pangolin + newt creds)
//   6. Tinyauth   — the ForwardAuth middleware that fronts Pangolin
//
// Workload-plane probes (added 2026-08-02 post-trilogy-cleanup):
//   7.  meaisinfoghlaim (port 8080) — llama-swap OpenAI-compatible API
//   8.  paddleocr        (port 8000) — forms OCR
//   9.  dots-ocr         (port 8001) — tesseract fallback
//   10. olmocr           (port 8003) — tables + latex
//   11. docling-serve    (port 5001) — doctags
//   12. mlx-omni         (port 10240) — MLX OpenAI-compatible gateway
//   13. llama-swap       (port 8080) — GGUF model swapper
//   14. ocr-router       (port 8090) — OCR capability router
//
// Exits 0 only if all 14 are healthy.

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth, ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";
import { pocketIdHealth } from "../auth-pocketid-admin.ts";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);

const TINYAUTH_URL = process.env.TINYAUTH_URL ?? "http://localhost:10000";
const TINYAUTH_HEALTH_PATH = process.env.TINYAUTH_HEALTH_PATH ?? "/api/healthz";

// Host the workload probes run against. Defaults to localhost (i.e. the
// bunchloch host where iac:health is normally invoked). Override with
// HEALTH_WORKLOAD_HOST for cross-host probes.
const WORKLOAD_HOST = process.env.HEALTH_WORKLOAD_HOST ?? "127.0.0.1";
const PROTO = process.env.HEALTH_PROTO ?? "http";

// Per-stack probe config: [name, port, health-path].
const WORKLOAD_PROBES: Array<[string, number, string]> = [
  ["meaisinfoghlaim", 8080, "/health"],
  ["paddleocr", 8000, "/health"],
  ["dots-ocr", 8001, "/health"],
  ["olmocr", 8003, "/health"],
  ["docling-serve", 5001, "/v1/health"],
  ["mlx-omni", 10240, "/v1/models"],
  ["llama-swap", 8080, "/health"],
  ["ocr-router", 8090, "/health"],
];

export async function health() {
  logStep("Health check (14-way: komodo + pangolin + infisical + newt + pocket-id + tinyauth + 8 workload-plane probes)");
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

  // 3. Infisical (HTTP-only check + machine-identity report)
  try {
    const { infisicalAuthReport } = await import("../clients/infisical-client.ts");
    const r = await infisicalAuthReport();
    if (r.healthy) {
      logOk(r.detail);
    } else {
      logError(r.detail);
      allOk = false;
    }
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
    if (pid.healthy) {
      // v2.9.0 architecture: the local SQLite may be empty (it's a dev instance);
      // the production instance is on arm1-oci (DNS-routed). So we report the
      // version + connectivity, and use the admin API (with API key) to count users.
      let userCount = pid.dbUsers;
      let oidcClientCount = pid.dbOidcClients;
      if (process.env.POCKETID_API_KEY) {
        try {
          const { pocketIdListUsers, pocketIdListOidcClients } = await import("../auth-pocketid-admin.ts");
          const users = await pocketIdListUsers("", process.env.POCKETID_API_KEY);
          const clients = await pocketIdListOidcClients("", process.env.POCKETID_API_KEY);
          userCount = users.length;
          oidcClientCount = clients.length;
        } catch (e) {
          // API key may be missing or invalid; fall back to local DB counts
        }
      }
      if (userCount > 0) {
        logOk(`pocket-id: v${pid.version}, ${userCount} users, ${oidcClientCount} OIDC clients`);
      } else if (pid.dbUsers === 0) {
        logWarn(`pocket-id: v${pid.version} but local DB has 0 users (production instance on arm1-oci may have users — set POCKETID_API_KEY to query via API)`);
      }
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

  // 7-14. Workload-plane probes (meaisinfoghlaim + 6 OCR backends + ocr-router).
  // Each probe hits the canonical /health endpoint (or the equivalent) on
  // the configured port. 5s timeout. Failure is non-fatal for any one probe
  // so the operator can see which specific backend is down.
  for (const [name, port, path] of WORKLOAD_PROBES) {
    const url = `${PROTO}://${WORKLOAD_HOST}:${port}${path}`;
    try {
      const r = await fetch(url, { signal: AbortSignal.timeout(5000) });
      if (r.ok) {
        logOk(`${name}: ${url} returned ${r.status}`);
      } else {
        logError(`${name}: ${url} returned ${r.status}`);
        allOk = false;
      }
    } catch (e) {
      logError(`${name}: ${url} unreachable (${(e as Error).message.slice(0, 80)})`);
      allOk = false;
    }
  }

  // 15. Edge TLS verification (added 2026-08-17-biep-v3-bring-up-v1 P1.8).
  // Invokes scripts/check-edge-tls.sh --strict --all so the iac:health
  // 14-way claim is no longer false-positive — it now catches the
  // OpenSSL verify return code 21 (TRAEFIK DEFAULT CERT) + HTTP 000
  // (offline-site binding) failure modes documented in the
  // 2026-08-06-token-plan-apis-lc-doc-pipeline-and-edge-tls-remediation-v1
  // change.
  try {
    const tlsOut = (await execAsync(
      "bash scripts/check-edge-tls.sh --strict --all",
    )).stdout.trim();
    const okLine = tlsOut.split("\n").find((l) => l.includes("verified") || l.includes("OK"));
    logOk(`edge-tls: ${okLine ?? "all 17 hostnames healthy"}`);
  } catch (e) {
    const stderr = (e as { stderr?: string }).stderr ?? "";
    logError(
      `edge-tls: scripts/check-edge-tls.sh --strict --all failed\n${stderr.slice(0, 400)}`,
    );
    allOk = false;
  }

  finish(allOk);
}

function finish(allOk: boolean): never {
  process.exit(allOk ? 0 : 1);
}
