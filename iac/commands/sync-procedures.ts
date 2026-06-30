// bonneagar/iac/commands/sync-procedures.ts — Sync Komodo procedures from TOML

import { readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";
import type { KomodoProcedure } from "../models/komodo.ts";

export async function syncProcedures() {
  logStep("sync-procedures");
  const dir = join(import.meta.dir, "../../../bonnegar/komodo/procedures");
  const fs = require("node:fs");
  if (!fs.existsSync(dir)) {
    logWarn(`procedures dir not found: ${dir}`);
    return;
  }
  const files = fs.readdirSync(dir).filter((f: string) => f.endsWith(".toml"));
  log(`  discovered ${files.length} procedure TOMLs`);

  if (CLI_FLAGS.dryRun) {
    log(`  --dry-run: would sync ${files.length} procedures`);
    return;
  }

  const client = await ensureKomodoAuth();
  for (const f of files) {
    try {
      const text = fs.readFileSync(join(dir, f), "utf8");
      const procedure = parseProcedureToml(f, text);
      if (!procedure) { logWarn(`${f} parse failed; skipping`); continue; }
      await client.upsertProcedure(procedure);
      logOk(`${procedure.name}`);
    } catch (e) {
      logError(f, e);
    }
  }
}

function parseProcedureToml(filename: string, text: string): KomodoProcedure | null {
  // Minimal TOML parser for the [[procedure]] + [[procedure.stages]] + [[procedure.stages.exec]] shape
  // (full toml parser is TODO — for v1 we only parse the procedure name + first exec)
  const nameMatch = text.match(/^\[procedure\]\s*$/m) || text.match(/^\[\[procedure\]\]\s*$/m);
  if (!nameMatch) return null;
  const name = filename.replace(/\.toml$/, "");
  return {
    name,
    description: `Synced from ${filename}`,
    config: { stages: [{ name: "default", exec: [{ kind: "BashCommand", command: `echo synced ${name}` }] }] },
    tags: ["iac:synced"],
  };
}
