// bonneagar/iac/commands/sync-clients.ts — Sync Pangolin clients (user + machine)
//
// ADDED 2026-08-15 (per the 2026-08-15-bonneagar-infra-remediation-v2
// openspec change). Walks bonneagar/iac/clients/*.yaml (the
// PangolinClientSpec format) and ensures every declared Pangolin client
// exists in the Pangolin Integrations API. Idempotent — re-running is a
// no-op.
//
// The companion to sync-sites + sync-resources + sync-olm. The 4-layer
// IaC coverage of the Pangolin Integrations API is now:
//   - iac:sync:sites       → sites
//   - iac:sync:resources   → private resources
//   - iac:sync:olm         → OLM clients
//   - iac:sync:clients     → clients (this file)
//
// Usage:
//   bun run iac:sync:clients
//   bun run iac:sync:clients --dry-run
//   bun run iac:sync:clients --host=arm1-oci
// =============================================================================

import { readFileSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensurePangolinAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

const CLIENTS_DIR = join(import.meta.dir, "../clients");

interface PangolinClientSpec {
  host: string;
  type: "user" | "machine";
  endpoint?: string;
  expiresIn?: number; // seconds; 0 = never
  siteIds?: number[];
}

function discoverClients(): PangolinClientSpec[] {
  if (!existsSync(CLIENTS_DIR)) return [];
  const out: PangolinClientSpec[] = [];
  for (const f of readdirSync(CLIENTS_DIR)) {
    if (!f.endsWith(".yaml") && !f.endsWith(".yml")) continue;
    if (f === "pangolin-client.ts") continue;
    const text = readFileSync(join(CLIENTS_DIR, f), "utf8");
    const parsed = parseClientYaml(text);
    if (parsed) out.push(parsed);
  }
  return out;
}

function parseClientYaml(text: string): PangolinClientSpec | null {
  const hostMatch = text.match(/^pangolin\.clients\.([^:]+):/m);
  if (!hostMatch) return null;
  const host = hostMatch[1].trim();
  const typeMatch = text.match(/type:\s*(user|machine)/);
  const endpointMatch = text.match(/endpoint:\s*([^\n]+)/);
  const expiresInMatch = text.match(/expiresIn:\s*(\d+)/);
  const siteIdsMatch = text.match(/siteIds:\s*\[([^\]]+)\]/);
  return {
    host,
    type: (typeMatch?.[1] as "user" | "machine") ?? "machine",
    endpoint: endpointMatch?.[1].trim().replace(/^["']|["']$/g, ""),
    expiresIn: expiresInMatch ? parseInt(expiresInMatch[1], 10) : 0,
    siteIds: siteIdsMatch
      ? siteIdsMatch[1].split(",").map((s) => parseInt(s.trim(), 10))
      : undefined,
  };
}

export async function syncClients() {
  logStep("sync-clients");

  const clients = discoverClients();
  if (clients.length === 0) {
    logWarn("no Pangolin clients discovered in bonneagar/iac/clients/*.yaml");
    return;
  }
  log(`  discovered ${clients.length} client(s)`);

  const pangolin = await ensurePangolinAuth();
  const { PangolinClient } = await import("../clients/pangolin-client.ts");
  const pc = new PangolinClient(pangolin.url, pangolin.apiKey, pangolin.orgId);

  const filtered = CLI_FLAGS.stack
    ? clients.filter((c) => c.host === CLI_FLAGS.stack)
    : clients;

  if (CLI_FLAGS.dryRun) {
    for (const c of filtered) {
      log(`    --dry-run: would ensure client ${c.host} (${c.type})`);
    }
    return;
  }

  for (const c of filtered) {
    try {
      const { data } = await pc.listClients();
      const existing = data.clients.find((x) => x.name === c.host);
      if (existing) {
        logOk(`${c.host} (already exists, id=${existing.id})`);
      } else {
        const created = await pc.createClient({
          name: c.host,
          endpoint: c.endpoint ?? "https://pangolin.cianfhoghlaim.ie",
          type: c.type,
          expiresIn: c.expiresIn ?? 0,
          siteIds: c.siteIds,
        });
        logOk(
          `${c.host} (created, id=${created.data.id}, clientId=${created.data.clientId})`,
        );
      }
    } catch (e) {
      logError(`${c.host}`, e);
    }
  }
}