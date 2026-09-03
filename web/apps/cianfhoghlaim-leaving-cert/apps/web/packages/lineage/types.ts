// packages/lineage/types.ts
//
// Shared types for the BIEP v1 lineage viewer. Used by:
//   - the per-subject `/[lang]/leaving-cert/[subject]/lineage` route loader
//     (R26) — deserializes the Hono `/api/lineage/:subject` response
//   - the `<StepPreview>` left pane (Phase 4.3) — renders the per-field state
//   - the `<LineageDag>` right pane (Phase 4.4) — renders the DAG nodes
//   - the Zustand store (Phase 4.6) — drives the click-to-highlight state
//
// Per openspec/changes/2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1
// R28 (BAML LineageTrace) + R29 (marimo + MotherDuck mapping) + R30
// (DuckLake → Zod + TanStack DB codegen — the LineageRow shape is what the
// generated collection helpers return) + R32 (CocoInsight click-to-highlight).

import type { BIEPSubjectDef, BIEPMotherDuckRef } from "../../src/lib/bi-ep";

export type LineageLanguage = "en" | "ga";

/**
 * One row in the lineage viewer's step-by-step preview. Each row maps to
 * exactly one BAML extraction step (e.g. `ExtractCurriculumSyllabus` against
 * the Mathematics syllabus PDF page 14).
 *
 * The `lineage` payload is the BAML `LineageTrace` from
 * `baml_src/.../lc_extraction/_shared/lineage_trace.baml` (R28). The
 * `marimo_cell_id` + `motherduck_ref` come from
 * `apps/web/src/lib/bi-ep.ts::BIEPMotherDuckRef` (R29).
 */
export interface LineageRow {
  /** Stable ID for the row. Format: `<subject>:<extraction_function>:<source_pdf>:<source_page>`. */
  id: string;
  /** The BAML function that produced this row. */
  extraction_function: string;
  /** The BAML client used (e.g. "ExtractEn"). */
  extraction_client: string;
  /** Human-readable label for the extraction step. */
  title: string;
  /** GA mirror label for the extraction step. */
  title_ga: string;
  /** The BAML output fields rendered by the left pane (in declared order). */
  fields: LineageField[];
  /** Provenance metadata (R28). */
  lineage: LineageTrace;
  /** Marimo notebook cell reference (R29). */
  marimo_cell_id: string;
  /** MotherDuck Dive + Flight reference (R29). */
  motherduck_ref: BIEPMotherDuckRef;
}

export interface LineageField {
  /** Stable field ID for the click-to-highlight state machine. */
  id: string;
  /** The BAML field path (e.g. `"module_topics[0].name_en"`). */
  path: string;
  /** The field value (stringified for display). */
  value: string;
  /** Display label for the field (EN). */
  label: string;
  /** Display label for the field (GA). */
  label_ga: string;
}

/** The BAML `LineageTrace` payload. Mirrors the generated Zod schema. */
export interface LineageTrace {
  source_pdf: string;
  source_page: number;
  extraction_function: string;
  extraction_client: string;
  extracted_at: string;
  confidence?: number | null;
  chunk_id?: string | null;
  subject?: string | null;
  language?: string | null;
}

/** The 5 color states a field or node can be in. */
export type LineageColorState =
  | "default"
  | "selected"
  | "upstream"
  | "downstream"
  | "dim";

/**
 * One node in the DAG. Lives in the right pane and represents the
 * intermediate stages of the extraction pipeline:
 *   pdf_page → ocr_chunk → baml_extraction → marimo_cell → web_component
 */
export interface LineageDagNode {
  id: string;
  kind: "pdf_page" | "ocr_chunk" | "baml_extraction" | "marimo_cell" | "web_component";
  label: string;
  label_ga: string;
  /** Optional click target (a row ID, field ID, or void). */
  click_target?: string | null;
}

export interface LineageDagEdge {
  /** The source node ID. */
  from: string;
  /** The target node ID. */
  to: string;
  /** The edge label (a field path or stage name). */
  label: string;
}

export interface LineageViewerProps {
  /** The resolved BIEP subject metadata (BIEPSubjectDef). */
  subject: BIEPSubjectDef;
  /** The display language (EN or GA). */
  language: LineageLanguage;
  /** The lineage rows fetched from `/api/lineage/:subject` (R30 + R31). */
  rows: LineageRow[];
  /** The bilingual label set for this language (R26 i18n). */
  labels: import("../../src/lib/lineage-routes").LineageLabels;
}
