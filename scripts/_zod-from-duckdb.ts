/**
 * scripts/_zod-from-duckdb.ts
 *
 * DuckDB column-type → Zod schema mapper.
 *
 * The canonical mapping table for the BIEP v1 line of work. Used by:
 * - `scripts/schema-generate.ts` — emits `apps/web/src/lib/bi-ep.gen.ts`
 * - `scripts/schema-validate.ts` — CI drift gate (regenerate in-memory, diff
 *   against the committed file)
 *
 * Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
 * R30 (DuckLake → Zod + TanStack DB collection codegen).
 *
 * The mapping is intentionally conservative: every DuckDB type maps to a Zod
 * schema that **accepts the DuckDB value**. Unknown types fall back to
 * `z.unknown()` (never throws), so the generator never breaks CI on a new
 * DuckDB type — the dev just gets a `z.unknown()` field and a warning in the
 * generator output.
 */

// =============================================================================
// Types
// =============================================================================

export interface DuckDBColumn {
  /** Column name (e.g. "topic_id"). */
  column_name: string;
  /** DuckDB logical type as a string (e.g. "VARCHAR", "INTEGER", "JSON"). */
  column_type: string;
  /** "YES" or "NO". */
  is_nullable: "YES" | "NO";
  /** Optional column comment from DuckDB. */
  comment?: string | null;
}

export interface DuckDBTable {
  database: string;
  schema: string;
  table: string;
  columns: DuckDBColumn[];
}

/** A generated Zod field — the TypeScript source that goes into bi-ep.gen.ts. */
export interface ZodFieldEmit {
  field_name: string;
  zod_source: string;
  /** True if the column is nullable (we emit `.nullable().optional()`). */
  is_nullable: boolean;
  /** True if this column's type fell back to `z.unknown()`. */
  is_unknown: boolean;
}

// =============================================================================
// DuckDB type → Zod schema source
// =============================================================================

/**
 * The canonical DuckDB type → Zod schema mapping table.
 *
 * Each entry is `(duckdbTypePattern, zodSchemaSource, isUnknown)`.
 * The walker matches patterns case-insensitively, in order.
 */
const DUCKDB_TO_ZOD: ReadonlyArray<{
  pattern: RegExp;
  zod_source: string;
  is_unknown: false;
}> = [
  // JSON / struct / list
  { pattern: /^JSON$/i, zod_source: "z.record(z.unknown())", is_unknown: false },
  { pattern: /^LIST<.*>$/i, zod_source: "z.array(z.unknown())", is_unknown: false },
  { pattern: /^STRUCT<.*>$/i, zod_source: "z.record(z.unknown())", is_unknown: false },
  { pattern: /^MAP<.*>$/i, zod_source: "z.record(z.unknown())", is_unknown: false },
  // Booleans
  { pattern: /^BOOLEAN$/i, zod_source: "z.boolean()", is_unknown: false },
  // Integers
  { pattern: /^TINYINT$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^SMALLINT$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^INTEGER$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^BIGINT$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^HUGEINT$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^UTINYINT$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^USMALLINT$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^UINTEGER$/i, zod_source: "z.number().int()", is_unknown: false },
  { pattern: /^UBIGINT$/i, zod_source: "z.number().int()", is_unknown: false },
  // Floating point
  { pattern: /^REAL$/i, zod_source: "z.number()", is_unknown: false },
  { pattern: /^FLOAT$/i, zod_source: "z.number()", is_unknown: false },
  { pattern: /^DOUBLE$/i, zod_source: "z.number()", is_unknown: false },
  { pattern: /^DECIMAL\(.*\)$/i, zod_source: "z.number()", is_unknown: false },
  // Dates + timestamps
  { pattern: /^DATE$/i, zod_source: "z.string().regex(/^\\d{4}-\\d{2}-\\d{2}$/)", is_unknown: false },
  { pattern: /^TIME$/i, zod_source: "z.string()", is_unknown: false },
  { pattern: /^TIMESTAMP$/i, zod_source: "z.string().datetime()", is_unknown: false },
  { pattern: /^TIMESTAMP WITH TIME ZONE$/i, zod_source: "z.string().datetime()", is_unknown: false },
  { pattern: /^TIMESTAMPTZ$/i, zod_source: "z.string().datetime()", is_unknown: false },
  // Strings + binary
  { pattern: /^VARCHAR$/i, zod_source: "z.string()", is_unknown: false },
  { pattern: /^TEXT$/i, zod_source: "z.string()", is_unknown: false },
  { pattern: /^CHAR.*$/i, zod_source: "z.string()", is_unknown: false },
  { pattern: /^BLOB$/i, zod_source: "z.string()", is_unknown: false }, // base64-encoded
  { pattern: /^UUID$/i, zod_source: "z.string().uuid()", is_unknown: false },
  // Geometry (PostGIS-style, fallback to string)
  { pattern: /^GEOMETRY$/i, zod_source: "z.string()", is_unknown: false },
];

