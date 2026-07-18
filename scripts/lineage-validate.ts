/**
 * scripts/lineage-validate.ts
 *
 * `bun run lineage:validate` — CI drift gate for the lineage registry.
 *
 * Re-walks `leaving_certificate/<subject>/{en,ga}/*.pdf` + the 4 NCCA root-level
 * PDFs, diffs against the committed `apps/web/src/lib/lineage-registry.ts`, and
 * exits non-zero if any PDF was added, removed, or its SHA-256 / page_count /
 * byte_size has changed.
 *
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
 * R27 (PDF source registry + filesystem walk + CI drift gate).
 *
 * Usage:
 *   bun run lineage:validate                 # default: walks from repo root
 *   bun run lineage:validate --root <path>   # override the leaving_cert dir
 *   bun run lineage:validate --quiet         # exit 0 silently on success
 *
 * Exit codes:
 *   0 — no drift (committed registry matches the filesystem)
 *   1 — drift detected (added / removed / changed PDFs)
 *   2 — registry file missing (run `bun run schema:generate` first)
 */

import * as fs from "node:fs/promises";
import * as path from "node:path";

import {
  walkLineageRegistry,
  diffRegistries,
  type LineageRegistry,
  type LineagePDFEntry,
} from "./_lineage-walker";

// =============================================================================
// CLI arg parsing
// =============================================================================

interface CliArgs {
  root: string;
  registry: string;
  quiet: boolean;
  help: boolean;
  repoRoot: string;
}

function parseArgs(argv: ReadonlyArray<string>): CliArgs {
  const args: CliArgs = {
    root: "",
    registry: "",
    quiet: false,
    help: false,
    repoRoot: "",
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];
    switch (arg) {
      case "--root":
        if (!next) throw new Error("--root requires a path argument");
        args.root = path.resolve(next);
        i++;
        break;
      case "--registry":
        if (!next) throw new Error("--registry requires a path argument");
        args.registry = path.resolve(next);
        i++;
        break;
      case "--quiet":
        args.quiet = true;
        break;
      case "--help":
      case "-h":
        args.help = true;
        break;
      default:
        if (arg.startsWith("--")) {
          throw new Error(`Unknown flag: ${arg}`);
        }
    }
  }
  return args;
}

function findRepoRoot(start: string): string {
  let dir = path.resolve(start);
  while (true) {
    try {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      require("node:fs").accessSync(path.join(dir, "pyproject.toml"));
      return dir;
    } catch {
      const parent = path.dirname(dir);
      if (parent === dir) return path.resolve(start);
      dir = parent;
    }
  }
}

// =============================================================================
// Registry loader
// =============================================================================

/**
 * Load the committed registry from
 * `apps/web/src/lib/lineage-registry.ts`. We can't `import` it directly
 * because it's auto-generated TS that depends on the type alias from
 * `@cianfhoghlaim/lineage-types` — instead we parse it as TS source via a
 * tiny regex extractor.
 */
async function loadCommittedRegistry(registryPath: string): Promise<LineageRegistry> {
  const source = await fs.readFile(registryPath, "utf8");

  // Find the `export const LINEAGE_REGISTRY: LineageRegistry = { ... };`
  // assignment and JSON-parse the RHS.
  const match = source.match(/export const LINEAGE_REGISTRY:\s*\w+\s*=\s*(\{[\s\S]*?\});/);
  if (!match) {
    throw new Error(
      `Could not find LINEAGE_REGISTRY export in ${registryPath}. ` +
        `Run \`bun run schema:generate\` to regenerate.`,
    );
  }
  try {
    return JSON.parse(match[1]) as LineageRegistry;
  } catch (err) {
    throw new Error(
      `Failed to JSON.parse LINEAGE_REGISTRY from ${registryPath}: ${(err as Error).message}`,
    );
  }
}

// =============================================================================
// Drift printer
// =============================================================================

