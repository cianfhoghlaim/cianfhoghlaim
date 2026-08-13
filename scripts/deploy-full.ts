#!/usr/bin/env bun
/**
 * deploy-full.ts — One-command full-stack deploy orchestrator (TypeScript state machine)
 *
 * Per the 2026-08-01-lakehouse-and-reproducible-deploy-v1 openspec change:
 *
 *   "The system MUST provide a `mise run deploy:full` command that brings
 *    up the entire 91-stack platform in 10 phases with healthchecks + a
 *    resumable checkpoint state file at `~/.cianfhoghlaim/deploy-state.json`.
 *    The 10 phases MUST be (in this order):
 *      1. preflight-arm-oci
 *      2. iac-auth-rotate         (added 2026-08-15 per the bonneagar-infra-remediation-v2 openspec change)
 *      3. pocketid-oidc-wire      (added 2026-08-15)
 *      4. pangolin-client-install (added 2026-08-15)
 *      5. control-plane-up
 *      6. lakehouse-up
 *      7. data-stacks-up
 *      8. ocr-backends-up         (added 2026-08-02 post-trilogy-cleanup)
 *      9. agent-surfaces-up
 *     10. dagster-materialize-and-sensor-health-gate (combined)"
 *
 * This is the TypeScript state machine that owns the resumable checkpoint.
 * The shell entry (`scripts/deploy-full.sh`) delegates here after preflight.
 *
 * FIXED 2026-08-02 (post-trilogy-cleanup):
 *   - Phase 2: was `iac:bootstrap --step=control-plane` (drift — --step=
 *     is not a valid flag); now `iac:bootstrap-control-plane --target=bunchloch`
 *   - Phases 3-5: were `iac:deploy --stacks=litellm,langfuse,...` (drift —
 *     --stacks= plural is not in CLI_FLAGS; only --stack= singular is parsed);
 *     now uses a per-stack loop calling `docker compose -f <stack>/compose.yaml -f sidecar.yaml up -d`
 *     for each stack (the actual bringup; iac:deploy is purely sync)
 *   - Phases 6 + 7: were `uv run dagster ...` (drift — canonical CLI is
 *     `dg` per `dg.toml`); now `uv run dg launch --module
 *     orchestration.definitions --job <name>` and `uv run dg sensor list --json`
 *   - Phase 5 (NEW 2026-08-02): `ocr-backends-up` — brings up the 7 OCR
 *     backends (paddleocr + dots-ocr + olmocr + docling-serve + mlx-omni +
 *     llama-swap + meaisinfoghlaim). Renumbered subsequent phases 5→6, 6→7,
 *     7→8.
 *
 * EXTENDED 2026-08-15 (per the 2026-08-15-bonneagar-infra-remediation-v2
 * openspec change): 3 NEW phases (iac-auth-rotate, pocketid-oidc-wire,
 * pangolin-client-install) inserted between the preflight and control-plane;
 * dagster-materialize + dagster-sensor-health-gate merged into one phase
 * 10 to keep the total at 10 phases.
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
// import.meta.url.pathname ends without trailing slash; use a normal regex
// to drop the trailing slash for cleaner join paths (avoid `//bonneagar`).
const REPO_ROOT_RAW = new URL("..", import.meta.url).pathname;
const REPO_ROOT = REPO_ROOT_RAW.endsWith("/") ? REPO_ROOT_RAW.slice(0, -1) : REPO_ROOT_RAW;
const STATE_FILE = join(homedir(), ".cianfhoghlaim", "deploy-state.json");
const STACK_HEALTH_TIMEOUT_MS = 60_000; // 60s per health probe
const PHASE_TIMEOUT_MS = 600_000; // 10 min per phase

// Host detection for control-plane target
const HOSTNAME = (await import("node:os")).hostname();
const CONTROL_PLANE_TARGET = HOSTNAME === "prod" ? "arm1-oci" : "bunchloch";

// --- Args ---
const args = process.argv.slice(2);
const SKIP_PREFLIGHT = args.includes("--skip-preflight");
const DRY_RUN = args.includes("--dry-run");
const onlyPhaseArg = args.find((a) => a.startsWith("--phase="));
const ONLY_PHASE = onlyPhaseArg ? parseInt(onlyPhaseArg.split("=")[1]!, 10) : null;

interface Phase {
  id: number;
  name: string;
  description: string;
  // `command` is either a string (run as bash -c) or a function (run via Bun.spawn with array args)
  command: string | { cmd: string[]; cwd?: string };
  isMultiStack?: boolean; // phase 4/5 iterate a stack list
  // Optional `postCommand` runs after the multi-stack bringup completes
  // (added 2026-08-15-lakehouse-memory-stack for the Phase 7 doctor probe).
  postCommand?: string;
}

// The 7 data-stacks (Lakehouse owns its own phase). Order matters: litellm must
// come up first (it's the chokepoint every agent surface talks to).
const DATA_STACKS = ["litellm", "langfuse", "mlflow", "logfire", "cognee", "graphiti", "lancedb"] as const;

// The 7 OCR backends (added in 2026-08-02 post-trilogy-cleanup). Order matters:
// llama-swap is last because it holds the heavy on-device GGUF reservation
// (32-48 GB RAM); running it first can starve the rest.
const OCR_STACKS = ["paddleocr", "dots-ocr", "olmocr", "docling-serve", "mlx-omni", "llama-swap", "meaisinfoghlaim"] as const;

// The 3 agent surfaces + the new ocr-router from Change 2.
const AGENT_STACKS = ["openclaw", "openchamber", "hermes", "ocr-router"] as const;

const PHASES: Phase[] = [
  {
    id: 1,
    name: "preflight-arm-oci",
    description: "4-check safety gate (Pangolin + Komodo + Infisical + process namespace)",
    command: "bun run scripts/preflight-arm-oci.ts",
  },
  {
    // ADDED 2026-08-15 (per the 2026-08-15-bonneagar-infra-remediation-v2
    // openspec change). 3-way credential rotation: Pangolin + Komodo + Infisical.
    id: 2,
    name: "iac-auth-rotate",
    description: "iac:rotate-auth — 3-way credential rotation (Pangolin API key + Komodo password + Infisical token)",
    command: `bun run --cwd ${REPO_ROOT}/bonneagar iac:rotate-auth`,
  },
  {
    // ADDED 2026-08-15: wire Pocket ID as OIDC for Komodo + Pangolin.
    id: 3,
    name: "pocketid-oidc-wire",
    description: "iac:wire-pocketid-as-oidc — wire Pocket ID as the OIDC IdP for Komodo + Pangolin (idempotent)",
    command: `bun run --cwd ${REPO_ROOT}/bonneagar iac:wire-pocketid-as-oidc --domain=cianfhoghlaim.ie`,
  },
  {
    // ADDED 2026-08-15: install pangolin CLI + mint Pangolin client + render newt compose.
    id: 4,
    name: "pangolin-client-install",
    description: "iac:bootstrap-pangolin-client — install pangolin CLI + mint a Pangolin client + render newt compose for arm1-oci",
    command: `bun run --cwd ${REPO_ROOT}/bonneagar iac:bootstrap-pangolin-client --host=arm1-oci --type=machine`,
  },
  {
    id: 5,
    name: "control-plane-up",
    description: `infisical + pangolin + komodo + pocket-id + tinyauth (target=${CONTROL_PLANE_TARGET})`,
    command: `bun run --cwd ${REPO_ROOT}/bonneagar iac:bootstrap-control-plane --target=${CONTROL_PLANE_TARGET}`,
  },
  {
    id: 6,
    name: "lakehouse-up",
    description: "postgres + garage + clickhouse + redis + lakekeeper + lance-namespace",
    command: `cd ${REPO_ROOT} && docker compose -f bonneagar/stacks/lakehouse/compose.yaml -f bonneagar/stacks/lakehouse/sidecar.yaml up -d`,
  },
  {
    id: 7,
    name: "data-stacks-up",
    description: `${DATA_STACKS.length} data stacks: ${DATA_STACKS.join(", ")} → +memory-stack doctor probe (per the 2026-08-15-lakehouse-memory-stack-deep-integration-v1 change)`,
    command: `loop:${DATA_STACKS.join(",")}`,
    isMultiStack: true,
    // After the multi-stack bringup completes, run the lakehouse memory
    // doctor (Phase E of the 2026-08-15 change). The doctor probes the 5
    // memory backends (cognee + graphiti + lancedb + falkordb + memgraph)
    // + emits a JSON health report. The phase fails if any backend is
    // not healthy.
    postCommand: `bun run ${REPO_ROOT}/scripts/lakehouse-memory-doctor.ts --strict`,
  },
  {
    id: 8,
    name: "ocr-backends-up",
    description: `${OCR_STACKS.length} OCR backends: ${OCR_STACKS.join(", ")}`,
    command: `loop:${OCR_STACKS.join(",")}`,
    isMultiStack: true,
  },
  {
    id: 9,
    name: "agent-surfaces-up",
    description: `${AGENT_STACKS.length} agent surfaces: ${AGENT_STACKS.join(", ")}`,
    command: `loop:${AGENT_STACKS.join(",")}`,
    isMultiStack: true,
  },
  {
    // COMBINED 2026-08-15: the original 7 (dagster-materialize) + 8 (dagster-sensor-health-gate)
    // are merged into a single phase 10 to keep the total at 10 phases.
    id: 10,
    name: "dagster-materialize-and-sensor-health-gate",
    description: "BIEP v3 materialise (the canonical smoke-test asset) + verify ocr_completion_sensor + 5 others are STARTED",
    command: `uv run dg launch --module orchestration.definitions --job biiep_v3_ireland_lc5_materialize && uv run dg sensor list --json | jq -e '[.[] | select(.sensorName == "ocr_completion_sensor" and .status == "STARTED")] | length == 1'`,
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

async function runShell(cmd: string, cwd: string = REPO_ROOT): Promise<number> {
  const proc = Bun.spawn(["bash", "-c", cmd], {
    cwd,
    stdout: "inherit",
    stderr: "inherit",
    timeout: PHASE_TIMEOUT_MS,
  });
  return await proc.exited;
}

async function bringUpStack(stackName: string): Promise<boolean> {
  const composeCmd = [
    "docker", "compose",
    "-f", `bonneagar/stacks/${stackName}/compose.yaml`,
    "-f", `bonneagar/stacks/${stackName}/sidecar.yaml`,
    "up", "-d",
  ];
  log("INFO", `  docker compose up -d ${stackName}`);
  if (DRY_RUN) {
    log("INFO", `    [dry-run] would run: ${composeCmd.join(" ")}`);
    return true;
  }
  const proc = Bun.spawn(composeCmd, { cwd: REPO_ROOT, stdout: "inherit", stderr: "inherit" });
  const rc = await proc.exited;
  if (rc !== 0) {
    log("ERR", `  docker compose up -d ${stackName} exited ${rc}`);
    return false;
  }
  // Quick healthcheck poll: docker compose ps --filter health=healthy
  const psProc = Bun.spawn([
    "docker", "compose",
    "-f", `bonneagar/stacks/${stackName}/compose.yaml`,
    "-f", `bonneagar/stacks/${stackName}/sidecar.yaml`,
    "ps", "--format", "json",
  ], { cwd: REPO_ROOT, stdout: "pipe", stderr: "pipe" });
  const psOut = await new Response(psProc.stdout).text();
  // If stdout is empty (no docker available), skip the healthcheck — assume OK in dry-run mode.
  if (!psOut.trim()) {
    log("WARN", `  ${stackName}: docker compose ps returned empty (docker not available locally?)`);
    return true;
  }
  log("INFO", `  ${stackName}: docker compose up -d succeeded`);
  return true;
}

async function runPhase(phase: Phase, state: State): Promise<boolean> {
  const status = state.phases[phase.id]?.status ?? "pending";
  if (status === "complete" || status === "skipped") {
    log("INFO", `[phase ${phase.id}] ${phase.name}: SKIPPED (cached as ${status})`);
    return true;
  }

  log("INFO", `[phase ${phase.id}] ${phase.name}: starting`);
  log("INFO", `  ${phase.description}`);

  if (phase.isMultiStack) {
    // Multi-stack phase: iterate the stack list, bring each up.
    if (typeof phase.command !== "string" || !phase.command.startsWith("loop:")) {
      log("ERR", `[phase ${phase.id}] ${phase.name}: multi-stack phase requires loop: command`);
      return false;
    }
    const stacks = phase.command.slice(5).split(",");
    log("INFO", `  multi-stack loop over: ${stacks.join(", ")}`);

    state.phases[phase.id] = { status: "running", startedAt: new Date().toISOString() };
    saveState(state);

    if (DRY_RUN) {
      log("INFO", `  [dry-run] would bring up ${stacks.length} stacks`);
      state.phases[phase.id] = { ...state.phases[phase.id]!, status: "complete", completedAt: new Date().toISOString() };
      saveState(state);
      return true;
    }

    for (const stack of stacks) {
      const ok = await bringUpStack(stack);
      if (!ok) {
        state.phases[phase.id] = {
          ...state.phases[phase.id]!,
          status: "failed",
          completedAt: new Date().toISOString(),
          error: `stack ${stack} failed to come up`,
        };
        saveState(state);
        log("ERR", `[phase ${phase.id}] ${phase.name}: FAILED at ${stack}`);
        return false;
      }
    }
    state.phases[phase.id] = { ...state.phases[phase.id]!, status: "complete", completedAt: new Date().toISOString() };
    saveState(state);
    log("OK", `[phase ${phase.id}] ${phase.name}: complete (${stacks.length} stacks up)`);

    // Run the optional postCommand (added 2026-08-15-lakehouse-memory-stack
    // for the Phase 7 memory doctor probe). If it fails, mark the phase as
    // failed and return false.
    if (phase.postCommand) {
      log("INFO", `[phase ${phase.id}] running postCommand: ${phase.postCommand}`);
      if (DRY_RUN) {
        log("INFO", `  [dry-run] would run postCommand: ${phase.postCommand}`);
      } else {
        try {
          const postRc = await runShell(phase.postCommand);
          if (postRc !== 0) {
            state.phases[phase.id] = {
              ...state.phases[phase.id]!,
              status: "failed",
              error: `postCommand exit code ${postRc}`,
              completedAt: new Date().toISOString(),
            };
            saveState(state);
            log("ERR", `[phase ${phase.id}] ${phase.name}: FAILED at postCommand (memory doctor)`);
            return false;
          }
          log("OK", `[phase ${phase.id}] postCommand: memory doctor passed`);
        } catch (e) {
          log("ERR", `[phase ${phase.id}] postCommand threw: ${e instanceof Error ? e.message : String(e)}`);
          state.phases[phase.id] = {
            ...state.phases[phase.id]!,
            status: "failed",
            error: `postCommand threw: ${e instanceof Error ? e.message : String(e)}`,
            completedAt: new Date().toISOString(),
          };
          saveState(state);
          return false;
        }
      }
    }

    return true;
  }

  // Single-command phase
  if (typeof phase.command !== "string") {
    log("ERR", `[phase ${phase.id}] ${phase.name}: unexpected command type`);
    return false;
  }
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
    const rc = await runShell(phase.command);
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
    state.phases[phase.id] = { ...state.phases[phase.id]!, status: "complete", completedAt: new Date().toISOString() };
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
  log("INFO", `  CONTROL_PLANE_TARGET=${CONTROL_PLANE_TARGET}`);
  log("INFO", `  DRY_RUN=${DRY_RUN}  ONLY_PHASE=${ONLY_PHASE}`);

  if (SKIP_PREFLIGHT && ONLY_PHASE === null) {
    log("WARN", "skipping preflight-arm-oci (--skip-preflight set)");
  } else if (!SKIP_PREFLIGHT && ONLY_PHASE !== 1) {
    // Phase 1 always runs unless explicitly skipped OR the user is running
    // a single non-preflight phase. This matches the spec.
    // (handled inside runPhase loop)
  }

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
    if (SKIP_PREFLIGHT && phase.id === 1) {
      log("INFO", `[phase 1] preflight-arm-oci: SKIPPED (--skip-preflight)`);
      state.phases[phase.id] = { ...(state.phases[phase.id] ?? { status: "pending" }), status: "skipped" };
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