/**
 * Convert one DuckDB column type to a Zod schema source.
 * Returns `z.unknown()` for unknown types (with `is_unknown = true` so the
 * generator can warn).
 */
export function duckdbColumnTypeToZod(
  columnType: string,
): { zod_source: string; is_unknown: boolean } {
  for (const { pattern, zod_source, is_unknown } of DUCKDB_TO_ZOD) {
    if (pattern.test(columnType)) {
      return { zod_source, is_unknown };
    }
  }
  return { zod_source: "z.unknown()", is_unknown: true };
}

// =============================================================================
// Per-column emitter
// =============================================================================

/**
 * Emit a Zod field for one DuckDB column. The output is a single line of
 * TypeScript source code that fits inside a `z.object({ ... })`.
 *
 * Example outputs:
 *   topic_id: z.string(),
 *   weight: z.number(),
 *   confidence: z.number().nullable().optional(),
 *   lineage: z.record(z.unknown()).nullable().optional(),
 */
export function emitZodField(column: DuckDBColumn): ZodFieldEmit {
  const { zod_source, is_unknown } = duckdbColumnTypeToZod(column.column_type);
  const isNullable = column.is_nullable === "YES";
  // Nullable columns get `.nullable().optional()` so Zod accepts `null`,
  // `undefined`, or a value of the underlying type.
  const wrapped = isNullable ? `${zod_source}.nullable().optional()` : zod_source;
  return {
    field_name: column.column_name,
    zod_source: `${column.column_name}: ${wrapped},`,
    is_nullable: isNullable,
    is_unknown,
  };
}

// =============================================================================
// Per-table emitter
// =============================================================================

/**
 * Emit a full Zod object schema for one DuckDB table.
 * Returns the TypeScript source code (no leading indentation).
 */
export function emitTableZodSchema(
  table: DuckDBTable,
  identifier: string,
): { source: string; unknown_columns: string[] } {
  const fields: ZodFieldEmit[] = table.columns.map(emitZodField);
  const unknownColumns = fields.filter((f) => f.is_unknown).map((f) => f.field_name);
  const body = fields.map((f) => `    ${f.zod_source}`).join("\n");
  const source = `export const ${identifier}Schema = z.object({\n${body}\n});\n\nexport type ${identifier} = z.infer<typeof ${identifier}Schema>;\n`;
  return { source, unknown_columns: unknownColumns };
}

// =============================================================================
// BIEP v1 static schema (offline fallback)
// =============================================================================

/**
 * The canonical BIEP v1 schema — used when DuckLake/MotherDuck is not
 * available (CI, local dev, offline development).
 *
 * Mirrors the 6 subjects × 4 tables = 24 tables declared in
 * `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.ts::BASE_BIEP_TABLES`.
 *
 * The columns are inferred from the per-subject BAML schemas
 * (`baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`,
 * `exam_paper_layout.baml`, `marking_scheme.baml`) plus the per-subject
 * CocoIndex embedding metadata (`lance_chunk_id`, `embedded_at`).
 */
