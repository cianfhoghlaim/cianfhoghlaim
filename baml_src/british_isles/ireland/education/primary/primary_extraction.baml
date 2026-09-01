// =============================================================================
// Primary Curriculum (ages 4-12) — Stage-Specific BAML Schema
// Bilingual EN/GA extraction of the NCCA Primary Curriculum Framework.
//
// Per the ireland-primary-jc-dlt-baml spec (Phase 1 of the
// 2026-07-14-ireland-primary-jc-dlt-baml-v1 change):
//   - 4 Primary curriculum areas: English, Gaeilge, Mathematics, SESE
//   - 8 Primary year levels: Junior Infants through 6th Class
//   - Stage-specific schema (no Senior Cycle / Leaving Cert LOs)
//
// The legacy canonical Primary schema lives at
// baml/education/stages/primary.baml (consumed by dlt/.../primary.py).
// This file adds the stage-specific extractor used by the combined
// cross-stage loop in primary_jc_combined.py.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
// =============================================================================

// -----------------------------------------------------------------------------
// Enums (the 8 Primary year levels, per NCCA)
// -----------------------------------------------------------------------------

enum PrimaryYearLevel {
  JUNIOR_INFANTS
    @description("Naíonáin Shóisearacha — age 4-5")
  SENIOR_INFANTS
    @description("Naíonáin Shinsearacha — age 5-6")
  FIRST
    @description("Rang a hAon — age 6-7")
  SECOND
    @description("Rang a Dó — age 7-8")
  THIRD
    @description("Rang a Trí — age 8-9")
  FOURTH
    @description("Rang a Ceathair — age 9-10")
  FIFTH
    @description("Rang a Cúig — age 10-11")
  SIXTH
    @description("Rang a Sé — age 11-12")
}

// The 4 Primary curriculum areas per the ireland-primary-jc-dlt-baml spec.
// (Science + Geography + History are bundled under SESE in the spec but
// surfaced as discrete subclasses here for downstream analytics.)
enum PrimaryArea {
  ENGLISH
  GAEILGE
  MATHEMATICS
  SESE
}

// The 5 Mathematics strands (per the ireland-primary-jc-dlt-baml spec).
enum PrimaryMathsStrand {
  NUMBER
  ALGEBRA
  SHAPE_SPACE
  MEASURE
  DATA
}

// -----------------------------------------------------------------------------
// Classes
// -----------------------------------------------------------------------------

class PrimaryLearningOutcomeStage {
  outcome_id string
    @description("Deterministic slug; e.g. 'maths_first_number_count_to_20'")
  text_en string
  text_ga string?
    @description("Irish translation (null if English-only outcome)")
  year_level PrimaryYearLevel
  area PrimaryArea
  maths_strand PrimaryMathsStrand?
    @description("Only set for area = MATHEMATICS; null otherwise")
  blooms_level string?
    @description("Bloom's taxonomy level: REMEMBER / UNDERSTAND / APPLY / ANALYSE / EVALUATE / CREATE")
  cross_curricular_links string[]
    @description("Other Primary areas this outcome links to (e.g. ['SESE', 'ENGLISH'])")
  extracted_at string
    @description("ISO 8601 datetime of BAML extraction")
}

class PrimaryStrandStage {
  strand_id string
    @description("Deterministic slug; e.g. 'maths_number', 'english_reading'")
  title_en string
  title_ga string?
  area PrimaryArea
  description_en string
  description_ga string?
  weighting_pct float?
    @description("Approximate percentage weighting in the curriculum")
  outcomes PrimaryLearningOutcomeStage[]
}

class PrimaryAreaSpecStage {
  // Document-level metadata
  area PrimaryArea
  language string
    @description("en | ga | bilingual")
  year_levels PrimaryYearLevel[]
    @description("Subset of the 8 Primary year levels this document covers")
  source_pdf string
  source_pages int

  // Document content
  rationale_en string
  rationale_ga string?
  strands PrimaryStrandStage[]
  total_learning_outcomes int

  // Cross-cutting
  integration_links string[]
    @description("Explicit text mentioning other curriculum areas")
  key_competencies string[]
    @description("NCCA key competencies (e.g. 'Being Creative', 'Communicating')")
  assessment_approach string?
    @description("Plain-English description of the assessment approach")

  // Provenance
  extracted_at string
    @description("ISO 8601 datetime of BAML extraction")
  extraction_confidence float
    @description("0.0-1.0; 1.0 = perfect parse")
}

// -----------------------------------------------------------------------------
// Function — the canonical Primary extractor (used by primary_jc_combined.py)
// -----------------------------------------------------------------------------
//
// Returns the canonical `PrimaryAreaSpecStage` Pydantic class.
// Mirrors the BIEP v1 `ExtractCurriculumSyllabus` shape but constrained
// to the 8 Primary year levels (no JC / LC outcomes leak through).

function ExtractPrimaryArea(
  text: string,
  area: string
) -> PrimaryAreaSpecStage {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}
