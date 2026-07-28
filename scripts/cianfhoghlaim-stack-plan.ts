#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-stack-plan.ts
 *
 * Compute the deployment plan for one or all stacks (read-only).
 * Stub for now — Phase 6 will wire this to Komodo + Pangolin REST.
 */

import { readdirSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");
const STACKS_DIR = join(ROOT, "bonneagar", "stacks");

function* walkStacks(dir: string): Generator<string> {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = join(dir, entry);
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) yield full;
  }
}

function main(): number {
  const args = process.argv.slice(2);
  let single: string | null = null;
  for (const arg of args) {
    if (!arg.startsWith("--")) single = arg;
  }
  const targets = single ? [join(STACKS_DIR, single)] : Array.from(walkStacks(STACKS_DIR));
  console.log(`stack-plan: ${targets.length} stacks planned (no-op stub).`);
  for (const dir of targets) {
    console.log(`  - ${relative(STACKS_DIR, dir)}`);
  }
  return 0;
}

process.exit(main());