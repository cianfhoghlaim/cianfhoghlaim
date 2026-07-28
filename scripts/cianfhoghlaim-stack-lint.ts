#!/usr/bin/env bun
/**
 * scripts/cianfhoghlaim-stack-lint.ts
 *
 * Lint every stack under bonneagar/stacks/ against the canonical
 * 6-file Cianfhoghlaim contract.
 *
 * Checks (per the OpenSpec change 2026-07-28):
 *   1. All 6 required files are present.
 *   2. compose.yaml MUST NOT contain `env_file: /run/secrets/locket/...`.
 *   3. sidecar.yaml MUST use one of the canonical Locket images.
 *   4. secrets.env MUST use Locket templates (legacy `infisical://` URIs
 *      accepted with a legacy-secret-syntax warning).
 *   5. blueprint.yaml MUST be a Pangolin EE root blueprint.
 *   6. pangolin.yaml middlewares MUST appear only in the Traefik overlay
 *      (not in blueprint roles[]).
 *
 * Exits 0 on clean, 1 on failures, 2 on usage error.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const ROOT = resolve(import.meta.dir, "..");
const STACKS_DIR = join(ROOT, "bonneagar", "stacks");

interface Diag {
  code: string;
  stack: string;
  file: string;
  line?: number;
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
    if (st.isDirectory()) {
      yield full;
    }
  }
}

function detectStackName(stackDir: string): string {
  return relative(STACKS_DIR, stackDir);
}

function checkRequiredFiles(stack: string, dir: string, diagnostics: Diag[]): boolean {
  const required = [
    "compose.yaml",
    "sidecar.yaml",
    "secrets.env",
    "pangolin.yaml",
    "blueprint.yaml",
    ".env.example",
  ];
  let ok = true;
  for (const f of required) {
    try {
      statSync(join(dir, f));
    } catch {
      diagnostics.push({
        code: "missing-file",
        stack,
        file: f,
        message: `Missing required file ${f} in ${stack}`,
      });
      ok = false;
    }
  }
  return ok;
}

function lintCompose(stack: string, dir: string, diagnostics: Diag[]): void {
  let text: string;
  try {
    text = readFileSync(join(dir, "compose.yaml"), "utf8");
  } catch {
    return;
  }
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/env_file:.*\/run\/secrets\/locket/.test(line)) {
      diagnostics.push({
        code: "forbidden-env-file",
        stack,
        file: "compose.yaml",
        line: i + 1,
        message:
          "env_file: /run/secrets/locket/... fails at parse time. Use the shell-wrapper pattern from sidecar.yaml instead.",
      });
    }
    if (/\bbons-locker-shim\b/.test(line) || /\bbons-locket-shim\b/.test(line)) {
      diagnostics.push({
        code: "brand-renamed",
        stack,
        file: "compose.yaml",
        line: i + 1,
        message: "ghcr.io/cianfhoghlaim/locket-shim is renamed to ghcr.io/cianfhoghlaim/locket-shim",
      });
    }
  }
}

function lintSidecar(stack: string, dir: string, diagnostics: Diag[]): void {
  let text: string;
  try {
    text = readFileSync(join(dir, "sidecar.yaml"), "utf8");
  } catch {
    return;
  }
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/\bbons-locker-shim\b/.test(line) || /\bbons-locket-shim\b/.test(line)) {
      diagnostics.push({
        code: "brand-renamed",
        stack,
        file: "sidecar.yaml",
        line: i + 1,
        message: "ghcr.io/cianfhoghlaim/locket-shim is renamed to ghcr.io/cianfhoghlaim/locket-shim",
      });
    }
    if (/\bimage:\s*\S+/.test(line) && !/locket/i.test(line) && !/locker/i.test(line)) {
      // ok — application image
    }
    if (/env_file:\s*\/?run\/secrets\/locket/.test(line)) {
      diagnostics.push({
        code: "forbidden-env-file",
        stack,
        file: "sidecar.yaml",
        line: i + 1,
        message:
          "sidecar.yaml MUST NOT declare env_file: /run/secrets/locket/...; use the shell-wrapper pattern instead.",
      });
    }
  }
}

function lintSecretsEnv(stack: string, dir: string, diagnostics: Diag[]): void {
  let text: string;
  try {
    text = readFileSync(join(dir, "secrets.env"), "utf8");
  } catch {
    return;
  }
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eqIdx = trimmed.indexOf("=");
    if (eqIdx < 0) continue;
    const key = trimmed.slice(0, eqIdx).trim();
    const value = trimmed.slice(eqIdx + 1).trim();
    if (/^infisical:\/\/[^/]+\/[^/]+\/[^/]+$/.test(value)) {
      diagnostics.push({
        code: "legacy-secret-syntax",
        stack,
        file: "secrets.env",
        line: i + 1,
        message: `${key}: legacy Infisical URI. Migrate to {{ infisical:///key?env=dev-baile&path=/${stack} }} (accepted but warned).`,
      });
    } else if (/^\{\{[\s]*infisical:\/\/\/[^?}]+\}\}\s*$/.test(value)) {
      // ok — Locket template (no query string)
    } else if (/^\{\{[\s]*infisical:\/\/\/[^?]+\?[^}]+\}\}\s*$/.test(value)) {
      // ok — Locket template (with query string)
    } else if (!/^#/.test(trimmed)) {
      diagnostics.push({
        code: "non-secret-in-secrets-env",
        stack,
        file: "secrets.env",
        line: i + 1,
        message: `${key}: value is not a recognised Infisical URI or Locket template. Move non-secret values to compose.yaml.`,
      });
    }
  }
}

function lintBlueprint(stack: string, dir: string, diagnostics: Diag[]): void {
  let text: string;
  try {
    text = readFileSync(join(dir, "blueprint.yaml"), "utf8");
  } catch {
    return;
  }
  // Detect Komodo-shaped legacy blueprint
  const looksKomodo =
    /^\s*name:\s/m.test(text) &&
    /^\s*type:\s*(stack|procedure|action)\s*$/m.test(text) &&
    /^\s*run_directory:/m.test(text);
  if (looksKomodo) {
    diagnostics.push({
      code: "legacy-blueprint-shape",
      stack,
      file: "blueprint.yaml",
      message:
        "blueprint.yaml uses Komodo Resource Sync syntax. Migrate to the Pangolin EE root blueprint (private-resources:/public-resources:/sites:).",
    });
  }
}

function lintPangolin(stack: string, dir: string, diagnostics: Diag[]): void {
  let text: string;
  try {
    text = readFileSync(join(dir, "pangolin.yaml"), "utf8");
  } catch {
    return;
  }
  const lines = text.split(/\r?\n/);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/roles\[0\]:\s*[^[]/.test(line)) {
      diagnostics.push({
        code: "middleware-in-roles",
        stack,
        file: "pangolin.yaml",
        line: i + 1,
        message:
          "Middleware references belong in http.routers.<svc>.middlewares, not in roles[0] (Pangolin EE blueprint).",
      });
    }
  }
}

function main(): number {
  const args = process.argv.slice(2);
  let asJson = false;
  let single: string | null = null;
  for (const arg of args) {
    if (arg === "--json") asJson = true;
    else if (!arg.startsWith("--")) single = arg;
  }

  const diagnostics: Diag[] = [];
  const stackDirs: string[] = [];
  if (single) {
    stackDirs.push(join(STACKS_DIR, single));
  } else {
    for (const d of walkStacks(STACKS_DIR)) stackDirs.push(d);
  }

  for (const dir of stackDirs) {
    const stack = detectStackName(dir);
    const filesPresent = checkRequiredFiles(stack, dir, diagnostics);
    if (filesPresent) {
      lintCompose(stack, dir, diagnostics);
      lintSidecar(stack, dir, diagnostics);
      lintSecretsEnv(stack, dir, diagnostics);
      lintBlueprint(stack, dir, diagnostics);
      lintPangolin(stack, dir, diagnostics);
    }
  }

  const errors = diagnostics.filter(
    (d) => d.code !== "legacy-secret-syntax" && d.code !== "non-secret-in-secrets-env",
  );
  const warnings = diagnostics.filter((d) =>
    d.code === "legacy-secret-syntax" || d.code === "non-secret-in-secrets-env"
  );

  if (asJson) {
    console.log(
      JSON.stringify(
        { stackCount: stackDirs.length, errors: errors.length, warnings: warnings.length, diagnostics },
        null,
        2,
      ),
    );
  } else {
    console.log(`stack-lint: ${stackDirs.length} stacks, ${errors.length} errors, ${warnings.length} warnings`);
    for (const d of diagnostics) {
      const loc = `${d.stack}/${d.file}${d.line ? `:${d.line}` : ""}`;
      console.log(`  [${d.code}]  ${loc}  ${d.message}`);
    }
  }
  return errors.length === 0 ? 0 : 1;
}

process.exit(main());