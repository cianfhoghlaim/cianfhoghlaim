/**
 * @cianfhoghlaim/contracts — shared TS types + Zod schemas.
 *
 * Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1** openspec
 * change. The 5 web apps + the hono-api gateway import their shared
 * types from this package instead of duplicating them in each app.
 */

import { z } from "zod";

// ─── Per-subject schema (BIEP axis) ────────────────────────────────────────

export const BIEP_SUBJECTS: readonly string[] = [
  "mathematics", "chemistry", "physics", "biology",
  "english", "gaeilge", "history", "geography",
  "computer_science", "french", "german", "spanish",
  "music", "art", "religious_education",
] as const;

export const SubjectSchema = z.enum(BIEP_SUBJECTS as [string, ...string[]]);

// ─── Per-jurisdiction schema ──────────────────────────────────────────────

export const BRITISH_ISLES_JURISDICTIONS = [
  "england", "northern_ireland", "scotland", "wales",
  "isle_of_man", "jersey", "guernsey",
] as const;

export const COMMONWEALTH_JURISDICTIONS = [
  "australia", "canada", "india", "new_zealand",
  "nigeria", "south_africa",
] as const;

export const EUROPEAN_NATIONS_JURISDICTIONS = [
  "ireland", "france", "germany", "spain", "italy",
  "poland", "ukraine", "netherlands", "sweden",
] as const;

export const JurisdictionSchema = z.enum([
  ...BRITISH_ISLES_JURISDICTIONS,
  ...COMMONWEALTH_JURISDICTIONS,
  ...EUROPEAN_NATIONS_JURISDICTIONS,
] as [string, ...string[]]);

// ─── Tertiary (university) schema ─────────────────────────────────────────

export const TERTIARY_INSTITUTIONS = [
  "uog",          // University of Galway (1st tertiary example, per Wave 2)
  "nui_federation",  // NUI federation (UCD + UCC + NUIM)
  "british_isles_tertiary",
] as const;

export const TertiaryInstitutionSchema = z.enum([...TERTIARY_INSTITUTIONS] as [string, ...string[]]);

// ─── Pipeline event payload (the AG-UI SSE payload shape) ─────────────────

export const PipelineEventSchema = z.object({
  event_type: z.enum([
    "RUN_STARTED",
    "RUN_FINISHED",
    "STEP_STARTED",
    "STEP_FINISHED",
    "TEXT_MESSAGE_START",
    "TEXT_MESSAGE_CONTENT",
    "TEXT_MESSAGE_END",
    "TOOL_CALL_START",
    "TOOL_CALL_ARGS",
    "TOOL_CALL_END",
    "TOOL_CALL_RESULT",
    "STATE_DELTA",
    "MESSAGES_SNAPSHOT",
  ]),
  run_id: z.string(),
  thread_id: z.string(),
  timestamp: z.string().datetime(),
  payload: z.record(z.string(), z.unknown()).optional(),
});

export type PipelineEvent = z.infer<typeof PipelineEventSchema>;

// ─── CocoIndex + dlt integration schemas ─────────────────────────────────

export const SourceKindSchema = z.enum([
  "syllabus", "exam_papers", "personal_archive", "official_docs",
  "comics", "crypto", "pdf", "media",
]);

export const DestinationSchema = z.enum([
  "ducklake_cianfhoghlaim", "ducklake_oideachais",
  "ducklake_educational", "ducklake_crypteolas",
  "ducklake_tertiary", "ducklake_uog", "ducklake_cie",
  "motherduck", "motherduck_ducklake",
  "filesystem_local", "filesystem_s3", "filesystem_gcs", "filesystem_azure",
  "iceberg_rest", "iceberg_lakekeeper",
]);

export type SourceKind = z.infer<typeof SourceKindSchema>;
export type DestinationName = z.infer<typeof DestinationSchema>;

// ─── Generated schemas (DuckLake/DuckDB introspection) ────────────────────
//
// Per the 2026-08-26 schema-contract remediation: `scripts/schema-generate.ts`
// introspects the live DuckLake/DuckDB schema (or the static BIEP v1 schema
// in --offline mode) and writes here. This is the canonical location —
// import table schemas from here, not from a per-app generated file.
// Regenerate with `bun run schema:generate`; CI drift-checks with
// `bun run schema:validate` (wired into mise run core:ci).

export * from "./generated/bi-ep.gen";
