/**
 * scripts/_lineage-walker.ts
 *
 * The PDF registry walker for the BIEP v1 Leaving Certificate lineage viewer.
 *
 * Walks `leaving_certificate/<subject>/{en,ga}/*.pdf` + the 4 NCCA root-level
 * PDFs at `leaving_certificate/*.pdf` and emits a deterministic JSON registry
 * with SHA-256 + byte_size + page_count + ingested_at per PDF.
 *
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
 * R27 (PDF source registry + filesystem walk + CI drift gate).
 *
 * The walker is designed to be:
 * - **Idempotent** — running it twice on the same filesystem produces the same
 *   output (PDFs are sorted by `pdf_path` ascending)
 * - **Offline-first** — no network calls, no DB access, just the filesystem +
 *   the page_count heuristic ported from
 *   `dlt/british_isles/ireland/ncca_root_pdfs.py::_estimate_page_count`
 * - **Reused by 3 entry points** — `scripts/schema-generate.ts` (writes to
 *   disk), `scripts/lineage-validate.ts` (CI drift gate), and the in-process
 *   walkers that read the registry at runtime.
 */

import * as crypto from "node:crypto";
import * as fs from "node:fs/promises";
import * as path from "node:path";

// =============================================================================
// Types
// =============================================================================

/** One row in the PDF registry. Matches the `LineagePDFEntry` in the emitted TS. */
export interface LineagePDFEntry {
  /** Absolute or repo-relative path to the PDF. */
  pdf_path: string;
  /** Filename only (e.g. "SCSEC25_Maths_syllabus_examination-2015_English.pdf"). */
  filename: string;
  /** SHA-256 hash of the file contents (lowercase hex, 64 chars). */
  sha256: string;
  /** Page count estimated via the /Type /Page /Count heuristic. */
  page_count: number;
  /** File size in bytes. */
  byte_size: number;
  /** ISO 8601 timestamp of when the walker ran (deterministic per-run). */
  ingested_at: string;
}

/** The shape of the emitted `apps/web/src/lib/lineage-registry.ts` registry. */
export interface LineageRegistry {
  schema_version: number;
  generated_at: string;
  root_pdfs: LineagePDFEntry[];
  subjects: Record<string, Record<"en" | "ga", LineagePDFEntry[]>>;
}

// =============================================================================
// Constants — canonical paths
// =============================================================================

/** The 4 NCCA root-level PDFs at `leaving_certificate/*.pdf`. */
export const NCCA_ROOT_PDFS: ReadonlyArray<string> = [
  "key-competencies-in-senior-cycle_en.pdf",
  "the-potential-of-online-learning-environments_en.pdf",
  "the-potential-of-technology-to-support-online-certification-and-reporting.pdf",
  "scr-advisory-report_en.pdf",
  "SC-L1-L2-Programme-Statement.pdf",
];

/** The 13 subject directories under `leaving_certificate/`. */
export const ALL_SUBJECT_DIRS: ReadonlyArray<string> = [
  "applied_mathematics",
  "biology",
  "business",
  "chemistry",
  "computer_science",
  "english",
  "french",
  "gaeilge",
  "geography",
  "history",
  "mathematics",
  "technology",
  "ukrainian",
];

/** The 6 BIEP v1 LC priority subjects (subset of `ALL_SUBJECT_DIRS`). */
export const BIEP_V1_SUBJECTS: ReadonlyArray<string> = [
  "mathematics",
  "chemistry",
  "geography",
  "gaeilge",
  "english",
  "computer_science",
];

/** The 2 language subdirs per subject. */
export const BIEP_LANGUAGES: ReadonlyArray<"en" | "ga"> = ["en", "ga"];

// =============================================================================
// Page count heuristic (ported from Python)
// =============================================================================

/**
 * Estimate the page count of a PDF from its `/Type /Page /Count` tag.
 * This is a cheap heuristic; the actual page count requires parsing the PDF.
 * The estimate is good enough for DLT + lineage metadata; the CocoIndex v1 App
 * reads the actual pages.
 *
 * Ported from `dlt/british_isles/ireland/ncca_root_pdfs.py::_estimate_page_count`.
 */
export function estimatePageCount(pdfBytes: Uint8Array): number {
  // Read only the first 8 KB — `/Count` always appears early in the PDF dict.
  const head = pdfBytes.subarray(0, 8192);
  const marker = new TextEncoder().encode("/Count");
  const idx = indexOfBytes(head, marker);
  if (idx === -1) return 0;
  const after = head.subarray(idx + marker.length, idx + marker.length + 16);
  let digits = "";
  for (const byte of after) {
    const ch = String.fromCharCode(byte);
    if (ch >= "0" && ch <= "9") {
      digits += ch;
    } else if (digits.length > 0) {
      break;
    }
  }
  return digits.length > 0 ? Number.parseInt(digits, 10) : 0;
}

