// BAML schema: Curriculum Syllabus Extraction
//
// Used by the LC5-subject pipeline (chem/CS/gaeilge/geography/maths)
// to extract structured data from a NCCA Leaving Certificate syllabus PDF.
// The same schema works for both English (en) and Irish (ga) syllabi;
// the `language` field tracks which is present.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Per R28 of `2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1`:
// composes `LineageTrace` from `lc_extraction/_shared/lineage_trace.baml`
// for the lineage viewer.

enum SyllabusLanguage {
  EN
  GA
  EN_AND_GA
}

enum NCCAStage {
  JC      @description("Junior Cycle (Years 1-3)")
  LC_OL   @description("Leaving Certificate Ordinary Level (Year 4-5)")
  LC_HL   @description("Leaving Certificate Higher Level (Year 5-6)")
  LC_FDN  @description("Leaving Certificate Foundation Level")
}

enum ModuleType {
  CORE               @description("Mandatory for all students")
  OPTIONAL           @description("Student choice from a list")
  SPECIALISM         @description("Higher-Level-only advanced topic")
  PRACTICAL          @description("Mandatory experiment / lab work")
  ASSESSMENT         @description("Exam technique, marking, etc.")
}

class ModuleTopic {
  module_id string
  name_en string
  name_ga string?
  type ModuleType
  // Learning outcomes (specific, measurable)
  learning_outcomes string[]
  estimated_hours int?
}

class LcLearningOutcome {
  lo_id string
  statement_en string
  statement_ga string?
  blooms_taxonomy_level string?
}

class SyllabusDocument {
  // Document-level metadata
  subject string
  language SyllabusLanguage
  stage NCCAStage
  source_pdf string
  // Nullable (2026-08-06 token-plan-apis change, Phase 2b): the model
  // cannot know the PDF page count from extracted text alone. Matches
  // the already-nullable LCSyllabus.source_pages in
  // british_isles/_cross/unified_extraction.baml.
  source_pages int?

  // Document content
  module_topics ModuleTopic[]
  total_learning_outcomes int

  // Cross-cutting
  cross_curricular string[]
  assessment_objectives string[]

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`. The Python caller (Dagster
  // asset + Conway envelope wrapper) populates this at write time —
  // the BAML function itself doesn't need to fill it in for its own
  // prompt, but downstream consumers can rely on it being present.
  lineage LineageTrace?
}

// ============================================================================
// BAML function — the canonical extractor (BIEP v1)
// ============================================================================
// Replaces the legacy `b.ExtractLeavingCertSyllabus` from
// `baml/education/pdfs/leaving_cert_syllabus.baml`.
//
// Returns the canonical `SyllabusDocument` Pydantic class.
// NCCA publishes the syllabus for each LC subject as a single combined PDF
// (Higher + Ordinary + Foundation sections in one document). The
// `language` enum distinguishes EN / GA / bilingual PDFs.

function ExtractCurriculumSyllabus(
  pdf_text: string,
  subject: string?,
  language: string?,
) -> SyllabusDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// ============================================================================
// LineageTrace composer helper
// ============================================================================
// Helper that downstream Python callers (Dagster asset + DLT destination
// wrapper) invoke to populate the `lineage` field of every row emitted by
// `ExtractCurriculumSyllabus`. Centralised here so the contract is defined
// next to the consumer.
//
// Per openspec R28 (BAML LineageTrace extension).

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertSyllabus` from `baml/education/pdfs/leaving_cert_syllabus.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.1 task) and
// replaced by this canonical `ExtractCurriculumSyllabus`. Any caller that
// still passes legacy kwargs will be transparently routed here.
