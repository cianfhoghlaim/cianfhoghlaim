// BAML schema: Computer Science Interactive Grading (BIEP v1 Phase 2 — per-subject)
//
// Per-subject interactive grading companion to
// `baml_src/education/marking/computer_science_marking.baml`. Two functions:
//
//   1. `GradeComputerScienceResponse(...)` — score a single LC Computer
//      Science response (pseudo-code / SQL / Big-O analysis / extended
//      algorithm answer) against the MarkingAllocation.
//
//   2. `ExplainComputerScienceMarkingScheme(...)` — produce the
//      per-subject rationale for the CS tutor agent.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

class ComputerScienceStepMark {
  step_index int
  step_label string @description("e.g. 'Identify loop bound', 'Apply GROUP BY', 'Derive Big-O'")
  marks_available int
  marks_awarded int
  feedback string
}

class ComputerScienceGrade {
  question_id string
  lo_code string?
  total_marks int
  marks_awarded int
  is_correct bool
  partial_credit_pct float
  is_higher_level bool
  question_type_tested string @description("e.g. 'PSEUDOCODE', 'SQL', 'BIG_O', 'CODE_TRACE'")
  step_marks ComputerScienceStepMark[]
  overall_feedback string
  detector_mistakes string[] @description("e.g. 'off_by_one', 'missing_group_by', 'big_o_miscalculated'")
  next_recommended_lo string?
  badge_earned bool
}

class ComputerScienceMarkingRationale {
  marking_scheme_id string
  band_descriptions string[]
  pseudo_code_coding_style string @description("What pseudocode style earns full marks")
  big_o_analysis_strategy string @description("How Big-O questions are graded")
  sql_aggregation_strategy string @description("How SQL aggregation queries are graded")
  difficulty_summary string
}

function GradeComputerScienceResponse(
  student_answer: string,
  question: "baml_src.education.lc_extraction.exam_paper_layout.Question",
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkAllocation",
  is_higher_level: bool,
) -> ComputerScienceGrade {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExplainComputerScienceMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> ComputerScienceMarkingRationale {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// test computer_science_grading_smoke {
//   functions [GradeComputerScienceResponse]
//   args {
//     student_answer <<< "SELECT name FROM students WHERE class = 'CS';" >>>
//     question { q_id { "q4a" } part { "a" } text_en { "Write a SQL query to count students per class" } question_type { DATABASE_QUERY } marks { 6 } related_lo_id { "LC-CS-LO-4.1" } }
//     marking_scheme { q_id { "q4a" } total_marks { 6 } partial_credit_rules { "2 marks SELECT, 2 marks COUNT, 2 marks GROUP BY" } common_mistakes { "Forgot GROUP BY" } sample_answer { "SELECT class, COUNT(*) FROM students GROUP BY class;" } }
//     is_higher_level { false }
//   }
// }