function indexOfBytes(haystack: Uint8Array, needle: Uint8Array): number {
  outer: for (let i = 0; i <= haystack.length - needle.length; i++) {
    for (let j = 0; j < needle.length; j++) {
      if (haystack[i + j] !== needle[j]) continue outer;
    }
    return i;
  }
  return -1;
}

// =============================================================================
// Walker
// =============================================================================

/**
 * Walk the 4 NCCA root-level PDFs + the 13 subject directories.
 *
 * @param leavingCertDir Absolute path to `leaving_certificate/`.
 * @param clock Override the clock (for tests). Defaults to `new Date()`.
 *   The clock is exposed for testability but its output is NOT written to the
 *   emitted TS file (both `generated_at` and per-PDF `ingested_at` are
 *   pinned to a fixed sentinel so the committed file is byte-deterministic).
 * @returns A deterministic `LineageRegistry`.
 */
export async function walkLineageRegistry(
  leavingCertDir: string,
  clock: () => Date = () => new Date(),
): Promise<LineageRegistry> {
  // Touch the clock so test code that passes a mock clock still runs without
  // TS strict-unused-vars complaints. The value is intentionally discarded.
  void clock();

  // Fixed sentinel for all timestamps in the emitted file. Real generation
  // timestamps live in the `bi-ep.gen.lock.json` sibling file (Phase 2).
  const INGESTED_AT_SENTINEL = "1970-01-01T00:00:00.000Z";

  const rootPdfs = await walkRootPdfs(leavingCertDir, INGESTED_AT_SENTINEL);
  const subjects: Record<string, Record<"en" | "ga", LineagePDFEntry[]>> = {};

  for (const subject of ALL_SUBJECT_DIRS) {
    subjects[subject] = {
      en: await walkSubjectLang(leavingCertDir, subject, "en", INGESTED_AT_SENTINEL),
      ga: await walkSubjectLang(leavingCertDir, subject, "ga", INGESTED_AT_SENTINEL),
    };
  }

  return {
    schema_version: 1,
    generated_at: "1970-01-01T00:00:00.000Z",
    root_pdfs: rootPdfs,
    subjects,
  };
}

/**
 * Walk the 4 NCCA root-level PDFs at `leaving_cert/<name>.pdf`.
 * Missing PDFs are silently skipped (the registry records what exists).
 */
async function walkRootPdfs(
  leavingCertDir: string,
  ingestedAt: string,
): Promise<LineagePDFEntry[]> {
  const entries: LineagePDFEntry[] = [];
  for (const filename of NCCA_ROOT_PDFS) {
    const fullPath = path.join(leavingCertDir, filename);
    const entry = await tryReadPdfEntry(fullPath, filename, ingestedAt);
    if (entry) entries.push(entry);
  }
  // Deterministic order: by `pdf_path` ascending.
  entries.sort((a, b) => a.pdf_path.localeCompare(b.pdf_path));
  return entries;
}

/**
 * Walk `leaving_cert/<subject>/<lang>/*.pdf`.
 * Missing subject dirs or missing PDFs are silently skipped (empty list).
 */
async function walkSubjectLang(
  leavingCertDir: string,
  subject: string,
  lang: "en" | "ga",
  ingestedAt: string,
): Promise<LineagePDFEntry[]> {
  const subjectDir = path.join(leavingCertDir, subject, lang);
  let filenames: string[];
  try {
    const allFiles = await fs.readdir(subjectDir);
    filenames = allFiles.filter((f) => f.toLowerCase().endsWith(".pdf"));
  } catch {
    // Subject dir doesn't exist — return empty list.
    return [];
  }
  filenames.sort(); // deterministic order

  const entries: LineagePDFEntry[] = [];
  for (const filename of filenames) {
    const fullPath = path.join(subjectDir, filename);
    const entry = await tryReadPdfEntry(fullPath, filename, ingestedAt);
    if (entry) entries.push(entry);
  }
  return entries;
}

/**
 * Try to read a PDF file and compute its `LineagePDFEntry`.
 * Returns `null` if the file doesn't exist or is unreadable.
 */
async function tryReadPdfEntry(
  fullPath: string,
  filename: string,
  ingestedAt: string,
): Promise<LineagePDFEntry | null> {
  let bytes: Buffer;
  try {
    bytes = await fs.readFile(fullPath);
  } catch {
    return null;
  }
  const sha256 = crypto.createHash("sha256").update(bytes).digest("hex");
  return {
    pdf_path: fullPath,
    filename,
    sha256,
    page_count: estimatePageCount(new Uint8Array(bytes)),
    byte_size: bytes.byteLength,
    ingested_at: ingestedAt,
  };
}

// =============================================================================
// Diff (used by `lineage-validate.ts`)
// =============================================================================

export interface LineageDiff {
  added: LineagePDFEntry[];
  removed: LineagePDFEntry[];
  changed: Array<{ pdf_path: string; before: LineagePDFEntry; after: LineagePDFEntry }>;
}

