// BAML schema: Guernsey subject taxonomy (Crown Dependency)
//
// Per the 2026-07-31-biep-v3-crown-dependencies-v1 change.
//
// Guernsey uses the English GCSE + A-Level system (with a small
// number of additional local qualifications). Administered by the
// States of Guernsey Education Services.
//
// Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/

enum GuernseyLevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  BTEC
}

enum GuernseySubject {
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
  // Humanities
  HISTORY
  GEOGRAPHY
  RELIGIOUS_STUDIES
  // Languages
  FRENCH
  GERMAN
  SPANISH
  // Arts
  ART_AND_DESIGN
  MUSIC
  DRAMA
  MEDIA_STUDIES
  // Business
  BUSINESS
  ECONOMICS
  // PE
  PHYSICAL_EDUCATION
  // Other
  PSYCHOLOGY
  SOCIOLOGY
  LAW
  DESIGN_AND_TECHNOLOGY
  CHILD_DEVELOPMENT
  HEALTH_AND_SOCIAL_CARE
  OTHER
}

// ============================================================================
// BAML function — the Guernsey syllabus extractor (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change
// + the 2026-07-31-biep-v3-crown-dependencies-v1 change (now promoted to
// a per-jurisdiction proper pipeline).
//
// Extracts the structured syllabus data from a Guernsey PDF
// specification. Guernsey uses the English GCSE + A-Level system
// (with a small number of additional local qualifications). Administered
// by the States of Guernsey Education Services.

class GuernseySyllabusSpec {
  source_pdf string
  source_pages int
  subject GuernseySubject
  level GuernseyLevel
  title string
  version string
  first_teaching_year int?
  last_certification_year int?
  total_marks int
  component_papers int

  // Local qualifications flag (e.g. the Guernsey BTEC)
  is_local_qualification bool        @description("True if this is a Guernsey local qualification (not English GCSE/A-Level)")

  topics GuernseyTopic[]
  assessment_objectives GuernseyAssessmentObjective[]
}

class GuernseyTopic {
  topic_code string
  topic_label string
  strand string
  learning_outcomes string[]
  weighting_pct int
}

class GuernseyAssessmentObjective {
  ao_id string
  ao_label string
  ao_description string
  weighting_pct int
}

function ExtractGuernseySyllabus(
  pdf_text: string,
  subject: GuernseySubject?,
  level: GuernseyLevel?,
) -> GuernseySyllabusSpec {  client BIEPV3Extract
  prompt #"
    Extract the structured syllabus data from this Guernsey (States of
    Guernsey Education Services) PDF specification for the subject
    {{ subject }} at the {{ level }} level. Flag whether the
    qualification is a Guernsey local qualification via the
    is_local_qualification field.

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}