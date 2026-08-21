// BAML schema: Chemistry Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// Chemistry-specific discriminator (ChemQuestionType + ChemExperimentType +
// ChemCommonMistake) for the 4 mandatory NCCA experiment questions + the
// short-answer + structured-response mix.
//
// Replaces the generic ExtractMarkingSchemeGuideline path for
// `subject="chemistry"`.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum ChemQuestionType {
  SHORT_ANSWER      @description("Short factual answer (1-2 sentences)")
  STRUCTURE_DRAWING @description("Lewis structure, organic structure, 3D drawing")
  BALANCED_EQUATION @description("Balance the chemical equation")
  CALCULATION       @description("Stoichiometry or moles calculation")
  EXPERIMENT        @description("Mandatory experiment question (one of 4 from NCCA list)")
  EXTENDED_RESPONSE @description("Longer essay-style answer (organic pathways, periodic trends)")
  DIAGRAM_BASED     @description("Interpret a phase diagram / energy profile / titration curve")
}

enum ChemExperimentType {
  TITRATION       @description("Acid-base titration")
  REACTIVITY      @description("Reactivity series / displacement")
  DISTILLATION    @description("Distillation / separation techniques")
  INDICATOR       @description("Indicator + pH")
  ELECTROLYSIS    @description("Electrolysis of aqueous solution")
  ORGANIC_PREP    @description("Preparation of an organic compound")
  WATER_ANALYSIS  @description("Water analysis (hardness, treatment)")
  NONE            @description("No experiment question in this paper")
}

enum ChemCommonMistake {
  UNBALANCED_EQUATION   @description("Did not balance the chemical equation fully")
  STATE_SYMBOL_MISSING  @description("Omitted (s), (l), (g), or (aq) state symbol")
  SIGNIFICANT_FIGURES   @description("Wrong significant figures in calculation")
  MOLAR_RATIO_WRONG     @description("Wrong mole ratio from balanced equation")
  PHENOLPHTHALEIN_NEAR_END @description("Stopped titration too early before colour change")
  HYDRATION_FORGOTTEN   @description("Forgot hydrate waters in crystal calculations")
  LE_CHATELIER_MISREAD  @description("Misread Le Chatelier principle direction")
  ISOMER_CONFUSION      @description("Confused isomer pair (functional group isomer)")
}

class ChemSubjectDiscriminator {
  primary_topic string @description("e.g. 'Organic Chemistry', 'Acids & Bases', 'Kinetics'")
  has_mandatory_experiment bool @description("Always true for LC Chemistry")
  experiment_types ChemExperimentType[] @description("The 4 mandatory NCCA experiments referenced")
  dominant_question_types ChemQuestionType[] @description("Mix in this paper")
  most_common_mistake ChemCommonMistake
  has_data_booklet bool @description("LC Chemistry always provides a data booklet")
}

class ChemistryMarkingScheme {
  subject string @description("Always 'chemistry'")
  scheme_code string
  language string
  level string @description("HL / OL")
  year int
  source_pdf string

  grade_descriptors GradeDescriptor[]
  mark_allocations MarkAllocation[]

  subject_specific ChemSubjectDiscriminator

  total_marks int
  total_questions int
  mandatory_experiment_questions int @description("Usually 4")
}

function ExtractChemistryMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?,
) -> ChemistryMarkingScheme {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// test chemistry_marking_extraction_smoke {
//   functions [ExtractChemistryMarkingScheme]
//   args {
//     pdf_text <<<
//       "Marking scheme for LC Chemistry Paper 2 HL 2024. Mandatory
//        experiments: titration, distillation. Most common mistake:
//        student forgot to include state symbols in the balanced equation."
//     >>>
//     year { 2024 }
//     level { "hl" }
//   }
// }
