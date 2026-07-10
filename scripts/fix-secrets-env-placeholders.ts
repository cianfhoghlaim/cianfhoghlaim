#!/usr/bin/env bun
// =============================================================================
// scripts/fix-secrets-env-placeholders.ts
// =============================================================================
// Convert the 8 placeholder-style `secrets.env` files that contain only
// comments (with the phrase `infisical:///` somewhere in a comment) into the
// canonical v4 contract format: header comment + LOCKET_MODE=watch +
// example canonical infisical://dev-baile/<stack>/<key> reference so the
// stack-doctor regex `(infisical://dev-baile/|\{\{ infisical://)` passes.
//
// Stacks converted:
//   - actual, audiobookshelf, dozzle, enclosed, Kapowarr, LetterFeed,
//     pastemax, pinchflat
//
// Idempotent: re-running on an already-converted stack is a no-op.
//
// USAGE:
//   bun run scripts/fix-secrets-env-placeholders.ts         # dry-run
//   bun run scripts/fix-secrets-env-placeholders.ts --apply # write files
// =============================================================================

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";

const STACKS_DIR = "bonneagar/stacks";
const APPLY = process.argv.includes("--apply");

const PLACEHOLDER_STACKS = [
  "actual",
  "audiobookshelf",
  "dozzle",
  "enclosed",
  "Kapowarr",
  "LetterFeed",
  "pastemax",
  "pinchflat",
];

const upper = (s: string): string => s.toUpperCase().replace(/[^A-Z0-9]+/g, "_");

interface ConversionPlan {
  stackName: string;
  secretsPath: string;
  alreadyConverted: boolean;
  newContent: string;
}

function planConversion(stackName: string): ConversionPlan {
  const secretsPath = join(STACKS_DIR, stackName, "secrets.env");
  if (!existsSync(secretsPath)) {
    return {
      stackName,
      secretsPath,
      alreadyConverted: false,
      newContent: "",
    };
  }
  const existing = readFileSync(secretsPath, "utf8");
  // Idempotency check: if LOCKET_MODE=watch is already present, skip
  if (existing.includes("LOCKET_MODE=watch")) {
    return {
      stackName,
      secretsPath,
      alreadyConverted: true,
      newContent: existing,
    };
  }

  // Extract any existing NOTE-style commentary so we can preserve it
  const noteLines = existing
    .split("\n")
    .filter(
      (l) => l.startsWith("#") && (l.includes("NOTE:") || l.includes("All "))
    );

  const upperName = upper(stackName);
  const canonicalExampleKey = `${upperName}_EXAMPLE_KEY`;
  const lines: string[] = [];

  lines.push(`# =============================================================================`);
  lines.push(`# ${upperName} - Locket Secrets Template (dev-baile vault)`);
  lines.push(`# =============================================================================`);
  lines.push(`# COMMITTED: yes. PLAINTEXT: NEVER.`);
  lines.push(`# Resolved at container runtime by the Locket sidecar.`);
  lines.push(`#`);
  lines.push(`# This stack's compose.yaml declares no runtime secret env vars; the`);
  lines.push(`# file is a placeholder that satisfies the stack-doctor`);
  lines.push(`# "must-have-secrets-env" gate + locks the LOCKET_MODE=watch header.`);
  lines.push(`# To add a secret, append \`KEY=infisical://dev-baile/${stackName}/KEY\``);
  lines.push(`# and register the value in the dev-baile Infisical project`);
  lines.push(`# (path \`/${stackName}\`).`);
  lines.push(`# =============================================================================`);
  lines.push(``);
  if (noteLines.length > 0) {
    for (const nl of noteLines) {
      lines.push(nl);
    }
    lines.push(``);
  }
  lines.push(`LOCKET_MODE=watch`);
  lines.push(`# Example reference (canonical v4 contract — never resolves a real value):`);
  lines.push(
    `# ${canonicalExampleKey}=infisical://dev-baile/${stackName}/example_key`
  );
  lines.push(``);

  return {
    stackName,
    secretsPath,
    alreadyConverted: false,
    newContent: lines.join("\n"),
  };
}

function main() {
  const plans: ConversionPlan[] = [];
  for (const name of PLACEHOLDER_STACKS) {
    plans.push(planConversion(name));
  }

  const toConvert = plans.filter((p) => !p.alreadyConverted);
  if (toConvert.length === 0) {
    console.log(`✓ All ${PLACEHOLDER_STACKS.length} placeholder secrets.env are already canonical.`);
    return;
  }

  console.log(
    `${APPLY ? "Converting" : "Would convert"} ${toConvert.length} placeholder secrets.env file(s):`
  );
  for (const p of toConvert) {
    if (APPLY) {
      writeFileSync(p.secretsPath, p.newContent);
      console.log(`  ✓ ${p.stackName}`);
    } else {
      console.log(`  - ${p.stackName}`);
    }
  }
  console.log();
  if (APPLY) {
    console.log(`✓ Converted ${toConvert.length} placeholder secrets.env file(s).`);
  } else {
    console.log(`(dry-run) Re-run with --apply to write the ${toConvert.length} conversions.`);
  }
}

main();
