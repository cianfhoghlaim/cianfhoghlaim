/**
 * scripts/schema-generate.ts
 *
 * The `bun run schema:generate` CLI — emits two committed artifacts:
 *
 * 1. `apps/web/src/lib/lineage-registry.ts`
 *    Walks `leaving_certificate/<subject>/{en,ga}/*.pdf` + the 4 NCCA
 *    root-level PDFs and emits a deterministic JSON registry with SHA-256 +
 *    byte_size + page_count + ingested_at per PDF.
 *    Per openspec R27.
 *
 * 2. `apps/web/src/lib/bi-ep.gen.ts` + `bi-ep.gen.lock.json`
 *    For each of the 6 BIEP v1 subjects × 4 tables (syllabus / papers /
 *    marking_schemes / topics), emits a Zod schema + a TanStack DB collection
 *    config. The lock file records the DuckLake schema version + the
 *    generated-file hash for drift detection.
 *    Per openspec R30.
 *
 * Usage:
 *   bun run schema:generate                       # default: walks from repo root
 *   bun run schema:generate --root <path>         # override the leaving_cert dir
 *   bun run schema:generate --offline              # skip DuckLake; use static BIEP v1 schema
 *   bun run schema:generate --local-db <path>       # introspect a local .duckdb file (default: data/oideachais.duckdb if present)
 *   bun run schema:generate --help
 *
 * The CLI is **idempotent** — running it twice on the same filesystem +
 * DuckLake schema produces byte-identical output. Determinism comes from:
 * - Sorted PDF enumeration (by `pdf_path` ascending)
 * - Stable JSON indentation (2 spaces, no trailing newline drift)
 * - Deterministic timestamp from a clock override (defaults to UTC ISO 8601)
 *
 * DuckLake/DuckDB introspection (2026-08-26 rewrite): shells out to
 * `uv run python3 scripts/_introspect_duckdb.py` instead of importing the
 * Node.js `duckdb` package directly. The Node native bindings for `duckdb`
 * are known-unreliable under bun (see `web/hono-api/src/data/duckdb.ts`'s
 * own comment about this); the Python `duckdb` package is already a pinned
 * repo dependency and works identically for local files and MotherDuck.
 * The introspection is now GENERIC (discovers whatever tables actually
 * exist) rather than a hardcoded 6-subject × 4-suffix cross product that
 * silently no-ops if that exact schema doesn't exist yet.
 *
 * Output relocation (2026-08-26): in addition to the legacy
 * `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
 * (kept so the existing app doesn't break), also emits the introspected
 * tables to `web/packages/contracts/src/generated/` — the new shared
 * canonical location per the schema-contract remediation plan. Every app
 * should import from `@cianfhoghlaim/contracts` going forward instead of
 * a per-app generated file.
 *
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
 * tasks.md Phase 1.
 */

import * as crypto from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";

import {
  walkLineageRegistry,
  emitRegistryTs,
  type LineageRegistry,
} from "./_lineage-walker";

import {
  buildBiepV1StaticTables,
  emitTableZodSchema,
  tableNameToIdentifier,
  type DuckDBTable,
} from "./_zod-from-duckdb";

// =============================================================================
// CLI arg parsing
// =============================================================================

interface CliArgs {
  root: string; // absolute path to leaving_certificate/
  offline: boolean; // skip DuckLake; use static BIEP v1 schema
  localDb: string; // absolute path to a local .duckdb file, or "" for auto-detect
  help: boolean;
  repoRoot: string; // absolute path to repo root (where apps/web/ lives)
}

