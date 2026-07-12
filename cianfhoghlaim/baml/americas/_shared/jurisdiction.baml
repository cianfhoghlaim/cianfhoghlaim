// Americas shared jurisdiction BAML schema.

class AmericasJurisdictionMetadata {
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug (us_us_ca, bra, mex, ven)")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase) of the parent country for sub-state jurisdictions")
  country_name string? @description("The English-language country name")
  official_languages string[] @description("List of the official language codes the jurisdiction publishes in (ISO 639-1)")
  jurisdiction_level string @description("sovereign_nation | us_state | canadian_province | mexican_state | brazilian_state | dependent_territory")
  political_status string? @description("federal_republic | presidential_republic | parliamentary_republic | federation | constitutional_monarchy")
  source_url string
  content_hash string?
}

function extract_americas_jurisdiction_metadata(
  jurisdiction: string,
  language: string,
  text: string
) -> AmericasJurisdictionMetadata {
  client Claude
  prompt #"
    Extract the canonical Americas jurisdiction metadata record from
    the following text. The jurisdiction is the sub-state slug or
    ISO 3166-1 alpha-3 of the jurisdiction the document describes.

    Jurisdiction: {{ jurisdiction }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
