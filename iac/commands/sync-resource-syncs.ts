// bonneagar/iac/commands/sync-resource-syncs.ts — Sync Komodo resource-syncs from TOML

import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";

export async function syncResourceSyncs() {
  logStep("sync-resource-syncs");
  const dir = "../../../bonnegar/komodo/resource-syncs";
  const fs = require("node:fs");
  const abs = join(import.meta.dir, dir);
  if (!fs.existsSync(abs)) {
    logWarn(`resource-syncs dir not found: ${abs}`);
    return;
  }
  const files = fs.readdirSync(abs).filter((f: string) => f.endsWith(".toml"));
  log(`  discovered ${files.length} resource-sync TOMLs`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would sync ${files.length} resource-syncs`);
    return;
  }

  const client = await ensureKomodoAuth();
  for (const f of files) {
    try {
      const text = fs.readFileSync(join(abs, f), "utf8");
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
  // TODO: full TOML parser (use @iarna/toml or similar)
  return {
    name,
    description: `Synced from ${filename}`,
    config: {
      resource_type: "Stack",
      repo: "cliste/bonneagar",
      branch: "main",
      directory: `bonnegar/komodo/${filename.replace('.toml', '')}`,
      managed: true,
      delete: false,
    },
    tags: ["iac:synced"],
  };
}
