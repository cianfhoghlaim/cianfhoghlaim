// BAML schema: NCCA JC Short Course Extraction
//
// Used by the BIEP v2 JC pipeline to extract the 16 NCCA Junior Cycle
// short courses (Coding, Chinese, Japanese, Russian, Polish, Lithuanian,
// Portuguese, Arabic, Hebrew, Philosophy, Film Studies, Financial Literacy,
// Media Literacy, Personal Professional Development, Digital Media,
// Athletic Studies).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/

class JCShortCourse {
  // Course identifiers
  course_slug string         @description("One of the 16 JC_SHORT_COURSES")
  course_code string?        @description("NCCA short-course code, e.g. 'JC-SC-COD'")

  // Metadata
  title_en string
  title_ga string?
  language string            @description("The instruction language (en, ga, or non-EN)")

  // Curriculum content
  brief_description_en string?
  brief_description_ga string?
  learning_outcomes string[]
  estimated_hours int
  class_contact_hours int?

  // Assessment
  has_cba bool
  cba_count int
  final_assessment_type string?  @description("e.g. 'written_exam', 'portfolio', 'oral'")

  // Heuristic metadata
  source_pdf string
  source_pages int

  // Cross-cutting
  specification_code string?
  specification_year int?
}


// ============================================================================
// BAML function — the canonical short-course extractor (BIEP v2)
// ============================================================================
// Returns the canonical `JCShortCourse` Pydantic class.

function ExtractJCShortCourse(
  pdf_text: string,
  course_slug: string?,
) -> JCShortCourse {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
