// BAML schema: Scotland subject taxonomy (SQA awarding body)
//
// Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change.
//
// Parallel to the AQA + OCR + Edexcel enums from Phase 3.
// Scotland has 3 qualification levels per subject:
//   - National 5 (Standard Grade successor)
//   - Higher
//   - Advanced Higher
//
// Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/

enum SCQFLevel {
  NATIONAL_5    @description("Scottish National 5 (SCQF Level 5)")
  HIGHER        @description("Scottish Higher (SCQF Level 6)")
  ADVANCED_HIGHER @description("Scottish Advanced Higher (SCQF Level 7)")
}

enum SCQFSubject {
  // Core STEM
  MATHEMATICS
  APPLICATIONS_OF_MATHEMATICS
  PURE_MATHEMATICS
  STATISTICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  HUMAN_BIOLOGY
  COMPUTING_SCIENCE
  // English + Lit
  ENGLISH
  ENGLISH_FOR_WORK_AND_LEISURE
  // Humanities
  HISTORY
  GEOGRAPHY
  MODERN_STUDIES
  POLITICS
  PHILOSOPHY
  RELIGIOUS_MORAL_EDUCATION
  // Languages
  FRENCH
  GERMAN
  SPANISH
  ITALIAN
  LATIN
  GAEILC
  // Arts
  ART_AND_DESIGN
  MUSIC
  MUSIC_TECHNOLOGY
  DRAMA
  // Business
  BUSINESS_MANAGEMENT
  ACCOUNTING
  ECONOMICS
  // VocTech
  DESIGN_AND_MANUFACTURE
  GRAPHIC_COMMUNICATION
  ENGINEERING_SCIENCE
  // PE
  PHYSICAL_EDUCATION
  // Other
  PSYCHOLOGY
  SOCIOLOGY
  LAW
  MEDIA_STUDIES
  HEALTH_AND_FOOD_TECHNOLOGY
  HOSPITALITY
  TRAVEL_AND_TOURISM
  EARLY_YEARS_AND_CHILDCARE
  CHILD_CARE_AND_DEVELOPMENT
  OTHER
}

// ============================================================================
// BAML function — the Scotland (SQA) syllabus extractor (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change
// + the 2026-07-30-biep-v3-sct-wls-ni-v1 change (now promoted to a
// per-jurisdiction proper pipeline).
//
// Extracts the structured syllabus data from a Scotland (SQA) PDF
// specification for any (subject, level) cohort.

class ScotlandSyllabusSpec {
  source_pdf string
  source_pages int
  subject SCQFSubject
  level SCQFLevel
  title string                       @description("The full title of the qualification (e.g. 'Mathematics Higher')")
  version string                    @description("e.g. '2024' or '2025-onwards'")
  first_teaching_year int?
  last_certification_year int?
  total_marks int
  component_papers int               @description("Number of exam papers (typically 1-3 for Scotland)")

  // Topic coverage
  topics ScotlandTopic[]

  // Assessment structure
  assessment_objectives ScotlandAssessmentObjective[]

  // Cross-references
  external_assessment_pct int       @description("Percentage of the grade from the external exam (rest is coursework)")
  coursework_pct int
}

class ScotlandTopic {
  topic_code string                   @description("e.g. 'MTH-3.1' or 'CH-2.4'")
  topic_label string                  @description("Human-readable topic title")
  strand string                       @description("The topic strand (e.g. 'Algebra', 'Calculus', 'Cell Biology')")
  learning_outcomes string[]
  weighting_pct int
}

class ScotlandAssessmentObjective {
  ao_id string                        @description("e.g. 'AO1' or 'AO2.1'")
  ao_label string
  ao_description string
  weighting_pct int
}

function ExtractScotlandSyllabus(
  pdf_text: string,
  subject: SCQFSubject?,
  level: SCQFLevel?
) -> ScotlandSyllabusSpec {
  client BIEPV3Extract
  prompt #"
    Extract the structured syllabus data from this Scotland (SQA)
    qualification PDF for the subject {{ subject }} at the
    {{ level }} level.

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#

}

test ExtractScotlandSyllabus {
  functions [ExtractScotlandSyllabus]
  args {
    pdf_text #"
      Mathematics Higher
      SQA Qualification Specification

      The Higher Mathematics Course enables learners to develop knowledge
      and skills in algebra, geometry, calculus, and statistics. The course
      is assessed via a single external examination worth 100 marks.

      Topics:
      - Algebra (AO1): 20%
      - Calculus (AO2): 25%
      - Geometry (AO3): 15%
      - Statistics (AO4): 20%
      - Number Theory (AO5): 10%
      - Proof and Reasoning (AO6): 10%
    "#
    subject "MATHEMATICS"
    level "HIGHER"
  }
}
