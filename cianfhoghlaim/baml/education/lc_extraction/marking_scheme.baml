// BAML schema: Marking Scheme Extraction
//
// Used by the LC5-subject pipeline to extract structured grading data
// from NCCA marking scheme guidelines (SCSEC##_guideline_material_eng.pdf).
// Each scheme maps question marks to grading bands + grade descriptors.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum MarkingBand {
  BAND_I   @description("Distinction-grade responses (>75%)")
  BAND_II  @description("Higher merit-grade responses (60-75%)")
  BAND_III @description("Merit-grade responses (50-60%)")
  BAND_IV  @description("Achieved-grade responses (40-50%)")
  BAND_V   @description("Low achieved / partial responses (<40%)")
}

class MarkAllocation {
  q_id: string
  total_marks: int
  partial_credit_rules: string[]
  common_mistakes: string[]
  sample_answer: string?
}

class GradeDescriptor {
  band: MarkingBand
  percentage_min: int       @description("e.g. 75 for H1")
  percentage_max: int       @description("e.g. 100 for H1")
  descriptor_text_en: string
  descriptor_text_ga: string?
  exemplar_responses: string[]
}

class MarkingScheme {
  subject: string
  scheme_code: string
  language: string
  level: string
  year: int
  source_pdf: string

  grade_descriptors: GradeDescriptor[]
  mark_allocations: MarkAllocation[]

  // Heuristic metrics (used by the 09_marking_scheme_complexity notebook)
  total_bands: int
  total_pages: int
  descriptor_word_count_avg: int
}
