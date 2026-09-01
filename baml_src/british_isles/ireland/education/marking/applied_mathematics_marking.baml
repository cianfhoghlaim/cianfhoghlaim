// BAML schema:  Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// -specific discriminator.

enum AppliedMathsQuestionType {
  SHORT_ANSWER      @description("Short factual answer (1-2 sentences)")
  EXTENDED_RESPONSE @description("Longer essay-style answer")
  CALCULATION       @description("Calculation question (with explicit marks breakdown)")
  PROOF             @description("Mathematical proof question")
  APPLIED           @description("Applied/contextualised question")
  DIAGRAM_BASED      @description("Diagram-based question")
}

enum AppliedMathsCommonMistake {
  ALGEBRAIC_ERROR         @description("Sign error in algebraic manipulation")
  UNIT_MISMATCH            @description("Mixed units in a calculation")
  ASSUMPTION_UNSTATED      @description("Failed to state assumption")
  METHOD_INCOMPLETE        @description("Incomplete method description")
  ROUNDING_ERROR           @description("Significant figure / rounding error")
  CONCEPT_CONFUSION        @description("Confused similar concepts (e.g. scalar vs vector)")
}

class AppliedMathsSubjectDiscriminator {
  primary_topic string @description("Main  topic tested")
  dominant_question_types AppliedMathsQuestionType[] @description("Mix in this paper")
  most_common_mistake AppliedMathsCommonMistake
}

class AppliedMathsMarkingScheme {
  subject string @description("Always 'applied_mathematics'")
  scheme_code string
  language string @description("EN (taught in English)")
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors LCGradeDescriptor[]
  mark_allocations LCMarkAllocation[]

  subject_specific AppliedMathsSubjectDiscriminator

  total_marks int
  total_questions int
}

function ExtractAppliedMathsMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?
) -> MarkingScheme {
  client Primary
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting the LC  marking scheme
    from the PDF text. Return the canonical MarkingScheme
    shape with grade_descriptors + mark_allocations +
    subject_specific (the -specific discriminator).

    PDF text: {{ pdf_text }}

    {{ ctx.output_format }}
  "#
}

test applied_mathematics_marking_sanity_v2 {
  functions [ExtractAppliedMathsMarkingScheme]
  args {
    pdf_text "Sample LC  marking scheme text..."
    year 2024
    level "HL"
  }
}
