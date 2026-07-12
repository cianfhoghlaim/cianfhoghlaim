// bonneagar/iac/commands/sync-sites.ts — Sync Pangolin sites via Integrations API
// The missing 3rd layer of the IaC:
//   - iac:sync:secrets    → secrets
//   - iac:sync:resources  → private resources
//   - iac:sync:sites      → sites (this file)
//
// Walks stacks/*/site.yaml; for each site declared:
//   1. Check if the site already exists via GET /org/{orgId}/site/{niceId}
//   2. If not, POST /org/{orgId}/site → returns { id, newtId, newtSecret }
//   3. Write newtId + newtSecret back to .infisical.env as
//      {infisicalSecretPrefix}_ID + {infisicalSecretPrefix}_SECRET
//      (or via the Infisical client if a machine identity is configured)
//
// The returned credentials are what deploy-newt-bunchloch-v2 /
// deploy-pangolin-newt-arm1-oci read at startup time (via Locket from
// Infisical).
//
// Companion openspec change: 2026-07-14-iac-sync-sites-pangolin-integrations-api-v1
// =============================================================================

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { discoverSites } from "../sources/discover-sites.ts";
import { ensurePangolinAuth, ensureInfisicalAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

export async function syncSites() {
  logStep("sync-sites");

  const sites = discoverSites();
  if (sites.length === 0) {
    logWarn("no sites discovered in any stack's site.yaml");
    return;
  }
  log(`  discovered ${sites.length} site(s)`);

  if (CLI_FLAGS.dryRun) {
    for (const s of sites) {
      log(`    --dry-run: would provision site ${s.niceId} (${s.name})`);
    }
    return;
  }

  const pangolin = await ensurePangolinAuth();
  let infisical: Awaited<ReturnType<typeof ensureInfisicalAuth>> | null = null;
  try {
    infisical = await ensureInfisicalAuth();
  } catch (e) {
    logWarn(`infisical: not configured — credentials will be written to local .env only (${(e as Error).message})`);
  }

  for (const s of sites) {
    try {
      const existing = await pangolin.getSite(s.niceId).catch(() => null);
      let siteId: number;
      let newtId: string;
      let newtSecret: string;

      if (existing) {
        logOk(`${s.niceId} (already exists, id=${existing.id})`);
        siteId = existing.id!;
        // For an existing site, we may not have the original newtId + newtSecret
        // (they're write-only). Skip credential writeback; the operator must
        // re-mint via the Pangolin UI if the credentials are lost.
        newtId = "(existing — see Pangolin UI)";
        newtSecret = "(existing — see Pangolin UI)";
      } else {
        const created = await pangolin.createSite({
          name: s.name,
          description: s.description,
          address: s.address,
          type: s.type ?? "local",
        });
        siteId = created.data?.id ?? 0;
        newtId = (created.data as { newtId?: string })?.newtId ?? "";
        newtSecret = (created.data as { newtSecret?: string })?.newtSecret ?? "";
        logOk(`${s.niceId} (created, id=${siteId}, newtId=${newtId.slice(0, 8)}...)`);

        if (s.infisicalSecretPrefix && (newtId || newtSecret)) {
          await writebackCredentials(s, newtId, newtSecret, infisical);
        }
      }
    } catch (e) {
      logError(`${s.niceId}`, e);
    }
  }
}

async function writebackCredentials(
  site: { niceId: string; infisicalSecretPrefix?: string; infisicalSecretPath?: string },
  newtId: string,
  newtSecret: string,
  infisical: Awaited<ReturnType<typeof ensureInfisicalAuth>> | null,
) {
  const prefix = site.infisicalSecretPrefix ?? `PANGOLIN_NEWT_${site.niceId.toUpperCase().replace(/-/g, "_")}`;
  const path = site.infisicalSecretPath ?? "/pangolin";
  const idVar = `${prefix}_ID`;
  const secretVar = `${prefix}_SECRET`;

  // 1. Always write to local .env (canonical for cianfhoghlaim worktree)
  const envPath = join(import.meta.dir, "../../../.env");
  if (existsSync(envPath)) {
    const original = readFileSync(envPath, "utf8");
    const updated = upsertEnvVar(original, idVar, newtId) + "\n" + upsertEnvVar(upsertEnvVar(original, idVar, newtId), secretVar, newtSecret);
    writeFileSync(envPath, updated);
    logOk(`  wrote ${idVar} + ${secretVar} to local .env`);
  }

  // 2. Optionally write to Infisical vault (so other hosts can fetch via Locket)
  if (infisical) {
    try {
      const projectId = process.env.INFISICAL_PROJECT_ID ?? "f3cff583-b74b-4804-b9d3-db8b68885236";
      const environment = process.env.INFISICAL_ENVIRONMENT ?? "dev";
      await (infisical as unknown as { createSecret: (args: { projectId: string; environment: string; path: string; key: string; value: string; secretType?: string }) => Promise<unknown> })
        .createSecret({ projectId, environment, path, key: idVar, value: newtId, secretType: "shared" });
      await (infisical as unknown as { createSecret: (args: { projectId: string; environment: string; path: string; key: string; value: string; secretType?: string }) => Promise<unknown> })
        .createSecret({ projectId, environment, path, key: secretVar, value: newtSecret, secretType: "shared" });
      logOk(`  wrote ${idVar} + ${secretVar} to Infisical ${path}`);
    } catch (e) {
      logError(`  infisical writeback failed`, e);
    }
  }
}

function upsertEnvVar(content: string, key: string, value: string): string {
  const escaped = value.replace(/\\/g, "\\\\").replace(/"/g, '\\"');
  const line = `${key}="${escaped}"`;
  const regex = new RegExp(`^${key}=.*$`, "m");
  if (regex.test(content)) {
    return content.replace(regex, line);
  }
  return content + "\n" + line;
}
