// BAML schema: English Interactive Grading (BIEP v1 Phase 2 — per-subject)
//
// Per-subject interactive grading companion to
// `baml_src/education/marking/english_marking.baml`. Two functions:
//
//   1. `GradeEnglishResponse(...)` — score a single LC English response
//      (comprehension / comparative essay / composition) against the
//      MarkingAllocation, producing an `EnglishGrade`.
//
//   2. `ExplainEnglishMarkingScheme(...)` — produce the per-subject
//      rationale for the english tutor agent.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

class EnglishStepMark {
  step_index int
  step_label string @description("e.g. 'Identify thesis', 'Cite prescribed text', 'Analyse technique'")
  marks_available int
  marks_awarded int
  feedback string
}

class EnglishGrade {
  question_id string
  lo_code string?
  total_marks int
  marks_awarded int
  is_correct bool
  partial_credit_pct float
  is_higher_level bool
  genre_tested string @description("e.g. 'COMPREHENSION', 'COMPARATIVE', 'COMPOSITION'")
  step_marks EnglishStepMark[]
  overall_feedback string
  detector_mistakes string[] @description("e.g. 'paraphrase_not_analysis', 'missing_citation', 'vocab_generic'")
  next_recommended_lo string?
  badge_earned bool
}

class EnglishMarkingRationale {
  marking_scheme_id string
  band_descriptions string[]
  comparative_essay_strategy string @description("How 3-text comparative essays are graded")
  composition_strategy string @description("How composition is graded post-2017 spec")
  annotation_technique_examples string[] @description("Concrete examples of high-quality annotation")
  difficulty_summary string
}

function GradeEnglishResponse(
  student_answer: string,
  question: "baml_src.education.lc_extraction.exam_paper_layout.Question",
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.LCMarkAllocation",
  is_higher_level: bool
) -> EnglishGrade {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

function ExplainEnglishMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme"
) -> EnglishMarkingRationale {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// test english_grading_smoke {
//   functions [GradeEnglishResponse]
//   args {
//     student_answer <<< "In the play, the protagonist is sad throughout." >>>
//     question { q_id { "q3b" } part { "b" } text_en { "Analyse how King Lear portrays madness in Act 3" } question_type { EXTENDED_RESPONSE } marks { 20 } related_lo_id { "LC-ENG-LO-3.2" } }
//     marking_scheme { q_id { "q3b" } total_marks { 20 } partial_credit_rules { "8 marks textual evidence, 8 marks analysis, 4 marks structure" } common_mistakes { "Paraphrases instead of analyses; no line refs" } sample_answer { "Lear's descent into madness is signalled through the storm on the heath (Act 3.2)..." } }
//     is_higher_level { true }
//   }
// }
