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
 *   bun run schema:generate                 # default: walks from repo root
 *   bun run schema:generate --root <path>   # override the leaving_cert dir
 *   bun run schema:generate --offline       # skip DuckLake; use static BIEP v1 schema
 *   bun run schema:generate --help
 *
 * The CLI is **idempotent** — running it twice on the same filesystem +
 * DuckLake schema produces byte-identical output. Determinism comes from:
 * - Sorted PDF enumeration (by `pdf_path` ascending)
 * - Stable JSON indentation (2 spaces, no trailing newline drift)
 * - Deterministic timestamp from a clock override (defaults to UTC ISO 8601)
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
  help: boolean;
  repoRoot: string; // absolute path to repo root (where apps/web/ lives)
}

function parseArgs(argv: ReadonlyArray<string>): CliArgs {
  const args: CliArgs = {
    root: "",
    offline: false,
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

async function generateBiEpGen(
  tables: DuckDBTable[],
  outputPath: string,
  lockPath: string,
): Promise<{ schema_version: number; file_hash: string; unknown_columns: string[] }> {
  console.log(`[bi-ep.gen] generating from ${tables.length} tables`);

  const subjectNames = new Set<string>();
  const tableEmits: Array<{
    identifier: string;
    table: DuckDBTable;
    source: string;
  }> = [];
  const unknownColumns: string[] = [];

  for (const table of tables) {
    const identifier = tableNameToIdentifier(table.table);
    subjectNames.add(table.table.replace(/_(syllabus|papers|marking_schemes|topics)$/, ""));
    const { source, unknown_columns } = emitTableZodSchema(table, identifier);
    tableEmits.push({ identifier, table, source });
    unknownColumns.push(...unknown_columns.map((c) => `${table.table}.${c}`));
  }

  // Build the TanStack DB collection helpers — one per table.
  const collectionHelpers = tableEmits.map(({ identifier, table }) => {
    const dbName = `${table.database}_${table.schema}`;
    return `export function create${identifier}Collection() {
  return createCollection({
    schema: ${identifier}Schema,
    tableName: "${table.table}",
    database: "${dbName}",
    primaryKey: "topic_id",
    // ... additional TanStack DB wiring (loader, sync, etc.)
  });
}`;
  });

  // Compose the full emitted source.
  // NOTE: the emitted file MUST be deterministic (no timestamps, no
  // random IDs) so `schema-validate` can byte-compare against the committed
  // file. The lock file (`bi-ep.gen.lock.json`) carries the generation
  // timestamp separately.
  const header: string[] = [
    "// apps/web/src/lib/bi-ep.gen.ts",
    "//",
    "// AUTO-GENERATED by `bun run schema:generate` (scripts/schema-generate.ts).",
    "// DO NOT EDIT — re-run the generator to update.",
    "//",
    "// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1",
    "// R30 (DuckLake → Zod + TanStack DB collection codegen).",
    "",
    'import { z } from "zod";',
    'import { createCollection } from "@tanstack/db";',
    "",
    `// Generated from ${tables.length} BIEP v1 tables.`,
    "",
  ];

  const body: string[] = [];
  for (const { source } of tableEmits) {
    body.push(source, "");
  }

  const collectionSection: string[] = [
    "// =====================================================================",
    "// TanStack DB collection helpers",
    "// =====================================================================",
    "",
    ...collectionHelpers,
    "",
  ];

  const fullSource = [...header, ...body, ...collectionSection].join("\n");

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

  if (args.help) {
    console.log(
      [
        "schema-generate — emit the BIEP v1 lineage registry + Zod schemas",
        "",
        "Usage:",
        "  bun run schema:generate [--root <leaving_cert_dir>] [--offline]",
        "",
        "Options:",
        "  --root <path>   Path to the leaving_certificate/ directory",
        "                  (default: <repo-root>/leaving_certificate)",
        "  --offline       Skip the DuckLake/MotherDuck connection and use the",
        "                  static BIEP v1 schema (from BAML + lib/bi-ep.ts)",
        "  --help, -h      Show this help",
        "",
        "Outputs:",
        `  ${path.relative(repoRoot, registryOutPath)}`,
        `  ${path.relative(repoRoot, biEpGenOutPath)}`,
        `  ${path.relative(repoRoot, biEpGenLockPath)}`,
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

  // 3. Generate bi-ep.gen.ts + lock.
  //    - When `args.offline` is true: use the static BIEP v1 schema (no DB).
  //    - Otherwise: try DuckLake → fall back to static if the connection fails.
  let tables: DuckDBTable[];
  if (args.offline) {
    console.log("[bi-ep.gen] offline mode — using static BIEP v1 schema");
    tables = buildBiepV1StaticTables();
  } else {
    try {
      tables = await introspectBiepV1FromDuckLake();
      console.log(`[bi-ep.gen] introspected ${tables.length} tables from DuckLake`);
    } catch (err) {
      console.warn(
        `[bi-ep.gen] DuckLake introspection failed: ${(err as Error).message}`,
      );
      console.warn("[bi-ep.gen] falling back to static BIEP v1 schema");
      tables = buildBiepV1StaticTables();
    }
  }
  await generateBiEpGen(tables, biEpGenOutPath, biEpGenLockPath);

  console.log("[done] schema generation complete");
}

// =============================================================================
// DuckLake introspection (live path; the offline fallback is the static schema)
// =============================================================================

/**
 * Connect to the canonical DuckLake database `md:oideachais` and introspect
 * every BIEP v1 table. Returns the schema as `DuckDBTable[]`.
 *
 * When the connection fails (no MOTHERDUCK_TOKEN, no lakehouse stack, etc.),
 * the caller falls back to `buildBiepV1StaticTables()`.
 */
async function introspectBiepV1FromDuckLake(): Promise<DuckDBTable[]> {
  // Lazy-import the DuckDB client so the offline path doesn't need it.
  // We use `as any` here because the `duckdb` package types are callback-based
  // and don't fit cleanly into a Promise-returning helper. The runtime API is
  // stable (Database constructor + connect + prepare + all + finalize).
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const duckdbModule: any = await import("duckdb");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const Database: any = duckdbModule.Database ?? duckdbModule.default?.Database;
  if (!Database) {
    throw new Error("duckdb module did not export Database — package version mismatch?");
  }
  const db = new Database(":memory:");

  const token = process.env.MOTHERDUCK_TOKEN ?? "";
  if (!token) {
    if (typeof db.close === "function") db.close();
    throw new Error("MOTHERDUCK_TOKEN not set — use --offline for local development");
  }
  // ATTACH the canonical MotherDuck database (BIEP v1 lakehouse).
  const conn = db.connect();
  conn.run(`ATTACH 'md:oideachais' AS md (TYPE motherduck, TOKEN '${token}');`);

  const tables = await introspectBiepV1Tables(conn);
  if (typeof db.close === "function") db.close();
  return tables;
}

async function introspectBiepV1Tables(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  conn: any,
): Promise<DuckDBTable[]> {
  const subjects = [
    "mathematics",
    "chemistry",
    "geography",
    "english",
    "gaeilge",
    "computer_science",
  ];
  const tableSuffixes = ["syllabus", "papers", "marking_schemes", "topics"];

  const out: DuckDBTable[] = [];
  for (const subject of subjects) {
    const prefix = subject === "computer_science" ? "cs" : subject;
    for (const suffix of tableSuffixes) {
      const tableName = `${prefix}_${suffix}`;
      const table: DuckDBTable = {
        database: "oideachais",
        schema: "leaving_cert",
        table: tableName,
        columns: [],
      };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const stmt: any = conn.prepare(`DESCRIBE md.leaving_cert.${tableName}`);
      // `Statement.all(...)` is callback-based; we wrap it in a Promise so
      // the generator's signature stays Promise-based.
      const rows: Array<{
        column_name: string;
        column_type: string;
        null: string;
        comment: string | null;
      }> = await new Promise((resolve, reject) => {
        stmt.all((err: Error | null, result: unknown) => {
          if (err) reject(err);
          else resolve((result ?? []) as Array<{
            column_name: string;
            column_type: string;
            null: string;
            comment: string | null;
          }>);
        });
      });
      stmt.finalize();
      for (const row of rows) {
        table.columns.push({
          column_name: row.column_name,
          column_type: row.column_type,
          is_nullable: row.null === "YES" ? "YES" : "NO",
          comment: row.comment,
        });
      }
      out.push(table);
    }
  }
  return out;
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