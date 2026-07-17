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
) -> GaeilgeGrade {
  client Default
  prompt #"
    Is grádaitheoir Gaeilge don Ardteistiméireacht thú. Déan marcáil ar
    fhreagra an dalta de réir na scéime marcála.

    Ceist:
    - ID: {{ question.q_id }}
    - Cineál: {{ question.question_type }}
    - Marcanna: {{ question.marks }}

    Scéim mharcála:
    - q_id: {{ marking_scheme.q_id }}
    - total_marks: {{ marking_scheme.total_marks }}
    - partial_credit_rules: {{ marking_scheme.partial_credit_rules }}
    - common_mistakes: {{ marking_scheme.common_mistakes }}
    - sample_answer: {{ marking_scheme.sample_answer }}

    Ardleibhéal: {{ is_higher_level }}

    Freagra an dalta:
    ---
    {{ student_answer }}
    ---

    Ríomh:
    - total_marks + GaeilgeStepMark[]
    - marks_awarded + is_correct + partial_credit_pct (0-100)
    - skill_tested (LEAMHTHUISCINT / LITRIOCHT / GRAMADACH)
    - overall_feedback_ga (Gaeilge, spreagúil)
    - detector_mistakes (e.g. sineadh_fada_missing, verbal_noun_misuse)
    - badge_earned (true iff partial_credit_pct >= 80)

    {{ ctx.output_format }}
  "#
}

function ExplainGaeilgeMarkingScheme(
  marking_scheme_id: string,
  marking_scheme: "baml_src.education.lc_extraction.marking_scheme.MarkingScheme",
) -> GaeilgeMarkingRationale {
  client Default
  prompt #"
    Is mínitheoir scéimeanna marcála Gaeilge don Ardteistiméireacht
    thú. Léirigh an réasúnaíocht atá taobh thiar den scéim.

    Marking scheme ID: {{ marking_scheme_id }}
    Marking scheme: {{ marking_scheme }}

    Tabhair ar ais:
    - band_descriptions_ga (cur síos ar gach banda, as Gaeilge)
    - cluastuiscint_weighting: conas a mharcáiltear an chluastuiscint
    - composition_strategy_ga: conas a roinntear marcanna scríbhneoireachta
    - sineadh_fada_rule: cén fáth a bhfuil an tsíneadh fada tábhachtach
    - difficulty_summary_ga

    {{ ctx.output_format }}
  "#
}

test gaeilge_grading_smoke {
  functions [GradeGaeilgeResponse]
  args {
    student_answer <<< "Léigh mé an sliocht agus cheap mé go raibh sé go maith." >>>
    question { q_id { "q1a" } part { "a" } text_en { "Déan cur síos ar an bpríomhphearsa sa sliocht" } text_ga { "Déan cur síos ar an bpríomhphearsa sa sliocht" } question_type { EXTENDED_RESPONSE } marks { 10 } related_lo_id { "LC-GAEL-LO-2.1" } }
    marking_scheme { q_id { "q1a" } total_marks { 10 } partial_credit_rules { "4 mharc sainiúlacht, 4 mharc tráchta, 2 mharc stíl" } common_mistakes { "Tuairimíocht gan ábhar ón téacs" } sample_answer { "Is é Seán an príomhphearsa sa sliocht; is léir ón gcomharthaíocht a thugann an t-údar air..." } }
    is_higher_level { true }
  }
}
