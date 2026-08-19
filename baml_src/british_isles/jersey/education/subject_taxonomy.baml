// BAML schema: Jersey subject taxonomy (Crown Dependency)
//
// Per the 2026-07-31-biep-v3-crown-dependencies-v1 change.
//
// Jersey has its own curriculum (a hybrid of English GCSE + French
// Baccalauréat). The Jersey Curriculum is administered by the
// States of Jersey Education Department.
//
// Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/

enum JerseyLevel {
  GCSE
  A_LEVEL
  INTERNATIONAL_BACCALAUREATE
  FRENCH_BACCALAUREAT
}

enum JerseySubject {
  // Core STEM (mirrors English GCSE)
  MATHEMATICS
  FURTHER_MATHEMATICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  COMPUTER_SCIENCE
  // English + Lit
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  // French (mandatory in Jersey)
  FRENCH
  // Humanities
  HISTORY
  GEOGRAPHY
  RELIGIOUS_STUDIES
  // Other languages
  GERMAN
  SPANISH
  LATIN
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
  OTHER
}

// ============================================================================
// BAML function — the Jersey syllabus extractor (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change
// + the 2026-07-31-biep-v3-crown-dependencies-v1 change (now promoted to
// a per-jurisdiction proper pipeline).
//
// Extracts the structured syllabus data from a Jersey PDF specification.
// Jersey has its own curriculum (a hybrid of English GCSE + French
// Baccalauréat). The Jersey Curriculum is administered by the States of
// Jersey Education Department.

class JerseySyllabusSpec {
  source_pdf string
  source_pages int
  subject JerseySubject
  level JerseyLevel
  title string                       @description("The full title of the qualification (e.g. 'Mathematics GCSE')")
  version string                    @description("e.g. '2024' or '2025-onwards'")
  first_teaching_year int?
  last_certification_year int?
  total_marks int
  component_papers int

  // French Baccalauréat flag
  is_french_bac bool                 @description("True if this is a French Baccalauréat qualification")

  // Topic coverage
  topics JerseyTopic[]
  assessment_objectives JerseyAssessmentObjective[]
}

class JerseyTopic {
  topic_code string
  topic_label string
  strand string
  learning_outcomes string[]
  weighting_pct int
}

class JerseyAssessmentObjective {
  ao_id string
  ao_label string
  ao_description string
  weighting_pct int
}

function ExtractJerseySyllabus(
  pdf_text: string,
  subject: JerseySubject?,
  level: JerseyLevel?,
) -> JerseySyllabusSpec {  client BIEPV3Extract
  prompt #"
    Extract the structured syllabus data from this Jersey (States of
    Jersey Education Department) PDF specification for the subject
    {{ subject }} at the {{ level }} level. Flag whether the
    qualification is a French Baccalauréat via the is_french_bac field.

    PDF text:
    {{ pdf_text }}

    {{ ctx.output_format }}
  "#

  catch_all (err) {
    JerseySyllabusSpec {
      source_pdf "",
      source_pages 0,
      subject jerseysubject {},
      level jerseylevel {},
      first_teaching_year null,
      last_certification_year null,
      total_marks 0,
      component_papers 0,
      topics null,
      assessment_objectives null,
    }
  }
}

test ExtractJerseySyllabus {
  functions [ExtractJerseySyllabus]
  args {
    pdf_text #"
      Mathematics GCSE
      States of Jersey Education Department

      The Jersey GCSE Mathematics course is taught in English and is
      modelled on the English GCSE with Jersey-specific additions. The
      course is assessed via three written papers (2 × 1.5 hours + 1 × 2
      hours), each worth 80 marks.

      Topics:
      - Number (AO1): 25%
      - Algebra (AO2): 30%
      - Geometry (AO3): 20%
      - Statistics (AO4): 25%
    "#
    subject "MATHEMATICS"
    level "GCSE"
  }
}