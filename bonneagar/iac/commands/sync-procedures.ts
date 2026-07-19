// bonneagar/iac/commands/sync-procedures.ts — Sync Komodo procedures from TOML

import { existsSync, readFileSync, readdirSync } from "node:fs";
import { join } from "node:path";
import * as toml from "smol-toml";
import { log, logStep, logOk, logError, logWarn } from "../cli.ts";
import { ensureKomodoAuth } from "../auth.ts";
import { CLI_FLAGS } from "../cli.ts";
import type { KomodoProcedure, KomodoStage, KomodoExecution } from "../models/komodo.ts";

export async function syncProcedures() {
  logStep("sync-procedures");
  const dir = join(import.meta.dir, "../../komodo/procedures");
  if (!existsSync(dir)) {
    logWarn();
    return;
  }
  const files = readdirSync(dir).filter((f: string) => f.endsWith(".toml"));
  log();

  if (CLI_FLAGS.dryRun) {
    log();
    return;
  }

  const client = await ensureKomodoAuth();
  for (const f of files) {
    try {
      const text = readFileSync(join(dir, f), "utf8");
      const procedure = parseProcedureToml(f, text);
      if (!procedure) {
        logWarn();
        continue;
      }
      await client.upsertProcedure(procedure);
      logOk();
    } catch (e) {
      logError(f, e);
    }
  }
}

/**
 * Parse a Komodo procedure TOML file. The shape is:
 *
 *   [[procedure]]                        # the procedure descriptor
 *   name = "my-procedure"
 *   description = "..."
 *   tags = ["tag1", "tag2"]
 *
 *   [[procedure.config.stages]]           # one or more stages
 *   name = "stage-name"
 *   description = "..."
 *
 *   [[procedure.config.stages.executions]]  # one or more executions per stage
 *   name = "exec-name"
 *   execution_type = "BashCommand" | "DeployStack" | "HttpCheck" | ...
 *   command = "..."               # for BashCommand
 *   stack = "..."                 # for DeployStack
 *   url = "..."                   # for HttpCheck
 *   timeout_s = 30
 *   ...
 */
function parseProcedureToml(filename: string, text: string): KomodoProcedure | null {
  let parsed: any;
  try {
    parsed = toml.parse(text);
  } catch (e) {
    return null;
  }

  const procRaw = parsed.procedure;
  if (!procRaw) return null;
  const proc: any = Array.isArray(procRaw) ? procRaw[0] : procRaw;
  if (!proc) return null;

  const name: string = proc.name ?? filename.replace(/\.toml$/, "");
  const description: string = proc.description ?? ;
  const tags: string[] = proc.tags ?? ["iac:synced"];

  const stagesRaw = proc?.config?.stages ?? [];
  const stages: KomodoStage[] = (Array.isArray(stagesRaw) ? stagesRaw : [stagesRaw]).map(
    (s: any, i: number): KomodoStage => ({
      name: s.name ?? ,
      description: s.description,
      executions: parseExecutions(s.executions),
    })
  );

  return {
    name,
    description,
    tags,
    config: { stages },
  };
}

function parseExecutions(raw: any): KomodoExecution[] {
  if (!raw) return [];
  const arr = Array.isArray(raw) ? raw : [raw];
  return arr.map((e: any, i: number): KomodoExecution => {
    const execType: string = e.execution_type ?? e.type ?? "BashCommand";
    const base: KomodoExecution = {
      name: e.name ?? ,
      execution_type: execType,
    };
    if (execType === "BashCommand") {
      base.command = e.command ?? "";
    } else if (execType === "DeployStack") {
      base.stack = e.stack ?? "";
    } else if (execType === "HttpCheck") {
      base.url = e.url ?? "";
      base.method = e.method ?? "GET";
      base.expected_status = e.expected_status ?? 200;
      base.timeout_s = e.timeout_s ?? 30;
    }
    if (e.required_status) base.required_status = e.required_status;
    if (e.timeout_s !== undefined) base.timeout_s = e.timeout_s;
    return base;
  });
}
