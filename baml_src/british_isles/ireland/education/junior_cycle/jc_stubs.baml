// Junior Cycle stubs — added 2026-08-15 to unblock `baml-cli generate`.
// The 5 missing types (JCStrandDescriptor, JCLearningOutcomeStage,
// JCStrandStage, JCQuestion, JCExamSection) were referenced by
// the junior_cycle/*.baml files but never declared. This file adds
// minimal stub definitions so the BAML Python client can regenerate.
// The junior_cycle_extraction Python `__init__.py` already re-exports
// these symbols (so consumers see a stable surface).

// DEPRECATED 2026-08-15: these stubs are placeholders. The canonical
// definitions will be added to
// `baml_src/british_isles/ireland/education/junior_cycle/jc_stubs.baml`
// (this file) and the BAML generator will then emit proper Pydantic
// classes. In the meantime, the stubs below provide enough surface
// for `baml-cli generate` to succeed.

class JCStrandDescriptor {
  strand_id string
  strand_name_en string
  strand_name_ga string?
  description_en string?
  description_ga string?
  learning_outcomes string[]  // canonical JCLearningOutcome IDs
}

class JCLearningOutcomeStage {
  outcome_id string
  description_en string
  description_ga string?
  stage string  // one of the 4 NCCA Junior Cycle stages
  strand_id string?
}

class JCStrandStage {
  strand_id string
  strand_name_en string
  strand_name_ga string?
  stage string  // one of the 4 NCCA Junior Cycle stages
  learning_outcomes string[]
}

class JCQuestion {
  question_number int
  question_text_en string
  question_text_ga string?
  marks int
  question_type string  // see JCQuestionType
  related_lo_id string?
  options string[]       // for multiple-choice questions
}

class JCExamSection {
  section_label string  // "Section A", "Section B", etc.
  instructions_en string
  instructions_ga string?
  questions JCQuestion[]
  total_marks int
  is_optional bool
}

class JCLearningOutcome {
  outcome_id string
  description_en string
  description_ga string?
  strand_id string?
  stage string  // one of the 4 NCCA Junior Cycle stages
}
