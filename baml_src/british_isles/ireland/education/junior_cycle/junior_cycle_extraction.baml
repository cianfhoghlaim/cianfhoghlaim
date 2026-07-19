// =============================================================================
// Junior Cycle (ages 12-15) — Stage-Specific BAML Schema
// Bilingual EN/GA extraction of the NCCA Junior Cycle specifications.
//
// Per the ireland-primary-jc-dlt-baml spec (Phase 1 of the
// 2026-07-14-ireland-primary-jc-dlt-baml-v1 change):
//   - 24 Junior Cycle subjects (English, Gaeilge, Mathematics, History,
//     Geography, Science, Business Studies, French, German, Spanish,
//     Italian, Russian, Japanese, Arabic, Music, Art, Home Economics,
//     Wood Technology, Metalwork, Technical Graphics, Materials
//     Technology Wood, Materials Technology Metal, Engineering, Coding)
//   - 3 year levels: Year 1, Year 2, Year 3 (no Transition Year in v1)
//   - Stage-specific schema (no Leaving Cert / Senior Cycle LOs)
//
// The legacy canonical JC schema lives at
// baml/education/stages/junior_cycle.baml (consumed by
// dlt/.../junior_cycle.py for the per-subject loop).
// This file adds the stage-specific extractor used by the combined
// cross-stage loop in primary_jc_combined.py.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
// =============================================================================

// -----------------------------------------------------------------------------
// Enums
// -----------------------------------------------------------------------------

enum JCYearLevel {
  YEAR_1
  YEAR_2
  YEAR_3
}

// The 24 NCCA Junior Cycle subjects per the ireland-primary-jc-dlt-baml spec.
enum JCSubject {
  ENGLISH
  GAEILGE
  MATHEMATICS
  HISTORY
  GEOGRAPHY
  SCIENCE
  BUSINESS_STUDIES
  FRENCH
  GERMAN
  SPANISH
  ITALIAN
  RUSSIAN
  JAPANESE
  ARABIC
  MUSIC
  ART
  HOME_ECONOMICS
  WOOD_TECHNOLOGY
  METALWORK
  TECHNICAL_GRAPHICS
  MATERIALS_TECHNOLOGY_WOOD
  MATERIALS_TECHNOLOGY_METAL
  ENGINEERING
  CODING
}

// The 4 JC Science strands (per the ireland-primary-jc-dlt-baml spec).
enum JCScienceStrand {
  BIOLOGICAL_WORLD
  CHEMICAL_WORLD
  PHYSICAL_WORLD
  EARTH_SPACE
}

// Junior Cycle level distinction (Ordinary is the default; L1/L2
// Learning Programmes are also valid for the 2026+ framework).
enum JCLevel {
  ORDINARY
  LEVEL_1_LEARNING_PROGRAMME
  LEVEL_2_LEARNING_PROGRAMME
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class JCLearningOutcomeStage {
  lo_id string
    @description("Deterministic slug; e.g. 'sci_year_1_bio_cells'")
  text_en string
  text_ga string?
    @description("Irish translation (null if English-only LO)")
  year_level JCYearLevel
  science_strand JCScienceStrand?
    @description("Only set for subject = SCIENCE; null otherwise")
  blooms_level string?
    @description("Bloom's taxonomy level")
  cross_curricular_links string[]
  extracted_at string
    @description("ISO 8601 datetime of BAML extraction")
}

class JCStrandStage {
  strand_id string
    @description("Deterministic slug")
  title_en string
  title_ga string?
  description_en string
  description_ga string?
  outcomes JCLearningOutcomeStage[]
}

class JCSubjectSpecStage {
  // Document-level metadata
  subject JCSubject
  language string
    @description("en | ga | bilingual")
  level JCLevel
  source_pdf string
  source_pages int

  // Document content
  title_en string
  title_ga string?
  rationale_en string
  rationale_ga string?
  strands JCStrandStage[]
  total_learning_outcomes int

  // Cross-cutting
  cross_curricular_links string[]
  assessment_objectives string[]
  key_skills string[]
    @description("NCCA Junior Cycle key skills (e.g. 'Information Literacy', 'Being Creative')")

  // Provenance
  extracted_at string
    @description("ISO 8601 datetime of BAML extraction")
  extraction_confidence float
    @description("0.0-1.0; 1.0 = perfect parse")
}

// -----------------------------------------------------------------------------
// Function — the canonical JC extractor (used by primary_jc_combined.py)
// -----------------------------------------------------------------------------
//
// Returns the canonical `JCSubjectSpecStage` Pydantic class.
// Mirrors the BIEP v1 `ExtractCurriculumSyllabus` shape but constrained
// to the 3 JC year levels (Year 1 + Year 2 + Year 3 only — no TY, no LC).

function ExtractJCSubjectSpec(
  text: string,
  subject: string,
) -> JCSubjectSpecStage {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}