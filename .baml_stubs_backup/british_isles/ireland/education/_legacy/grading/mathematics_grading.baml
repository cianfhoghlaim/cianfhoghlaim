// BAML schema: Mathematics Interactive Grading (BIEP v1 Phase 2 — per-subject)
//
// Per-subject interactive grading companion to
// `baml_src/education/marking/mathematics_marking.baml` + the canonical
// `MarkingScheme` + `ExamPaper` (QuestionSection[]). Two functions:
//
//   1. `GradeMathematicsResponse(student_answer, question, marking_scheme)`
//      — score a single LC Mathematics response against the per-question
//        MarkingAllocation, producing a `MathematicsGrade` with per-step
//        marks + concrete + worked-example feedback.
//
//   2. `ExplainMathematicsMarkingScheme(marking_scheme)` — produce the
//      per-subject rationale (why each band sits where it does, which
//      mistakes count how many marks) used to coach the math tutor agent.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Grade output type
// ============================================================================

class MathematicsStepMark {
  step_index int @description("1-indexed step in the worked solution")
  step_label string @description("Label, e.g. 'Set up chain rule', 'Apply dy/dx'")
  marks_available int
  marks_awarded int
  feedback string @description("Per-step feedback (concrete, encouraging)")
}

class MathematicsGrade {
  question_id string
  lo_code string? @description("If the question is linked to an NCCA LO")
  total_marks int
  marks_awarded int
  is_correct bool
  partial_credit_pct float
  is_higher_level bool
  step_marks MathematicsStepMark[]
  overall_feedback string @description("1-3 sentence summary feedback")
  most_common_mistake_made string? @description("If a tagged mistake was detected")
  next_recommended_lo string?
  badge_earned bool @description("True iff partial_credit_pct >= 80")
}

// ============================================================================
// Explanation / rationale output type
// ============================================================================

class MathematicsMarkingRationale {
  marking_scheme_id string
  band_descriptions string[] @description("Human-readable rationale per grade band H1..H7 / O1..O7")
  common_mistake_weightings string[] @description("How each mistake category is penalised")
  typical_full_marks_strategy string @description("What a full-marks response looks like for this scheme")
  partial_credit_strategy string @description("How marks are awarded when the answer is partial")
  difficulty_summary string @description("Short student-facing summary of difficulty")
}

// ============================================================================
// BAML functions (grade + explain)
// ============================================================================

function GradeMathematicsResponse(
  student_answer: string,
  question: "baml_src.education.lc_extraction.exam_paper_layout.Question",
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkAllocation",
  is_higher_level: bool,
) -> MathematicsGrade {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExplainMathematicsMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> MathematicsMarkingRationale {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// test mathematics_grading_smoke {
//   functions [GradeMathematicsResponse]
//   args {
//     student_answer <<< "dy/dx = 3x^2 - 4x + 2 (after applying chain rule wrong, missed a negative sign)" >>>
//     question { q_id { "q3a" } part { "a" } text_en { "Differentiate (x^3 - 2x^2 + 2x)^2" } question_type { WORKED_SOLUTION } marks { 12 } related_lo_id { "LC-MATHS-LO-2.4" } }
//     marking_scheme { q_id { "q3a" } total_marks { 12 } partial_credit_rules { "M1: chain rule, M1: power rule, A1: correct derivative" } common_mistakes { "Sign error when applying chain rule" } sample_answer { "dy/dx = 2(x^3 - 2x^2 + 2x)(3x^2 - 4x + 2)" } }
//     is_higher_level { true }
//   }
// }