export function buildBiepV1StaticTables(): DuckDBTable[] {
  // The 6 BIEP v1 priority subjects — keep in lock-step with
  // `_lineage-walker.ts::BIEP_V1_SUBJECTS`.
  const subjects: ReadonlyArray<string> = [
    "mathematics",
    "chemistry",
    "geography",
    "english",
    "gaeilge",
    "computer_science",
  ];
  const out: DuckDBTable[] = [];

  for (const subject of subjects) {
    const subjectLabel = subject === "computer_science" ? "cs" : subject;
    const prefix = subjectLabel;

    // ---- syllabus ----
    out.push({
      database: "oideachais",
      schema: "leaving_cert",
      table: `${prefix}_syllabus`,
      columns: [
        { column_name: "subject", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "language", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "stage", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "module_id", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "name_en", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "name_ga", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "module_type", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "estimated_hours", column_type: "INTEGER", is_nullable: "YES" },
        { column_name: "learning_outcomes", column_type: "JSON", is_nullable: "YES" },
        { column_name: "cross_curricular", column_type: "JSON", is_nullable: "YES" },
        { column_name: "assessment_objectives", column_type: "JSON", is_nullable: "YES" },
        { column_name: "source_pdf", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "source_pages", column_type: "INTEGER", is_nullable: "NO" },
        { column_name: "extracted_at", column_type: "TIMESTAMP", is_nullable: "YES" },
      ],
    });

    // ---- papers (past exam papers) ----
    out.push({
      database: "oideachais",
      schema: "leaving_cert",
      table: `${prefix}_papers`,
      columns: [
        { column_name: "subject", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "language", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "paper_year", column_type: "INTEGER", is_nullable: "NO" },
        { column_name: "paper_level", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "paper_code", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "title_en", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "title_ga", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "question_count", column_type: "INTEGER", is_nullable: "YES" },
        { column_name: "total_marks", column_type: "INTEGER", is_nullable: "YES" },
        { column_name: "layout_metadata", column_type: "JSON", is_nullable: "YES" },
        { column_name: "source_pdf", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "source_pages", column_type: "INTEGER", is_nullable: "NO" },
        { column_name: "extracted_at", column_type: "TIMESTAMP", is_nullable: "YES" },
      ],
    });

    // ---- marking_schemes ----
    out.push({
      database: "oideachais",
      schema: "leaving_cert",
      table: `${prefix}_marking_schemes`,
      columns: [
        { column_name: "subject", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "language", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "paper_year", column_type: "INTEGER", is_nullable: "NO" },
        { column_name: "paper_level", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "paper_code", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "pclm_guidance", column_type: "JSON", is_nullable: "YES" },
        { column_name: "marks_per_question", column_type: "JSON", is_nullable: "YES" },
        { column_name: "common_errors", column_type: "JSON", is_nullable: "YES" },
        { column_name: "source_pdf", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "source_pages", column_type: "INTEGER", is_nullable: "NO" },
        { column_name: "extracted_at", column_type: "TIMESTAMP", is_nullable: "YES" },
      ],
    });

    // ---- topics (the per-topic NCCA learning outcomes + per-topic
      // frequency / Bloom's taxonomy / marks allocation) ----
    out.push({
      database: "oideachais",
      schema: "leaving_cert",
      table: `${prefix}_topics`,
      columns: [
        { column_name: "topic_id", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "subject", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "name_en", column_type: "VARCHAR", is_nullable: "NO" },
        { column_name: "name_ga", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "blooms_level", column_type: "VARCHAR", is_nullable: "YES" },
        { column_name: "weight", column_type: "DOUBLE", is_nullable: "YES" },
        { column_name: "estimated_hours", column_type: "INTEGER", is_nullable: "YES" },
        { column_name: "learning_outcomes", column_type: "JSON", is_nullable: "YES" },
        { column_name: "lineage", column_type: "JSON", is_nullable: "YES" },
        { column_name: "extraction_confidence", column_type: "DOUBLE", is_nullable: "YES" },
        { column_name: "extracted_at", column_type: "TIMESTAMP", is_nullable: "YES" },
      ],
    });
  }

  return out;
}

// =============================================================================
// Per-table identifier helpers
// =============================================================================

/**
 * Convert a snake_case table name into a PascalCase identifier.
 * `mathematics_topics` → `MathematicsTopics`
 * `cs_topics` → `CsTopics`
 */
export function tableNameToIdentifier(tableName: string): string {
  return tableName
    .split("_")
    .map((part) => {
      if (part.length === 0) return "";
      // Special-case the 2-letter subject prefix "cs" to "Cs"
      if (part === "cs") return "Cs";
      return part.charAt(0).toUpperCase() + part.slice(1);
    })
    .join("");
}