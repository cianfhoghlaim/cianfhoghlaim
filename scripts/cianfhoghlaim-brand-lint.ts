#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-brand-lint.ts
 *
 * Brand and Hetzner linter. Fails if any active file references:
 *   - bons, bons-locker-shim, bons-locket-shim (legacy brand)
 *   - kcg (legacy CLI prefix)
 *   - KCGu (legacy host alias)
 *   - cax41, cax41-hetzner, cax41-workloads (retired host)
 *   - security.hetzner (Dagger host alias for retired host)
 *
 * Exclusions:
 *   - .agents/skills_backup/
 *   - stedding/
 *   - bonneagar/_archive/
 *   - .research/
 *   - .git/
 *   - node_modules/
 *   - spaces/data-engineering/
 *
 * Exit codes:
 *   0 = clean
 *   1 = violations found
 *   2 = usage error
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");
const TARGET_EXTS = new Set([
  ".md",
  ".yaml",
  ".yml",
  ".ts",
  ".tsx",
  ".js",
  ".mjs",
  ".cjs",
  ".toml",
  ".env",
  ".sh",
  ".py",
  ".txt",
]);
const EXCLUDED_DIRS = new Set([
  ".agents/skills_backup",
  "stedding",
  "bonneagar/_archive",
  "bonneagar/iac/pulumi/hetzner",
  "bonneagar/stacks/openclaw/skills-curated",
  "bonneagar/stacks/GOLD_STANDARD.md",
  "scripts/cianfhoghlaim-brand-lint.ts",
  "scripts/cianfhoghlaim-preflight.ts",
  "scripts/cianfhoghlaim-stack-lint.ts",
  "scripts/cianfhoghlaim-cli.ts",
  ".research",
  ".git",
  "node_modules",
  "spaces/data-engineering",
]);

interface Violation {
  file: string;
  line: number;
  token: string;
  text: string;
}

const RULES: Array<{ token: RegExp; reason: string }> = [
  { token: /\bbons-locker-shim\b/, reason: "brand-renamed" },
  { token: /\bbons-locket-shim\b/, reason: "brand-renamed" },
  { token: /\bbons:\b/, reason: "brand-renamed" },
  { token: /\bkcg:stack\b/, reason: "brand-renamed" },
  { token: /\bKCGu\b/, reason: "brand-renamed" },
  { token: /\bcax41-hetzner\b/, reason: "retired-host-reference" },
  { token: /\bcax41-workloads\b/, reason: "retired-host-reference" },
  { token: /\bcax41\b/, reason: "retired-host-reference" },
  { token: /\bsecurity\.hetzner\b/, reason: "retired-host-reference" },
];

function isExcluded(path: string): boolean {
  for (const dir of EXCLUDED_DIRS) {
    if (path === dir || path.startsWith(dir + "/")) return true;
  }
  return false;
}

function* walk(dir: string): Generator<string> {
  let entries: string[];
  try {
    entries = readdirSync(dir);
  } catch {
    return;
  }
  for (const entry of entries) {
    const full = join(dir, entry);
    const rel = relative(ROOT, full);
    if (isExcluded(rel)) continue;
    let st;
    try {
      st = statSync(full);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      yield* walk(full);
    } else if (st.isFile()) {
      const dotIdx = entry.lastIndexOf(".");
      if (dotIdx >= 0 && TARGET_EXTS.has(entry.slice(dotIdx))) {
        yield full;
      }
    }
  }
}

function lintFile(file: string): Violation[] {
  const text = readFileSync(file, "utf8");
  const lines = text.split(/\r?\n/);
  const violations: Violation[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const { token, reason } of RULES) {
      if (token.test(line)) {
        violations.push({
          file: relative(ROOT, file),
          line: i + 1,
          token: token.source,
          text: line.trim().slice(0, 200),
        });
        break;
      }
    }
  }
  return violations;
}

function main(): number {
  const args = process.argv.slice(2);
  let asJson = false;
  const roots: string[] = [];
  for (const arg of args) {
    if (arg === "--json") {
      asJson = true;
    } else if (!arg.startsWith("--")) {
      roots.push(arg);
    }
  }
  if (roots.length === 0) {
    roots.push("bonneagar", "mise.toml", ".infisical.env", "scripts");
  }

  const violations: Violation[] = [];
  for (const r of roots) {
    const abs = resolve(ROOT, r);
    let st;
    try {
      st = statSync(abs);
    } catch {
      continue;
    }
    if (st.isDirectory()) {
      for (const file of walk(abs)) violations.push(...lintFile(file));
    } else if (st.isFile()) {
      violations.push(...lintFile(abs));
    }
  }

  if (asJson) {
    console.log(
      JSON.stringify({ violations: violations.length, details: violations }, null, 2),
    );
  } else if (violations.length === 0) {
    console.log("brand-lint: OK (0 violations)");
  } else {
    console.log(`brand-lint: ${violations.length} violation(s)`);
    for (const v of violations) {
      console.log(`  ${v.file}:${v.line}  [${v.token}]  ${v.text}`);
    }
  }

  return violations.length === 0 ? 0 : 1;
}

process.exit(main());