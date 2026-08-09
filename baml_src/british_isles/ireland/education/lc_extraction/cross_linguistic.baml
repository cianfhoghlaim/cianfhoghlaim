// BAML schema: Cross-Linguistic Concept Mapping (EN ↔ GA)
//
// Used by the LC5-subject pipeline to link equivalent topics between
// English-language and Irish-language syllabi. Critical for gaeilge
// (which is taught through Irish) but also relevant to chemistry /
// geography / maths where the L1 vs L2 translation matters.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

class GaelicTopic {
  ga_term string
  ga_part_of_speech string  @description("noun, verb, adjective, etc.")
  ga_definition_en string
  source_pdf string
  subject string
}

class EnglishEquivalent {
  en_term string
  en_definition string
  matches_se_focmara_clause bool  @description("True if also found in the Foclóir Maith / Gramadach na Gaeilge")
}

class CrossLinguisticConcept {
  subject string
  concept_id string
  gaelic GaelicTopic
  english EnglishEquivalent
  // Translation fidelity: 1.0 = exact equivalent, 0.0 = culture-specific
  translation_fidelity float
  // Cultural / contextual notes
  notes string?

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`.
  lineage LineageTrace?
}

// ============================================================================
// BAML function: Cross-Linguistic Concept Extraction (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
// this `ExtractCrossLinguisticConcept` function is the v3 canonical entry
// point. The `CrossLinguisticConcept` class above is the return type.
//
// The function is invoked by the Ireland LC + JC pipelines for the
// gaeilge (and other bilingual) subjects to map topics between the
// English-language and Irish-language versions of the same syllabus.

function ExtractCrossLinguisticConcept(
  pdf_text_en: string,
  pdf_text_ga: string?,
  subject: string?,
  concept_id: string?,
) -> CrossLinguisticConcept[] {
  client BIEPV3Extract
  prompt #"
    You are an expert at cross-linguistic concept mapping between English
    and Irish (Gaeilge) versions of the same Irish Leaving Certificate
    {{ subject }} syllabus.

    For each cross-linguistic concept you find, extract:
    - The subject slug
    - The concept_id (e.g. 'LC-MA-2.1')
    - The Irish (Gaeilge) topic: ga_term, ga_part_of_speech, ga_definition_en, source_pdf
    - The English equivalent: en_term, en_definition, matches_se_focmara_clause
    - Translation fidelity (1.0 = exact equivalent, 0.0 = culture-specific)
    - Optional cultural / contextual notes

    English PDF text:
    {{ pdf_text_en }}

    Irish PDF text:
    {{ pdf_text_ga }}

    Subject:
    {{ subject }}

    Concept ID (optional):
    {{ concept_id }}

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}
