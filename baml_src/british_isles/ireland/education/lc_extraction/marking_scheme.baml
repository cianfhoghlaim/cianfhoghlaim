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
  q_id string
  total_marks int
  partial_credit_rules string[]
  common_mistakes string[]
  sample_answer string?
}

class GradeDescriptor {
  band MarkingBand
  percentage_min int       @description("e.g. 75 for H1")
  percentage_max int       @description("e.g. 100 for H1")
  descriptor_text_en string
  descriptor_text_ga string?
  exemplar_responses string[]
}

class MarkingScheme {
  subject string
  scheme_code string
  language string
  level string
  year int
  source_pdf string

  grade_descriptors GradeDescriptor[]
  mark_allocations MarkAllocation[]

  // Heuristic metrics (used by the 09_marking_scheme_complexity notebook)
  total_bands int
  total_pages int
  descriptor_word_count_avg int
}

// ============================================================================
// BAML function — the canonical extractor (BIEP v1)
// ============================================================================
// Replaces the legacy `b.ExtractLeavingCertMarkingScheme` from
// `baml/education/pdfs/leaving_cert_marking_scheme.baml`.
//
// Returns the canonical `MarkingScheme` Pydantic class with
// `GradeDescriptor[]` + `MarkAllocation[]` for the 5 grade bands.

function ExtractMarkingSchemeGuideline(
  pdf_text: string,
  subject: string?,
  year: int?,
  paper: string?,
) -> MarkingScheme {
  client ExtractEn
  prompt #"
    You are an Irish Leaving Certificate marking-scheme guideline
    analyst. Given the text of an NCCA marking-scheme PDF (the
    companion document to an exam paper), extract the structured
    scheme.

    Subject context: {{ subject }}
    Year: {{ year }}
    Paper context: {{ paper }} (e.g. "paper-1", "paper-2")

    Grade descriptors (one per band):
      - band: BAND_I (Distinction, >75%) / BAND_II (Higher Merit, 60-75%) /
              BAND_III (Merit, 50-60%) / BAND_IV (Achieved, 40-50%) /
              BAND_V (Low Achieved, <40%)
      - percentage_min / percentage_max: integer bounds (0-100)
      - descriptor_text_en: full plain-English descriptor
      - descriptor_text_ga: Irish translation (null if EN-only)
      - exemplar_responses: array of quoted exemplar responses

    Mark allocations (one per question):
      - q_id: deterministic ("q1a", "q2b(i)")
      - total_marks: integer
      - partial_credit_rules: array of strings ("M1A1: 1 method mark + 1 accuracy mark")
      - common_mistakes: array of strings
      - sample_answer: canonical full-credit answer text (or null)

    Document-level fields:
      - subject: canonical subject slug
      - scheme_code: e.g. "SCSEC25_Maths_marking_2024"
      - language: "EN" or "GA"
      - level: "HL" / "OL" / "FDN"
      - year: integer
      - source_pdf: filename
      - grade_descriptors[]: the populated descriptors
      - mark_allocations[]: the populated allocations
      - total_bands: 5 (always; one per MarkingBand)
      - total_pages: integer
      - descriptor_word_count_avg: integer average word count per band

    Marking scheme text:
    ---
    {{ pdf_text }}
    ---

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertMarkingScheme` from `baml/education/pdfs/leaving_cert_marking_scheme.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.3 task) and
// replaced by this canonical `ExtractMarkingSchemeGuideline`.
