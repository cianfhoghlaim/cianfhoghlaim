// BAML schema: Gaeilge Marking Scheme Extractor (BIEP v1 Phase 2 — per-subject)
//
// Per-subject extension of the canonical `MarkingScheme` class in
// `baml_src/education/lc_extraction/marking_scheme.baml`. Adds the
// Gaeilge (Irish) specific discriminator (GaelSkillType + GaelRegister +
// GaelCommonMistake). Gaeilge is taught IN IRISH — the marking scheme
// itself is bilingual but primary fields are GA.
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum GaelSkillType {
  LEAMHTHUISCINT     @description("Léamhthuiscint — reading comprehension")
  LITRIOCHT          @description("Litríocht — literature analysis (prós / filíocht)")
  CLUASTUISCINT      @description("Cluastuiscint — listening comprehension")
  SCRIBHNEOIREACHT   @description("Scríbhneoireacht — composition")
  GRAMADACH          @description("Gramadach — grammar / conjugation")
  AISTRIUCHAN        @description("Aistriúchán — translation EN ↔ GA")
  COMHRA             @description("Comhrá — conversation / dialogue")
  FILIOCHT_RECAP     @description("Filíocht — poetry memorised recital")
}

enum GaelRegister {
  LITEARTHA     @description("Litearth — literary register")
  GNEITHIUL     @description("Gnéithiúil — formal register")
  LAETHUIL      @description("Laethúil — daily / colloquial register")
  SEANCHAIS     @description("Seanchais — oral tradition register")
  ITHEOIREACHT  @description("Itheoireacht — academic / scholarly")
  CUMASCA       @description("Cumasca — mixed register")
}

enum GaelCommonMistake {
  SINEADH_FADA_MISSING      @description("Missing síneadh fada on Irish vowels")
  GENITIVE_WRONG            @description("Wrong genitive case form on a noun")
  VERBAL_NOUN_AS_NOUN        @description("Used verbal noun where finite verb form was needed")
  PREPOSITION_MISUSE         @description("Wrong preposition usage for the idiomatic expression")
  TRANSLATION_LITERAL        @description("Translation is too literal, lacks native idiom")
  LITERATURE_OUT_OF_CONTEXT  @description("Literature point lacks the prescribed text context")
  COMPOSITION_LANGUAGE_LEVEL @description("Composition language below expected Tánaiste level")
}

class GaelSubjectDiscriminator {
  primary_skill GaelSkillType @description("Dominant skill tested")
  dominant_register GaelRegister @description("Dominant register (Gaeilge register family)")
  has_cluastuiscint bool @description("LC Gaeilge has a cluastuiscint paper")
  composition_word_count_min int? @description("Min words for composition (e.g. 400 for HL)")
  most_common_mistake GaelCommonMistake
  text_ga_primary bool @description("Always true — primary content is in Irish")
}

class GaeilgeMarkingScheme {
  subject string @description("Always 'gaeilge'")
  scheme_code string
  language string @description("Always 'ga' (taught in Irish)")
  level string @description("HL / OL / FDN")
  year int
  source_pdf string

  grade_descriptors GradeDescriptor[]
  mark_allocations MarkAllocation[]

  subject_specific GaelSubjectDiscriminator

  total_marks int
  total_questions int
  cluastuiscint_marks int? @description("Marks allocated to cluastuiscint component")
}

function ExtractGaeilgeMarkingScheme(
  pdf_text: string,
  year: int?,
  level: string?,
) -> GaeilgeMarkingScheme {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    GaeilgeMarkingScheme {
      scheme_code "",
      year 0,
      source_pdf "",
      grade_descriptors null,
      mark_allocations null,
      subject_specific gaelsubjectdiscriminator {},
      total_marks 0,
      total_questions 0,
    }
  }
}

// test gaeilge_marking_extraction_smoke {
//   functions [ExtractGaeilgeMarkingScheme]
//   args {
//     pdf_text <<<
//       "Scéim mharcála don Ghaeilge Ardteistiméireachta 2024. An botún
//        is coitianta: an fhoirceann a bheith in easnamh ar gutaí Gaeilge."
//     >>>
//     year { 2024 }
//     level { "hl" }
//   }
// }
