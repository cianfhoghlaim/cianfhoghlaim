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

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`.
  lineage LineageTrace?
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
) -> MarkingScheme {  client ExtractEn
  prompt #"
    You are an expert at reading official NCCA/State Examinations
    Commission marking scheme guideline documents for the Irish Leaving
    Certificate and extracting their grading structure with fidelity —
    every mark allocation, grade band, and descriptor below MUST be
    grounded in the PDF text given; never invent a mark total or a
    descriptor that isn't actually present.

    Subject: {{ subject }}
    Year (if known): {{ year }}
    Paper reference (if known): {{ paper }}

    From the marking scheme text below, extract:
    - subject: the subject slug
    - scheme_code: the document's own reference code if visible in the
      text, else derive a short slug from the subject and year
    - language: 'EN' or 'GA' based on the language of the text
    - level: 'OL', 'HL', or 'FDN' — read from the document's own header
    - year: the year stated in the document, else the year given above
    - source_pdf: leave as an empty string; the Python caller fills this
      in from the actual file path
    - grade_descriptors: every distinct grade band the document
      describes, each with:
      - band: BAND_I (>75%), BAND_II (60-75%), BAND_III (50-60%),
        BAND_IV (40-50%), or BAND_V (<40%) — map the document's own
        percentage ranges or grade labels (H1-H8, O1-O8, etc.) onto
        these five bands by their percentage range
      - percentage_min / percentage_max: the band's percentage range as
        stated or implied by the document
      - descriptor_text_en / descriptor_text_ga: the document's own
        prose description of what a response in that band demonstrates
        (whichever language is present; leave the other empty)
      - exemplar_responses: short excerpts of any sample/exemplar
        answers the document quotes for that band, if present
    - mark_allocations: every question-level mark allocation the
      document specifies, each with:
      - q_id: the question identifier the scheme refers to (matching
        the exam paper's own numbering, e.g. '1', '2(b)')
      - total_marks: the marks allocated to that question
      - partial_credit_rules: any explicit partial-credit rules stated
        (e.g. 'award 2 marks for correct method even if final answer
        wrong')
      - common_mistakes: any explicitly noted common errors or
        misconceptions the scheme warns markers to watch for
      - sample_answer: a worked sample answer if the scheme provides one
    - total_bands: the count of distinct grade_descriptors
    - total_pages: your best count of distinct pages represented in the text
    - descriptor_word_count_avg: the average word count across all
      descriptor_text_en values (0 if none)

    If a field has no support in the text, leave it empty or its
    numeric default rather than fabricating content.

    Marking scheme PDF text:
    {{ pdf_text }}

    {{ _.role("user") }}
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
