#!/usr/bin/env bun
/**
 * scripts/_run_mise_task.ts
 *
 * Tiny helper that runs a `mise run <task>` subprocess and returns its
 * exit code. Used by the `notebook:check` + `notebook:gate`
 * subcommands in scripts/cianfhoghlaim-cli.ts.
 *
 * Per the 2026-08-10-marimo-v14-cascading-effects-verification-v1 change.
 *
 * Usage:
 *   bun scripts/_run_mise_task.ts biep:v3:marimo:all
 *   bun scripts/_run_mise_task.ts biep:v3:ireland:gate --milestone=m1
 */
import { spawn } from "node:child_process";

const task = process.argv[2];
if (!task) {
  console.error("usage: _run_mise_task.ts <task> [args...]");
  process.exit(2);
}
const args = process.argv.slice(3);

const child = spawn("mise", ["run", task, ...args], {
  stdio: "inherit",
  env: process.env,
});
child.on("exit", (code) => process.exit(code ?? 1));
