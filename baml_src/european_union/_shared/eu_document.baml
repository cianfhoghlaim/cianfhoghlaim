// Multilingual EU document class.
//
// The canonical BAML extraction target for the EU institutional
// pipeline. One row per `(document_id, language)` is mapped to one
// `EUDocument` instance.

class EUMultilingualText {
  bg string? @description("Bulgarian text")
  hr string? @description("Croatian text")
  cs string? @description("Czech text")
  da string? @description("Danish text")
  nl string? @description("Dutch text")
  en string? @description("English text")
  et string? @description("Estonian text")
  fi string? @description("Finnish text")
  fr string? @description("French text")
  de string? @description("German text")
  el string? @description("Greek text")
  hu string? @description("Hungarian text")
  ga string? @description("Irish / Gaeilge text")
  it string? @description("Italian text")
  lv string? @description("Latvian text")
  lt string? @description("Lithuanian text")
  mt string? @description("Maltese text")
  pl string? @description("Polish text")
  pt string? @description("Portuguese text")
  ro string? @description("Romanian text")
  sk string? @description("Slovak text")
  sl string? @description("Slovenian text")
  es string? @description("Spanish text")
  sv string? @description("Swedish text")
}

class EUDocument {
  document_id string @description("The institution-specific document id (CELEX, case id, dataset id, publication id, ...)")
  institution EUInstitution @description("The EU institution that published the document")
  language EULanguage @description("The language this row carries")
  title string @description("Document title in the row's language")
  summary string? @description("Short summary in the row's language")
  publication_date string? @description("ISO 8601 publication date")
  official_status string? @description("in_force / amended / repealed / published")
  document_kind string? @description("regulation / directive / decision / treaty / case_law / dataset_metadata / press_release / epar / national_education_structure / parliamentary_document / council_document / cellar_resource / eu_publication / portal_entry / eu_publication / surveillance_dataset / vocational_training_resource / school_education_resource / ehds_dataset")
  source_url string @description("Canonical source URL")
  content_hash string? @description("Hash of the document body for change detection")
  multilingual_text EUMultilingualText? @description("Cross-language metadata when the document carries translations")
  @@stream.done
}

function ExtractEUDocument(
  language: EULanguage,
  text: string
) -> EUDocument {
  client Claude
  prompt #"
    Extract a structured multilingual EU document from the following
    raw text. The document is published in {{ language }} by one of
    the EU institutions.

    Return a single EUDocument with the canonical multilingual
    document shape. Preserve the original text in the row's language;
    do NOT translate.

    Document text:
    {{ text }}

    {{ ctx.output_format }}
  "#
}


// ============================================================
// Bilingual English + Irish extraction (added by 2026-07-15-eu-multilingual-irish-english-v1)
// ============================================================

class BilingualTextEnGa {
  en string? @description("English text")
  ga string? @description("Irish / Gaeilge text")
}

class EUExtractableBilingualDocument {
  url string
  institution EUInstitution
  language EULanguage
  celex_id string?
  title BilingualTextEnGa
  summary BilingualTextEnGa?
  publication_date string?
  source_url string
  content_hash string?
  language_availability map<string, string> @description("Per-language availability: 'full' | 'partial' | 'none'")
}

function ExtractEUDocumentBilingualEnGa(
  institution: EUInstitution,
  language: EULanguage,
  text: string
) -> EUExtractableBilingualDocument {
  client Claude
  prompt #"
    Extract the canonical EU document from the following text.
    When the source document is in English or Irish (Gaeilge), populate
    the corresponding BilingualTextEnGa fields. When in another
    language, set the en/ga fields to null and the language_availability
    accordingly.

    Institution: {{ institution }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
