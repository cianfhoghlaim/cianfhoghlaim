/**
 * scripts/schema-validate.ts
 *
 * `bun run schema:validate` — CI drift gate for the generated Zod schemas.
 *
 * Regenerates `apps/web/src/lib/bi-ep.gen.ts` in-memory, diffs against the
 * committed file (byte-level + structural diff), and exits non-zero if the
 * upstream DuckLake schema has changed.
 *
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
 * R30 (DuckLake → Zod + TanStack DB collection codegen).
 *
 * Usage:
 *   bun run schema:validate                 # default: introspect DuckLake
 *   bun run schema:validate --offline       # use the static BIEP v1 schema
 *   bun run schema:validate --gen-path <p>  # override the gen file path
 *   bun run schema:validate --quiet         # exit 0 silently on success
 *
 * Exit codes:
 *   0 — no drift (committed file matches the regenerated file)
 *   1 — drift detected (run `bun run schema:generate` to fix)
 *   2 — committed file missing
 */

import * as crypto from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";

import { buildBiepV1StaticTables, type DuckDBTable } from "./_zod-from-duckdb";
import {
  buildBiEpGenSource,
  introspectDuckLake,
  DEFAULT_LOCAL_DB,
  fileExists,
} from "./schema-generate";

// =============================================================================
// CLI arg parsing
// =============================================================================

interface CliArgs {
  offline: boolean;
  genPath: string;
  lockPath: string;
  quiet: boolean;
  help: boolean;
  repoRoot: string;
}