function parseArgs(argv: ReadonlyArray<string>): CliArgs {
  const args: CliArgs = {
    root: "",
    offline: false,
    localDb: "",
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
      case "--offline":
        args.offline = true;
        break;
      case "--local-db":
        if (!next) throw new Error("--local-db requires a path argument");
        args.localDb = path.resolve(next);
        i++;
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

// =============================================================================
// Default path resolution
// =============================================================================

/**
 * Find the repo root by walking up from CWD until we find `pyproject.toml`.
 * Falls back to CWD if not found.
 */
function findRepoRoot(start: string): string {
  let dir = path.resolve(start);
  while (true) {
    try {
      // eslint-disable-next-line @typescript-eslint/no-require-imports
      require("node:fs").accessSync(path.join(dir, "pyproject.toml"));
      return dir;
    } catch {
      const parent = path.dirname(dir);
      if (parent === dir) {
        return path.resolve(start);
      }
      dir = parent;
    }
  }
}

// =============================================================================
// lineage-registry.ts emitter
// =============================================================================

async function generateLineageRegistry(
  leavingCertDir: string,
  outputPath: string,
): Promise<{ count: number; sha256: string }> {
  console.log(`[lineage] walking ${leavingCertDir}`);
  const registry = await walkLineageRegistry(leavingCertDir);
  const source = emitRegistryTs(registry);
  await fs.writeFile(outputPath, source, "utf8");
  const sha256 = crypto.createHash("sha256").update(source).digest("hex");
  const totalCount =
    registry.root_pdfs.length +
    Object.values(registry.subjects).reduce(
      (acc, langs) => acc + langs.en.length + langs.ga.length,
      0,
    );
  console.log(
    `[lineage] wrote ${outputPath} (${totalCount} PDFs, sha256=${sha256.slice(0, 12)}…)`,
  );
  return { count: totalCount, sha256 };
}

// =============================================================================
// bi-ep.gen.ts emitter (the DuckLake → Zod + TanStack DB codegen)
// =============================================================================

/**
 * Pure in-memory source builder — no filesystem I/O. Shared by both
 * `schema-generate.ts` (writes the result to disk) and
 * `schema-validate.ts` (diffs the result against the committed file
 * without writing). Keeping this as one function means a fix here
 * (e.g. the 2026-08-26 Zod v4 `z.record()` / identifier-collision /
 * TanStack-stub-removal fixes) can't drift out of sync between the two
 * scripts the way the pre-2026-08-26 versions had.
 */
export function buildBiEpGenSource(tables: DuckDBTable[]): {
  source: string;
  unknown_columns: string[];
} {
  const subjectNames = new Set<string>();
  const tableEmits: Array<{
    identifier: string;
    table: DuckDBTable;
    source: string;
  }> = [];
  const unknownColumns: string[] = [];
  const seenIdentifiers = new Set<string>();

  for (const table of tables) {
    let identifier = tableNameToIdentifier(table.table);
    if (seenIdentifiers.has(identifier)) {
      // Two tables in different schemas share a table name (e.g. a
      // non-dlt-staging duplicate). Disambiguate with the schema name
      // rather than silently emitting a duplicate `export const` — that
      // would be invalid TypeScript.
      const disambiguated = `${tableNameToIdentifier(table.schema)}${identifier}`;
      console.warn(
        `[bi-ep.gen] identifier collision: "${identifier}" (table "${table.table}") ` +
          `already used — disambiguating to "${disambiguated}"`,
      );
      identifier = disambiguated;
    }
    seenIdentifiers.add(identifier);
    subjectNames.add(table.table.replace(/_(syllabus|papers|marking_schemes|topics)$/, ""));
    const { source, unknown_columns } = emitTableZodSchema(table, identifier);
    tableEmits.push({ identifier, table, source });
    unknownColumns.push(...unknown_columns.map((c) => `${table.table}.${c}`));
  }

  // NOTE (2026-08-26): TanStack DB collection helpers are intentionally
  // NOT emitted here. The prior version hardcoded `primaryKey: "topic_id"`
  // for every table (wrong for the 3-of-4 table kinds that don't have that
  // column) and a bare `createCollection({schema, tableName, database,
  // primaryKey})` call that does not typecheck against @tanstack/db's real
  // `createCollection` signature (confirmed via `tsc --noEmit` against the
  // introspected output — it needs a `getKey` + a sync strategy, both of
  // which are app-specific decisions this generic generator cannot invent).
  // Emitting code presented as working but that doesn't typecheck is worse
  // than not emitting it. When an app actually wires TanStack DB collections
  // (Phase 5 UI work), hand-write `getKey`/sync per collection against the
  // Zod schemas below, which DO typecheck and ARE the real contract.

  // Compose the full emitted source.
  // NOTE: the emitted file MUST be deterministic (no timestamps, no
  // random IDs) so `schema-validate` can byte-compare against the committed
  // file. The lock file (`bi-ep.gen.lock.json`) carries the generation
  // timestamp separately.
  const header: string[] = [
    "// AUTO-GENERATED by `bun run schema:generate` (scripts/schema-generate.ts).",
    "// DO NOT EDIT — re-run the generator to update.",
    "//",
    "// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1",
    "// R30 (DuckLake → Zod codegen). Source of truth: introspected DuckDB/DuckLake",
    "// table schemas (see scripts/_introspect_duckdb.py), not a hand-maintained list.",
    "// TanStack DB collection helpers are NOT emitted — see schema-generate.ts",
    "// for why (they need a per-collection sync strategy this generator can't invent).",
    "",
    'import { z } from "zod";',
    "",
    `// Generated from ${tables.length} table(s).`,
    "",
  ];

  const body: string[] = [];
  for (const { source } of tableEmits) {
    body.push(source, "");
  }

  const fullSource = [...header, ...body].join("\n");
  return { source: fullSource, unknown_columns: unknownColumns };
}

/** File-writing wrapper around `buildBiEpGenSource` — used by `main()`. */
async function generateBiEpGen(
  tables: DuckDBTable[],
  outputPath: string,
  lockPath: string,
): Promise<{ schema_version: number; file_hash: string; unknown_columns: string[] }> {
  console.log(`[bi-ep.gen] generating from ${tables.length} tables`);
  const { source: fullSource, unknown_columns: unknownColumns } = buildBiEpGenSource(tables);

  await fs.writeFile(outputPath, fullSource, "utf8");
  const fileHash = crypto.createHash("sha256").update(fullSource).digest("hex");

  // Emit the lock file — schema_version + file hash + per-table column count.
  const lock = {
    schema_version: 1,
    generated_at: new Date().toISOString(),
    file_hash: fileHash,
    table_count: tables.length,
    tables: tables.map((t) => ({
      name: t.table,
      database: t.database,
      schema: t.schema,
      column_count: t.columns.length,
    })),
    unknown_columns: unknownColumns,
  };
  await fs.writeFile(lockPath, JSON.stringify(lock, null, 2) + "\n", "utf8");

  console.log(
    `[bi-ep.gen] wrote ${outputPath} (${tables.length} tables, ${unknownColumns.length} unknown columns, hash=${fileHash.slice(0, 12)}…)`,
  );
  return { schema_version: 1, file_hash: fileHash, unknown_columns: unknownColumns };
}

// =============================================================================
// Main
// =============================================================================

async function main(): Promise<void> {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);
  const repoRoot = args.repoRoot || findRepoRoot(process.cwd());
  const leavingCertDir = args.root || path.join(repoRoot, "leaving_certificate");
  const registryOutPath = path.join(
    repoRoot,
    "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/lineage-registry.ts",
  );
  const biEpGenOutPath = path.join(
    repoRoot,
    "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts",
  );
  const biEpGenLockPath = path.join(
    repoRoot,
    "web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.lock.json",
  );
  // New canonical shared location (2026-08-26) — every app should import
  // from @cianfhoghlaim/contracts instead of a per-app generated file.
  const contractsGenOutPath = path.join(
    repoRoot,
    "web/packages/contracts/src/generated/bi-ep.gen.ts",
  );
  const contractsGenLockPath = path.join(
    repoRoot,
    "web/packages/contracts/src/generated/bi-ep.gen.lock.json",
  );

  if (args.help) {
    console.log(
      [
        "schema-generate — emit the BIEP v1 lineage registry + Zod schemas",
        "",
        "Usage:",
        "  bun run schema:generate [--root <leaving_cert_dir>] [--offline] [--local-db <path>]",
        "",
        "Options:",
        "  --root <path>      Path to the leaving_certificate/ directory",
        "                     (default: <repo-root>/leaving_certificate)",
        "  --offline          Skip DuckDB entirely; use the static BIEP v1 schema",
        "                     (from BAML + lib/bi-ep.ts)",
        "  --local-db <path>  Introspect a local .duckdb file instead of MotherDuck",
        "                     (default: data/oideachais.duckdb if it exists)",
        "  --help, -h         Show this help",
        "",
        "Outputs:",
        `  ${path.relative(repoRoot, registryOutPath)}`,
        `  ${path.relative(repoRoot, biEpGenOutPath)}  (legacy, kept for the existing app)`,
        `  ${path.relative(repoRoot, biEpGenLockPath)}`,
        `  ${path.relative(repoRoot, contractsGenOutPath)}  (new canonical — import from here)`,
        `  ${path.relative(repoRoot, contractsGenLockPath)}`,
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
    console.error(`[error] pass --root <path> to override`);
    process.exit(1);
  }

  // 2. Generate the lineage registry (filesystem walk — always works).
  await generateLineageRegistry(leavingCertDir, registryOutPath);

  // 3. Generate bi-ep.gen.ts + lock (legacy path) + the new canonical
  //    contracts-package output.
  //    - When `args.offline` is true: use the static BIEP v1 schema (no DB).
  //    - Else if `--local-db` given (or data/oideachais.duckdb exists):
  //      introspect that local file (works with no MOTHERDUCK_TOKEN).
  //    - Else: try MotherDuck → fall back to static if unreachable.
  let tables: DuckDBTable[];
  if (args.offline) {
    console.log("[bi-ep.gen] offline mode — using static BIEP v1 schema");
    tables = buildBiepV1StaticTables();
  } else {
    let localDbCandidate = args.localDb;
    if (!localDbCandidate) {
      const defaultDbPath = path.join(repoRoot, DEFAULT_LOCAL_DB);
      if (await fileExists(defaultDbPath)) {
        localDbCandidate = defaultDbPath;
      }
    }
    try {
      if (localDbCandidate) {
        console.log(`[bi-ep.gen] introspecting local DuckDB file: ${localDbCandidate}`);
        tables = await introspectDuckLake(repoRoot, { localDb: localDbCandidate });
      } else if (process.env.MOTHERDUCK_TOKEN) {
        console.log("[bi-ep.gen] introspecting MotherDuck: md:oideachais");
        tables = await introspectDuckLake(repoRoot, { motherduckUri: "md:oideachais" });
      } else {
        throw new Error(
          "no local DB found and MOTHERDUCK_TOKEN not set — use --offline or --local-db",
        );
      }
      console.log(`[bi-ep.gen] introspected ${tables.length} tables`);
      if (tables.length === 0) {
        console.warn(
          "[bi-ep.gen] introspection returned 0 tables — falling back to static BIEP v1 schema",
        );
        tables = buildBiepV1StaticTables();
      }
    } catch (err) {
      console.warn(`[bi-ep.gen] DuckDB introspection failed: ${(err as Error).message}`);
      console.warn("[bi-ep.gen] falling back to static BIEP v1 schema");
      tables = buildBiepV1StaticTables();
    }
  }
  await generateBiEpGen(tables, biEpGenOutPath, biEpGenLockPath);
  await fs.mkdir(path.dirname(contractsGenOutPath), { recursive: true });
  await generateBiEpGen(tables, contractsGenOutPath, contractsGenLockPath);

  console.log("[done] schema generation complete");
}

// =============================================================================
// DuckLake introspection (live path; the offline fallback is the static schema)
// =============================================================================

interface IntrospectResult {
  source: string;
  tables: DuckDBTable[];
}

/**
 * Shell out to `scripts/_introspect_duckdb.py` to discover every table
 * actually present in the target database (local file or MotherDuck).
 *
 * Rewritten 2026-08-26 to avoid the Node.js `duckdb` native package
 * (unreliable under bun) and to discover real tables instead of assuming
 * a hardcoded 6×4 BIEP v1 cross-product that may not exist yet in the
 * target database.
 */
export async function introspectDuckLake(
  repoRoot: string,
  opts: { localDb?: string; motherduckUri?: string; schemaFilter?: string },
): Promise<DuckDBTable[]> {
  const args = ["run", "python3", "scripts/_introspect_duckdb.py"];
  if (opts.localDb) {
    args.push("--db", opts.localDb);
  } else if (opts.motherduckUri) {
    args.push("--motherduck", opts.motherduckUri);
  } else {
    throw new Error("introspectDuckLake requires either localDb or motherduckUri");
  }
  if (opts.schemaFilter) {
    args.push("--schema", opts.schemaFilter);
  }

  const proc = Bun.spawn(["uv", ...args], {
    cwd: repoRoot,
    stdout: "pipe",
    stderr: "pipe",
  });
  const [stdout, stderr, exitCode] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
    proc.exited,
  ]);
  if (stderr.trim()) {
    // The Python helper logs per-table DESCRIBE warnings to stderr but
    // still succeeds overall — surface them as warnings, not failures.
    console.warn(`[bi-ep.gen] introspection warnings:\n${stderr.trim()}`);
  }
  if (exitCode !== 0) {
    throw new Error(`_introspect_duckdb.py exited ${exitCode}: ${stderr.trim()}`);
  }
  let parsed: IntrospectResult;
  try {
    parsed = JSON.parse(stdout.trim().split("\n").pop() ?? "{}") as IntrospectResult;
  } catch (err) {
    throw new Error(`failed to parse introspection JSON: ${(err as Error).message}\nstdout: ${stdout}`);
  }
  return parsed.tables;
}

/** Default local DuckDB file to try when no --local-db / --offline flag is given. */
export const DEFAULT_LOCAL_DB = "data/oideachais.duckdb";

export async function fileExists(p: string): Promise<boolean> {
  try {
    await fs.access(p);
    return true;
  } catch {
    return false;
  }
}

// =============================================================================
// Entry point
// =============================================================================

if (import.meta.main) {
  main().catch((err) => {
    console.error(err);
    process.exit(1);
  });
}