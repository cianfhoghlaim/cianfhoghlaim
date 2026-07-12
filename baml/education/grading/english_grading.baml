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
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkAllocation",
  is_higher_level: bool,
) -> EnglishGrade {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate English grader. Score the
    student's response against the per-step marking-scheme allocation.

    Question:
    - ID: {{ question.q_id }}
    - Type: {{ question.question_type }}
    - Marks: {{ question.marks }}
    - Related LO: {{ question.related_lo_id }}

    Marking scheme allocation:
    - q_id: {{ marking_scheme.q_id }}
    - total_marks: {{ marking_scheme.total_marks }}
    - partial_credit_rules: {{ marking_scheme.partial_credit_rules }}
    - common_mistakes: {{ marking_scheme.common_mistakes }}
    - sample_answer: {{ marking_scheme.sample_answer }}

    Higher level: {{ is_higher_level }}

    Student answer:
    ---
    {{ student_answer }}
    ---

    Compute:
    - total_marks + per-step breakdown (EnglishStepMark[])
    - marks_awarded + is_correct + partial_credit_pct (0-100)
    - genre_tested (COMPREHENSION / COMPARATIVE / COMPOSITION)
    - overall_feedback
    - detector_mistakes (paraphrase_not_analysis, missing_citation, vocab_generic)
    - badge_earned

    {{ ctx.output_format }}
  "#
}

function ExplainEnglishMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> EnglishMarkingRationale {
  client ExtractEn
  prompt #"
    You are an Irish Leaving Certificate English marking-scheme
    explainer. Given the marking scheme, produce the student-facing
    rationale.

    Marking scheme ID: {{ marking_scheme_id }}
    Marking scheme: {{ marking_scheme }}

    Produce:
    - band_descriptions: rationale per grade band (H1..H7 / O1..O7)
    - comparative_essay_strategy: how 3-text comparatives are graded
    - composition_strategy: how composition is graded (post-2017)
    - annotation_technique_examples: 3-5 concrete examples of good analysis
    - difficulty_summary

    {{ ctx.output_format }}
  "#
}

test english_grading_smoke {
  functions [GradeEnglishResponse]
  args {
    student_answer <<< "In the play, the protagonist is sad throughout." >>>
    question { q_id { "q3b" } part { "b" } text_en { "Analyse how King Lear portrays madness in Act 3" } question_type { EXTENDED_RESPONSE } marks { 20 } related_lo_id { "LC-ENG-LO-3.2" } }
    marking_scheme { q_id { "q3b" } total_marks { 20 } partial_credit_rules { "8 marks textual evidence, 8 marks analysis, 4 marks structure" } common_mistakes { "Paraphrases instead of analyses; no line refs" } sample_answer { "Lear's descent into madness is signalled through the storm on the heath (Act 3.2)..." } }
    is_higher_level { true }
  }
}