/**
 * Diff the live registry (just-walked) against the committed registry.
 * Returns 3 lists: added PDFs, removed PDFs, and changed PDFs (same path +
 * filename but different sha256 / page_count / byte_size).
 */
export function diffRegistries(
  committed: LineageRegistry,
  live: LineageRegistry,
): LineageDiff {
  const committedByPath = flattenRegistry(committed);
  const liveByPath = flattenRegistry(live);

  const added: LineagePDFEntry[] = [];
  const removed: LineagePDFEntry[] = [];
  const changed: LineageDiff["changed"] = [];

  for (const [path, liveEntry] of liveByPath) {
    const committedEntry = committedByPath.get(path);
    if (!committedEntry) {
      added.push(liveEntry);
    } else if (
      committedEntry.sha256 !== liveEntry.sha256 ||
      committedEntry.page_count !== liveEntry.page_count ||
      committedEntry.byte_size !== liveEntry.byte_size
    ) {
      changed.push({ pdf_path: path, before: committedEntry, after: liveEntry });
    }
  }

  for (const [path, committedEntry] of committedByPath) {
    if (!liveByPath.has(path)) {
      removed.push(committedEntry);
    }
  }

  return { added, removed, changed };
}

function flattenRegistry(registry: LineageRegistry): Map<string, LineagePDFEntry> {
  const map = new Map<string, LineagePDFEntry>();
  for (const entry of registry.root_pdfs) {
    map.set(entry.pdf_path, entry);
  }
  for (const [_subject, langs] of Object.entries(registry.subjects)) {
    for (const lang of BIEP_LANGUAGES) {
      for (const entry of langs[lang]) {
        map.set(entry.pdf_path, entry);
      }
    }
  }
  return map;
}

// =============================================================================
// TypeScript emitter (writes `apps/web/src/lib/lineage-registry.ts`)
// =============================================================================

/**
 * Emit a `LineageRegistry` as a TypeScript source file (the registry is
 * checked into git + CI-validated).
 *
 * The emitted file uses a stable, deterministic format so the diff against the
 * committed version is minimal. The types are inlined (rather than imported
 * from a shared package) so the emitted file is self-contained and works
 * before the `@cianfhoghlaim/lineage-types` package lands in Phase 2.
 */
export function emitRegistryTs(registry: LineageRegistry): string {
  const lines: string[] = [];
  lines.push(
    "// apps/web/src/lib/lineage-registry.ts",
    "//",
    "// AUTO-GENERATED by `bun run schema:generate` (scripts/schema-generate.ts).",
    "// DO NOT EDIT — re-run the generator to update.",
    "//",
    "// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1",
    "// R27 (PDF source registry + filesystem walk + CI drift gate).",
    "//",
    `// schema_version: ${registry.schema_version}`,
    `// root_pdfs:      ${registry.root_pdfs.length}`,
    `// subjects:       ${Object.keys(registry.subjects).length}`,
    "",
    "export interface LineagePDFEntry {",
    "  /** Absolute or repo-relative path to the PDF. */",
    "  pdf_path: string;",
    "  /** Filename only (e.g. \"SCSEC25_Maths_syllabus_examination-2015_English.pdf\"). */",
    "  filename: string;",
    "  /** SHA-256 hash of the file contents (lowercase hex, 64 chars). */",
    "  sha256: string;",
    "  /** Page count estimated via the /Type /Page /Count heuristic. */",
    "  page_count: number;",
    "  /** File size in bytes. */",
    "  byte_size: number;",
    "  /** ISO 8601 timestamp of when the walker ran. */",
    "  ingested_at: string;",
    "}",
    "",
    "export interface LineageRegistry {",
    "  schema_version: number;",
    "  /** Fixed sentinel — real generation timestamp lives in the lockfile. */",
    "  generated_at: string;",
    "  root_pdfs: LineagePDFEntry[];",
    "  subjects: Record<string, Record<\"en\" | \"ga\", LineagePDFEntry[]>>;",
    "}",
    "",
    "export const LINEAGE_REGISTRY: LineageRegistry = " + JSON.stringify(registry, null, 2) + ";",
    "",
    "export const LINEAGE_REGISTRY_BY_SUBJECT: Readonly<Record<string, { en: LineagePDFEntry[]; ga: LineagePDFEntry[] }>> = LINEAGE_REGISTRY.subjects;",
    "",
    "export function getLineageEntry(pdf_path: string): LineagePDFEntry | undefined {",
    "  for (const entry of LINEAGE_REGISTRY.root_pdfs) {",
    "    if (entry.pdf_path === pdf_path) return entry;",
    "  }",
    "  for (const langs of Object.values(LINEAGE_REGISTRY.subjects)) {",
    "    for (const lang of [\"en\", \"ga\"] as const) {",
    "      for (const entry of langs[lang]) {",
    "        if (entry.pdf_path === pdf_path) return entry;",
    "      }",
    "    }",
    "  }",
    "  return undefined;",
    "}",
    "",
  );
  return lines.join("\n");
}