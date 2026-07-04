// BAML schema: Cross-Linguistic Concept Mapping (EN ↔ GA)
//
// Used by the LC5-subject pipeline to link equivalent topics between
// English-language and Irish-language syllabi. Critical for gaeilge
// (which is taught through Irish) but also relevant to chemistry /
// geography / maths where the L1 vs L2 translation matters.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

class GaelicTopic {
  ga_term: string
  ga_part_of_speech: string  @description("noun, verb, adjective, etc.")
  ga_definition_en: string
  source_pdf: string
  subject: string
}

class EnglishEquivalent {
  en_term: string
  en_definition: string
  matches_se_focmara_clause: bool  @description("True if also found in the Foclóir Maith / Gramadach na Gaeilge")
}

class CrossLinguisticConcept {
  subject: string
  concept_id: string
  gaelic: GaelicTopic
  english: EnglishEquivalent
  // Translation fidelity: 1.0 = exact equivalent, 0.0 = culture-specific
  translation_fidelity: float
  // Cultural / contextual notes
  notes: string?
}
