// BAML schema: Gaeilge Interactive Grading (BIEP v1 Phase 2 — per-subject)
//
// Per-subject interactive grading companion to
// `baml_src/education/marking/gaeilge_marking.baml`. Two functions in
// Irish (Gaeilge-medium feedback is canonical for this subject).
//
//   1. `GradeGaeilgeResponse(...)` — score a single LC Gaeilge response
//      (Léamhthuiscint / Litríocht / Scríbhneoireacht) against the
//      MarkingAllocation, producing a `GaeilgeGrade`.
//
//   2. `ExplainGaeilgeMarkingScheme(...)` — produce the per-subject
//      rationale (Irish-language rationale is canonical here).
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

class GaeilgeStepMark {
  step_index int
  step_label string @description("e.g. 'Freagra ar cheist', 'Anailís litríochta'")
  marks_available int
  marks_awarded int
  feedback_ga string  @description("Gaeilge feedback (canonical)")
  feedback_en string? @description("English translation helper, optional")
}

class GaeilgeGrade {
  question_id string
  lo_code string?
  total_marks int
  marks_awarded int
  is_correct bool
  partial_credit_pct float
  is_higher_level bool
  skill_tested string @description("e.g. 'LEAMHTHUISCINT', 'LITRIOCHT', 'GRAMADACH'")
  step_marks GaeilgeStepMark[]
  overall_feedback_ga string  @description("Overall Gaeilge feedback (canonical)")
  overall_feedback_en string? @description("English translation helper, optional")
  detector_mistakes string[] @description("e.g. 'sineadh_fada_missing', 'verbal_noun_misuse'")
  next_recommended_lo string?
  badge_earned bool
}

class GaeilgeMarkingRationale {
  marking_scheme_id string
  band_descriptions_ga string[] @description("Bainc-chur síos ar gach banda (Gaeilge)")
  cluastuiscint_weighting string @description("Conas a mharcáiltear an chluastuiscint")
  composition_strategy_ga string @description("Conas a roinntear marcanna ar an scríbhneoireacht")
  sineadh_fada_rule string @description("Cén fáth a bhfuil an tsíneadh fada chomh tábhachtach")
  difficulty_summary_ga string @description("Achoimre ghairid ar an deacracht")
}

function GradeGaeilgeResponse(
  student_answer: string,
  question: "baml_src.education.lc_extraction.exam_paper_layout.Question",
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkAllocation",
  is_higher_level: bool,
) -> GaeilgeGrade {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

function ExplainGaeilgeMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> GaeilgeMarkingRationale {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// test gaeilge_grading_smoke {
//   functions [GradeGaeilgeResponse]
//   args {
//     student_answer <<< "Léigh mé an sliocht agus cheap mé go raibh sé go maith." >>>
//     question { q_id { "q1a" } part { "a" } text_en { "Déan cur síos ar an bpríomhphearsa sa sliocht" } text_ga { "Déan cur síos ar an bpríomhphearsa sa sliocht" } question_type { EXTENDED_RESPONSE } marks { 10 } related_lo_id { "LC-GAEL-LO-2.1" } }
//     marking_scheme { q_id { "q1a" } total_marks { 10 } partial_credit_rules { "4 mharc sainiúlacht, 4 mharc tráchta, 2 mharc stíl" } common_mistakes { "Tuairimíocht gan ábhar ón téacs" } sample_answer { "Is é Seán an príomhphearsa sa sliocht; is léir ón gcomharthaíocht a thugann an t-údar air..." } }
//     is_higher_level { true }
//   }
// }
