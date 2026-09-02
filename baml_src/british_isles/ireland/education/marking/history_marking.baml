// BAML schema:  Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// -specific discriminator.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum HistoryQuestionType {
  SHORT_ANSWER      @description("Short factual answer (1-2 sentences)")
  EXTENDED_RESPONSE @description("Longer essay-style answer")
  CALCULATION       @description("Calculation question")
  DATA_ANALYSIS     @description("Data interpretation question")
  ESSAY              @description("Essay question")
  DIAGRAM_BASED      @description("Diagram-based question")
}

enum HistoryCommonMistake {
  TOPIC_MISUNDERSTANDING  @description("Common conceptual misconception")
  CALCULATION_ERROR       @description("Common computational error")
  METHOD_INCOMPLETE       @description("Incomplete method description")
}

class HistorySubjectDiscriminator {
  primary_topic string @description("Main  topic tested")
  dominant_question_types HistoryQuestionType[] @description("Mix in this paper")
  most_common_mistake HistoryCommonMistake
}

class HistoryMarkingScheme {
  subject string @description("Always 'history'")
  scheme_code string
  language string @description("EN (taught in English)")
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors LCGradeDescriptor[]
  mark_allocations LCMarkAllocation[]

  subject_specific HistorySubjectDiscriminator

  total_marks int
  total_questions int
}

function ExtractHistoryMarkingScheme(
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

test history_marking_sanity_v2 {
  functions [ExtractHistoryMarkingScheme]
  args {
    pdf_text "Sample LC  marking scheme text..."
    year 2024
    level "HL"
  }
}
