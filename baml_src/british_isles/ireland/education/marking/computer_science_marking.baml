// BAML schema: Computer Science Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// Computer Science-specific discriminator (CsQuestionType + CsNotationType
// + CsCommonMistake). LC Computer Science mixes short-answer, pseudo-code
// / code (Python-ish), database query, network diagram questions.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

// Reuse the canonical `MarkingBand` + `GradeDescriptor` + `MarkAllocation`
// classes from the BIEP v1 marking-scheme schema. Reference these by their
// bare class names (BAML 0.222+ resolves cross-file imports via the
// import statement below).
enum CsQuestionType {
  SHORT_ANSWER       @description("Short factual answer (1-3 sentences)")
  PSEUDOCODE         @description("Write pseudo-code / trace through pseudo-code")
  CODE_WRITE         @description("Write a function in a specified language (often Python-ish)")
  CODE_TRACE         @description("Trace through given code and predict the output")
  DATABASE_QUERY     @description("Write / interpret SQL")
  DIAGRAM_NETWORK    @description("Interpret / annotate a network / topology diagram")
  DIAGRAM_BIG_O      @description("Analyse runtime complexity / Big-O")
  EXTENDED_RESPONSE  @description("Computer-system / algorithm explanation (5-10 marks)")
}

enum CsNotationType {
  PSEUDOCODE_TEXT @description("Plain English pseudo-code (NCCA style)")
  PYTHON_ISH      @description("Python-derived pseudo-code with snake_case")
  JAVASCRIPT_ISH  @description("JavaScript-style pseudo-code")
  SQL             @description("Structured Query Language")
  MIXED           @description("Mix of notations across questions")
}

enum CsCommonMistake {
  OFF_BY_ONE            @description("Off-by-one error in loop bound or array index")
  INFINITE_LOOP         @description("Constructed an infinite loop")
  RECURSION_NO_BASE     @description("Recursive function missing base case")
  SQL_GROUP_BY_MISSED   @description("SQL query needed GROUP BY for the aggregation")
  BIG_O_MISCALCULATED   @description("Wrong Big-O analysis of the algorithm")
  VARIABLE_SCOPE_LEAK   @description("Variable leaked into unintended scope")
  MISSING_TYPE_HINT     @description("Pseudo-code missing the expected type annotation")
  PROTOCOL_CONFUSION    @description("Confused TCP vs UDP / HTTP vs HTTPS")
}

class CsSubjectDiscriminator {
  primary_question_type CsQuestionType @description("Dominant question type in this paper")
  notation_mix CsNotationType @description("Notation used across the paper")
  has_code_write bool @description("Paper 2 has code-write / programming questions")
  has_database_section bool @description("Always true for LC CS (databases is mandatory)")
  has_algorithm_analysis bool @description("Always true for LC CS (algorithm analysis mandatory)")
  most_common_mistake CsCommonMistake
}

class ComputerScienceMarkingScheme {
  subject string @description("Always 'computer_science'")
  scheme_code string
  language string @description("EN only for CS")
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors GradeDescriptor[]
  mark_allocations MarkAllocation[]

  subject_specific CsSubjectDiscriminator

  total_marks int
  total_questions int
  practical_skill_marks int? @description("Marks for the practical / programming paper")
}

function ExtractComputerScienceMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?,
) -> ComputerScienceMarkingScheme {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// test computer_science_marking_extraction_smoke {
//   functions [ExtractComputerScienceMarkingScheme]
//   args {
//     pdf_text <<<
//       "Marking scheme for LC Computer Science Paper 2 HL 2024. Mix of
//        pseudo-code, SQL queries, Big-O analysis. Most common mistake:
//        off-by-one error in loop boundaries."
//     >>>
//     year { 2024 }
//     level { "hl" }
//   }
// }
