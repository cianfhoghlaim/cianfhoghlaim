// BAML schema: Geography Interactive Grading (BIEP v1 Phase 2 — per-subject)
//
// Per-subject interactive grading companion to
// `baml_src/education/marking/geography_marking.baml`. Two functions:
//
//   1. `GradeGeographyResponse(...)` — score a single LC Geography
//      response (OS-map, discursive essay, case study) against the
//      MarkingAllocation.
//
//   2. `ExplainGeographyMarkingScheme(...)` — produce the per-subject
//      rationale for the geography tutor agent.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

class GeographyStepMark {
  step_index int
  step_label string @description("e.g. 'Identify river feature on OS map', 'Apply grid reference', 'Case-study detail'")
  marks_available int
  marks_awarded int
  feedback string
}

class GeographyGrade {
  question_id string
  lo_code string?
  total_marks int
  marks_awarded int
  is_correct bool
  partial_credit_pct float
  is_higher_level bool
  skill_tested string @description("e.g. 'OS_MAP', 'DISCURSIVE_ESSAY', 'CASE_STUDY'")
  step_marks GeographyStepMark[]
  overall_feedback string
  detector_mistakes string[] @description("e.g. 'OS_map_misread', 'case_study_vague'")
  next_recommended_lo string?
  badge_earned bool
}

class GeographyMarkingRationale {
  marking_scheme_id string
  band_descriptions string[]
  os_map_question_weighting string @description("How OS map Qs are graded")
  discursive_essay_strategy string @description("How SRP / discursive essays are graded")
  case_study_requirement string @description("Why place-specific detail is required")
  difficulty_summary string
}

function GradeGeographyResponse(
  student_answer: string,
  question: "baml_src.education.lc_extraction.exam_paper_layout.Question",
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkAllocation",
  is_higher_level: bool,
) -> GeographyGrade {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExplainGeographyMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> GeographyMarkingRationale {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// test geography_grading_smoke {
//   functions [GradeGeographyResponse]
//   args {
//     student_answer <<< "The river meander is located at grid reference O 234 567." >>>
//     question { q_id { "q2a" } part { "a" } text_en { "Identify a meander on the OS map" } question_type { DIAGRAM_BASED } marks { 6 } related_lo_id { "LC-GEOG-LO-1.2" } }
//     marking_scheme { q_id { "q2a" } total_marks { 6 } partial_credit_rules { "2 marks grid ref, 2 marks feature type, 2 marks label" } common_mistakes { "Easting/northing swapped" } sample_answer { "A meander is visible at O 234 567 on the River Shannon" } }
//     is_higher_level { false }
//   }
// }