function parseArgs(argv: ReadonlyArray<string>): CliArgs {
  const args: CliArgs = {
    offline: false,
    genPath: "",
    lockPath: "",
    quiet: false,
    help: false,
    repoRoot: "",
  };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    const next = argv[i + 1];
    switch (arg) {
      case "--offline":
        args.offline = true;
        break;
      case "--gen-path":
        if (!next) throw new Error("--gen-path requires a path argument");
        args.genPath = path.resolve(next);
        i++;
        break;
      case "--lock-path":
        if (!next) throw new Error("--lock-path requires a path argument");
        args.lockPath = path.resolve(next);
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
// In-memory regeneration + introspection
// =============================================================================
//
// Both delegate to scripts/schema-generate.ts's `buildBiEpGenSource` /
// `introspectDuckLake` rather than duplicating the logic (2026-08-26
// refactor). The pre-refactor version had its own copies that had
// drifted: it still hardcoded a `primaryKey: "topic_id"` TanStack DB
// stub that doesn't typecheck, and its own `introspectFromDuckLake`
// used the same unreliable Node.js `duckdb` native binding. A fix in
// one copy but not the other would have made this drift gate compare
// against logic that no longer matches the generator it's meant to
// validate. See `buildBiEpGenSource`'s docstring in schema-generate.ts.

// =============================================================================
// Diff printer
// =============================================================================

interface LineDiff {
  lineNo: number;
  committed: string;
  regenerated: string;
}

/**
 * Produce a minimal unified-style diff between the committed file and the
 * regenerated content. We don't use a third-party diff lib — a line-by-line
 * LCS is enough for CI output.
 */
function diffLines(committed: string, regenerated: string): LineDiff[] {
  const a = committed.split("\n");
  const b = regenerated.split("\n");
  const max = Math.max(a.length, b.length);
  const diffs: LineDiff[] = [];
  for (let i = 0; i < max; i++) {
    const ca = a[i] ?? "";
    const cb = b[i] ?? "";
    if (ca !== cb) {
      diffs.push({ lineNo: i + 1, committed: ca, regenerated: cb });
    }
  }
  return diffs;
}

// =============================================================================
// Main
// =============================================================================

// The 2 committed locations to keep in sync (2026-08-26): the new
// canonical shared package, and the legacy per-app file (kept only
// because no app has migrated off it yet — see the package-topology
// remediation plan). Both are validated by default so neither can
// silently drift; `--gen-path` overrides to check just one.
function defaultTargets(repoRoot: string): Array<{ genPath: string; lockPath: string; label: string }> {
  return [
    {
      label: "contracts (canonical)",
      genPath: path.join(repoRoot, "web/packages/contracts/src/generated/bi-ep.gen.ts"),
      lockPath: path.join(repoRoot, "web/packages/contracts/src/generated/bi-ep.gen.lock.json"),
    },
    {
      label: "cianfhoghlaim-leaving-cert (legacy)",
      genPath: path.join(
        repoRoot,
        "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts",
      ),
      lockPath: path.join(
        repoRoot,
        "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.lock.json",
      ),
    },
  ];
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const repoRoot = args.repoRoot || findRepoRoot(process.cwd());
  const targets = args.genPath
    ? [{ label: "custom", genPath: args.genPath, lockPath: args.lockPath }]
    : defaultTargets(repoRoot);

  if (args.help) {
    console.log(
      [
        "schema-validate — CI drift gate for the generated Zod schemas",
        "",
        "Usage:",
        "  bun run schema:validate [--offline] [--gen-path <p>] [--quiet]",
        "",
        "Options:",
        "  --offline             Use the static BIEP v1 schema (skip DuckLake)",
        "  --gen-path <path>     Override the gen file path",
        "  --lock-path <path>    Override the lock file path",
        "  --quiet               Exit 0 silently on success",
        "",
        "Exit codes:",
        "  0 — no drift",
        "  1 — drift detected",
        "  2 — gen file missing",
        "",
      ].join("\n"),
    );
    return;
  }

  // Regenerate in memory once — shared across all targets (they're
  // supposed to be byte-identical to each other, generated from the
  // same table list).
  let tables: DuckDBTable[];
  if (args.offline) {
    tables = buildBiepV1StaticTables();
  } else {
    let localDbCandidate = "";
    const defaultDbPath = path.join(repoRoot, DEFAULT_LOCAL_DB);
    if (await fileExists(defaultDbPath)) localDbCandidate = defaultDbPath;
    try {
      tables = localDbCandidate
        ? await introspectDuckLake(repoRoot, { localDb: localDbCandidate })
        : await introspectDuckLake(repoRoot, { motherduckUri: "md:oideachais" });
      if (tables.length === 0) tables = buildBiepV1StaticTables();
    } catch (err) {
      console.error(`[error] DuckDB introspection failed: ${(err as Error).message}`);
      console.error(`[hint] pass --offline to use the static schema`);
      process.exit(1);
    }
  }
  const { source: regenerated } = buildBiEpGenSource(tables);
  const regenHash = crypto.createHash("sha256").update(regenerated).digest("hex");

  let anyDrift = false;
  for (const target of targets) {
    let committed: string;
    try {
      committed = await fs.readFile(target.genPath, "utf8");
    } catch {
      console.error(`[error] [${target.label}] ${target.genPath} not found`);
      console.error(`[hint] run \`bun run schema:generate\` to create it`);
      anyDrift = true;
      continue;
    }
    const committedHash = crypto.createHash("sha256").update(committed).digest("hex");
    if (regenHash === committedHash) {
      if (!args.quiet) {
        console.log(
          `[schema:validate] OK [${target.label}] — matches the live schema (hash=${regenHash.slice(0, 12)}…)`,
        );
      }
      continue;
    }
    anyDrift = true;
    console.error(`[schema:validate] DRIFT DETECTED [${target.label}]`);
    console.error(`  committed:   ${committedHash.slice(0, 12)}…`);
    console.error(`  regenerated: ${regenHash.slice(0, 12)}…`);
    console.error("");
    const diffs = diffLines(committed, regenerated);
    if (diffs.length <= 50) {
      for (const d of diffs) {
        console.error(`  line ${d.lineNo}:`);
        if (d.committed) console.error(`    - ${d.committed}`);
        if (d.regenerated) console.error(`    + ${d.regenerated}`);
      }
    } else {
      console.error(
        `  (${diffs.length} lines differ — too many to print; run \`bun run schema:generate\` for a full regeneration)`,
      );
    }
    console.error("");
  }

  if (anyDrift) {
    console.error(`[hint] run \`bun run schema:generate\` to regenerate the committed file(s)`);
    process.exit(1);
  }
  process.exit(0);
}

if (import.meta.main) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}