// BAML schema: Junior Cycle Curriculum Syllabus Extraction
//
// Used by the BIEP v2 JC pipeline to extract structured curriculum data
// from NCCA Junior Cycle subject specification PDFs (jc_<subject>_<lang>.pdf).
// The same schema works for both English (en) and Irish (ga) specs;
// the `language` field tracks which is present.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Reference: openspec/changes/2026-07-20-biep-v2-junior-cycle-extraction-v1/

enum JuniorCycleLanguage {
  EN
  GA
  EN_AND_GA
}

enum JuniorCycleSubjectSlug {
  ENGLISH
  GAEILGE
  MATHEMATICS
  IRISH_HISTORY
  GEOGRAPHY
  SCIENCE
  BUSINESS_STUDIES
  FRENCH
  GERMAN
  SPANISH
  ITALIAN
  HOME_ECONOMICS
  MUSIC
  ART
  TECHNOLOGY
  ENGINEERING
  GRAPHICS
  WOOD_TECHNOLOGY
}

enum YearBand {
  YEAR_1  @description("Junior Cycle Year 1")
  YEAR_2  @description("Junior Cycle Year 2")
  YEAR_3  @description("Junior Cycle Year 3")
  TY      @description("Transition Year (optional)")
}

enum JCStrand {
  ORAL_LANGUAGE
  READING
  WRITING
  NUMBER
  ALGEBRA
  SHAPE_SPACE
  MEASURE
  DATA
  CONTINUITY_CHANGE
  NATURE_SCIENCE
  PHYSICAL_WORLD
  BIOLOGICAL_WORLD
  CHEMICAL_WORLD
  EARTH_SPACE
  PEOPLE_LIVING
  PAST
  STORY
  CREATIVE_ARTS
  EXPRESSIVE_ARTS
  CRAFT_DESIGN
  ACTIVE_LEARNING
  DIGITAL_LEARNING
  CROSS_CURRICULAR
  OTHER  @description("Catch-all for strands not explicitly enumerated")
}

class JuniorCycleLearningOutcome {
  lo_id string
  year YearBand
  strand JCStrand
  statement_en string
  statement_ga string?
  blooms_taxonomy_level string?
}

class JuniorCycleStrandDescriptor {
  strand JCStrand
  year YearBand
  title_en string
  title_ga string?
  learning_outcomes JCLearningOutcome[]
  estimated_hours int?
}

class JuniorCycleCurriculumSpec {
  // Document-level metadata
  subject JuniorCycleSubjectSlug
  language JuniorCycleLanguage
  source_pdf string
  source_pages int

  // Per-year strand breakdown
  strands JCStrandDescriptor[]

  // Cross-cutting
  total_learning_outcomes int
  cba_count int
  has_optional_ty bool

  // BJCP / NCCA identifiers
  specification_code string?
  specification_year int?

  // Document classification (for downstream routing)
  doc_confidence float?
}

// ============================================================================
// BAML function — the canonical JC curriculum extractor (BIEP v2)
// ============================================================================
// Replaces the legacy `b.ExtractJCCurriculum` from
// `baml/education/stages/junior_cycle.baml` (which was stage-level only).
//
// Returns the canonical `JCCurriculumSpec` Pydantic class with per-year
// `JCStrandDescriptor[]` and per-outcome `JCLearningOutcome[]`.

function ExtractJuniorCycleCurriculum(
  pdf_text: string,
  subject: string?,
  language: string?,
  year: int?,
) -> JuniorCycleCurriculumSpec {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
