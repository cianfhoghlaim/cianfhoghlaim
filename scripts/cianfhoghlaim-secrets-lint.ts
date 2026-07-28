#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-secrets-lint.ts
 *
 * Lint secrets.env references against the canonical Cianfhoghlaim
 * contract. Equivalent to cianfhoghlaim stack lint, scoped to the
 * secrets.env layer.
 *
 * Flags:
 *   --verify     Verify references resolve against Infisical (no values printed)
 *   --stack=X    Limit to one stack
 *
 * Exit codes:
 *   0 = clean
 *   1 = violations found
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");
const STACKS_DIR = join(ROOT, "bonneagar", "stacks");

interface Diag {
  stack: string;
  file: string;
  line: number;
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

const URI_RE = /^infisical:\/\/[^/]+\/[^/]+\/[^/]+$/;
const TEMPLATE_NO_QS_RE = /^\{\{[\s]*infisical:\/\/\/[^?}]+\}\}\s*$/;
const TEMPLATE_QS_RE = /^\{\{[\s]*infisical:\/\/\/[^?]+\?[^}]+\}\}\s*$/;

function lint(stack: string, file: string): Diag[] {
  const text = readFileSync(file, "utf8");
  const lines = text.split(/\r?\n/);
  const diags: Diag[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx < 0) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const value = trimmed.slice(eqIdx + 1).trim();
    if (URI_RE.test(value)) {
      diags.push({
        stack,
        file: "secrets.env",
        line: i + 1,
        code: "legacy-secret-syntax",
        message: `${key}: legacy Infisical URI. Migrate to {{ infisical:///key?env=dev-baile&path=/${stack} }} (accepted but warned).`,
      });
    } else if (TEMPLATE_NO_QS_RE.test(value) || TEMPLATE_QS_RE.test(value)) {
      // ok
    } else {
      diags.push({
        stack,
        file: "secrets.env",
        line: i + 1,
        code: "non-secret-in-secrets-env",
        message: `${key}: value is not a recognised Infisical URI or Locket template.`,
      });
    }
  }
  return diags;
}

function main(): number {
  const args = process.argv.slice(2);
  let asJson = false;
  let single: string | null = null;
  let verify = false;
  for (const arg of args) {
    if (arg === "--json") asJson = true;
    else if (arg === "--verify") verify = true;
    else if (arg.startsWith("--stack=")) single = arg.slice("--stack=".length);
    else if (!arg.startsWith("--")) single = arg;
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
    const f = join(dir, "secrets.env");
    try {
      statSync(f);
    } catch {
      continue;
    }
    diagnostics.push(...lint(stack, f));
  }

  const errors = diagnostics.filter((d) => d.code === "non-secret-in-secrets-env");
  const warnings = diagnostics.filter((d) => d.code === "legacy-secret-syntax");

  if (verify) {
    // Verification against Infisical is intentionally not implemented in
    // this change — it requires live API access and an authenticated machine
    // identity. Stays a stub until Phase 6 wires the @infisical/sdk client.
    if (!asJson) console.log("secrets: verify — stub (not yet wired to @infisical/sdk)");
  }

  if (asJson) {
    console.log(
      JSON.stringify(
        { stacks: targets.length, errors: errors.length, warnings: warnings.length, diagnostics },
        null,
        2,
      ),
    );
  } else {
    console.log(`secrets-lint: ${targets.length} stacks, ${errors.length} errors, ${warnings.length} warnings`);
  }
  return errors.length === 0 ? 0 : 1;
}

process.exit(main());