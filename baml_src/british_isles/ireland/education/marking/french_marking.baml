// BAML schema:  Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// -specific discriminator.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum FrenchQuestionType {
  SHORT_ANSWER      @description("Short factual answer (1-2 sentences)")
  EXTENDED_RESPONSE @description("Longer essay-style answer")
  CALCULATION       @description("Calculation question")
  DATA_ANALYSIS     @description("Data interpretation question")
  ESSAY              @description("Essay question")
  DIAGRAM_BASED      @description("Diagram-based question")
}

enum FrenchCommonMistake {
  TOPIC_MISUNDERSTANDING  @description("Common conceptual misconception")
  CALCULATION_ERROR       @description("Common computational error")
  METHOD_INCOMPLETE       @description("Incomplete method description")
}

class FrenchSubjectDiscriminator {
  primary_topic string @description("Main  topic tested")
  dominant_question_types FrenchQuestionType[] @description("Mix in this paper")
  most_common_mistake FrenchCommonMistake
}

class FrenchMarkingScheme {
  subject string @description("Always 'french'")
  scheme_code string
  language string @description("EN (taught in English)")
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors LCGradeDescriptor[]
  mark_allocations LCMarkAllocation[]

  subject_specific FrenchSubjectDiscriminator

  total_marks int
  total_questions int
}

function ExtractFrenchMarkingScheme(
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

test french_marking_sanity_v2 {
  functions [ExtractFrenchMarkingScheme]
  args {
    pdf_text "Sample LC  marking scheme text..."
    year 2024
    level "HL"
  }
}
