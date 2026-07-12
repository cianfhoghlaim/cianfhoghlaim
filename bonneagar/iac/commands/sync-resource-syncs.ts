// bonneagar/iac/commands/sync-resource-syncs.ts — Sync Komodo resource-syncs from TOML

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";
import { CONFIG } from "../config.ts";

export async function syncResourceSyncs() {
  logStep("sync-resource-syncs");
  const dir = "../../komodo/resource-syncs";
  const abs = join(import.meta.dir, dir);
  if (!existsSync(abs)) {
    logWarn(`resource-syncs dir not found: ${abs}`);
    return;
  }
  const files = readdirSync(abs).filter((f: string) => f.endsWith(".toml"));
  log(`  discovered ${files.length} resource-sync TOMLs`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would sync ${files.length} resource-syncs`);
    return;
  }

  const client = await ensureKomodoAuth();
  for (const f of files) {
    try {
      const text = readFileSync(join(abs, f), "utf8");
      const sync = parseResourceSyncToml(f, text);
      if (!sync) { logWarn(`${f} parse failed; skipping`); continue; }
      await client.upsertResourceSync(sync);
      logOk(`${sync.name}`);
    } catch (e) {
      logError(f, e);
    }
  }
}

function parseResourceSyncToml(filename: string, text: string): any {
  // Minimal TOML parser for the [[resource_sync]] shape
  const name = filename.replace(/\.toml$/, "");
  // TODO: full TOML parser (use @iarna/toml or smol-toml) — added in v5 follow-up
  return {
    name,
    description: `Synced from ${filename}`,
    config: {
      resource_type: "Stack",
      repo: CONFIG.gitRepo,
      branch: CONFIG.gitBranch,
      git_provider: CONFIG.gitProvider,
      git_account: CONFIG.gitRepo.split("/")[0],
      directory: `bonneagar/komodo/${filename.replace('.toml', '')}`,
      managed: true,
      delete: false,
    },
    tags: ["iac:synced"],
  };
}
