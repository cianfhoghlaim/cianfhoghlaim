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

function ExtractCommonwealthJurisdictionMetadata(
  countryCode: string,
  language: string,
  text: string
) -> CommonwealthJurisdictionMetadata {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
