#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-topology.ts
 *
 * Validate host placement (arm1-oci / bunchloch) for one or all stacks.
 * No deploy operation performed — read-only.
 *
 * Subcommands:
 *   validate [stack]
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");
const STACKS_DIR = join(ROOT, "bonneagar", "stacks");
const ALLOWED_HOSTS = new Set(["arm1-oci", "bunchloch"]);

interface Diag {
  stack: string;
  file: string;
  line?: number;
  code: string;
  message: string;
}

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
  let subcommand = args[0];
  let single: string | null = null;
  if (subcommand && !subcommand.startsWith("--")) {
    args.shift();
  } else {
    subcommand = "validate";
  }
  single = args[0] && !args[0].startsWith("--") ? args[0] : null;

  if (subcommand !== "validate") {
    console.error(`Unknown subcommand: ${subcommand}`);
    return 2;
  }

  const diagnostics: Diag[] = [];
  const targets: string[] = [];
  if (single) {
    targets.push(join(STACKS_DIR, single));
  } else {
    for (const d of walkStacks(STACKS_DIR)) targets.push(d);
  }

  for (const dir of targets) {
    const stack = relative(STACKS_DIR, dir);
    let text: string;
    try {
      text = readFileSync(join(dir, "blueprint.yaml"), "utf8");
    } catch {
      // No blueprint — skip; this stack is non-routed (CLI, internal tool, etc.)
      continue;
    }
    // Look for `sites:` entries
    const sitesRe = /sites:\s*\n((?:\s*-\s*\S+\s*\n)+)/m;
    const m = text.match(sitesRe);
    if (!m) {
      diagnostics.push({
        stack,
        file: "blueprint.yaml",
        code: "missing-sites",
        message: "Pangolin EE blueprint missing sites[]",
      });
      continue;
    }
    const sites = (m[1].match(/-\s*(\S+)/g) || []).map((s) => s.replace(/^-\s*/, ""));
    for (const site of sites) {
      if (!ALLOWED_HOSTS.has(site)) {
        diagnostics.push({
          stack,
          file: "blueprint.yaml",
          code: "invalid-host",
          message: `Unknown site "${site}" (allowed: ${[...ALLOWED_HOSTS].join(", ")})`,
        });
      }
    }
  }

  if (diagnostics.length === 0) {
    console.log(`topology: ${targets.length} stacks, all sites valid`);
    return 0;
  } else {
    console.log(`topology: ${targets.length} stacks, ${diagnostics.length} issue(s)`);
    for (const d of diagnostics) console.log(`  [${d.code}]  ${d.stack}/${d.file}  ${d.message}`);
    return 1;
  }
}

process.exit(main());