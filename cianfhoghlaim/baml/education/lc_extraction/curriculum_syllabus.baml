// BAML schema: Curriculum Syllabus Extraction
//
// Used by the LC5-subject pipeline (chem/CS/gaeilge/geography/maths)
// to extract structured data from a NCCA Leaving Certificate syllabus PDF.
// The same schema works for both English (en) and Irish (ga) syllabi;
// the `language` field tracks which is present.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

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
  module_id: string
  name_en: string
  name_ga: string?
  type: ModuleType
  // Learning outcomes (specific, measurable)
  learning_outcomes: string[]
  estimated_hours: int?
}

class LearningOutcome {
  lo_id: string
  statement_en: string
  statement_ga: string?
  blooms_taxonomy_level: string?
}

class SyllabusDocument {
  // Document-level metadata
  subject: string
  language: SyllabusLanguage
  stage: NCCAStage
  source_pdf: string
  source_pages: int

  // Document content
  module_topics: ModuleTopic[]
  total_learning_outcomes: int

  // Cross-cutting
  cross_curricular: string[]
  assessment_objectives: string[]
}
