// Commonwealth of Nations shared jurisdiction BAML schema.

class CommonwealthJurisdictionMetadata {
  country_code string @description("ISO 3166-1 alpha-3 (lowercase) of the country the document is about")
  country_name string? @description("The English-language name of the country")
  region string? @description("Commonwealth region — africa | asia | caribbean | europe | pacific | americas")
  official_languages string[] @description("List of the official language codes the jurisdiction publishes in (ISO 639-1)")
  jurisdiction_level string @description("commonwealth_member | commonwealth_associated")
  political_status string? @description("constitutional_monarchy | parliamentary_republic | federal_republic | presidential_republic | unitary_state | federation")
  head_of_state string? @description("The current head of state (monarch for the 15 Commonwealth realms; otherwise president or equivalent)")
  source_url string
  content_hash string?
}

function extract_commonwealth_jurisdiction_metadata(
  country_code: string,
  language: string,
  text: string
) -> CommonwealthJurisdictionMetadata {
  client Claude
  prompt #"
    Extract the canonical Commonwealth jurisdiction metadata record
    from the following text. The country_code is the ISO 3166-1 alpha-3
    of the country the document describes.

    Country: {{ country_code }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
