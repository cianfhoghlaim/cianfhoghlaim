// BAML schema: LineageTrace
//
// A provenance payload composed into the output of every canonical
// Leaving Certificate extraction function (R28 of the
// `2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1` openspec
// change). Carries the full chain of where the data came from so the
// lineage viewer at `/[lang]/leaving-cert/[subject]/lineage` can render
// the per-page PDF.js source view + the marimo cell reference + the
// CocoIndex chunk ID.
//
// Additive — never modifies the existing extraction classes. All fields
// are nullable in spirit (the `?` suffix on optional ones) so existing
// callers that ignore the `lineage` field continue to work unchanged.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Core class
// ============================================================================

class LineageTrace {
  // Source document
  source_pdf string @description("Absolute path (or R2 key) to the source NCCA / SEC / gaois PDF the row was extracted from. Matches `lineage-registry.ts` LineagePDFEntry.pdf_path.")
  source_page int @description("1-indexed PDF page number where the row (or its primary content) lives.")

  // Extraction step
  extraction_function string @description("The BAML function name that produced this row (e.g. 'ExtractCurriculumSyllabus').")
  extraction_client string @description("The BAML client used (e.g. 'ExtractEn' / 'ExtractGa' / 'ExtractEnStrong' / 'LocalVision').")
  extracted_at string @description("ISO 8601 UTC timestamp of when the extraction ran.")

  // Optional confidence / cross-link metadata
  confidence float? @description("Optional 0.0-1.0 confidence score. Populated when the BAML client returns one; null otherwise.")
  chunk_id string? @description("The CocoIndex chunk ID when this row was embedded (nullable for v1).")

  // Subject + language context (so the lineage viewer can route by subject)
  subject string? @description("The BIEP v1 LC subject this row belongs to (one of mathematics / chemistry / geography / english / gaeilge / computer_science). Nullable for root-level / cross-subject extractions.")
  language string? @description("The source PDF language ('EN' or 'GA').")
}
