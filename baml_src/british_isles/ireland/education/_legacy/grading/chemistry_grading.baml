// BAML schema: Chemistry Interactive Grading (BIEP v1 Phase 2 — per-subject)
//
// Per-subject interactive grading companion to
// `baml_src/education/marking/chemistry_marking.baml`. Two functions:
//
//   1. `GradeChemistryResponse(...)` — score a single LC Chemistry
//      response (equation, calculation, structure-drawing, etc.) against
//      the per-question MarkingAllocation, producing a `ChemistryGrade`.
//
//   2. `ExplainChemistryMarkingScheme(...)` — produce the per-subject
//      rationale for the chemistry tutor agent.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

class ChemistryStepMark {
  step_index int
  step_label string @description("e.g. 'Balance equation', 'State symbols', 'Convert moles'")
  marks_available int
  marks_awarded int
  feedback string
}

class ChemistryGrade {
  question_id string
  lo_code string?
  total_marks int
  marks_awarded int
  is_correct bool
  partial_credit_pct float
  is_higher_level bool
  step_marks ChemistryStepMark[]
  overall_feedback string
  detector_mistakes string[] @description("e.g. 'unbalanced_equation', 'state_symbol_missing'")
  next_recommended_lo string?
  badge_earned bool
}

class ChemistryMarkingRationale {
  marking_scheme_id string
  band_descriptions string[]
  experiment_question_weighting string @description("How the 4 mandatory experiment questions are graded")
  state_symbol_rule string @description("Why (s),(l),(g),(aq) matter so much for full marks")
  common_mistake_penalties string[]
  difficulty_summary string
}

function GradeChemistryResponse(
  student_answer: string,
  question: "baml_src.education.lc_extraction.exam_paper_layout.Question",
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkAllocation",
  is_higher_level: bool,
) -> ChemistryGrade {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function ExplainChemistryMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> ChemistryMarkingRationale {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// test chemistry_grading_smoke {
//   functions [GradeChemistryResponse]
//   args {
//     student_answer <<< "Mg(s) + HCl(aq) → MgCl2 + H2 (missing state symbols, unbalanced)" >>>
//     question { q_id { "q4a" } part { "a" } text_en { "Write the balanced equation for magnesium + hydrochloric acid" } question_type { BALANCED_EQUATION } marks { 6 } related_lo_id { "LC-CHEM-LO-3.1" } }
//     marking_scheme { q_id { "q4a" } total_marks { 6 } partial_credit_rules { "2 marks formula, 2 marks balancing, 2 marks state symbols" } common_mistakes { "Forgot state symbols; unbalanced" } sample_answer { "Mg(s) + 2HCl(aq) → MgCl2(aq) + H2(g)" } }
//     is_higher_level { false }
//   }
// }