function formatEntry(entry: LineagePDFEntry, prefix = "  "): string {
  return `${prefix}- ${entry.pdf_path} (sha256=${entry.sha256.slice(0, 12)}…, pages=${entry.page_count}, bytes=${entry.byte_size})`;
}

function formatChangedEntry(
  diff: { pdf_path: string; before: LineagePDFEntry; after: LineagePDFEntry },
): string {
  const lines: string[] = [];
  lines.push(`  ${diff.pdf_path}`);
  if (diff.before.sha256 !== diff.after.sha256) {
    lines.push(`    sha256: ${diff.before.sha256.slice(0, 12)}… → ${diff.after.sha256.slice(0, 12)}…`);
  }
  if (diff.before.page_count !== diff.after.page_count) {
    lines.push(`    page_count: ${diff.before.page_count} → ${diff.after.page_count}`);
  }
  if (diff.before.byte_size !== diff.after.byte_size) {
    lines.push(`    byte_size: ${diff.before.byte_size} → ${diff.after.byte_size}`);
  }
  return lines.join("\n");
}

// =============================================================================
// Main
// =============================================================================

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const repoRoot = args.repoRoot || findRepoRoot(process.cwd());
  const leavingCertDir = args.root || path.join(repoRoot, "leaving_certificate");
  const registryPath =
    args.registry ||
    path.join(
      repoRoot,
      "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/lineage-registry.ts",
    );

  if (args.help) {
    console.log(
      [
        "lineage-validate — CI drift gate for the lineage registry",
        "",
        "Usage:",
        "  bun run lineage:validate [--root <dir>] [--registry <path>] [--quiet]",
        "",
        "Options:",
        "  --root <dir>         Path to the leaving_certificate/ directory",
        "  --registry <path>    Path to the committed registry TS file",
        "  --quiet              Exit 0 silently on success",
        "",
        "Exit codes:",
        "  0 — no drift",
        "  1 — drift detected",
        "  2 — registry file missing",
        "",
      ].join("\n"),
    );
    return;
  }

  // 1. Verify the leaving_cert directory exists.
  try {
    const stat = await fs.stat(leavingCertDir);
    if (!stat.isDirectory()) {
      throw new Error(`Not a directory: ${leavingCertDir}`);
    }
  } catch (err) {
    console.error(`[error] leaving_certificate directory not found: ${leavingCertDir}`);
    process.exit(1);
  }

  // 2. Verify the registry file exists.
  let committed: LineageRegistry;
  try {
    committed = await loadCommittedRegistry(registryPath);
  } catch (err) {
    console.error(`[error] ${(err as Error).message}`);
    console.error(`[hint] run \`bun run schema:generate\` to create the registry`);
    process.exit(2);
  }

  // 3. Walk the filesystem + diff.
  const live = await walkLineageRegistry(leavingCertDir);
  const diff = diffRegistries(committed, live);

  // 4. Report.
  if (diff.added.length === 0 && diff.removed.length === 0 && diff.changed.length === 0) {
    if (!args.quiet) {
      console.log("[lineage:validate] OK — registry matches the filesystem");
    }
    process.exit(0);
  }

  console.error("[lineage:validate] DRIFT DETECTED");
  if (diff.added.length > 0) {
    console.error(`\n  Added (${diff.added.length}):`);
    for (const entry of diff.added) {
      console.error(formatEntry(entry));
    }
  }
  if (diff.removed.length > 0) {
    console.error(`\n  Removed (${diff.removed.length}):`);
    for (const entry of diff.removed) {
      console.error(formatEntry(entry));
    }
  }
  if (diff.changed.length > 0) {
    console.error(`\n  Changed (${diff.changed.length}):`);
    for (const c of diff.changed) {
      console.error(formatChangedEntry(c));
    }
  }
  console.error(
    `\n[hint] run \`bun run schema:generate\` to regenerate the committed registry`,
  );
  process.exit(1);
}

if (import.meta.main) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}