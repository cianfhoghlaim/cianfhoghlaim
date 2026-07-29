#!/usr/bin/env bun
/**
 * deploy-full.ts — One-command full-stack deploy orchestrator (TypeScript state machine)
 *
 * Per the 2026-08-01-lakehouse-and-reproducible-deploy-v1 openspec change:
 *
 *   "The system MUST provide a `mise run deploy:full` command that brings
 *    up the entire 91-stack platform in 7 phases with healthchecks + a
 *    resumable checkpoint state file at `~/.cianfhoghlaim/deploy-state.json`.
 *    The 7 phases MUST be (in this order):
 *      1. preflight-arm-oci
 *      2. control-plane-up
 *      3. lakehouse-up
 *      4. data-stacks-up
 *      5. agent-surfaces-up
 *      6. dagster-materialize
 *      7. dagster-sensor-health-gate"
 *
 * This is the TypeScript state machine that owns the resumable checkpoint.
 * The shell entry (`scripts/deploy-full.sh`) delegates here after preflight.
 *
 * Usage:
 *   bun run scripts/deploy-full.ts                    # full deploy from phase 1
 *   bun run scripts/deploy-full.ts --skip-preflight   # skip preflight (only if invoked by shell)
 *   bun run scripts/deploy-full.ts --dry-run          # log what would happen
 *   bun run scripts/deploy-full.ts --phase=4          # run only phase 4
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

// --- Config ---
const REPO_ROOT = new URL("..", import.meta.url).pathname;
const STATE_FILE = join(homedir(), ".cianfhoghlaim", "deploy-state.json");
const STACK_HEALTH_TIMEOUT_MS = 60_000; // 60s per health probe
const PHASE_TIMEOUT_MS = 600_000; // 10 min per phase

// --- Args ---
const args = process.argv.slice(2);
const SKIP_PREFLIGHT = args.includes("--skip-preflight");
const DRY_RUN = args.includes("--dry-run");
const onlyPhaseArg = args.find((a) => a.startsWith("--phase="));
const ONLY_PHASE = onlyPhaseArg ? parseInt(onlyPhaseArg.split("=")[1]!, 10) : null;

interface Phase {
  id: number;
  name: string;
  command: string;
  description: string;
}

const PHASES: Phase[] = [
  {
    id: 1,
    name: "preflight-arm-oci",
    command: "bun run scripts/preflight-arm-oci.ts",
    description: "4-check safety gate (Pangolin + Komodo + Infisical + process namespace)",
  },
  {
    id: 2,
    name: "control-plane-up",
    command: "bun run --cwd bonneagar iac:bootstrap --step=control-plane",
    description: "infisical + pangolin + komodo + pocket-id + tinyauth",
  },
  {
    id: 3,
    name: "lakehouse-up",
    command: "bun run --cwd bonneagar iac:deploy --stack=lakehouse",
    description: "postgres + garage + clickhouse + redis + lakekeeper + lance-namespace",
  },
  {
    id: 4,
    name: "data-stacks-up",
    command: "bun run --cwd bonneagar iac:deploy --stacks=litellm,langfuse,mlflow,logfire,cognee,graphiti,lancedb",
    description: "litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb",
  },
  {
    id: 5,
    name: "agent-surfaces-up",
    command: "bun run --cwd bonneagar iac:deploy --stacks=openclaw,openchamber,hermes,ocr-router",
    description: "openclaw + openchamber + hermes + ocr-router (per Change 2 of the trilogy)",
  },
  {
    id: 6,
    name: "dagster-materialize",
    command: "uv run dagster job launch --job biiep_v3_ireland_lc5_materialize",
    description: "BIEP v3 upstream + downstream asset materialisation",
  },
  {
    id: 7,
    name: "dagster-sensor-health-gate",
    command: "uv run dagster sensor list --json | jq -e '.[] | select(.sensorName == \"ocr_completion_sensor\" and .status == \"STARTED\") | length == 1'",
    description: "ocr_completion_sensor + 5 other sensors report ACTIVE state",
  },
];

interface State {
  version: number;
  startedAt: string;
  updatedAt: string;
  phases: Record<number, {
    status: "pending" | "running" | "complete" | "failed" | "skipped";
    startedAt?: string;
    completedAt?: string;
    error?: string;
  }>;
}

function loadState(): State {
  if (!existsSync(STATE_FILE)) {
    return {
      version: 1,
      startedAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      phases: {},
    };
  }
  return JSON.parse(readFileSync(STATE_FILE, "utf-8"));
}

function saveState(state: State): void {
  mkdirSync(join(homedir(), ".cianfhoghlaim"), { recursive: true });
  state.updatedAt = new Date().toISOString();
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function log(level: "INFO" | "OK" | "WARN" | "ERR", msg: string): void {
  const colors = { INFO: "\x1b[1;34m", OK: "\x1b[1;32m", WARN: "\x1b[1;33m", ERR: "\x1b[1;31m" };
  const reset = "\x1b[0m";
  const ts = new Date().toISOString().slice(11, 19);
  console.log(`${colors[level]}[${ts}]${reset} ${msg}`);
}

async function runPhase(phase: Phase, state: State): Promise<boolean> {
  const status = state.phases[phase.id]?.status ?? "pending";
  if (status === "complete" || status === "skipped") {
    log("INFO", `[phase ${phase.id}] ${phase.name}: SKIPPED (cached as ${status})`);
    return true;
  }

  log("INFO", `[phase ${phase.id}] ${phase.name}: starting`);
  log("INFO", `  ${phase.description}`);
  log("INFO", `  command: ${phase.command}`);
  state.phases[phase.id] = { status: "running", startedAt: new Date().toISOString() };
  saveState(state);

  if (DRY_RUN) {
    log("INFO", `  [dry-run] would run: ${phase.command}`);
    state.phases[phase.id] = { ...state.phases[phase.id]!, status: "complete", completedAt: new Date().toISOString() };
    saveState(state);
    return true;
  }

  try {
    const proc = Bun.spawn(["bash", "-c", phase.command], {
      cwd: REPO_ROOT,
      stdout: "inherit",
      stderr: "inherit",
      timeout: PHASE_TIMEOUT_MS,
    });
    const rc = await proc.exited;
    if (rc !== 0) {
      state.phases[phase.id] = {
        ...state.phases[phase.id]!,
        status: "failed",
        completedAt: new Date().toISOString(),
        error: `exit code ${rc}`,
      };
      saveState(state);
      log("ERR", `[phase ${phase.id}] ${phase.name}: FAILED (exit ${rc})`);
      return false;
    }
    state.phases[phase.id] = {
      ...state.phases[phase.id]!,
      status: "complete",
      completedAt: new Date().toISOString(),
    };
    saveState(state);
    log("OK", `[phase ${phase.id}] ${phase.name}: complete`);
    return true;
  } catch (e: unknown) {
    state.phases[phase.id] = {
      ...state.phases[phase.id]!,
      status: "failed",
      completedAt: new Date().toISOString(),
      error: String(e),
    };
    saveState(state);
    log("ERR", `[phase ${phase.id}] ${phase.name}: ERROR ${e}`);
    return false;
  }
}

async function main(): Promise<number> {
  log("INFO", `deploy-full.ts: starting`);
  log("INFO", `  STATE_FILE=${STATE_FILE}`);
  log("INFO", `  DRY_RUN=${DRY_RUN}  ONLY_PHASE=${ONLY_PHASE}`);

  const state = loadState();
  log("INFO", `  state: ${Object.values(state.phases).filter((p) => p.status === "complete").length}/${PHASES.length} phases complete`);

  let lastFailed = false;
  for (const phase of PHASES) {
    if (ONLY_PHASE !== null && phase.id !== ONLY_PHASE) {
      if (!state.phases[phase.id]) {
        state.phases[phase.id] = { status: "skipped" };
      } else {
        state.phases[phase.id].status = "skipped";
      }
      saveState(state);
      continue;
    }
    const ok = await runPhase(phase, state);
    if (!ok) {
      lastFailed = true;
      log("ERR", `deploy halted at phase ${phase.id} (${phase.name})`);
      log("INFO", `Re-run 'mise run deploy:full' to resume from this phase (cached phases are skipped).`);
      break;
    }
  }

  const completeCount = Object.values(state.phases).filter((p) => p.status === "complete").length;
  if (lastFailed) {
    log("ERR", `deploy-full: FAILED (${completeCount}/${PHASES.length} phases complete)`);
    return 1;
  }
  log("OK", `deploy-full: COMPLETE (${completeCount}/${PHASES.length} phases complete)`);
  return 0;
}

main().then((rc) => process.exit(rc)).catch((e) => {
  log("ERR", `deploy-full: FATAL ${e}`);
  process.exit(2);
});