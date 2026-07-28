// BAML schema: Wales subject taxonomy (WJEC awarding body)
//
// Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change.
//
// WJEC (Welsh Joint Education Committee) is the awarding body for
// Wales. The Curriculum for Wales uses 2 main qualification levels:
//   - GCSE
//   - A-Level
//
// Welsh-medium subjects are flagged via the language field
// (cy = Cymraeg / Welsh).
//
// Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/

enum WJECLevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  WELSH_BACCALAUREATE
}

enum WJECSubject {
  // Core STEM
  MATHEMATICS
  FURTHER_MATHEMATICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  COMPUTER_SCIENCE
  // English + Lit
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  // Welsh-medium
  WELSH_LANGUAGE
  WELSH_LITERATURE
  // Humanities
  HISTORY
  GEOGRAPHY
  WELSH_HISTORY
  WELSH_GEOGRAPHY
  RELIGIOUS_STUDIES
  PHILOSOPHY
  // Languages
  FRENCH
  GERMAN
  SPANISH
  ITALIAN
  LATIN
  // Arts
  ART_AND_DESIGN
  MUSIC
  DRAMA
  MEDIA_STUDIES
  // Business
  BUSINESS
  ECONOMICS
  LAW
  // PE
  PHYSICAL_EDUCATION
  // Other
  PSYCHOLOGY
  SOCIOLOGY
  POLITICS
  HEALTH_AND_SOCIAL_CARE
  ENGINEERING
  DESIGN_AND_TECHNOLOGY
  FOOD_TECHNOLOGY
  TEXTILES
  OTHER
}

// ============================================================================
// BAML function — the Wales (WJEC) syllabus extractor (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change
// + the 2026-07-30-biep-v3-sct-wls-ni-v1 change (now promoted to a
// per-jurisdiction proper pipeline).
//
// Extracts the structured syllabus data from a Wales (WJEC) PDF
// specification for any (subject, level, language) cohort.
// Welsh-medium subjects are flagged via the language field (cy = Cymraeg).

class WalesSyllabusSpec {
  source_pdf string
  source_pages int
  subject WJECSubject
  level WJECLevel
  title string                       @description("The full title of the qualification (e.g. 'Mathematics GCSE')")
  version string                    @description("e.g. '2024' or '2025-onwards'")
  first_teaching_year int?
  last_certification_year int?
  total_marks int
  component_papers int

  // Welsh-medium flag
  is_welsh_medium bool              @description("True if the subject is taught in Welsh (Cymraeg)")

  // Topic coverage
  topics WalesTopic[]

  // Assessment structure
  assessment_objectives WalesAssessmentObjective[]
}

class WalesTopic {
  topic_code string                   @description("e.g. 'MAT-3.1' or 'BIO-2.4'")
  topic_label string
  strand string                       @description("e.g. 'Algebra', 'Calculus', 'Cell Biology'")
  learning_outcomes string[]
  weighting_pct int
}

class WalesAssessmentObjective {
  ao_id string
  ao_label string
  ao_description string
  weighting_pct int
}

function ExtractWalesSyllabus(
  pdf_text: string,
  subject: WJECSubject?,
  level: WJECLevel?,
) -> WalesSyllabusSpec {  client BIEPV3Extract
  prompt #"
    Extract the structured syllabus data from this Wales (WJEC)
    qualification PDF for the subject {{ subject }} at the {{ level }}
    level. Flag whether the subject is taught in Welsh (Cymraeg) via
    the is_welsh_medium field.

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}